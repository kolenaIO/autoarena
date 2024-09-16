import dataclasses
from datetime import datetime
from enum import Enum
from typing import Literal, Optional, Union

from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class Project:
    slug: str  # stem of the database file
    filename: str  # name of database file
    filepath: str  # full path to database file


@dataclass(frozen=True)
class CreateProjectRequest:
    name: str


@dataclass(frozen=True)
class Model:
    id: int
    name: str
    created: datetime
    elo: float
    q025: Optional[float]
    q975: Optional[float]
    n_responses: int
    n_votes: int


@dataclass(frozen=True)
class ModelResponse:
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
    model_b_id: Optional[int] = None  # when empty, get all pairings


WinnerType = Union[Literal["A", "B", "-"], str]  # should be one of the literal values, but could be anything


@dataclass(frozen=True)
class HeadToHeadHistoryItem:
    judge_id: int
    judge_name: str
    winner: WinnerType


@dataclass(frozen=True)
class HeadToHead:
    prompt: str
    response_a_id: int
    response_a: str
    response_b_id: int
    response_b: str
    history: list[HeadToHeadHistoryItem] = dataclasses.field(default_factory=list)


@dataclass(frozen=True)
class HeadToHeadVoteRequest:  # this is always coming from humans
    response_a_id: int
    response_b_id: int
    winner: WinnerType


class TaskType(str, Enum):
    AUTO_JUDGE = "auto-judge"
    RECOMPUTE_LEADERBOARD = "recompute-leaderboard"
    FINE_TUNE = "fine-tune"


class TaskStatus(str, Enum):
    STARTED = "started"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class Task:
    id: int
    task_type: TaskType
    created: datetime
    progress: float  # on [0,1]
    status: TaskStatus
    logs: str


@dataclass(frozen=True)
class HasActiveTasks:
    has_active: bool


@dataclass(frozen=True)
class TriggerAutoJudgeRequest:
    judge_ids: list[int]
    fraction: float  # on [0,1]
    skip_existing: bool


class JudgeType(str, Enum):
    HUMAN = "human"
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    COHERE = "cohere"
    GEMINI = "gemini"
    TOGETHER = "together"
    BEDROCK = "bedrock"
    CUSTOM = "custom"  # TODO: not sure how to handle calling this yet -- will it just be another Ollama model?


@dataclass(frozen=True)
class Judge:
    id: int
    judge_type: JudgeType
    created: datetime
    name: str
    model_name: Optional[str]
    system_prompt: Optional[str]
    description: str
    enabled: bool
    n_votes: int


@dataclass(frozen=True)
class CreateJudgeRequest:
    judge_type: JudgeType
    name: str
    model_name: str
    system_prompt: str
    description: str


@dataclass(frozen=True)
class UpdateJudgeRequest:
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
