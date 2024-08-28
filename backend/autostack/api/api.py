from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Model:
    id: int
    name: str
    created: datetime
    elo: float
