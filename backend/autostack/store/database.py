from contextlib import contextmanager
from pathlib import Path

import duckdb
import pandas as pd

DATABASE_DIRECTORY = (Path(__file__).parent / ".." / ".." / ".data").resolve()
DATABASE_FILE = DATABASE_DIRECTORY / "database.duckdb"
SCHEMA_FILE = Path(__file__).parent / "schema.sql"


@contextmanager
def get_database_connection() -> duckdb.DuckDBPyConnection:
    conn = duckdb.connect(str(DATABASE_FILE))
    try:
        yield conn
    finally:
        conn.close()


def setup_database(battles_parquet: str) -> None:
    DATABASE_DIRECTORY.mkdir(parents=True, exist_ok=True)
    project_name = Path(battles_parquet).stem

    df_battles = pd.read_parquet(battles_parquet)
    # TODO: should probably preprocess to avoid doing this here
    df_battles["winner"] = df_battles.apply(
        lambda r: "A" if r.winner_model_a > 0 else "B" if r.winner_model_b else "-",
        axis=1,
    )

    with get_database_connection() as conn:
        schema_sql = SCHEMA_FILE.read_text()

        # 1. set up schema
        conn.sql(schema_sql)

        # 2. seed with project
        conn.execute(
            """
            INSERT INTO project (name)
            VALUES (?)
            ON CONFLICT (name) DO NOTHING
        """,
            [project_name],
        )
        (project_id,) = conn.execute("SELECT id FROM project WHERE name = ?", [project_name]).fetchall()[0]

        # 3. seed with judges
        conn.execute(
            """
            INSERT INTO judge (project_id, name, description)
            VALUES (?, ?, ?)
            ON CONFLICT (project_id, name) DO NOTHING
        """,
            [project_id, "Human", "Manual ratings submitted via the 'Head-to-Head' tab"],
        )
        (judge_id,) = conn.execute(
            """
            SELECT j.id
            FROM judge j
            WHERE name = ?
            AND project_id = ?
        """,
            ["Human", project_id],
        ).fetchall()[0]

        # 4. seed with models
        models = list(set(df_battles["model_a"]) & set(df_battles["model_b"]))
        df_model = pd.DataFrame([(project_id, m) for m in models], columns=["project_id", "name"])
        conn.sql("""
            INSERT INTO model (project_id, name)
            SELECT project_id, name
            FROM df_model
            ON CONFLICT (project_id, name) DO NOTHING
        """)
        df_model = conn.execute("SELECT id, name FROM model WHERE project_id = ?", [project_id]).df()

        # 5. seed with results
        result_cols_a = ["model_a", "prompt", "response_a"]
        df_result_a = df_battles[result_cols_a].rename(columns=dict(model_a="model", response_a="response"))
        result_cols_b = ["model_b", "prompt", "response_b"]
        df_result_b = df_battles[result_cols_b].rename(columns=dict(model_b="model", response_b="response"))
        df_result = pd.concat([df_result_a, df_result_b])
        df_result = pd.merge(df_result, df_model, left_on="model", right_on="name", how="left")
        df_result = df_result[df_result["response"].notna()]  # drop empty responses
        df_result = df_result.drop_duplicates(subset=["id", "prompt"], keep="last")  # drop duplicate rows
        conn.sql("""
            INSERT INTO result (model_id, prompt, response)
            SELECT id, prompt, response
            FROM df_result
            ON CONFLICT (model_id, prompt) DO NOTHING
        """)
        df_result = conn.execute(
            """
            SELECT r.id AS result_a_id, m.name AS model, prompt, response
            FROM result r
            JOIN model m ON m.id = r.model_id
            WHERE m.project_id = ?
        """,
            [project_id],
        ).df()

        # 6. seed with battles
        right_on = ["model", "prompt"]
        df_battle = pd.merge(df_battles, df_result, left_on=["model_a", "prompt"], right_on=right_on, how="left")
        df_result = df_result.rename(columns=dict(result_a_id="result_b_id"))
        df_battle = pd.merge(df_battle, df_result, left_on=["model_b", "prompt"], right_on=right_on, how="left")
        df_battle = df_battle[df_battle["result_a_id"].notna()]  # drop empty battles
        df_battle = df_battle[df_battle["result_b_id"].notna()]  # drop empty battles
        df_battle = df_battle.drop_duplicates(subset=["result_a_id", "result_b_id"], keep="last")
        df_battle["judge_id"] = judge_id
        conn.execute("""
            INSERT INTO battle (result_a_id, result_b_id, judge_id, winner)
            SELECT result_a_id, result_b_id, judge_id, winner
            FROM df_battle
            ON CONFLICT (result_a_id, result_b_id, judge_id) DO NOTHING
        """)

        conn.commit()


def get_df_battle(project_id: int) -> pd.DataFrame:
    with get_database_connection() as conn:
        df_battle = conn.execute(
            """
            SELECT
                b.id AS battle_id,
                ma.id AS model_a_id,
                ma.name AS model_a_name,
                mb.id AS model_b_id,
                mb.name AS model_b_name,
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
            WHERE j.project_id = ?
        """,
            [project_id],
        ).df()
        return df_battle
