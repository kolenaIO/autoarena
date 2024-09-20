import contextvars
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
        # NOTE: this special handling ensures that the data directory and any other endpoint-specific context is
        #  captured, as a returned StreamingResponse isn't actually read until _after_ the endpoint returns
        sse_stream = contextvars.copy_context().run(self._as_sse_stream, object_stream)
        super().__init__(sse_stream, media_type="text/event-stream")

    @staticmethod
    async def _as_sse_stream(object_stream: AsyncIterator[TDataclass]) -> AsyncIterator[str]:
        async for obj in object_stream:
            obj_json = RootModel[TDataclass](obj).model_dump_json()
            yield f"data: {obj_json}\n\n"


Params = ParamSpec("Params")
ReturnType = TypeVar("ReturnType")


def schedule_background_task(
    background_tasks: BackgroundTasks,
    task: Callable[Params, ReturnType],
    *args: Params.args,
    **kwargs: Params.kwargs,
) -> None:
    """Schedule a background task using the calling context, preserving any endpoint-specific configuration."""
    background_tasks.add_task(contextvars.copy_context().run, task, *args, **kwargs)
