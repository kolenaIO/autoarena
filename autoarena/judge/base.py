import os
from abc import ABCMeta, abstractmethod
from typing import Optional

from loguru import logger

from autoarena.api import api
from autoarena.api.api import JudgeType


class AutomatedJudge(metaclass=ABCMeta):
    API_KEY_NAME: Optional[str]  # if set, verify that this exists in environment on init

    _model_name: str
    _system_prompt: str

    _n_calls: int
    _input_tokens: int
    _output_tokens: int

    def __init__(self, model_name: str, system_prompt: str):
        self._model_name = model_name
        self._system_prompt = system_prompt
        key = os.environ.get(self.API_KEY_NAME, None) if self.API_KEY_NAME is not None else None
        if self.API_KEY_NAME is not None and key is None:
            message = f"API key '{self.API_KEY_NAME}' must be set in environment running AutoArena to use '{self.name}'"
            raise RuntimeError(message)

    @property
    @abstractmethod
    def judge_type(self) -> JudgeType:
        """Enum type for this judge, e.g. 'human' or 'ollama'"""

    @property
    def name(self) -> str:
        return self._model_name

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def system_prompt(self) -> str:
        return self._system_prompt

    @property
    @abstractmethod
    def description(self) -> str:
        """Freeform description for this judge, usually ending without a period"""

    @abstractmethod
    def judge(self, h2h: api.HeadToHead) -> str:  # TODO: return more information than just winner?
        raise NotImplementedError

    @staticmethod
    def verify_environment() -> None:
        """
        Verify that the current environment contains any necessary configuration, such as API keys, necessary to
        interact with this judge. Throw an exception if not.
        """

    def log_usage(self) -> None:
        logger.info(
            f"'{self.name}' used {self._input_tokens} input tokens and {self._output_tokens} output tokens "
            f"over {self._n_calls} calls",
        )


class WrappingJudge(AutomatedJudge, metaclass=ABCMeta):
    wrapped: AutomatedJudge

    def __init__(self, judge: AutomatedJudge):
        super().__init__(judge.model_name, judge.system_prompt)
        self.wrapped = judge

    @property
    def judge_type(self) -> JudgeType:
        return self.wrapped.judge_type

    @property
    def name(self) -> str:
        return self.wrapped.name

    @property
    def model_name(self) -> str:
        return self.wrapped.model_name

    @property
    def system_prompt(self) -> str:
        return self.wrapped.system_prompt

    @property
    def description(self) -> str:
        return self.wrapped.description

    def log_usage(self) -> None:
        self.wrapped.log_usage()
