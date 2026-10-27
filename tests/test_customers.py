from generator.generation.catalog import build_catalog
from generator.generation.customers import build_customers
from generator.generation.rng import make_rng
from generator.models import Customer

CATALOG = build_catalog()


def _build(seed: int, count: int = 100) -> tuple[Customer, ...]:
    return build_customers(count, CATALOG, make_rng(seed, "customers"))


def test_builds_requested_count_with_sequential_ids() -> None:
    customers = _build(42, count=50)
    assert [c.customer_id for c in customers] == list(range(1, 51))


def test_same_seed_gives_same_customers() -> None:
    assert _build(42) == _build(42)


def test_different_seed_gives_different_customers() -> None:
    assert _build(1) != _build(2)


def test_emails_are_unique_and_use_reserved_domain() -> None:
    customers = _build(42, count=500)
    emails = [c.email for c in customers]
    assert len(emails) == len(set(emails))
    assert all(email.endswith("@gmail.com") for email in emails)


def test_cities_are_valid() -> None:
    valid_city_ids = {city.city_id for city in CATALOG.cities}
    assert all(c.city_id in valid_city_ids for c in _build(42, count=500))


def test_big_cities_have_more_customers() -> None:
    moscow_id = next(c.city_id for c in CATALOG.cities if c.city_name == "Москва")
    customers = _build(42, count=20_000)
    share = sum(1 for c in customers if c.city_id == moscow_id) / len(customers)
    # Вес Москвы 13.1 из 29.6 суммарно, то есть около 44%
    assert 0.40 < share < 0.48


def test_full_name_has_first_and_last_name() -> None:
    assert all(len(c.full_name.split()) == 2 for c in _build(42))
