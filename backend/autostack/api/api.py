from dataclasses import dataclass
from datetime import datetime
from typing import Literal


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
class HeadToHeadsRequest:
    project_id: int  # TODO: is this required given that models are scoped to projects?
    model_a_id: int
    model_b_id: int


@dataclass(frozen=True)
class HeadToHead:
    prompt: str
    result_a_id: int
    response_a: str
    result_b_id: int
    response_b: str
    # TODO: also add voting history from any judgements already made?


@dataclass(frozen=True)
class HeadToHeadJudgementRequest:
    project_id: int
    judge_name: str  # TODO: id..?
    result_a_id: int
    result_b_id: int
    winner: Literal["A", "B", "-"]


TaskType = Literal["auto-judge", "fine-tune", "recompute-confidence-intervals"]


@dataclass(frozen=True)
class Task:
    id: int
    task_type: TaskType
    created: datetime
    progress: float  # on [0,1]
    status: str
