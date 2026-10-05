"""Тесты рендера: форматирование цен, длина сообщений ≤ 4096."""
from __future__ import annotations

from pathlib import Path

import pytest

from bot.catalog import load_catalog
from bot import render

BASE_DIR = Path(__file__).resolve().parent.parent
CATALOG_PATH = BASE_DIR / "data" / "catalog.json"


@pytest.fixture()
def catalog() -> dict:
    return load_catalog(CATALOG_PATH)


def test_format_number() -> None:
    assert render.format_number(5000) == "5\u00A0000"
    assert render.format_number(100000) == "100\u00A0000"
    assert render.format_number(2000000) == "2\u00A0000\u00A0000"


def test_format_price_from() -> None:
    price = {"kind": "from", "from": 5000, "unit": "rub"}
    result = render.format_price(price)
    assert "5\u00A0000" in result
    assert "₽" in result


def test_format_price_range() -> None:
    price = {"kind": "range", "from": 20000, "to": 35000, "unit": "rub"}
    result = render.format_price(price)
    assert "20\u00A0000" in result
    assert "35\u00A0000" in result


def test_format_price_free() -> None:
    price = {"kind": "free", "unit": "rub"}
    assert render.format_price(price) == "бесплатно"


def test_format_price_rub_per_hour() -> None:
    price = {"kind": "range", "from": 8000, "to": 15000, "unit": "rub_per_hour"}
    result = render.format_price(price)
    assert "₽/час" in result


def test_format_price_rub_per_month() -> None:
    price = {"kind": "from", "from": 50000, "unit": "rub_per_month"}
    result = render.format_price(price)
    assert "₽/мес." in result


def test_format_price_rub_per_session() -> None:
    price = {"kind": "regional", "unit": "rub_per_session", "nn": {"kind": "range", "from": 20000, "to": 25000}, "other": {"kind": "range", "from": 45000, "to": 60000}}
    nn = render.format_price_regional_nn(price)
    other = render.format_price_regional_other(price)
    assert "₽ за заседание" in nn
    assert "₽ за заседание" in other


def test_service_card_length(catalog: dict) -> None:
    for svc in catalog["services"]:
        section = next(s for s in catalog["sections"] if s["id"] == svc["section"])
        card = render.render_service_card(svc, section.get("note"))
        assert len(card) <= 4096, f"Услуга {svc['id']}: карточка длиннее 4096 символов"


def test_price_full_length(catalog: dict) -> None:
    messages = render.render_price_full(catalog)
    for i, msg in enumerate(messages):
        assert len(msg) <= 4096, f"Сообщение прайса {i}: длиннее 4096 символов"


def test_split_message_short() -> None:
    text = "Короткий текст"
    parts = render.split_message(text)
    assert parts == [text]


def test_split_message_long() -> None:
    text = "Абзац 1\n\nАбзац 2\n\n" + "Длинный абзац. " * 500
    parts = render.split_message(text)
    for part in parts:
        assert len(part) <= 4096


def test_split_message_preserves_content() -> None:
    text = "Абзац 1\n\nАбзац 2\n\n" + "Длинный абзац. " * 500
    parts = render.split_message(text)
    combined = "\n\n".join(parts)
    assert "Абзац 1" in combined
    assert "Абзац 2" in combined


def test_regional_card_shows_both_prices(catalog: dict) -> None:
    court_1 = next(s for s in catalog["services"] if s["id"] == "court_1")
    section = next(s for s in catalog["sections"] if s["id"] == "court_1".replace("court_1", "court"))
    card = render.render_service_card(court_1, section.get("note"))
    assert "Нижний Новгород" in card
    assert "Москва" in card


def test_turnkey_card_no_other_cities(catalog: dict) -> None:
    turnkey = next(s for s in catalog["services"] if s["id"] == "court_turnkey")
    section = next(s for s in catalog["sections"] if s["id"] == "court")
    card = render.render_service_card(turnkey, section.get("note"))
    assert "иные города" not in card


def test_subscription_card_shows_hours(catalog: dict) -> None:
    sub = next(s for s in catalog["services"] if s["id"] == "sub_start")
    section = next(s for s in catalog["sections"] if s["id"] == "subscription")
    card = render.render_service_card(sub, section.get("note"))
    assert "часов" in card.lower() or "часы" in card.lower()
