from fastapi import APIRouter

import autostack.api.api as API

from autostack.database import get_database_connection


def router() -> APIRouter:
    r = APIRouter()

    @r.get("")
    @r.get("/")
    def get_root() -> str:
        return "root"

    @r.get("/models")
    def get_models() -> list[API.Model]:
        with get_database_connection() as conn:
            models = conn.execute("SELECT id, name FROM model").fetchall()
        return [API.Model(id=id, name=name) for id, name in models]

    return r
