import operator
from collections.abc import Generator, Mapping
from typing import Any

from sqlalchemy import ColumnElement, Select, select

from checks.repository.models.base import BaseModel
from checks.repository.models.check import CheckModel


def _get_whereclauses_for_sa_query(
    model: type[BaseModel],
    filters: Mapping[str, Any],
) -> Generator[ColumnElement[Any], None, None]:
    for field_name_and_operator_name, filter_value in filters.items():
        field_name, operator_name = field_name_and_operator_name.split("__")
        operator_function = getattr(operator, operator_name)
        model_field = getattr(model, field_name)
        if filter_value is not None or operator_function in {
            operator.is_,
            operator.is_not,
        }:
            yield operator_function(model_field, filter_value)


def get_select_checks_sql_query(
    check_id: int,
    filters: Mapping[str, Any],
) -> Select[tuple[CheckModel]]:
    return select(CheckModel).where(
        CheckModel.id == check_id,
        *_get_whereclauses_for_sa_query(CheckModel, filters),
    )
