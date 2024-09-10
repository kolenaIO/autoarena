from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from starlette.responses import FileResponse, HTMLResponse

from autoarena.error import NotFoundError

ROBOTS_TXT = "User-agent: *\nDisallow: /"


def ui_router() -> APIRouter:
    build_static_dir = Path(__file__).parent / "ui"
    dev_static_dir = Path(__file__).parent.parent / "ui" / "dist"
    static_dir = build_static_dir if build_static_dir.exists() else dev_static_dir

    r = APIRouter()

    @r.get("/robots.txt", response_class=PlainTextResponse)
    async def robots_txt() -> str:
        return ROBOTS_TXT

    @r.get("/assets/{file_path:path}")
    async def assets(file_path: str) -> FileResponse:
        path = static_dir / "assets" / file_path
        if not path.is_file():
            raise NotFoundError("file not found")
        return FileResponse(path)

    @r.get("/{full_path:path}")
    async def catch_all(full_path: str) -> HTMLResponse:
        with (static_dir / "index.html").open("r") as f:
            return HTMLResponse(f.read())

    return r
