from abc import ABC, abstractmethod
from collections.abc import Iterable
from datetime import datetime
from decimal import Decimal
from functools import cached_property
from typing import Annotated, Generic, Literal, Self, TypedDict, TypeVar
from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
    PastDatetime,
    PositiveInt,
    computed_field,
    model_validator,
)

from checks.domain.base import IdSchema
from checks.domain.constants import PaymentType

money_field = Field(
    decimal_places=2,
    gt=0,
    description="Гроші",
    examples=["123.45", "1"],
)
_Money = Annotated[Decimal, money_field]


class _ProductCreate(BaseModel, frozen=True):
    name: str
    price: _Money
    quantity: Annotated[int, Field(ge=1)]

    @cached_property
    def total(self) -> Decimal:
        return self.price * self.quantity


class _Payment(BaseModel, from_attributes=True):
    type: PaymentType
    amount: _Money


_ProductTypeVar = TypeVar("_ProductTypeVar", bound=_ProductCreate)


class _CheckABC(BaseModel, ABC, Generic[_ProductTypeVar]):
    products_field: Annotated[
        tuple[_ProductTypeVar, ...],
        Field(exclude=True, alias="products", min_length=1),
    ]
    payment: _Payment

    @property
    @abstractmethod
    def products(self) -> Iterable[_ProductTypeVar]:
        raise NotImplementedError

    @computed_field(return_type=_Money)  # type: ignore[misc]
    @cached_property
    def total(self) -> Decimal | Literal[0]:
        return sum(product.total for product in self.products)

    @model_validator(mode="after")
    def check_money(self) -> Self:
        if self.payment.amount >= self.total:
            return self
        raise ValueError("payment.amount is less then total cost")


class CheckCreate(_CheckABC[_ProductCreate]):
    # pylint: disable=too-few-public-methods
    @computed_field  # type: ignore[misc]
    @cached_property
    def products(self) -> tuple[_ProductCreate, ...]:
        return self.products_field


class _Product(_ProductCreate, from_attributes=True):
    @computed_field  # type: ignore[misc]
    @cached_property
    def total(self) -> _Money:
        return super().total


class Check(IdSchema, _CheckABC[_Product]):
    public_id: UUID
    user_id: PositiveInt
    created_at: PastDatetime

    @computed_field  # type: ignore[misc]
    @cached_property
    def products(self) -> tuple[_Product, ...]:
        return self.products_field

    @computed_field  # type: ignore[misc]
    @cached_property
    def rest(
        self,
    ) -> Annotated[
        Decimal,
        Field(
            ge=0,
            decimal_places=2,
            description=money_field.description,
            examples=money_field.examples,
        ),
    ]:
        return self.payment.amount - self.total


class CheckFilters(TypedDict, total=False):
    created_at__ge: datetime | None
    created_at__le: datetime | None
    total__ge: Decimal | None
    total__le: Decimal | None
    payment_type__eq: PaymentType | None
