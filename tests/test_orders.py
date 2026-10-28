from collections import Counter
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

import pytest

from generator.generation.catalog import build_catalog
from generator.generation.customers import build_customers
from generator.generation.orders import OrderConditions, OrderFactory
from generator.generation.rng import make_rng
from generator.models import DeliveryMethod, OrderItem, PaymentMethod

AT = datetime(2026, 10, 19, 12, 0, 0)
CATALOG = build_catalog()
CUSTOMERS = build_customers(500, CATALOG, make_rng(42, "customers"))
PRICES = {product.product_id: product.price for product in CATALOG.products}


def make_factory(seed: int = 42, first_order_id: int = 1, first_item_id: int = 1) -> OrderFactory:
    return OrderFactory(
        CATALOG, CUSTOMERS, seed=seed, first_order_id=first_order_id, first_item_id=first_item_id
    )


@pytest.fixture(scope="module")
def sample() -> list[tuple[OrderItem, ...]]:
    """Большая выборка заказов, создаётся один раз на весь модуль."""
    factory = make_factory()
    return [factory.build_order(AT) for _ in range(20_000)]


def test_items_of_one_order_share_order_level_fields() -> None:
    factory = make_factory()
    for _ in range(200):
        items = factory.build_order(AT)
        assert items
        first = items[0]
        for item in items:
            assert item.order_id == first.order_id
            assert item.customer_id == first.customer_id
            assert item.device_type == first.device_type
            assert item.payment_method == first.payment_method
            assert item.delivery_method == first.delivery_method
            assert item.promo_code == first.promo_code
            assert item.created_at == AT
        assert len({item.product_id for item in items}) == len(items)


def test_ids_are_sequential() -> None:
    factory = make_factory()
    orders = [factory.build_order(AT) for _ in range(100)]
    assert [order[0].order_id for order in orders] == list(range(1, 101))
    item_ids = [item.order_item_id for order in orders for item in order]
    assert item_ids == list(range(1, len(item_ids) + 1))


def test_start_ids_are_respected() -> None:
    items = make_factory(first_order_id=1000, first_item_id=5000).build_order(AT)
    assert items[0].order_id == 1000
    assert items[0].order_item_id == 5000


def test_same_seed_gives_same_orders() -> None:
    first, second = make_factory(42), make_factory(42)
    assert [first.build_order(AT) for _ in range(50)] == [second.build_order(AT) for _ in range(50)]


def test_different_seed_gives_different_orders() -> None:
    first, second = make_factory(1), make_factory(2)
    assert [first.build_order(AT) for _ in range(50)] != [second.build_order(AT) for _ in range(50)]


def test_cash_is_never_used_with_post(sample: list[tuple[OrderItem, ...]]) -> None:
    pairs = {(item.delivery_method, item.payment_method) for order in sample for item in order}
    assert (DeliveryMethod.POST, PaymentMethod.CASH) not in pairs
    assert (DeliveryMethod.COURIER, PaymentMethod.CASH) in pairs  # наличные бывают в целом


def test_quantity_limits_depend_on_price(sample: list[tuple[OrderItem, ...]]) -> None:
    for order in sample:
        for item in order:
            limit = 4 if PRICES[item.product_id] < Decimal("5000") else 2
            assert 1 <= item.quantity <= limit


def test_no_promo_means_catalog_price() -> None:
    factory = make_factory()
    conditions = OrderConditions(promo_probability=0.0)
    for _ in range(200):
        for item in factory.build_order(AT, conditions):
            assert not item.promo_code
            assert item.unit_price == PRICES[item.product_id]


def test_promo_applies_discount() -> None:
    factory = make_factory()
    conditions = OrderConditions(promo_probability=1.0, promo_discount=Decimal("0.10"))
    for _ in range(200):
        for item in factory.build_order(AT, conditions):
            expected = (PRICES[item.product_id] * Decimal("0.90")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            assert item.promo_code
            assert item.unit_price == expected


def test_default_promo_share(sample: list[tuple[OrderItem, ...]]) -> None:
    share = sum(1 for order in sample if order[0].promo_code) / len(sample)
    assert 0.07 < share < 0.09


def test_unavailable_products_are_never_sold() -> None:
    baseline = make_factory()
    counts = Counter(item.product_id for _ in range(3000) for item in baseline.build_order(AT))
    sold_out = counts.most_common(1)[0][0]  # самый ходовой товар

    factory = make_factory()
    conditions = OrderConditions(unavailable_product_ids=frozenset({sold_out}))
    for _ in range(3000):
        assert all(item.product_id != sold_out for item in factory.build_order(AT, conditions))


def test_all_products_unavailable_raises() -> None:
    everything = frozenset(product.product_id for product in CATALOG.products)
    with pytest.raises(ValueError):
        make_factory().build_order(AT, OrderConditions(unavailable_product_ids=everything))


def test_conditions_are_validated() -> None:
    with pytest.raises(ValueError):
        OrderConditions(promo_probability=1.5)
    with pytest.raises(ValueError):
        OrderConditions(promo_discount=Decimal("1.0"))


def test_cheap_products_sell_more(sample: list[tuple[OrderItem, ...]]) -> None:
    cheap = expensive = 0
    for order in sample:
        for item in order:
            price = PRICES[item.product_id]
            if price < 5000:
                cheap += 1
            elif price >= 40000:
                expensive += 1
    assert cheap > 2 * expensive


def test_customer_activity_is_skewed(sample: list[tuple[OrderItem, ...]]) -> None:
    per_customer = Counter(order[0].customer_id for order in sample)
    mean = len(sample) / len(CUSTOMERS)
    assert max(per_customer.values()) > 3 * mean
