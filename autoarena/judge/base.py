import os
from abc import ABCMeta, abstractmethod
from typing import Optional

from autoarena.api import api
from autoarena.api.api import JudgeType


class Judge(metaclass=ABCMeta):
    @property
    @abstractmethod
    def judge_type(self) -> JudgeType:
        """Enum type for this judge, e.g. 'human' or 'ollama'"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name for this judge, e.g. 'GPT-4o mini'"""

    @property
    @abstractmethod
    def model_name(self) -> Optional[str]:
        """Machine-readable model name, e.g. 'gpt-4o-mini'. None for human judge"""

    @property
    @abstractmethod
    def system_prompt(self) -> Optional[str]:
        """System prompt for this judge, None for human judge"""

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


class WrappingJudge(Judge, metaclass=ABCMeta):
    wrapped: Judge

    def __init__(self, judge: Judge):
        self.wrapped = judge

    @property
    def judge_type(self) -> JudgeType:
        return self.wrapped.judge_type

    @property
    def name(self) -> str:
        return self.wrapped.name

    @property
    def model_name(self) -> Optional[str]:
        return self.wrapped.model_name

    @property
    def system_prompt(self) -> Optional[str]:
        return self.wrapped.system_prompt

    @property
    def description(self) -> str:
        return self.wrapped.description


class AutomatedJudge(Judge, metaclass=ABCMeta):
    API_KEY_NAME: Optional[str]  # if set, verify that this exists in environment on init

    _model_name: str
    _system_prompt: str

    def __init__(self, model_name: str, system_prompt: str):
        self._model_name = model_name
        self._system_prompt = system_prompt
        key = os.environ.get(self.API_KEY_NAME, None) if self.API_KEY_NAME is not None else None
        if self.API_KEY_NAME is not None and key is None:
            message = f"API key '{self.API_KEY_NAME}' must be set in environment running AutoArena to use '{self.name}'"
            raise RuntimeError(message)

    @property
    def name(self) -> str:
        return self._model_name

    @property
    def model_name(self) -> Optional[str]:
        return self._model_name

    @property
    def system_prompt(self) -> Optional[str]:
        return self._system_prompt
