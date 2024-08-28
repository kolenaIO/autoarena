from dataclasses import dataclass


@dataclass(frozen=True)
class Model:
    id: int
    name: str
