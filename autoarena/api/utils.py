from io import StringIO
from typing import TypeVar, AsyncIterator

import pandas as pd
from pydantic import RootModel
from starlette.responses import StreamingResponse

from autoarena.store.database import data_directory, get_data_directory

T = TypeVar("T")  # should be a Pydantic dataclass


async def as_sse_stream(object_stream: AsyncIterator[T]) -> AsyncIterator[str]:
    with data_directory(get_data_directory()):
        async for obj in object_stream:
            obj_json = RootModel[T](obj).model_dump_json()
            yield f"data: {obj_json}\n\n"


# TODO: figure out a way to gracefully terminate this when the server is exiting
class SSEStreamingResponse(StreamingResponse):
    def __init__(self, object_stream: AsyncIterator[T]):
        super().__init__(as_sse_stream(object_stream), media_type="text/event-stream")


def download_csv_response(df: pd.DataFrame, stem: str) -> StreamingResponse:
    stream = StringIO()
    df.to_csv(stream, index=False)
    return StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{stem}.csv"'},
    )
