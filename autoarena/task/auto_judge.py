import dataclasses
import time
from collections import defaultdict
from typing import Optional, Callable

import pandas as pd
from loguru import logger
from pydantic.dataclasses import dataclass
from tenacity import retry, stop_after_attempt, RetryCallState, wait_random_exponential

from autoarena.api import api
from autoarena.judge.base import AutomatedJudge
from autoarena.judge.executor import JudgeExecutor
from autoarena.judge.factory import judge_factory
from autoarena.judge.wrapper import JudgeWrapper, retrying_wrapper, fixing_wrapper, ab_shuffling_wrapper
from autoarena.service.elo import EloService, DEFAULT_ELO_CONFIG, EloConfig
from autoarena.service.head_to_head import HeadToHeadService
from autoarena.service.judge import JudgeService
from autoarena.service.model import ModelService
from autoarena.service.task import TaskService
from autoarena.store.utils import id_slug


class GracefulExit(RuntimeError): ...


@dataclass(frozen=True)
class AutoJudgeTask:
    project_slug: str
    task_id: int
    models: list[api.Model]
    judges: list[api.Judge]
    fraction: float = 1.0
    skip_existing: bool = False
    t_start: float = dataclasses.field(default_factory=time.time)
    judge_wrappers: list[JudgeWrapper] = dataclasses.field(
        default_factory=lambda: [retrying_wrapper, fixing_wrapper, ab_shuffling_wrapper]
    )
    update_every: int = 10
    elo_config: EloConfig = DEFAULT_ELO_CONFIG

    def __post_init__(self) -> None:
        if self.fraction <= 0 or self.fraction > 1:
            raise ValueError(f"Invalid fraction: {self.fraction} must be on (0,1]")
        if len(self.models) == 0:
            raise ValueError("No models provided")
        if len(self.judges) == 0:
            raise ValueError("No judges provided")

    @classmethod
    def create(
        cls,
        project_slug: str,
        models: Optional[list[api.Model]] = None,
        judges: Optional[list[api.Judge]] = None,
        fraction: float = 1.0,
        skip_existing: bool = False,
    ) -> Optional["AutoJudgeTask"]:
        models = models if models is not None else ModelService.get_all(project_slug)
        judges = judges if judges is not None else JudgeService.get_all(project_slug)
        enabled_judges = [j for j in judges if j.enabled and j.judge_type is not api.JudgeType.HUMAN]
        if len(enabled_judges) == 0:
            logger.warning("No enabled judges found, can't run automated judgement")
            return None  # do nothing if no judges are configured, do not create a task
        message = f"Started automated judging task using {len(enabled_judges)} judge(s)"
        task_id = TaskService.create(project_slug, api.TaskType.AUTO_JUDGE, message).id
        logger.info(message)
        return AutoJudgeTask(project_slug, task_id, models, enabled_judges, fraction, skip_existing)

    def log(
        self,
        message: str,
        status: api.TaskStatus = api.TaskStatus.IN_PROGRESS,
        progress: Optional[float] = None,
        level: str = "INFO",
    ) -> None:
        TaskService.update(self.project_slug, self.task_id, message, status=status, progress=progress)
        logger.log(level, message)

    # this is a beast, but most of the bulk comes from logging
    def run(self, executor: JudgeExecutor) -> None:
        try:
            self._run_inner(executor)
        except GracefulExit:
            pass
        except Exception as e:
            TaskService.update(self.project_slug, self.task_id, f"Failed ({e})", status=api.TaskStatus.FAILED)
            message = "See AutoArena service logs for more information"
            TaskService.update(self.project_slug, self.task_id, message, status=api.TaskStatus.FAILED)
            logger.error(f"Automated judgement failed: {e}")
            raise e

    def _retrieve_head_to_heads(self) -> pd.DataFrame:
        h2h_requests = [api.HeadToHeadsRequest(model_a_id=m.id) for m in self.models]
        df_h2h = pd.concat([HeadToHeadService.get_df(self.project_slug, request) for request in h2h_requests])
        if len(df_h2h) == 0:
            self.log("No head-to-heads found, exiting", status=api.TaskStatus.COMPLETED, progress=1, level="WARNING")
            raise GracefulExit

        df_h2h["response_id_slug"] = df_h2h.apply(lambda r: id_slug(r.response_a_id, r.response_b_id), axis=1)
        df_h2h = df_h2h.drop_duplicates(subset=["response_id_slug"], keep="first")
        n_models = len(set(df_h2h.model_a_id) | set(df_h2h.model_b_id))
        self.log(f"Found {len(df_h2h)} total head-to-heads between {n_models} model(s) to judge")

        if self.fraction < 1:
            n_total = len(df_h2h)
            df_h2h = df_h2h.sample(frac=self.fraction)
            self.log(f"Using subset of {len(df_h2h)} out of {n_total} head-to-heads ({int(100 * self.fraction)}%)")

        return df_h2h

    def _instantiate_judges_with_head_to_heads(
        self,
        df_h2h: pd.DataFrame,
    ) -> list[tuple[AutomatedJudge, list[api.HeadToHead]]]:
        judges_with_h2hs: list[tuple[AutomatedJudge, list[api.HeadToHead]]] = []
        for judge in self.judges:
            automated_judge = judge_factory(judge, wrappers=self.judge_wrappers)
            head_to_heads = [
                api.HeadToHead(r.prompt, r.response_a_id, r.response_a, r.response_b_id, r.response_b)
                for r in df_h2h.itertuples()
                if not self.skip_existing or judge.name not in {h["judge_name"] for h in r.history}
            ]
            n_skipping = len(df_h2h) - len(head_to_heads)
            if n_skipping > 0:
                self.log(f"Skipping {n_skipping} for '{judge.name}' with existing votes, {len(head_to_heads)} to run")
            if len(head_to_heads) == 0:
                message = f"No head-to-heads without votes found for '{judge.name}', skipping this judge"
                self.log(message, level="WARNING")
            else:
                judges_with_h2hs.append((automated_judge, head_to_heads))

        if len(judges_with_h2hs) == 0:
            message = "No head-to-heads without votes found for any judges, exiting"
            self.log(message, status=api.TaskStatus.COMPLETED, progress=1, level="WARNING")
            raise GracefulExit

        self.log(f"Running {len(judges_with_h2hs)} judge(s):")
        for j, _ in judges_with_h2hs:
            self.log(f"  * {j.name}")

        return judges_with_h2hs

    def _run_inner(self, executor: JudgeExecutor) -> None:
        df_h2h = self._retrieve_head_to_heads()
        judges_with_h2hs = self._instantiate_judges_with_head_to_heads(df_h2h)
        judge_id_by_name = {j.name: j.id for j in self.judges}
        out_columns = ["response_a_id", "response_b_id", "judge_id", "winner"]

        responses: dict[str, list[tuple[int, int, int, str]]] = defaultdict(lambda: [])
        n_h2h_by_judge_name = {judge.name: len(h2hs) for judge, h2hs in judges_with_h2hs}
        n_total = sum(len(h2hs) for _, h2hs in judges_with_h2hs)
        t_start_judging = time.time()
        for auto_judge, h2h, winner in executor.execute(judges_with_h2hs):
            judge_id = judge_id_by_name[auto_judge.name]
            responses[auto_judge.name].append((h2h.response_a_id, h2h.response_b_id, judge_id, winner))
            n_this_judge = len(responses[auto_judge.name])
            n_responses = sum(len(r) for r in responses.values())
            progress = 0.95 * (n_responses / n_total)
            if n_this_judge % self.update_every == 0:
                message = f"Judged {n_this_judge} of {n_h2h_by_judge_name[auto_judge.name]} with '{auto_judge.name}'"
                self.log(message, progress=progress)
                df_h2h_chunk = pd.DataFrame(responses[auto_judge.name][-self.update_every :], columns=out_columns)
                self._try_write(lambda: HeadToHeadService.upload_head_to_heads(self.project_slug, df_h2h_chunk))
            if n_this_judge == n_h2h_by_judge_name[auto_judge.name]:
                message = (
                    f"Judge '{auto_judge.name}' finished judging {n_h2h_by_judge_name[auto_judge.name]} head-to-heads "
                    f"in {time.time() - t_start_judging:0.1f} seconds"
                )
                self.log(message, progress=progress)
                for usage_summary_line in auto_judge.get_usage_summary():
                    self.log(usage_summary_line)
                df_h2h_all = pd.DataFrame(responses[auto_judge.name], columns=out_columns)
                self._try_write(lambda: HeadToHeadService.upload_head_to_heads(self.project_slug, df_h2h_all))

        self.log("Recomputing leaderboard rankings", progress=0.975)
        self._try_write(lambda: EloService.reseed_scores(self.project_slug, config=self.elo_config))
        message = f"Completed automated judging in {time.time() - self.t_start:0.1f} seconds"
        self.log(message, progress=1, status=api.TaskStatus.COMPLETED, level="SUCCESS")

    @staticmethod
    def _try_write(write_thunk: Callable[[], None]) -> None:
        """
        We're running into a limitation of DuckDB here -- concurrent writes are not well-supported. Give a best effort
        by retrying write attempts, an [officially endorsed strategy](https://duckdb.org/docs/connect/concurrency.html).

        This situation could be improved but requires answering tough questions about what kind of operations we want to
        optimize the persistence layer for, and what kind of operations we're OK with it struggling with.
        """

        def _log_retry(retry_state: RetryCallState) -> None:
            logger.warning(f"Retrying write attempt {retry_state.attempt_number} (error: {retry_state.outcome})")

        @retry(wait=wait_random_exponential(max=5), stop=stop_after_attempt(5), after=_log_retry)
        def _try_write_inner(thunk: Callable[[], None]) -> None:
            thunk()

        return _try_write_inner(write_thunk)
