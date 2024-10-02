CREATE TABLE IF NOT EXISTS judge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    judge_type TEXT NOT NULL, -- enum e.g. 'human', 'ollama', 'openai'; see api.JudgeType
    created TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,
    name TEXT NOT NULL UNIQUE,
    model_name TEXT, -- null for 'human' type
    system_prompt TEXT, -- null for 'human' type
    description TEXT NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS model (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,
    name TEXT NOT NULL UNIQUE,
    elo DOUBLE PRECISION NOT NULL DEFAULT 1000,
    q025 DOUBLE PRECISION,
    q975 DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS response (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id INTEGER NOT NULL,
    created TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    FOREIGN KEY (model_id) REFERENCES model (id) ON DELETE CASCADE,
    -- TODO: should we allow dupes for nondeterminism? This is a convenience to skip duplicate inserts
    UNIQUE (model_id, prompt)
);
CREATE INDEX IF NOT EXISTS response_prompt_idx ON response (prompt);

-- TODO: would be great to use enum but it does not have an idempotent CREATE option
-- CREATE TYPE WINNER AS ENUM ('A', 'B', '-');
-- utility to create a deterministic slug from 2 numeric IDs presented in any order
CREATE TABLE IF NOT EXISTS head_to_head (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    response_id_slug TEXT NOT NULL, -- see id_slug macro
    response_a_id INTEGER NOT NULL,
    response_b_id INTEGER NOT NULL,
    judge_id INTEGER NOT NULL,
    created TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,
    winner TEXT NOT NULL, -- e.g. "A", "B", "-"
    FOREIGN KEY (response_a_id) REFERENCES response (id) ON DELETE CASCADE,
    FOREIGN KEY (response_b_id) REFERENCES response (id) ON DELETE CASCADE,
    FOREIGN KEY (judge_id) REFERENCES judge (id) ON DELETE CASCADE,
    -- TODO: allow duplicate ratings from same judge (e.g. human)? Unique for now for convenience
    UNIQUE (response_id_slug, judge_id)
);

CREATE TABLE IF NOT EXISTS task (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_type TEXT NOT NULL, -- enum e.g. 'auto-judge', 'recompute-leaderboard'; see api.TaskType
    created TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,
    progress DOUBLE PRECISION NOT NULL DEFAULT 0, -- on [0,1]
    status TEXT NOT NULL, -- enum e.g. 'started', 'in-progress'; see api.TaskStatus
    logs TEXT NOT NULL DEFAULT '' -- freeform
);

CREATE TABLE IF NOT EXISTS migration (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    migration_index INTEGER NOT NULL UNIQUE,
    filename TEXT NOT NULL UNIQUE,
    created TIMESTAMPTZ NOT NULL DEFAULT current_timestamp
);
