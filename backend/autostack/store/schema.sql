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
    created TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    FOREIGN KEY (project_id) REFERENCES project (id),
    UNIQUE (project_id, name)
);

CREATE SEQUENCE IF NOT EXISTS model_id START 1;
CREATE TABLE IF NOT EXISTS model (
    id INTEGER PRIMARY KEY DEFAULT nextval('model_id'),
    project_id INTEGER NOT NULL,
    created TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,
    name TEXT NOT NULL,
    elo DOUBLE NOT NULL DEFAULT 1000, -- TODO: should this default be set elsewhere?
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

CREATE SEQUENCE IF NOT EXISTS battle_id START 1;
CREATE TABLE IF NOT EXISTS battle (
    id INTEGER PRIMARY KEY DEFAULT nextval('battle_id'),
    result_a_id INTEGER NOT NULL,
    result_b_id INTEGER NOT NULL,
    judge_id INTEGER NOT NULL,
    created TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,
    winner TEXT NOT NULL, -- e.g. "A", "B", "-"
    FOREIGN KEY (result_a_id) REFERENCES result (id),
    FOREIGN KEY (result_b_id) REFERENCES result (id),
    FOREIGN KEY (judge_id) REFERENCES judge (id),
    -- TODO: allow duplicate ratings from same judge (e.g. human)? Unique for now for convenience
    UNIQUE (result_a_id, result_b_id, judge_id)
);
