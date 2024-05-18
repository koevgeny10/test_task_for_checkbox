# mypy: ignore-errors
from sqlalchemy import URL, create_mock_engine
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable

from checks.repository.models.base import BaseModel


def sql_for_statement(stmt) -> None:
    return stmt.compile(dialect=postgresql.asyncpg.dialect())


def sql_for_model(model) -> None:
    return sql_for_statement(CreateTable(model.__table__))


def _dump(
    sql,
    *multiparams,  # noqa: ARG001
    **params,  # pylint: disable=unused-argument  # noqa: ARG001
) -> None:
    print(sql_for_statement(sql))  # noqa:T201


def sql_for_all_models() -> None:
    engine = create_mock_engine(URL.create(drivername="postgresql"), _dump)
    BaseModel.metadata.create_all(engine, checkfirst=False)
