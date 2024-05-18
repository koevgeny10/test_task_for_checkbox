import operator
from collections.abc import Generator, Mapping
from typing import Any, TypeVar
from uuid import UUID

from sqlalchemy import ColumnElement, Select, func, select

from checks.domain.base import PageParams
from checks.domain.check import CheckFilters
from checks.repository.models.base import BaseModel
from checks.repository.models.check import CheckModel
from checks.repository.models.user import UserModel


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


SelectReturn = TypeVar("SelectReturn")


def get_select_query_with_additional_filters(
    stmt: Select[tuple[SelectReturn]],
    user_id: int,
    check_filters: CheckFilters | None = None,
) -> Select[tuple[SelectReturn]]:
    if check_filters is not None:
        stmt = stmt.where(
            *_get_whereclauses_for_sa_query(CheckModel, check_filters),
        )
    return stmt.where(
        CheckModel.user_id == user_id,
    )


def get_select_count_checks(
    user_id: int,
    check_filters: CheckFilters | None = None,
) -> Select[tuple[int]]:
    return get_select_query_with_additional_filters(
        select(func.count()),  # pylint: disable=not-callable
        user_id,
        check_filters,
    )


def get_select_checks_sql_query(
    user_id: int,
    check_filters: CheckFilters | None = None,
    page_params: PageParams | None = None,
) -> Select[tuple[CheckModel]]:
    stmt = get_select_query_with_additional_filters(
        select(CheckModel),
        user_id,
        check_filters,
    )
    if page_params is not None:
        offset = page_params.get("offset")
        if offset is not None:
            stmt = stmt.offset(offset)
        limit = page_params.get("limit")
        if limit is not None:
            stmt = stmt.limit(limit)
    return stmt


def get_select_user_filtered_by_email_sql_query(
    email: str,
) -> Select[tuple[UserModel]]:
    return select(UserModel).where(UserModel.email == email)


def get_select_check_by_public_id_sql_query(
    check_public_id: UUID,
) -> Select[tuple[CheckModel]]:
    return select(CheckModel).where(CheckModel.public_id == check_public_id)
