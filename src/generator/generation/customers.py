"""Пул клиентов интернет-магазина."""

import random

from generator.generation.catalog import Catalog
from generator.models import Customer

_MALE_FIRST: tuple[tuple[str, str], ...] = (
    ("Иван", "ivan"),
    ("Алексей", "alexey"),
    ("Дмитрий", "dmitry"),
    ("Сергей", "sergey"),
    ("Андрей", "andrey"),
    ("Михаил", "mikhail"),
    ("Артём", "artem"),
    ("Никита", "nikita"),
    ("Максим", "maxim"),
    ("Егор", "egor"),
    ("Тимур", "timur"),
    ("Канье", "kanye"),
    ("Данил", "danil"),
)

_FEMALE_FIRST: tuple[tuple[str, str], ...] = (
    ("Анна", "anna"),
    ("Мария", "maria"),
    ("Елена", "elena"),
    ("Ольга", "olga"),
    ("Наталья", "natalia"),
    ("Екатерина", "ekaterina"),
    ("Дарья", "daria"),
    ("Анастасия", "anastasia"),
    ("Виктория", "viktoria"),
    ("Полина", "polina"),
)

_LAST: tuple[tuple[str, str, str], ...] = (
    ("Иванов", "Иванова", "ivanov"),
    ("Петров", "Петрова", "petrov"),
    ("Смирнов", "Смирнова", "smirnov"),
    ("Кузнецов", "Кузнецова", "kuznetsov"),
    ("Попов", "Попова", "popov"),
    ("Соколов", "Соколова", "sokolov"),
    ("Лебедев", "Лебедева", "lebedev"),
    ("Козлов", "Козлова", "kozlov"),
    ("Новиков", "Новикова", "novikov"),
    ("Мороз", "Мороз", "moroz"),
    ("Волков", "Волкова", "volkov"),
    ("Фёдоров", "Фёдорова", "fedorov"),
    ("Гаффоров", "Гаффорова", "gafforov"),
    ("Гончарук", "Гончарук", "goncharuk"),
    ("Кайданович", "Кайданович", "kaydanovich"),
    ("Вест", "Вест", "west"),
    ("Макан", "Макан", "macan"),
    ("Киркоров", "Киркорова", "kirkorov"),
    ("Шаман", "Шаман", "shaman"),
    ("Золочевский", "Золочевская", "zolo"),
)


def build_customers(count: int, catalog: Catalog, rng: random.Random) -> tuple[Customer, ...]:
    """Создаёт `count` клиентов; города выбираются пропорционально населению.

    Порядок обращений к rng фиксирован: сначала города, затем для каждого
    клиента — пол, имя, фамилия.
    """
    city_ids = [city.city_id for city in catalog.cities]
    chosen_cities = rng.choices(city_ids, weights=catalog.city_weights, k=count)

    customers: list[Customer] = []
    for offset, city_id in enumerate(chosen_cities):
        customer_id = offset + 1
        is_female = rng.random() < 0.5
        first_ru, first_lat = rng.choice(_FEMALE_FIRST if is_female else _MALE_FIRST)
        last_male, last_female, last_lat = rng.choice(_LAST)
        last_ru = last_female if is_female else last_male
        customers.append(
            Customer(
                customer_id=customer_id,
                full_name=f"{first_ru} {last_ru}",
                email=f"{first_lat}.{last_lat}{customer_id}@gmail.com",
                city_id=city_id,
            )
        )
    return tuple(customers)
