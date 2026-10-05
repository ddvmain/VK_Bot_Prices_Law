"""Сборка клавиатур для бота.

Все клавиатуры соблюдают ограничения ВКонтакте:
- не более 10 строк;
- не более 5 кнопок в строке;
- подпись текстовой кнопки — не более 40 символов;
- payload — не более 255 байт.
"""
from __future__ import annotations

import json
from typing import Any

from vkbottle import Keyboard, Text, OpenLink

from . import texts

MAX_ROWS = 10
MAX_BUTTONS_PER_ROW = 5
MAX_LABEL_LENGTH = 40
MAX_PAYLOAD_BYTES = 255


def _make_payload(cmd: str, **kwargs: Any) -> str:
    """Создаёт JSON-payload для кнопки, проверяя длину."""
    data = {"cmd": cmd, **kwargs}
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    if len(payload.encode("utf-8")) > MAX_PAYLOAD_BYTES:
        raise ValueError(f"Payload превышает {MAX_PAYLOAD_BYTES} байт: {payload}")
    return payload


def _check_label(label: str) -> str:
    """Проверяет длину подписи кнопки."""
    if len(label) > MAX_LABEL_LENGTH:
        raise ValueError(f"Подпись кнопки превышает {MAX_LABEL_LENGTH} символов: {label!r}")
    return label


def _short_section_label(section: dict[str, Any]) -> str:
    """Возвращает сокращённую подпись для кнопки раздела (≤ 40 символов)."""
    emoji = section.get("emoji", "")
    title = section["title"]
    label = f"{emoji} {title}" if emoji else title
    if len(label) <= MAX_LABEL_LENGTH:
        return label
    # Сокращаем название, добавляя многоточие
    available = MAX_LABEL_LENGTH - len(emoji) - 2 if emoji else MAX_LABEL_LENGTH - 1
    shortened = title[:available].rstrip() + "…"
    return f"{emoji} {shortened}" if emoji else shortened


def main_menu_keyboard() -> str:
    """Главное меню с тремя кнопками."""
    keyboard = Keyboard(inline=False)
    keyboard.row()
    keyboard.add(Text(_check_label(texts.BTN_SERVICES), payload=_make_payload("menu_services")))
    keyboard.row()
    keyboard.add(Text(_check_label(texts.BTN_PRICE), payload=_make_payload("menu_price")))
    keyboard.row()
    keyboard.add(Text(_check_label(texts.BTN_MANAGER), payload=_make_payload("menu_manager")))
    return keyboard.get_json()


def sections_keyboard(sections: list[dict[str, Any]]) -> str:
    """Клавиатура со списком разделов каталога."""
    keyboard = Keyboard(inline=False)
    for section in sections:
        keyboard.row()
        label = _short_section_label(section)
        keyboard.add(Text(_check_label(label), payload=_make_payload("section", id=section["id"])))
    keyboard.row()
    keyboard.add(Text(_check_label(texts.BTN_HOME), payload=_make_payload("menu_home")))
    return keyboard.get_json()


def section_services_keyboard(services: list[dict[str, Any]]) -> str:
    """Клавиатура со списком услуг раздела."""
    keyboard = Keyboard(inline=False)
    for svc in services:
        keyboard.row()
        keyboard.add(Text(_check_label(svc["short_title"]), payload=_make_payload("service", id=svc["id"])))
    keyboard.row()
    keyboard.add(Text(_check_label(texts.BTN_BACK_TO_SECTIONS), payload=_make_payload("back_sections")))
    keyboard.row()
    keyboard.add(Text(_check_label(texts.BTN_HOME), payload=_make_payload("menu_home")))
    return keyboard.get_json()


def service_card_keyboard(service_id: str) -> str:
    """Клавиатура карточки услуги."""
    keyboard = Keyboard(inline=False)
    keyboard.row()
    keyboard.add(Text(_check_label(texts.BTN_ORDER_MANAGER), payload=_make_payload("order_manager", id=service_id)))
    keyboard.row()
    keyboard.add(Text(_check_label(texts.BTN_BACK_TO_SECTION), payload=_make_payload("back_section", id=service_id)))
    keyboard.row()
    keyboard.add(Text(_check_label(texts.BTN_HOME), payload=_make_payload("menu_home")))
    return keyboard.get_json()


def price_menu_keyboard(sections: list[dict[str, Any]]) -> str:
    """Клавиатура меню прайс-листа."""
    keyboard = Keyboard(inline=False)
    keyboard.row()
    keyboard.add(Text(_check_label(texts.BTN_FULL_PRICE), payload=_make_payload("price_full")))
    for section in sections:
        keyboard.row()
        label = _short_section_label(section)
        keyboard.add(Text(_check_label(label), payload=_make_payload("price_section", id=section["id"])))
    keyboard.row()
    keyboard.add(Text(_check_label(texts.BTN_HOME), payload=_make_payload("menu_home")))
    return keyboard.get_json()


def price_footer_keyboard() -> str:
    """Клавиатура в конце прайс-листа."""
    keyboard = Keyboard(inline=False)
    keyboard.row()
    keyboard.add(Text(_check_label(texts.BTN_MANAGER), payload=_make_payload("menu_manager")))
    keyboard.row()
    keyboard.add(Text(_check_label(texts.BTN_HOME), payload=_make_payload("menu_home")))
    return keyboard.get_json()


def manager_link_keyboard(manager_vk_id: int) -> str:
    """Inline-клавиатура с ссылкой на менеджера."""
    keyboard = Keyboard(inline=True)
    keyboard.row()
    keyboard.add(
        OpenLink(
            label=_check_label(texts.BTN_WRITE_MANAGER),
            link=f"https://vk.com/write{manager_vk_id}",
        )
    )
    return keyboard.get_json()
