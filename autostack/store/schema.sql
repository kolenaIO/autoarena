CREATE SEQUENCE IF NOT EXISTS project_id START 1;
CREATE TABLE IF NOT EXISTS project (
    id INTEGER PRIMARY KEY DEFAULT nextval('project_id'),
    created TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,
    name TEXT NOT NULL UNIQUE
);

CREATE SEQUENCE IF NOT EXISTS judge_id START 1;
CREATE TABLE IF NOT EXISTS judge (
    id INTEGER PRIMARY KEY DEFAULT nextval('judge_id'),
    project_id INTEGER NOT NULL,
    judge_type TEXT NOT NULL, -- e.g. 'human', 'ollama', 'openai'
    created TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,
    name TEXT NOT NULL,
    model_name TEXT, -- null for 'human' type
    system_prompt TEXT, -- null for 'human' type
    description TEXT NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (project_id) REFERENCES project (id),
    UNIQUE (project_id, name)
);

CREATE SEQUENCE IF NOT EXISTS model_id START 1;
CREATE TABLE IF NOT EXISTS model (
    id INTEGER PRIMARY KEY DEFAULT nextval('model_id'),
    project_id INTEGER NOT NULL,
    created TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,
    name TEXT NOT NULL,
    elo DOUBLE PRECISION NOT NULL DEFAULT 1000,
    q025 DOUBLE PRECISION,
    q975 DOUBLE PRECISION,
    FOREIGN KEY (project_id) REFERENCES project (id),
    UNIQUE (project_id, name)
);

CREATE SEQUENCE IF NOT EXISTS result_id START 1;
CREATE TABLE IF NOT EXISTS result (
    id INTEGER PRIMARY KEY DEFAULT nextval('result_id'),
    model_id INTEGER NOT NULL,
    created TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    FOREIGN KEY (model_id) REFERENCES model (id),
    -- TODO: should we allow dupes for nondeterminism? This is a convenience to skip duplicate inserts
    UNIQUE (model_id, prompt)
);

-- TODO: would be great to use enum but it does not have an idempotent CREATE option
-- CREATE TYPE WINNER AS ENUM ('A', 'B', '-');
-- utility to create a deterministic slug from 2 numeric IDs presented in any order
CREATE OR REPLACE MACRO id_slug(id_a, id_b) AS
    IF(id_a < id_b, id_a, id_b)::INTEGER || '-' || IF(id_a < id_b, id_b, id_a)::INTEGER;
CREATE OR REPLACE MACRO invert_winner(winner) AS IF(winner = 'A', 'B', IF(winner = 'B', 'A', winner));
CREATE SEQUENCE IF NOT EXISTS battle_id START 1;
CREATE TABLE IF NOT EXISTS battle (
    id INTEGER PRIMARY KEY DEFAULT nextval('battle_id'),
    result_id_slug TEXT NOT NULL, -- see id_slug macro
    result_a_id INTEGER NOT NULL,
    result_b_id INTEGER NOT NULL,
    judge_id INTEGER NOT NULL,
    created TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,
    winner TEXT NOT NULL, -- e.g. "A", "B", "-"
    FOREIGN KEY (result_a_id) REFERENCES result (id),
    FOREIGN KEY (result_b_id) REFERENCES result (id),
    FOREIGN KEY (judge_id) REFERENCES judge (id),
    -- TODO: allow duplicate ratings from same judge (e.g. human)? Unique for now for convenience
    UNIQUE (result_id_slug, judge_id)
);

CREATE SEQUENCE IF NOT EXISTS task_id START 1;
CREATE TABLE IF NOT EXISTS task (
    id INTEGER PRIMARY KEY DEFAULT nextval('task_id'),
    project_id INTEGER NOT NULL,
    task_type TEXT NOT NULL, -- e.g. 'fine-tune', 'auto-judge', 'recompute-confidence-intervals'
    created TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,
    progress DOUBLE PRECISION NOT NULL DEFAULT 0, -- on [0,1]
    status TEXT NOT NULL DEFAULT 'Started', -- freeform
    FOREIGN KEY (project_id) REFERENCES project (id)
);
