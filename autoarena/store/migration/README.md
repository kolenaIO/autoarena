# Migrations

Define project database file schema migrations in this directory with filenames following the format:

```shell
{index}__{name}.sql  # e.g. "000__init.sql"
```

Migrations are applied in ascending order of `index`. When a new version of AutoArena is run on older project files,
any migrations that have not yet been run are run to migrate the project to the latest schema.
