from abc import ABCMeta, abstractmethod

from autostack.api import api
from autostack.api.api import JudgeType


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
    def description(self) -> str:
        """Freeform description for this judge, usually ending without a period"""

    @abstractmethod
    def judge_batch(self, batch: list[api.HeadToHead]) -> list[str]:  # TODO: return more information than just winner?
        ...
