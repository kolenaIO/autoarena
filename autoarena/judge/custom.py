import importlib
from abc import abstractmethod, ABCMeta
from typing import Type, Optional

from loguru import logger

from autoarena.api import api
from autoarena.api.api import JudgeType
from autoarena.judge.base import Judge


class CustomJudge(Judge, metaclass=ABCMeta):
    # don't override these
    @property
    def judge_type(self) -> JudgeType:
        return JudgeType.CUSTOM

    @property
    def model_name(self) -> Optional[str]:
        return f"{type(self).__module__}.{type(self).__qualname__}"

    # fine to override these
    @property
    def name(self) -> str:
        return f"{type(self).__qualname__}"

    @property
    def system_prompt(self) -> Optional[str]:
        return None

    @property
    def description(self) -> str:
        return f"Custom judge implemented in '{self.name}'"

    # must implement this
    @abstractmethod
    def judge(self, h2h: api.HeadToHead) -> str:
        raise NotImplementedError


def register_custom_judge_class(judge_class_import_path: str) -> None:
    global CUSTOM_JUDGE_CLASSES
    path_parts = judge_class_import_path.split(".")
    judge_class_name = path_parts.pop()
    import_path = ".".join(path_parts)
    imported_module = importlib.import_module(import_path)
    judge_class = getattr(imported_module, judge_class_name)
    if not issubclass(judge_class, CustomJudge):
        raise TypeError(f"Custom judge class '{judge_class}' is not a subclass of type '{CustomJudge.__name__}'")
    CUSTOM_JUDGE_CLASSES[judge_class_import_path] = judge_class
    logger.success(f"Registered custom judge '{judge_class.__name__}' from '{import_path}'")


CUSTOM_JUDGE_CLASSES: dict[str, Type[CustomJudge]] = {}


def create_custom_judge(judge: api.Judge) -> CustomJudge:
    global CUSTOM_JUDGE_CLASSES
    judge_class = CUSTOM_JUDGE_CLASSES.get(judge.model_name or judge.name, None)
    if judge_class is None:
        raise RuntimeError(f"Custom judge class '{judge.model_name}' not registered")
    return judge_class()
