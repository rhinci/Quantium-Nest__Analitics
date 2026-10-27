"""Справочники магазина Quantium Nest: города, бренды, категории, товары.

Данные заданы вручную, чтобы аналитика получалась осмысленной
(«Apple iPhone 15», а не «product_37»). Случайность в генераторе появляется
позже — при выборе, какой именно товар купят.
"""

from dataclasses import dataclass
from decimal import Decimal

from generator.models import Brand, Category, City, Product

# (название города, население в млн — используется как вес при выборе города клиента)
_CITIES: tuple[tuple[str, float], ...] = (
    ("Москва", 13.1),
    ("Санкт-Петербург", 5.6),
    ("Новосибирск", 1.6),
    ("Екатеринбург", 1.5),
    ("Казань", 1.3),
    ("Нижний Новгород", 1.2),
    ("Красноярск", 1.2),
    ("Самара", 1.2),
    ("Краснодар", 1.1),
    ("Владивосток", 0.6),
    ("Хабаровск", 0.6),
    ("Иркутск", 0.6),
)

# (название бренда, страна происхождения)
_BRANDS: tuple[tuple[str, str], ...] = (
    ("Apple", "USA"),
    ("Samsung", "South Korea"),
    ("Xiaomi", "China"),
    ("Huawei", "China"),
    ("Lenovo", "China"),
    ("ASUS", "Taiwan"),
    ("HP", "USA"),
    ("Dell", "USA"),
    ("LG", "South Korea"),
    ("Sony", "Japan"),
    ("JBL", "USA"),
    ("Anker", "China"),
    ("Logitech", "Switzerland"),
)

# (category_id, название, parent_category_id). Корни: parent = None.
_CATEGORIES: tuple[tuple[int, str, int | None], ...] = (
    (1, "Смартфоны и гаджеты", None),
    (2, "Компьютеры", None),
    (3, "ТВ и аудио", None),
    (4, "Аксессуары", None),
    (5, "Смартфоны", 1),
    (6, "Умные часы", 1),
    (7, "Ноутбуки", 2),
    (8, "Планшеты", 2),
    (9, "Мониторы", 2),
    (10, "Телевизоры", 3),
    (11, "Наушники", 3),
    (12, "Колонки", 3),
    (13, "Зарядные устройства", 4),
    (14, "Периферия", 4),
)

# (category_id, бренд, модель, цена в рублях строкой — чтобы Decimal был точным)
_PRODUCTS: tuple[tuple[int, str, str, str], ...] = (
    # Смартфоны
    (5, "Apple", "iPhone 15 128GB", "79990.00"),
    (5, "Samsung", "Galaxy S24 256GB", "74990.00"),
    (5, "Xiaomi", "Redmi Note 13 128GB", "17990.00"),
    (5, "Xiaomi", "14T 256GB", "44990.00"),
    (5, "Huawei", "nova 12 256GB", "29990.00"),
    # Умные часы
    (6, "Apple", "Watch SE 40mm", "24990.00"),
    (6, "Samsung", "Galaxy Watch 6", "21990.00"),
    (6, "Xiaomi", "Smart Band 8", "3490.00"),
    (6, "Huawei", "Watch Fit 3", "9990.00"),
    # Ноутбуки
    (7, "Apple", "MacBook Air 13 M2", "99990.00"),
    (7, "Lenovo", "IdeaPad Slim 3 15", "42990.00"),
    (7, "ASUS", "VivoBook 15", "46990.00"),
    (7, "HP", "Pavilion 15", "54990.00"),
    (7, "Dell", "Inspiron 15", "51990.00"),
    (7, "Huawei", "MateBook D16", "62990.00"),
    # Планшеты
    (8, "Apple", "iPad 10.9 64GB", "37990.00"),
    (8, "Samsung", "Galaxy Tab A9+", "17990.00"),
    (8, "Xiaomi", "Pad 6", "28990.00"),
    (8, "Lenovo", "Tab M10", "11990.00"),
    # Мониторы
    (9, "LG", "UltraGear 27", "22990.00"),
    (9, "Samsung", "Odyssey G5 27", "24990.00"),
    (9, "ASUS", "ProArt 27", "33990.00"),
    (9, "Dell", "S2722QC 27", "29990.00"),
    # Телевизоры
    (10, "Samsung", "Crystal UHD 50", "39990.00"),
    (10, "LG", "OLED55 C3", "119990.00"),
    (10, "Sony", "Bravia 55 X75", "64990.00"),
    (10, "Xiaomi", "TV A 43", "24990.00"),
    # Наушники
    (11, "Apple", "AirPods Pro 2", "21990.00"),
    (11, "Sony", "WH-1000XM5", "27990.00"),
    (11, "JBL", "Tune 520BT", "4490.00"),
    (11, "Samsung", "Galaxy Buds2", "8990.00"),
    (11, "Xiaomi", "Redmi Buds 5", "2990.00"),
    # Колонки
    (12, "JBL", "Flip 6", "8990.00"),
    (12, "JBL", "Charge 5", "12990.00"),
    (12, "Sony", "SRS-XB13", "4990.00"),
    (12, "Xiaomi", "Sound Pocket", "2490.00"),
    # Зарядные устройства
    (13, "Anker", "PowerCore 10000", "2990.00"),
    (13, "Anker", "Nano 65W", "3490.00"),
    (13, "Samsung", "EP-T2510 25W", "1490.00"),
    (13, "Xiaomi", "Power Bank 20000", "3290.00"),
    # Периферия
    (14, "Logitech", "MX Master 3S", "9990.00"),
    (14, "Logitech", "K380", "3990.00"),
    (14, "Logitech", "G102", "1990.00"),
)


@dataclass(frozen=True, slots=True)
class Catalog:
    """Все справочники магазина одним объектом."""

    cities: tuple[City, ...]
    city_weights: tuple[float, ...]  # в том же порядке, что и cities
    brands: tuple[Brand, ...]
    categories: tuple[Category, ...]
    products: tuple[Product, ...]


def build_catalog() -> Catalog:
    """Собирает справочники из таблиц выше. Результат всегда одинаковый."""
    cities = tuple(
        City(city_id=index, city_name=name) for index, (name, _) in enumerate(_CITIES, start=1)
    )
    city_weights = tuple(population for _, population in _CITIES)

    brands = tuple(
        Brand(brand_id=index, brand_name=name, country_of_origin=country)
        for index, (name, country) in enumerate(_BRANDS, start=1)
    )
    brand_ids = {brand.brand_name: brand.brand_id for brand in brands}

    categories = tuple(
        Category(category_id=category_id, category_name=name, parent_category_id=parent)
        for category_id, name, parent in _CATEGORIES
    )

    products = tuple(
        Product(
            product_id=index,
            product_name=f"{brand} {model}",
            price=Decimal(price),
            category_id=category_id,
            brand_id=brand_ids[brand],
        )
        for index, (category_id, brand, model, price) in enumerate(_PRODUCTS, start=1)
    )

    return Catalog(
        cities=cities,
        city_weights=city_weights,
        brands=brands,
        categories=categories,
        products=products,
    )
