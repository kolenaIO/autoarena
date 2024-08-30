import dataclasses
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from typing import Annotated, Literal

import pandas as pd
import numpy as np
from fastapi import APIRouter, UploadFile, Form

from autostack.elo import compute_elo_single
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
    q025: float | None
    q975: float | None
    votes: int


@dataclass(frozen=True)
class HeadToHeadsRequest:
    project_id: int  # TODO: is this required given that models are scoped to projects?
    model_a_id: int
    model_b_id: int


@dataclass(frozen=True)
class HeadToHead:
    prompt: str
    result_a_id: int
    response_a: str
    result_b_id: int
    response_b: str
    # TODO: also add voting history from any judgements already made?


@dataclass(frozen=True)
class HeadToHeadJudgementRequest:
    project_id: int
    judge_name: str  # TODO: id..?
    result_a_id: int
    result_b_id: int
    winner: Literal["A", "B", "-"]


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
        df_model = df_model.replace({np.nan: None})
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

    @r.post("/model")
    async def upload_model_results(
        file: UploadFile,
        new_model_name: Annotated[str, Form()],
        project_id: Annotated[int, Form()],
    ) -> str:
        contents = await file.read()
        if file.content_type == "text/csv":
            df = pd.read_csv(BytesIO(contents))
        else:
            raise ValueError(f"unsupported file type: {file.content_type}")

        required_columns = {"prompt", "response"}
        missing_columns = required_columns - set(df.columns)
        if len(missing_columns) > 0:
            raise ValueError(f"missing required column(s): {missing_columns}")

        with get_database_connection() as conn:
            params = dict(project_id=project_id, model_name=new_model_name)
            conn.execute("INSERT INTO model (project_id, name) VALUES ($project_id, $model_name)", params)
            ((new_model_id,),) = conn.execute(
                "SELECT id FROM model WHERE project_id = $project_id AND name = $model_name",
                params,
            ).fetchall()
            df["model_id"] = new_model_id
            out = conn.execute("""
                INSERT INTO result (model_id, prompt, response)
                SELECT model_id, prompt, response
                FROM df
            """)

        print(out)
        return "foobar"

    @r.put("/head-to-heads")
    def get_head_to_heads(request: HeadToHeadsRequest) -> list[HeadToHead]:
        with get_database_connection() as conn:
            df_h2h = conn.execute(
                """
                SELECT
                    ra.id AS result_a_id,
                    rb.id AS result_b_id,
                    ra.prompt AS prompt,
                    ra.response AS response_a,
                    rb.response AS response_b
                FROM result ra
                JOIN result rb ON ra.prompt = rb.prompt
                WHERE ra.model_id = $model_a_id
                AND rb.model_id = $model_b_id
            """,
                dict(model_a_id=request.model_a_id, model_b_id=request.model_b_id),
            ).df()

        return [
            HeadToHead(
                prompt=r.prompt,
                result_a_id=r.result_a_id,
                response_a=r.response_a,
                result_b_id=r.result_b_id,
                response_b=r.response_b,
            )
            for r in df_h2h.itertuples()
        ]

    @r.post("/head-to-head/judgement")
    def submit_head_to_head_judgement(request: HeadToHeadJudgementRequest) -> None:
        with get_database_connection() as conn:
            # 1. create judge if necessary
            out = conn.execute(
                """
                SELECT 1
                FROM judge j
                WHERE j.project_id = $project_id
                AND j.name = $judge_name;
            """,
                dict(project_id=request.project_id, judge_name=request.judge_name),
            ).fetchall()
            if len(out) == 0:
                print(f"Adding judge '{request.judge_name}'...")
                conn.execute(
                    "INSERT INTO judge (project_id, name, description) VALUES ($project_id, $judge_name, '')",
                    dict(project_id=request.project_id, judge_name=request.judge_name),
                )

            # 2. insert battle record
            conn.execute(
                """
                INSERT INTO battle (result_a_id, result_b_id, judge_id, winner)
                SELECT $result_a_id, $result_b_id, j.id, $winner
                FROM judge j
                WHERE j.project_id = $project_id
                AND j.name = $judge_name
                ON CONFLICT (result_a_id, result_b_id, judge_id) DO UPDATE SET winner = EXCLUDED.winner
            """,
                dataclasses.asdict(request),
            )

            # 3. adjust elo scores
            df_model = conn.execute(
                """
                SELECT id, elo
                FROM model m
                WHERE EXISTS (SELECT 1 FROM result r WHERE r.id = $result_a_id AND r.model_id = m.id)
                UNION ALL
                SELECT id, elo
                FROM model m
                WHERE EXISTS (SELECT 1 FROM result r WHERE r.id = $result_b_id AND r.model_id = m.id)
            """,
                dict(result_a_id=request.result_a_id, result_b_id=request.result_b_id),
            ).df()
            model_a = df_model.iloc[0]
            model_b = df_model.iloc[1]
            elo_a, elo_b = compute_elo_single(model_a.elo, model_b.elo, request.winner)
            for model_id, elo in [(model_a.id, elo_a), (model_b.id, elo_b)]:
                conn.execute("UPDATE model SET elo = $elo WHERE id = $model_id", dict(model_id=model_id, elo=elo))

            # TODO: recompute confidence interval...?

    return r
