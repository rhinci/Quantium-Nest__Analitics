from generator.generation.catalog import build_catalog

CATALOG = build_catalog()


def _leaf_category_ids() -> set[int]:
    parents = {c.parent_category_id for c in CATALOG.categories}
    return {c.category_id for c in CATALOG.categories if c.category_id not in parents}


def test_ids_are_unique() -> None:
    for ids in (
        [c.city_id for c in CATALOG.cities],
        [b.brand_id for b in CATALOG.brands],
        [c.category_id for c in CATALOG.categories],
        [p.product_id for p in CATALOG.products],
    ):
        assert len(ids) == len(set(ids))


def test_products_reference_existing_brand_and_category() -> None:
    brand_ids = {b.brand_id for b in CATALOG.brands}
    category_ids = {c.category_id for c in CATALOG.categories}
    for product in CATALOG.products:
        assert product.brand_id in brand_ids
        assert product.category_id in category_ids


def test_products_belong_to_leaf_categories() -> None:
    leaves = _leaf_category_ids()
    assert all(p.category_id in leaves for p in CATALOG.products)


def test_category_tree_is_consistent() -> None:
    category_ids = {c.category_id for c in CATALOG.categories}
    roots = [c for c in CATALOG.categories if c.parent_category_id is None]
    assert roots
    for category in CATALOG.categories:
        if category.parent_category_id is not None:
            assert category.parent_category_id in category_ids


def test_every_leaf_category_has_products() -> None:
    used = {p.category_id for p in CATALOG.products}
    assert _leaf_category_ids() <= used


def test_prices_are_positive_with_two_decimals() -> None:
    for product in CATALOG.products:
        assert product.price > 0
        assert product.price.as_tuple().exponent == -2


def test_city_weights_match_cities() -> None:
    assert len(CATALOG.city_weights) == len(CATALOG.cities)
    assert all(weight > 0 for weight in CATALOG.city_weights)


def test_catalog_is_deterministic() -> None:
    assert build_catalog() == CATALOG
