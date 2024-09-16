from typing import Iterator, TypeVar

from pydantic import RootModel

T = TypeVar("T")  # should be a Pydantic dataclass


def as_sse_stream(object_stream: Iterator[T]) -> Iterator[str]:
    for obj in object_stream:
        obj_json = RootModel[T](obj).model_dump_json()
        yield f"data: {obj_json}\n\n"
