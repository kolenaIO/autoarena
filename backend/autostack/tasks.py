from datetime import datetime

import numpy as np

from autostack.api import api as API
from autostack.api.api import TaskType
from autostack.judge import OpenAIJudge, ABShufflingJudge
from autostack.store.database import get_database_connection, reseed_elo_scores


def _time_slug() -> str:
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")


def _insert_task(project_id: int, task_type: TaskType, status: str = "Started") -> int:
    with get_database_connection() as conn:
        ((task_id,),) = conn.execute(
            """
            INSERT INTO task (project_id, task_type, status)
            VALUES ($project_id, $task_type, $status)
            RETURNING id
            """,
            dict(project_id=project_id, task_type=task_type, status=f"{_time_slug()} {status}"),
        ).fetchall()
    return task_id


def _finish_task(task_id: int, status: str = "Done") -> None:
    _update_task(task_id, status, 1)


def _update_task(task_id: int, status: str, progress: float) -> None:
    with get_database_connection() as conn:
        params = dict(id=task_id, status=f"{_time_slug()} {status}", progress=progress)
        conn.execute("UPDATE task set progress = $progress, status = status || '\n' || $status WHERE id = $id", params)


def recompute_confidence_intervals(project_id: int) -> None:
    task_id = _insert_task(project_id, "recompute-confidence-intervals")
    try:
        with get_database_connection() as conn:
            reseed_elo_scores(conn, project_id)
    finally:
        _finish_task(task_id)


def auto_judge(project_id: int, model_id: int, model_name) -> None:
    status = f"Started auto-judge task for model '{model_name}'"
    task_id = _insert_task(project_id, "auto-judge", status)
    try:
        # 1. get pairs eligible for judging
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
        status = f"Found {len(df_h2h)} battles with {len(set(df_h2h["model_b_id"]))} models to judge"
        _update_task(task_id, status=status, progress=0)

        # TODO: actually implement judge selection logic
        # 2. get judge(s) configured for judging
        judge = ABShufflingJudge(OpenAIJudge("gpt-4o-mini"))
        with get_database_connection() as conn:
            conn.execute(
                """
                INSERT INTO judge (project_id, name, description)
                VALUES ($project_id, $name, $description)
                ON CONFLICT (project_id, name) DO NOTHING
            """,
                dict(project_id=project_id, name=judge.name, description=judge.description),
            )
            ((judge_id,),) = conn.execute(
                "SELECT id FROM judge WHERE project_id = $project_id AND name = $name",
                dict(project_id=project_id, name=judge.name),
            ).fetchall()
        _update_task(task_id, status=f"Using judge '{judge.name}'", progress=0)

        # 3. stream judgement requests
        head_to_heads = [
            API.HeadToHead(
                prompt=r.prompt,
                result_a_id=r.result_a_id,
                response_a=r.response_a,
                result_b_id=r.result_b_id,
                response_b=r.response_b,
            )
            for r in df_h2h.itertuples()
        ]
        batch_size = 8
        n_batches = len(head_to_heads) // batch_size
        responses = []
        for i, batch in enumerate(np.array_split(head_to_heads, n_batches)):
            responses.extend(judge.judge_batch(batch))  # TODO: stream to database?
            status = f"Judged {len(responses)} of {len(head_to_heads)} battles"
            _update_task(task_id, status, progress=(i + 1) / n_batches)

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
        _update_task(task_id, "Recomputed Elo scores and confidence intervals", progress=1)
    except Exception as e:
        _finish_task(task_id, f"Crashed ({e})")
    finally:
        _finish_task(task_id)
