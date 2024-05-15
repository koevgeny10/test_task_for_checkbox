# pylint: disable=too-few-public-methods
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, func, text
from sqlalchemy.orm import Mapped, composite, mapped_column, relationship

from checks.domain.constants import PaymentType
from checks.repository.models.base import BaseModel


class ProductModel(BaseModel):
    check_id: Mapped[int] = mapped_column(
        ForeignKey("checks.id", onupdate="CASCADE", ondelete="CASCADE"),
    )
    check: Mapped["CheckModel"] = relationship(
        back_populates="products",
        lazy="joined",
    )
    name: Mapped[str]
    price: Mapped[Decimal]
    quantity: Mapped[int]


@dataclass
class _Payment:
    type: PaymentType
    amount: Decimal


class CheckModel(BaseModel):
    public_id: Mapped[UUID] = mapped_column(
        unique=True,
        index=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
    )
    products: Mapped[list[ProductModel]] = relationship(
        back_populates="check",
        lazy="selectin",
    )
    payment_type: Mapped[PaymentType] = mapped_column()
    payment_amount: Mapped[Decimal] = mapped_column()
    payment: Mapped[_Payment] = composite(payment_type, payment_amount)
    total: Mapped[Decimal]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # pylint: disable=not-callable
    )

    def __init__(self, **kwargs: Any):
        products = kwargs.get("products")
        if hasattr(products, "__iter__"):
            deserialized_products = []
            for product in kwargs["products"]:
                if isinstance(product, dict):
                    product = ProductModel(**product)  # noqa: PLW2901
                deserialized_products.append(product)
            kwargs["products"] = deserialized_products

        payment = kwargs.get("payment")
        if isinstance(payment, dict):
            kwargs["payment"] = _Payment(**payment)

        super().__init__(**kwargs)
