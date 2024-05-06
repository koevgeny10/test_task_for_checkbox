from abc import ABC, abstractmethod
from collections.abc import Iterable
from decimal import Decimal
from functools import cached_property
from typing import Annotated, Generic, Literal, Self, TypeVar

from pydantic import (
    BaseModel,
    Field,
    PastDatetime,
    PositiveInt,
    computed_field,
    model_validator,
)

Money = Annotated[Decimal, Field(decimal_places=2, gt=0)]


class _ProductCreate(BaseModel, frozen=True):
    name: str
    price: Money
    quantity: PositiveInt

    @cached_property
    def total(self) -> Decimal:
        return self.price * self.quantity


class _Payment(BaseModel):
    type: Literal["cash", "cashless"]
    amount: Money


ProductTypeVar = TypeVar("ProductTypeVar", bound=_ProductCreate)


class _CheckABC(BaseModel, ABC, Generic[ProductTypeVar]):
    products_field: Annotated[
        set[ProductTypeVar],
        Field(exclude=True, alias="products", min_length=1),
    ]
    payment: _Payment

    @property
    @abstractmethod
    def products(self) -> Iterable[ProductTypeVar]:
        raise NotImplementedError

    @computed_field(return_type=Decimal)  # type: ignore[misc]
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
    def products(self) -> set[_ProductCreate]:
        return self.products_field


class _Product(_ProductCreate):
    total = computed_field(  # type: ignore[assignment, pydantic-field]
        _ProductCreate.total,
    )


class Check(_CheckABC[_Product], from_attributes=True):
    id: int
    created_at: PastDatetime

    @computed_field  # type: ignore[misc]
    @cached_property
    def products(self) -> set[_Product]:
        return self.products_field

    @computed_field  # type: ignore[misc]
    @cached_property
    def rest(self) -> Decimal:
        return self.payment.amount - self.total
