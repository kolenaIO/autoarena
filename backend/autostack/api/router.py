from fastapi import APIRouter


def router() -> APIRouter:
    r = APIRouter()

    @r.get("")
    @r.get("/")
    def get_root() -> str:
        return "root"

    return r
