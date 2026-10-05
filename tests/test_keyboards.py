"""Тесты клавиатур: ≤ 10 строк, ≤ 5 кнопок в строке, подпись ≤ 40 символов, payload ≤ 255 байт."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from bot.catalog import load_catalog
from bot import keyboards

BASE_DIR = Path(__file__).resolve().parent.parent
CATALOG_PATH = BASE_DIR / "data" / "catalog.json"

MAX_ROWS = 10
MAX_BUTTONS_PER_ROW = 5
MAX_LABEL_LENGTH = 40
MAX_PAYLOAD_BYTES = 255


@pytest.fixture()
def catalog() -> dict:
    return load_catalog(CATALOG_PATH)


def _validate_keyboard(keyboard_json: str | dict, name: str) -> None:
    """Проверяет клавиатуру на соответствие ограничениям ВК.

    Принимает JSON-строку (формат, который ожидает API ВКонтакте) или уже
    разобранный словарь.
    """
    if isinstance(keyboard_json, str):
        parsed = json.loads(keyboard_json)
        assert isinstance(parsed, dict), f"{name}: клавиатура не является объектом JSON"
        keyboard_json = parsed
    rows = keyboard_json.get("buttons", [])
    assert len(rows) <= MAX_ROWS, f"{name}: более {MAX_ROWS} строк"
    for i, row in enumerate(rows):
        assert len(row) <= MAX_BUTTONS_PER_ROW, f"{name}: строка {i} содержит более {MAX_BUTTONS_PER_ROW} кнопок"
        for btn in row:
            action = btn.get("action", {})
            label = action.get("label", "")
            assert len(label) <= MAX_LABEL_LENGTH, f"{name}: подпись {label!r} длиннее {MAX_LABEL_LENGTH} символов"
            payload = action.get("payload", "")
            if payload:
                payload_bytes = len(payload.encode("utf-8"))
                assert payload_bytes <= MAX_PAYLOAD_BYTES, (
                    f"{name}: payload {payload!r} превышает {MAX_PAYLOAD_BYTES} байт"
                )


def test_main_menu_keyboard() -> None:
    kb = keyboards.main_menu_keyboard()
    _validate_keyboard(kb, "main_menu")


def test_sections_keyboard(catalog: dict) -> None:
    sections = catalog["sections"]
    kb = keyboards.sections_keyboard(sections)
    _validate_keyboard(kb, "sections")


def test_section_services_keyboard(catalog: dict) -> None:
    for section in catalog["sections"]:
        services = [s for s in catalog["services"] if s["section"] == section["id"]]
        kb = keyboards.section_services_keyboard(services)
        _validate_keyboard(kb, f"section_services_{section['id']}")


def test_service_card_keyboard() -> None:
    kb = keyboards.service_card_keyboard("doc_claim")
    _validate_keyboard(kb, "service_card")


def test_price_menu_keyboard(catalog: dict) -> None:
    sections = catalog["sections"]
    kb = keyboards.price_menu_keyboard(sections)
    _validate_keyboard(kb, "price_menu")


def test_price_footer_keyboard() -> None:
    kb = keyboards.price_footer_keyboard()
    _validate_keyboard(kb, "price_footer")


def test_manager_link_keyboard() -> None:
    kb = keyboards.manager_link_keyboard(123456)
    _validate_keyboard(kb, "manager_link")


def test_all_keyboards_valid(catalog: dict) -> None:
    """Проверяет все клавиатуры разом."""
    sections = catalog["sections"]
    services = catalog["services"]

    _validate_keyboard(keyboards.main_menu_keyboard(), "main_menu")
    _validate_keyboard(keyboards.sections_keyboard(sections), "sections")
    _validate_keyboard(keyboards.price_menu_keyboard(sections), "price_menu")
    _validate_keyboard(keyboards.price_footer_keyboard(), "price_footer")
    _validate_keyboard(keyboards.manager_link_keyboard(123456), "manager_link")

    for section in sections:
        section_services = [s for s in services if s["section"] == section["id"]]
        _validate_keyboard(
            keyboards.section_services_keyboard(section_services),
            f"section_services_{section['id']}",
        )

    for svc in services:
        _validate_keyboard(
            keyboards.service_card_keyboard(svc["id"]),
            f"service_card_{svc['id']}",
        )


def test_keyboards_are_json_strings() -> None:
    """Клавиатуры должны возвращать JSON-строку (так ожидает API ВКонтакте)."""
    catalog = load_catalog(CATALOG_PATH)
    sections = catalog["sections"]
    services = catalog["services"]
    section_services = [s for s in services if s["section"] == sections[0]["id"]]

    for name, kb in [
        ("main_menu", keyboards.main_menu_keyboard()),
        ("sections", keyboards.sections_keyboard(sections)),
        ("section_services", keyboards.section_services_keyboard(section_services)),
        ("service_card", keyboards.service_card_keyboard(services[0]["id"])),
        ("price_menu", keyboards.price_menu_keyboard(sections)),
        ("price_footer", keyboards.price_footer_keyboard()),
        ("manager_link", keyboards.manager_link_keyboard(123456)),
    ]:
        assert isinstance(kb, str), f"{name}: ожидалась JSON-строка, получен {type(kb)}"
        parsed = json.loads(kb)
        assert isinstance(parsed, dict), f"{name}: строка не разбирается как JSON-объект"
