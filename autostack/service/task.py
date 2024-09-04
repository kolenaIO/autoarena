from collections import defaultdict
from datetime import datetime

import pandas as pd

from autostack.api import api
from autostack.api.api import JudgeType
from autostack.judge.base import Judge
from autostack.judge.executor import ThreadedExecutor
from autostack.judge.factory import judge_factory
from autostack.judge.utils import ABShufflingJudge, FixingJudge, RetryingJudge
from autostack.service.elo import EloService
from autostack.service.head_to_head import HeadToHeadService
from autostack.service.judge import JudgeService
from autostack.store.database import get_database_connection


class TaskService:
    @staticmethod
    def get_all(project_id: int) -> list[api.Task]:
        with get_database_connection() as conn:
            df_task = conn.execute(
                "SELECT id, task_type, created, progress, status FROM task WHERE project_id = $project_id",
                dict(project_id=project_id),
            ).df()
        return [api.Task(**r) for _, r in df_task.iterrows()]

    @staticmethod
    def create(project_id: int, task_type: api.TaskType, status: str = "Started") -> api.Task:
        with get_database_connection() as conn:
            ((task_id, created, progress, status),) = conn.execute(
                """
                INSERT INTO task (project_id, task_type, status)
                VALUES ($project_id, $task_type, $status)
                RETURNING id, created, progress, status
                """,
                dict(project_id=project_id, task_type=task_type, status=f"{TaskService._time_slug()} {status}"),
            ).fetchall()
        return api.Task(id=task_id, task_type=task_type, created=created, progress=progress, status=status)

    @staticmethod
    def update(task_id: int, status: str, progress: float) -> None:
        with get_database_connection() as conn:
            conn.execute(
                "UPDATE task SET progress = $progress, status = status || '\n' || $status WHERE id = $id",
                dict(id=task_id, status=f"{TaskService._time_slug()} {status}", progress=progress),
            )

    @staticmethod
    def finish(task_id: int, status: str = "Done") -> None:
        TaskService.update(task_id, status, progress=1)

    @staticmethod
    def _time_slug() -> str:
        return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

    # TODO: should this really be a long-running task? It only takes ~5 seconds for ~50k battles
    @staticmethod
    def recompute_confidence_intervals(project_id: int) -> None:
        task_objects = TaskService.get_all(project_id)
        if len([t for t in task_objects if t.task_type == "recompute-confidence-intervals" and t.progress < 1]) > 0:
            return  # only recompute if there isn't already a task in progress
        task_id = TaskService.create(project_id, "recompute-confidence-intervals").id
        try:
            EloService.reseed_scores(project_id)
        finally:
            TaskService.finish(task_id)

    @staticmethod
    def auto_judge(project_id: int, model_id: int, model_name) -> None:
        # 1. get judge(s) configured for judging
        all_judges = JudgeService.get_all(project_id)
        enabled_auto_judges = [j for j in all_judges if j.enabled and j.judge_type is not JudgeType.HUMAN]
        if len(enabled_auto_judges) == 0:
            return  # do nothing if no judges are configured, do not create a task
        status = f"Started auto-judge task for model '{model_name}'"
        task_id = TaskService.create(project_id, "auto-judge", status).id

        try:
            # 2. instantiate judge(s)
            TaskService.update(task_id, status=f"Using {len(enabled_auto_judges)} judge(s):", progress=0)
            judges: list[Judge] = [
                ABShufflingJudge(FixingJudge(RetryingJudge(judge_factory(j)))) for j in enabled_auto_judges
            ]
            for judge in judges:
                TaskService.update(task_id, status=f"  * {judge.name}", progress=0)

            # 3. get pairs eligible for judging
            df_h2h = HeadToHeadService.get_df(api.HeadToHeadsRequest(model_a_id=model_id))
            if len(df_h2h) == 0:
                TaskService.update(task_id, status="No head-to-heads found, exiting", progress=1)
                return
            status = f"Found {len(df_h2h)} head-to-heads versus {len(set(df_h2h.model_b_id))} model(s) to judge"
            TaskService.update(task_id, status=status, progress=0)

            # 4. stream judgement requests
            head_to_heads = [
                api.HeadToHead(**r)
                for _, r in df_h2h[["prompt", "result_a_id", "response_a", "result_b_id", "response_b"]].iterrows()
            ]
            executor = ThreadedExecutor(4)
            responses: dict[str, list[tuple[int, int, str]]] = defaultdict(lambda: [])
            n_total = len(head_to_heads) * len(judges)
            for judge, batch, judged_batch in executor.execute(judges, head_to_heads):
                this_responses = [(r.result_a_id, r.result_b_id, winner) for r, winner in zip(batch, judged_batch)]
                responses[judge.name].extend(this_responses)
                n_this_judge = len(responses[judge.name])
                status = f"Judged {n_this_judge} of {len(head_to_heads)} with '{judge.name}'"
                n_responses = sum(len(r) for r in responses.values())
                TaskService.update(task_id, status, progress=0.95 * (n_responses / n_total))

            # TODO: stream to database?
            # 5. upload judgements to database
            judge_id_by_name = {j.name: j.id for j in enabled_auto_judges}
            with get_database_connection() as conn:
                for judge_name, judge_responses in responses.items():
                    df_h2h_judged = df_h2h.copy()
                    df_h2h_judged["judge_id"] = judge_id_by_name[judge_name]
                    df_judgement = pd.DataFrame(judge_responses, columns=["result_a_id", "result_b_id", "winner"])
                    df_h2h_judged = pd.merge(df_h2h_judged, df_judgement, on=["result_a_id", "result_b_id"], how="left")
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
