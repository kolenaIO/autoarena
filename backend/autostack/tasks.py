import numpy as np

from autostack.api import api as API
from autostack.api.service import TaskService, JudgeService
from autostack.judge import ABShufflingJudge, OllamaJudge
from autostack.store.database import get_database_connection
from autostack.store.seed import reseed_elo_scores


def recompute_confidence_intervals(project_id: int) -> None:
    task_id = TaskService.create(project_id, "recompute-confidence-intervals").id
    try:
        with get_database_connection() as conn:
            reseed_elo_scores(conn, project_id)
    finally:
        TaskService.finish(task_id)


def auto_judge(project_id: int, model_id: int, model_name) -> None:
    status = f"Started auto-judge task for model '{model_name}'"
    task_id = TaskService.create(project_id, "auto-judge", status).id
    try:
        # 1. get pairs eligible for judging
        with get_database_connection(read_only=True) as conn:
            df_h2h = conn.execute(
                """
                SELECT
                    ra.prompt AS prompt,
                    ra.id AS result_a_id,
                    ra.response AS response_a,
                    rb.id AS result_b_id,
                    rb.response AS response_b,
                    rb.model_id AS model_b_id
                FROM result ra
                JOIN result rb ON ra.prompt = rb.prompt AND rb.model_id != ra.model_id
                JOIN model mb ON rb.model_id = mb.id
                WHERE ra.model_id = $model_id
                AND mb.project_id = $project_id
                """,
                dict(project_id=project_id, model_id=model_id),
            ).df()
        status = f"Found {len(df_h2h)} battles with {len(set(df_h2h["model_b_id"]))} models to judge"
        TaskService.update(task_id, status=status, progress=0)

        # TODO: actually implement judge selection logic
        # 2. get judge(s) configured for judging
        base_judge = OllamaJudge("gemma2:9b")  # OpenAIJudge("gpt-4o-mini")
        judge = ABShufflingJudge(base_judge)
        judge_id = JudgeService.create_idempotent(project_id, judge).id
        TaskService.update(task_id, status=f"Using judge '{judge.name}'", progress=0)

        # 3. stream judgement requests
        head_to_heads = [
            API.HeadToHead(**r)
            for _, r in df_h2h[["prompt", "result_a_id", "response_a", "result_b_id", "response_b"]].iterrows()
        ]
        batch_size = 8
        n_batches = len(head_to_heads) // batch_size
        responses = []
        for i, batch in enumerate(np.array_split(head_to_heads, n_batches)):
            responses.extend(judge.judge_batch(batch))  # TODO: stream to database?
            status = f"Judged {len(responses)} of {len(head_to_heads)} battles"
            TaskService.update(task_id, status, progress=(i + 1) / n_batches)

        # 4. upload judgements to database
        with get_database_connection() as conn:
            df_h2h_judged = df_h2h.copy()
            df_h2h_judged["judge_id"] = judge_id
            df_h2h_judged["winner"] = responses
            conn.execute("""
                INSERT INTO battle (result_a_id, result_b_id, judge_id, winner)
                SELECT result_a_id, result_b_id, judge_id, winner
                from df_h2h_judged
            """)

            # 5. recompute elo scores and confidence intervals
            reseed_elo_scores(conn, project_id)
        TaskService.update(task_id, "Recomputed Elo scores and confidence intervals", progress=1)
        TaskService.finish(task_id)
    except Exception as e:
        TaskService.finish(task_id, f"Crashed ({e})")
