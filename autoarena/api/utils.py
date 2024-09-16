import json
from typing import Iterator, TypeVar

from pydantic import RootModel

T = TypeVar("T")


def as_sse_stream(object_stream: Iterator[T]) -> Iterator[str]:
    for obj in object_stream:
        obj_json = RootModel[T](obj).model_dump_json()
        sse_dict = dict(message=f"event: {obj_json}\n")
        yield f"data: {json.dumps(sse_dict)}\n\n"
