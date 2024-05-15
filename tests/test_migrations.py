import pytest
from alembic.command import downgrade, upgrade
from alembic.script import Script, ScriptDirectory

from tests.constants import alembic_config


def get_revisions() -> list[Script]:
    # Get directory object with Alembic migrations
    revisions_dir = ScriptDirectory.from_config(alembic_config)
    # Get & sort migrations, from first to last
    revisions = list(revisions_dir.walk_revisions())
    revisions.reverse()
    return revisions


@pytest.mark.usefixtures("db_url")
@pytest.mark.parametrize("revision", get_revisions())
def test_migrations_stairway(revision: Script) -> None:
    upgrade(alembic_config, revision.revision)

    # We need -1 for downgrading first migration (its down_revision is None)
    downgrade(
        alembic_config,
        revision.down_revision or "-1",  # type: ignore[arg-type]
    )
    upgrade(alembic_config, revision.revision)
