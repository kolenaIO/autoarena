import sys
from io import StringIO
from typing import TypeVar, AsyncIterator, Callable

if sys.version_info[:2] >= (3, 10):
    from typing import ParamSpec
else:
    from typing_extensions import ParamSpec

import pandas as pd
from fastapi import BackgroundTasks
from pydantic import RootModel
from starlette.responses import StreamingResponse

from autoarena.store.database import DataDirectoryProvider


def download_csv_response(df: pd.DataFrame, stem: str) -> StreamingResponse:
    stream = StringIO()
    df.to_csv(stream, index=False)
    return StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{stem}.csv"'},
    )


TDataclass = TypeVar("TDataclass")  # should be a Pydantic dataclass


# TODO: figure out a way to gracefully terminate this when the server is exiting
class SSEStreamingResponse(StreamingResponse):
    """Encode a stream of dataclasses into SSE events streamed back to the client as they are yielded."""

    def __init__(self, object_stream: AsyncIterator[TDataclass]):
        super().__init__(self._as_sse_stream(object_stream), media_type="text/event-stream")

    @staticmethod
    def _as_sse_stream(object_stream: AsyncIterator[TDataclass]) -> AsyncIterator[str]:
        # NOTE: this special handling ensures that the data directory in endpoint handler context is captured, as a
        #  returned StreamingResponse isn't actually read until _after_ the endpoint returns, which is a problem if the
        #  stream relies on the data directory in context (e.g. by repeatedly reading from the project database)
        data_dir = DataDirectoryProvider.get()

        async def stream() -> AsyncIterator[str]:
            with DataDirectoryProvider.set(data_dir):
                async for obj in object_stream:
                    obj_json = RootModel[TDataclass](obj).model_dump_json()
                    yield f"data: {obj_json}\n\n"

        return stream()


Params = ParamSpec("Params")
ReturnType = TypeVar("ReturnType")


def schedule_background_task(
    background_tasks: BackgroundTasks,
    task: Callable[Params, ReturnType],
    *args: Params.args,
    **kwargs: Params.kwargs,
) -> None:
    """Schedule a background task with the correct data directory captured in execution context."""
    data_dir = DataDirectoryProvider.get()

    def task_inner(*a: Params.args, **k: Params.kwargs) -> ReturnType:
        with DataDirectoryProvider.set(data_dir):
            return task(*a, **k)

    background_tasks.add_task(task_inner, *args, **kwargs)
