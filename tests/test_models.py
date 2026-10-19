from dataclasses import FrozenInstanceError
from datetime import datetime
from decimal import Decimal

import pytest

from generator.models import (
    DeliveryMethod,
    DeviceType,
    OrderItem,
    PaymentMethod,
)


def make_item() -> OrderItem:
    return OrderItem(
        order_id=1,
        order_item_id=1,
        created_at=datetime(2026, 10, 19, 12, 0, 0),
        customer_id=42,
        device_type=DeviceType.MOBILE,
        payment_method=PaymentMethod.CARD,
        delivery_method=DeliveryMethod.COURIER,
        promo_code=False,
        product_id=7,
        quantity=2,
        unit_price=Decimal("199.90"),
    )


def test_order_item_is_immutable() -> None:
    item = make_item()
    with pytest.raises(FrozenInstanceError):
        item.quantity = 5  # type: ignore[misc]


def test_enums_behave_like_strings() -> None:
    assert PaymentMethod.CARD == "card"
    assert str(DeviceType.MOBILE) == "mobile"


def test_money_is_exact() -> None:
    item = make_item()
    assert item.unit_price * item.quantity == Decimal("399.80")
