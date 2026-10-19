"""Доменные модели генератора

Каждый класс описывает одну строку соответствующей таблицы ClickHouse.
Модули не знают ничего о БД: преобразованием в формат хранилища
занимается слой repository.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum


class DeviceType(StrEnum):
    """Устройство, с которого оформлен заказ."""

    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"


class PaymentMethod(StrEnum):
    """Способ оплаты."""

    CARD = "card"
    SBP = "sbp"
    CASH = "cash"
    INSTALLMENT = "installment"


class DeliveryMethod(StrEnum):
    """Способ доставки."""

    COURIER = "courier"
    PICKUP = "pickup"
    POST = "post"


@dataclass(frozen=True, slots=True)
class Brand:
    brand_id: int
    brand_name: str
    country_of_origin: str


@dataclass(frozen=True, slots=True)
class Category:
    category_id: int
    category_name: str
    parent_category_id: int | None


@dataclass(frozen=True, slots=True)
class Product:
    product_id: int
    product_name: str
    price: Decimal
    category_id: int
    brand_id: int


@dataclass(frozen=True, slots=True)
class City:
    city_id: int
    city_name: str


@dataclass(frozen=True, slots=True)
class Customer:
    customer_id: int
    full_name: str
    email: str
    city_id: int


@dataclass(frozen=True, slots=True)
class OrderItem:
    """Одна строка таблицы orders (одна позиция заказа)."""

    order_id: int
    order_item_id: int
    created_at: datetime
    customer_id: int
    device_type: DeviceType
    payment_method: PaymentMethod
    delivery_method: DeliveryMethod
    promo_code: bool
    product_id: int
    quantity: int
    unit_price: Decimal
