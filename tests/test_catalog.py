"""Тесты каталога: 6 разделов, 34 услуги, обязательные поля, уникальные id."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from bot.catalog import CatalogError, load_catalog

BASE_DIR = Path(__file__).resolve().parent.parent
CATALOG_PATH = BASE_DIR / "data" / "catalog.json"


@pytest.fixture()
def catalog() -> dict:
    return load_catalog(CATALOG_PATH)


def test_catalog_loads_without_error(catalog: dict) -> None:
    assert "sections" in catalog
    assert "services" in catalog


def test_six_sections(catalog: dict) -> None:
    assert len(catalog["sections"]) == 6


def test_thirty_four_services(catalog: dict) -> None:
    assert len(catalog["services"]) == 34


def test_unique_section_ids(catalog: dict) -> None:
    ids = [s["id"] for s in catalog["sections"]]
    assert len(ids) == len(set(ids))


def test_unique_service_ids(catalog: dict) -> None:
    ids = [s["id"] for s in catalog["services"]]
    assert len(ids) == len(set(ids))


def test_all_services_have_required_fields(catalog: dict) -> None:
    required = {"id", "section", "short_title", "title", "emoji", "description", "price"}
    for svc in catalog["services"]:
        missing = required - svc.keys()
        assert not missing, f"Услуга {svc.get('id')}: отсутствуют поля {missing}"


def test_all_services_reference_valid_sections(catalog: dict) -> None:
    section_ids = {s["id"] for s in catalog["sections"]}
    for svc in catalog["services"]:
        assert svc["section"] in section_ids, f"Услуга {svc['id']}: неизвестный раздел"


def test_price_kinds_are_valid(catalog: dict) -> None:
    valid_kinds = {"range", "from", "free", "regional"}
    for svc in catalog["services"]:
        assert svc["price"]["kind"] in valid_kinds, f"Услуга {svc['id']}: невалидный kind"


def test_price_units_are_valid(catalog: dict) -> None:
    valid_units = {"rub", "rub_per_hour", "rub_per_month", "rub_per_session"}
    for svc in catalog["services"]:
        assert svc["price"].get("unit") in valid_units, f"Услуга {svc['id']}: невалидный unit"


def test_short_title_length(catalog: dict) -> None:
    for svc in catalog["services"]:
        assert len(svc["short_title"]) <= 40, (
            f"Услуга {svc['id']}: short_title длиннее 40 символов"
        )


def test_regional_prices_have_nn_and_other(catalog: dict) -> None:
    for svc in catalog["services"]:
        if svc["price"]["kind"] == "regional":
            assert "nn" in svc["price"], f"Услуга {svc['id']}: regional без nn"
            assert "other" in svc["price"], f"Услуга {svc['id']}: regional без other"


def test_subscription_services_have_hours(catalog: dict) -> None:
    for svc in catalog["services"]:
        if svc["section"] == "subscription":
            assert "hours" in svc, f"Услуга {svc['id']}: тариф без поля hours"


def test_court_turnkey_has_no_other_cities(catalog: dict) -> None:
    """Услуга court_turnkey не должна содержать 'иные города' в описании."""
    turnkey = next(s for s in catalog["services"] if s["id"] == "court_turnkey")
    assert "иные города" not in turnkey["title"].lower()
