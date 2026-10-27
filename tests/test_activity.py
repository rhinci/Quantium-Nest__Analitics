from datetime import datetime, timedelta

import pytest

from generator.generation.activity import (
    activity_factor,
    hourly_factor,
    weekday_factor,
)

# 2026-10-19 — понедельник
MONDAY = datetime(2026, 10, 19)


def at(day_offset: int, hour: int, minute: int = 0) -> datetime:
    return MONDAY + timedelta(days=day_offset, hours=hour, minutes=minute)


def test_night_is_almost_zero() -> None:
    """Весь интервал 2:00–7:00 — активность почти нулевая."""
    start = at(0, 2)
    for minute in range(0, 5 * 60 + 1):
        assert hourly_factor(start + timedelta(minutes=minute)) < 0.1


def test_peaks_are_higher_than_afternoon_dip() -> None:
    dip = hourly_factor(at(0, 15))
    assert hourly_factor(at(0, 11)) > 1.5 * dip
    assert hourly_factor(at(0, 21)) > 1.5 * dip


def test_peak_windows_are_high() -> None:
    for hour in (10, 11, 12, 19, 20, 21, 22):
        assert hourly_factor(at(0, hour)) > 1.5


def test_daily_mean_is_one() -> None:
    mean = sum(hourly_factor(MONDAY + timedelta(minutes=minute)) for minute in range(24 * 60)) / (
        24 * 60
    )
    assert mean == pytest.approx(1.0, abs=1e-3)


def test_no_jump_at_hour_boundary() -> None:
    before = hourly_factor(at(0, 10, 59) + timedelta(seconds=59))
    after = hourly_factor(at(0, 11))
    assert abs(before - after) < 0.01


def test_no_jump_at_midnight() -> None:
    before = hourly_factor(at(0, 23, 59) + timedelta(seconds=59))
    after = hourly_factor(at(1, 0))
    assert abs(before - after) < 0.01


def test_weekdays_are_baseline() -> None:
    for day_offset in range(4):  # Пн–Чт
        assert weekday_factor(at(day_offset, 12)) == 1.0


def test_fri_sat_sun_are_higher() -> None:
    for day_offset in (4, 5, 6):  # Пт, Сб, Вс
        assert weekday_factor(at(day_offset, 12)) > 1.0


def test_activity_is_product_of_factors() -> None:
    saturday_evening = at(5, 21)
    expected = hourly_factor(saturday_evening) * weekday_factor(saturday_evening)
    assert activity_factor(saturday_evening) == pytest.approx(expected)
    assert activity_factor(saturday_evening) > activity_factor(at(0, 21))
