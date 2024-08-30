from autostack.api import api as API
from autostack.api.api import TaskType
from autostack.judge import OpenAIJudge
from autostack.store.database import get_database_connection, reseed_elo_scores


def _insert_task(project_id: int, task_type: TaskType) -> int:
    with get_database_connection() as conn:
        ((task_id,),) = conn.execute(
            """
            INSERT INTO task (project_id, task_type)
            VALUES ($project_id, $task_type)
            RETURNING id
            """,
            dict(project_id=project_id, task_type=task_type),
        ).fetchall()
    return task_id


def _finish_task(task_id: int) -> None:
    with get_database_connection() as conn:
        conn.execute("UPDATE task SET progress = 1, status = 'Done' WHERE id = $id", dict(id=task_id))


def recompute_confidence_intervals(project_id: int) -> None:
    task_id = _insert_task(project_id, "recompute-confidence-intervals")
    try:
        # TODO: implement me, see elo.py
        ...
    finally:
        _finish_task(task_id)


def auto_judge(project_id: int, model_id: int) -> None:
    task_id = _insert_task(project_id, "auto-judge")
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
        print(f"found {len(df_h2h)} eligible matchups with {len(set(df_h2h["model_b_id"]))} models")

        # TODO: actually implement
        # 2. get judge(s) configured for judging
        judge = OpenAIJudge("gpt-4o-mini")

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
        responses = judge.judge_batch(head_to_heads)
        print(f"got responses: {responses}")

        # 4. upload judgements to database
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

        print(f"done judging {project_id}, {model_id}")
    finally:
        _finish_task(task_id)
