from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from starlette.responses import FileResponse, HTMLResponse

from autoarena.error import NotFoundError


def ui_router() -> APIRouter:
    static_dir = Path(__file__).parent.parent / "ui" / "dist"

    r = APIRouter()

    @r.get("/robots.txt", response_class=PlainTextResponse)
    async def robots_txt():
        data = "User-agent: *\nDisallow: /"
        return data

    @r.get("/assets/{file_path:path}")
    async def assets(file_path):
        path = static_dir / "assets" / file_path
        if not path.is_file():
            raise NotFoundError("file not found")
        return FileResponse(path)

    @r.get("/{full_path:path}")
    async def catch_all(full_path: str):
        with (static_dir / "index.html").open("r") as f:
            return HTMLResponse(f.read())

    return r
