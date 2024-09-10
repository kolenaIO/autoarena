from pathlib import Path

import pytest

from autoarena.api import api
from autoarena.error import MigrationError
from autoarena.service.project import ProjectService
from autoarena.store.database import get_available_migrations, MIGRATION_DIRECTORY


def test__migration__new() -> None:
    project = ProjectService.create_idempotent(api.CreateProjectRequest(name="test__migration__new"))
    applied = ProjectService._get_applied_migrations(Path(project.filepath))
    available = get_available_migrations()
    assert len(available) == len(applied) > 0
    for i in range(len(available)):
        assert applied[i][0] == int(available[i].stem.split("__")[0])
        assert applied[i][1] == available[i].name


def test__migration__new__failed() -> None:
    migrations = get_available_migrations()
    next_migration_index = int(migrations[-1].name.split("__")[0]) + 1
    bad_migration_file = Path(MIGRATION_DIRECTORY) / f"{next_migration_index:03d}__bad.sql"
    try:
        with bad_migration_file.open("w") as f:
            f.write("CREATE TABLE whoopsies, this isn't valid SQL")
        with pytest.raises(MigrationError):
            ProjectService.create_idempotent(api.CreateProjectRequest(name="test__migration__new__failed"))
    finally:
        bad_migration_file.unlink()


def test__migration__existing() -> None:
    migrations = get_available_migrations()
    next_migration_index = int(migrations[-1].name.split("__")[0]) + 1
    new_migration_file = Path(MIGRATION_DIRECTORY) / f"{next_migration_index:03d}__bad.sql"
    try:
        with new_migration_file.open("w") as f:
            f.write("CREATE TABLE testing (id INTEGER PRIMARY KEY)")
        project = ProjectService.create_idempotent(api.CreateProjectRequest(name="test__migration__existing"))
        applied = ProjectService._get_applied_migrations(Path(project.filepath))
        assert applied[-1][0] == next_migration_index
        assert applied[-1][1] == new_migration_file.name
    finally:
        new_migration_file.unlink()
