import importlib
from typing import Type

from loguru import logger

from autoarena.api import api
from autoarena.judge.base import Judge


def register_custom_judge_class(judge_class_import_path: str) -> None:
    global CUSTOM_JUDGE_CLASSES
    path_parts = judge_class_import_path.split(".")
    judge_class_name = path_parts.pop()
    import_path = ".".join(path_parts)
    imported_module = importlib.import_module(import_path)
    judge_class = getattr(imported_module, judge_class_name)
    if not issubclass(judge_class, Judge):
        raise TypeError(f"Custom judge class '{judge_class}' is not a subclass of type '{Judge.__name__}'")
    CUSTOM_JUDGE_CLASSES[judge_class_import_path] = judge_class
    logger.success(f"Registered custom judge '{judge_class.__name__}' from '{import_path}'")


CUSTOM_JUDGE_CLASSES: dict[str, Type[Judge]] = {}


def create_custom_judge(judge: api.Judge) -> Judge:
    global CUSTOM_JUDGE_CLASSES
    judge_class = CUSTOM_JUDGE_CLASSES.get(judge.name, None)
    if judge_class is None:
        raise RuntimeError(f"Custom judge class '{judge.name}' not registered")
    return judge_class()
