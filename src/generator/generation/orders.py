"""Генерация заказов: клиент, товары, количество, устройство, оплата, доставка.

Порядок обращений к потоку случайных чисел "orders" зафиксирован:
клиент -> устройство -> доставка -> оплата -> промокод -> число позиций ->
товары -> количества. Изменение порядка меняет данные при том же seed.
"""

import random
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from itertools import accumulate

from generator.generation.catalog import Catalog
from generator.generation.rng import make_rng
from generator.models import (
    Customer,
    DeliveryMethod,
    DeviceType,
    OrderItem,
    PaymentMethod,
    Product,
)

_CENT = Decimal("0.01")
_CHEAP_LIMIT = Decimal("5000")

_ITEMS_PER_ORDER: tuple[tuple[int, float], ...] = (
    (1, 0.70),
    (2, 0.22),
    (3, 0.06),
    (4, 0.02),
)

_QUANTITY_CHEAP: tuple[tuple[int, float], ...] = (
    (1, 0.60),
    (2, 0.25),
    (3, 0.10),
    (4, 0.05),
)
_QUANTITY_EXPENSIVE: tuple[tuple[int, float], ...] = (
    (1, 0.93),
    (2, 0.07),
)

_DEVICES: tuple[tuple[DeviceType, float], ...] = (
    (DeviceType.MOBILE, 0.58),
    (DeviceType.DESKTOP, 0.35),
    (DeviceType.TABLET, 0.07),
)

_DELIVERY: tuple[tuple[DeliveryMethod, float], ...] = (
    (DeliveryMethod.COURIER, 0.45),
    (DeliveryMethod.PICKUP, 0.40),
    (DeliveryMethod.POST, 0.15),
)

_PAYMENT: tuple[tuple[PaymentMethod, float], ...] = (
    (PaymentMethod.CARD, 0.55),
    (PaymentMethod.SBP, 0.30),
    (PaymentMethod.INSTALLMENT, 0.08),
    (PaymentMethod.CASH, 0.07),
)
# При доставке почтой наличные не принимаются.
_PAYMENT_NO_CASH: tuple[tuple[PaymentMethod, float], ...] = tuple(
    option for option in _PAYMENT if option[0] is not PaymentMethod.CASH
)


@dataclass(frozen=True, slots=True)
class OrderConditions:
    """Условия, в которых создаётся заказ. Через них аномалии управляют заказами."""

    promo_probability: float = 0.08
    promo_discount: Decimal = Decimal("0.10")
    unavailable_product_ids: frozenset[int] = frozenset()

    def __post_init__(self) -> None:
        if not 0.0 <= self.promo_probability <= 1.0:
            raise ValueError("promo_probability должна быть в диапазоне [0, 1]")
        if not Decimal(0) <= self.promo_discount < Decimal(1):
            raise ValueError("promo_discount должна быть в диапазоне [0, 1)")


NORMAL_CONDITIONS = OrderConditions()


def _pick[T](rng: random.Random, options: tuple[tuple[T, float], ...]) -> T:
    """Выбирает значение из пар (значение, вес) с учётом весов."""
    values = [value for value, _ in options]
    weights = [weight for _, weight in options]
    return rng.choices(values, weights=weights)[0]


class OrderFactory:
    """Создаёт заказы: каждый вызов build_order возвращает позиции одного заказа."""

    def __init__(
        self,
        catalog: Catalog,
        customers: Sequence[Customer],
        seed: int,
        first_order_id: int = 1,
        first_item_id: int = 1,
    ) -> None:
        self._products = catalog.products
        self._customers = tuple(customers)

        # Популярность задаётся один раз и в отдельных потоках,
        # чтобы число созданных заказов не меняло список «хитов».
        product_rng = make_rng(seed, "product-popularity")
        self._product_weights = tuple(
            (1.0 / float(product.price) ** 0.5) * product_rng.lognormvariate(0.0, 0.5)
            for product in self._products
        )
        customer_rng = make_rng(seed, "customer-activity")
        self._customer_cum_weights = tuple(
            accumulate(customer_rng.lognormvariate(0.0, 1.0) for _ in self._customers)
        )

        self._rng = make_rng(seed, "orders")
        self._next_order_id = first_order_id
        self._next_item_id = first_item_id

    def build_order(
        self, at: datetime, conditions: OrderConditions = NORMAL_CONDITIONS
    ) -> tuple[OrderItem, ...]:
        """Создаёт один заказ на момент `at` с учётом условий."""
        rng = self._rng
        order_id = self._next_order_id
        self._next_order_id += 1

        customer = rng.choices(self._customers, cum_weights=self._customer_cum_weights)[0]
        device = _pick(rng, _DEVICES)
        delivery = _pick(rng, _DELIVERY)
        payment_options = _PAYMENT_NO_CASH if delivery is DeliveryMethod.POST else _PAYMENT
        payment = _pick(rng, payment_options)
        promo = rng.random() < conditions.promo_probability

        items: list[OrderItem] = []
        for product in self._choose_products(_pick(rng, _ITEMS_PER_ORDER), conditions):
            item_id = self._next_item_id
            self._next_item_id += 1
            items.append(
                OrderItem(
                    order_id=order_id,
                    order_item_id=item_id,
                    created_at=at,
                    customer_id=customer.customer_id,
                    device_type=device,
                    payment_method=payment,
                    delivery_method=delivery,
                    promo_code=promo,
                    product_id=product.product_id,
                    quantity=self._quantity(product.price),
                    unit_price=self._unit_price(product.price, promo, conditions),
                )
            )
        return tuple(items)

    def _choose_products(self, count: int, conditions: OrderConditions) -> list[Product]:
        """Выбирает `count` разных товаров среди доступных, с учётом популярности."""
        unavailable = conditions.unavailable_product_ids
        candidates = tuple(
            (product, weight)
            for product, weight in zip(self._products, self._product_weights, strict=True)
            if product.product_id not in unavailable
        )
        if not candidates:
            raise ValueError("Нет доступных товаров: все товары помечены как недоступные")

        wanted = min(count, len(candidates))
        chosen: list[Product] = []
        while len(chosen) < wanted:
            product = _pick(self._rng, candidates)
            if product not in chosen:
                chosen.append(product)
        return chosen

    def _quantity(self, price: Decimal) -> int:
        options = _QUANTITY_CHEAP if price < _CHEAP_LIMIT else _QUANTITY_EXPENSIVE
        return _pick(self._rng, options)

    @staticmethod
    def _unit_price(price: Decimal, promo: bool, conditions: OrderConditions) -> Decimal:
        if not promo:
            return price
        discounted = price * (Decimal(1) - conditions.promo_discount)
        return discounted.quantize(_CENT, rounding=ROUND_HALF_UP)
