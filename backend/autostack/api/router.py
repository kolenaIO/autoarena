from dataclasses import dataclass
from datetime import datetime

from fastapi import APIRouter

from autostack.store.database import get_database_connection


@dataclass(frozen=True)
class Project:
    id: int
    name: str
    created: datetime


@dataclass(frozen=True)
class CreateProjectRequest:
    name: str


@dataclass(frozen=True)
class Model:
    id: int
    name: str
    created: datetime
    elo: float
    q025: float
    q975: float
    votes: int


@dataclass(frozen=True)
class BattlesRequest:
    project_id: int
    model_a_id: int
    model_b_id: int


@dataclass(frozen=True)
class Battle:
    id: int
    prompt: str
    response_a: str
    response_b: str


def router() -> APIRouter:
    r = APIRouter()

    @r.get("/projects")
    def get_projects() -> list[Project]:
        with get_database_connection() as conn:
            df_project = conn.execute("SELECT id, name, created FROM project").df()
        return [Project(id=r.id, name=r.name, created=r.created) for r in df_project.itertuples()]

    @r.put("/project")
    def create_project(request: CreateProjectRequest) -> Project:
        with get_database_connection() as conn:
            params = dict(name=request.name)
            conn.execute("INSERT INTO project (name) VALUES ($name)", params)
            ((project_id, name, created),) = conn.execute(
                "SELECT id, name, created FROM project WHERE name = $name",
                params,
            ).fetchall()
        return Project(id=project_id, name=name, created=created)

    @r.get("/models/{project_id}")
    def get_models(project_id: int) -> list[Model]:
        with get_database_connection() as conn:
            df_model = conn.execute(
                """
                WITH vote_count_a AS (
                    SELECT m.id AS model_id, COUNT(1) AS vote_count
                    FROM model m
                    JOIN result r ON r.model_id = m.id
                    JOIN battle b ON r.id = b.result_a_id
                    GROUP BY m.id
                ), vote_count_b AS (
                    SELECT m.id AS model_id, COUNT(1) AS vote_count
                    FROM model m
                    JOIN result r ON r.model_id = m.id
                    JOIN battle b ON r.id = b.result_b_id
                    GROUP BY m.id
                )
                SELECT
                    id,
                    name,
                    created,
                    elo,
                    q025,
                    q975,
                    IFNULL(vca.vote_count, 0) + IFNULL(vcb.vote_count, 0) AS count
                FROM model m
                LEFT JOIN vote_count_a vca ON m.id = vca.model_id
                LEFT JOIN vote_count_b vcb ON m.id = vcb.model_id
                WHERE project_id = ?
            """,
                [project_id],
            ).df()
        return [
            Model(
                id=r.id,
                name=r.name,
                created=r.created,
                elo=r.elo,
                q025=r.q025,
                q975=r.q975,
                votes=r.count,
            )
            for r in df_model.itertuples()
        ]

    @r.put("/battles")
    def get_battles(request: BattlesRequest) -> list[Battle]:
        with get_database_connection() as conn:
            df_battle = conn.execute(
                """
                SELECT
                    b.id AS battle_id,
                    ma.id AS model_a_id,
                    mb.id AS model_b_id,
                    ra.prompt AS prompt,
                    ra.response AS response_a,
                    rb.response AS response_b,
                    b.winner
                FROM battle b
                JOIN result ra ON b.result_a_id = ra.id
                JOIN result rb ON b.result_b_id = rb.id
                JOIN model ma ON ra.model_id = ma.id
                JOIN model mb ON rb.model_id = mb.id
                JOIN judge j ON b.judge_id = j.id
                WHERE j.project_id = $project_id
                AND ma.id IN ($model_a_id, $model_b_id)
                AND mb.id IN ($model_a_id, $model_b_id)
            """,
                dict(project_id=request.project_id, model_a_id=request.model_a_id, model_b_id=request.model_b_id),
            ).df()

        condition = (df_battle["model_b_id"] == request.model_a_id) & (df_battle["model_a_id"] == request.model_b_id)
        columns = ["response_a", "response_b"]
        df_battle.loc[condition, columns] = df_battle.loc[condition, columns[::-1]].values
        return [
            Battle(id=r.battle_id, prompt=r.prompt, response_a=r.response_a, response_b=r.response_b)
            for r in df_battle.itertuples()
        ]

    return r
