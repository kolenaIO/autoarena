import numpy as np

from autostack.api import api as API
from autostack.api.api import JudgeType
from autostack.service.judge import JudgeService
from autostack.service.task import TaskService
from autostack.service.elo import EloService
from autostack.judge.utils import ABShufflingJudge
from autostack.judge.factory import judge_factory
from autostack.store.database import get_database_connection


def recompute_confidence_intervals(project_id: int) -> None:
    task_id = TaskService.create(project_id, "recompute-confidence-intervals").id
    try:
        EloService.reseed_scores(project_id)
    finally:
        TaskService.finish(task_id)


def auto_judge(project_id: int, model_id: int, model_name) -> None:
    # 1. get judge(s) configured for judging
    all_judges = JudgeService.get_all(project_id)
    enabled_auto_judges = [j for j in all_judges if j.enabled and j.judge_type is not JudgeType.HUMAN]
    if len(enabled_auto_judges) == 0:
        return  # do nothing if no judges are configured

    status = f"Started auto-judge task for model '{model_name}'"
    task_id = TaskService.create(project_id, "auto-judge", status).id

    try:
        # TODO: implement multi-judge?
        # 2. instantiate judge(s)
        if len(enabled_auto_judges) > 1:
            status = f"Ignoring {len(enabled_auto_judges) - 1} judges in favor of first"
            TaskService.update(task_id, status=status, progress=0)
        base_judge = enabled_auto_judges[0]
        judge = ABShufflingJudge(judge_factory(base_judge))
        judge_id = base_judge.id
        TaskService.update(task_id, status=f"Using judge '{judge.name}'", progress=0)

        # 3. get pairs eligible for judging
        with get_database_connection() as conn:
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
        if len(df_h2h) == 0:
            TaskService.update(task_id, status="No head-to-heads found, exiting", progress=1)
            return
        status = f"Found {len(df_h2h)} head-to-heads with {len(set(df_h2h["model_b_id"]))} models to judge"
        TaskService.update(task_id, status=status, progress=0)

        # 4. stream judgement requests
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
            TaskService.update(task_id, status, progress=0.95 * ((i + 1) / n_batches))

        # 5. upload judgements to database
        with get_database_connection() as conn:
            df_h2h_judged = df_h2h.copy()
            df_h2h_judged["judge_id"] = judge_id
            df_h2h_judged["winner"] = responses
            # TODO: does there need to be any conflict resolution here?
            conn.execute("""
                INSERT INTO battle (result_id_slug, result_a_id, result_b_id, judge_id, winner)
                SELECT id_slug(result_a_id, result_b_id), result_a_id, result_b_id, judge_id, winner
                FROM df_h2h_judged
            """)

        # 6. recompute elo scores and confidence intervals
        TaskService.update(task_id, "Recomputing Elo scores and confidence intervals", progress=0.96)
        EloService.reseed_scores(project_id)
        TaskService.update(task_id, "Recomputed Elo scores and confidence intervals", progress=1)
        TaskService.finish(task_id)
    except Exception as e:
        TaskService.finish(task_id, f"Failed ({e})")
        raise e
