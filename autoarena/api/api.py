import dataclasses
from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class Project:
    id: int
    name: str
    created: datetime


@dataclass(frozen=True)
class CreateProjectRequest:
    name: str


@dataclass(frozen=True)
class Model:
    id: int
    name: str
    created: datetime
    elo: float
    q025: float | None
    q975: float | None
    datapoints: int
    votes: int


@dataclass(frozen=True)
class ModelResult:
    prompt: str
    response: str


@dataclass(frozen=True)
class ModelHeadToHeadStats:
    other_model_id: int
    other_model_name: str
    judge_id: int
    judge_name: str
    count_wins: int
    count_losses: int
    count_ties: int


@dataclass(frozen=True)
class HeadToHeadsRequest:
    model_a_id: int
    model_b_id: int | None = None  # when empty, get all pairings


WinnerType = Literal["A", "B", "-"]


@dataclass(frozen=True)
class HeadToHeadHistoryItem:
    judge_id: int
    judge_name: str
    winner: WinnerType


@dataclass(frozen=True)
class HeadToHead:
    prompt: str
    result_a_id: int
    response_a: str
    result_b_id: int
    response_b: str
    history: list[HeadToHeadHistoryItem] = dataclasses.field(default_factory=list)


@dataclass(frozen=True)
class HeadToHeadJudgementRequest:  # this is always coming from humans
    project_id: int
    result_a_id: int
    result_b_id: int
    winner: WinnerType


TaskType = Literal["auto-judge", "fine-tune", "recompute-confidence-intervals"]


@dataclass(frozen=True)
class Task:
    id: int
    task_type: TaskType
    created: datetime
    progress: float  # on [0,1]
    status: str


class JudgeType(str, Enum):
    HUMAN = "human"
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    COHERE = "cohere"
    GEMINI = "gemini"
    CUSTOM = "custom"  # TODO: not sure how to handle calling this yet -- will it just be another Ollama model?


@dataclass(frozen=True)
class Judge:
    id: int
    judge_type: JudgeType
    created: datetime
    name: str
    model_name: str | None
    system_prompt: str | None
    description: str
    enabled: bool
    votes: int


@dataclass(frozen=True)
class CreateJudgeRequest:
    project_id: int
    judge_type: JudgeType
    name: str
    model_name: str
    system_prompt: str
    description: str


@dataclass(frozen=True)
class UpdateJudgeRequest:
    project_id: int
    judge_id: int
    enabled: bool
    # TODO: update name, description, system prompt?


@dataclass(frozen=True)
class EloHistoryItem:
    other_model_id: int
    other_model_name: str
    judge_id: int
    judge_name: str
    elo: float


@dataclass(frozen=True)
class CreateFineTuningTaskRequest:
    base_model: str
