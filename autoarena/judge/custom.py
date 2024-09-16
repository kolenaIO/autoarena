from autoarena.judge.base import AutomatedJudge

_CUSTOM_JUDGE_NAME_TO_CLASS: dict[str, type[AutomatedJudge]] = {}


def register_custom_judge_class(custom_judge_name: str, custom_judge_class: type[AutomatedJudge]) -> None:
    global _CUSTOM_JUDGE_NAME_TO_CLASS
    _CUSTOM_JUDGE_NAME_TO_CLASS[custom_judge_name] = custom_judge_class


def get_custom_judge_class(custom_judge_name: str) -> type[AutomatedJudge]:
    if custom_judge_name not in _CUSTOM_JUDGE_NAME_TO_CLASS:
        raise ValueError(f"No implementation for custom judge with name '{custom_judge_name}'")
    return _CUSTOM_JUDGE_NAME_TO_CLASS[custom_judge_name]


def clear_custom_judge_classes() -> None:
    global _CUSTOM_JUDGE_NAME_TO_CLASS
    _CUSTOM_JUDGE_NAME_TO_CLASS.clear()
