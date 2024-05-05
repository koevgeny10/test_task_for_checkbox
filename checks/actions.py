# ruff: noqa: ARG001
from checks.domain.check import Check, CheckCreate
from checks.domain.user import UserCreate


async def create_user(user_create: UserCreate) -> None:
    raise NotImplementedError


async def create_check(user_id: int, check_create: CheckCreate) -> Check:
    raise NotImplementedError


async def get_check(check_id: int) -> Check:
    raise NotImplementedError


async def get_check_in_text(check_id: int) -> str:
    raise NotImplementedError


async def get_checks(user_id: int) -> tuple[Check, ...]:
    raise NotImplementedError
