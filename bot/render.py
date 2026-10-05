"""Форматирование цен, карточек, прайса и разбиение длинных текстов."""
from __future__ import annotations

from typing import Any

from . import texts

NBSP = "\u00A0"
MAX_MESSAGE_LENGTH = 4096


def format_number(value: int) -> str:
    """Форматирует число с неразрывным пробелом как разделителем разрядов."""
    s = str(value)
    parts: list[str] = []
    while len(s) > 3:
        parts.insert(0, s[-3:])
        s = s[:-3]
    parts.insert(0, s)
    return NBSP.join(parts)


def _unit_str(unit: str) -> str:
    return {
        "rub": "₽",
        "rub_per_hour": "₽/час",
        "rub_per_month": "₽/мес.",
        "rub_per_session": "₽ за заседание",
    }.get(unit, "₽")


def format_price(price: dict[str, Any]) -> str:
    """Форматирует цену услуги в строку для прайс-листа."""
    kind = price["kind"]
    unit = price.get("unit", "rub")

    if kind == "free":
        return "бесплатно"

    us = _unit_str(unit)

    if kind == "from":
        from_val = format_number(price["from"])
        return f"от {from_val}{NBSP}{us}"
    if kind == "range":
        from_val = format_number(price["from"])
        to_val = format_number(price["to"])
        return f"от {from_val} до {to_val}{NBSP}{us}"
    return ""


def _format_regional_sub(sub: dict[str, Any], unit: str) -> str:
    """Форматирует одну из региональных цен (nn или other)."""
    us = _unit_str(unit)
    if sub["kind"] == "from":
        from_val = format_number(sub["from"])
        return f"от {from_val}{NBSP}{us}"
    from_val = format_number(sub["from"])
    to_val = format_number(sub["to"])
    return f"от {from_val} до {to_val}{NBSP}{us}"


def format_price_regional_nn(price: dict[str, Any]) -> str:
    """Форматирует цену для Нижнего Новгорода (regional)."""
    return _format_regional_sub(price["nn"], price.get("unit", "rub"))


def format_price_regional_other(price: dict[str, Any]) -> str:
    """Форматирует цену для Москвы/СПб/иных городов (regional)."""
    return _format_regional_sub(price["other"], price.get("unit", "rub"))


def render_service_card(service: dict[str, Any], section_note: str | None = None) -> str:
    """Рендерит карточку услуги."""
    price = service["price"]
    price_note = service.get("price_note")
    price_note_str = f"Примечание: {price_note}\n" if price_note else ""

    section_id = service["section"]
    show_price_note_in_card = section_id in ("documents", "court", "packages")

    if price["kind"] == "regional":
        is_turnkey = service["id"] == "court_turnkey"
        if is_turnkey:
            body = texts.SERVICE_CARD_REGIONAL_TURNKEY_TEMPLATE.format(
                emoji=service["emoji"],
                title=service["title"],
                description=service["description"],
                nn_price=format_price_regional_nn(price),
                other_price=format_price_regional_other(price),
                price_note=price_note_str,
                disclaimer=texts.DISCLAIMER_FULL,
            )
        else:
            body = texts.SERVICE_CARD_REGIONAL_TEMPLATE.format(
                emoji=service["emoji"],
                title=service["title"],
                description=service["description"],
                nn_price=format_price_regional_nn(price),
                other_price=format_price_regional_other(price),
                price_note=price_note_str,
                disclaimer=texts.DISCLAIMER_FULL,
            )
    elif "hours" in service:
        body = texts.SERVICE_CARD_HOURS_TEMPLATE.format(
            emoji=service["emoji"],
            title=service["title"],
            description=service["description"],
            price=format_price(price),
            hours=service["hours"],
            price_note=price_note_str,
            disclaimer=texts.DISCLAIMER_FULL,
        )
    else:
        body = texts.SERVICE_CARD_TEMPLATE.format(
            emoji=service["emoji"],
            title=service["title"],
            description=service["description"],
            price=format_price(price),
            price_note=price_note_str,
            disclaimer=texts.DISCLAIMER_FULL,
        )

    if show_price_note_in_card and section_note:
        body = body + "\n\n" + section_note

    return body


def render_price_section(section: dict[str, Any], services: list[dict[str, Any]]) -> str:
    """Рендерит один раздел прайс-листа."""
    lines = [texts.PRICE_SECTION_HEADER.format(emoji=section["emoji"], title=section["title"])]
    for svc in services:
        lines.append(texts.PRICE_LINE.format(title=svc["title"], price=format_price(svc["price"])))
    if section.get("note"):
        lines.append("")
        lines.append(texts.PRICE_NOTE.format(note=section["note"]))
    return "\n".join(lines)


def render_price_full(catalog: dict[str, Any]) -> list[str]:
    """Рендерит весь прайс-лист, разбитый на сообщения по разделам.

    Возвращает список строк — каждая строка — отдельное сообщение.
    Последним сообщением идёт блок «Условия».
    """
    sections = catalog["sections"]
    services = catalog["services"]
    messages: list[str] = []

    for section in sections:
        section_services = [s for s in services if s["section"] == section["id"]]
        text = render_price_section(section, section_services)
        messages.append(text)

    messages.append(texts.PRICE_FOOTER)
    return messages


def split_message(text: str, max_length: int = MAX_MESSAGE_LENGTH) -> list[str]:
    """Разбивает длинный текст на части по границам абзацев.

    Каждая часть не превышает max_length символов.
    """
    if len(text) <= max_length:
        return [text]

    paragraphs = text.split("\n\n")
    parts: list[str] = []
    current = ""

    for para in paragraphs:
        candidate = current + "\n\n" + para if current else para
        if len(candidate) <= max_length:
            current = candidate
        else:
            if current:
                parts.append(current)
            if len(para) > max_length:
                # Разбиваем длинный абзац по строкам, затем по словам
                lines = para.split("\n")
                current = ""
                for line in lines:
                    candidate = current + "\n" + line if current else line
                    if len(candidate) <= max_length:
                        current = candidate
                    else:
                        if current:
                            parts.append(current)
                        # Если строка всё ещё длинная — режем по словам
                        if len(line) > max_length:
                            words = line.split(" ")
                            current = ""
                            for word in words:
                                candidate = current + " " + word if current else word
                                if len(candidate) <= max_length:
                                    current = candidate
                                else:
                                    if current:
                                        parts.append(current)
                                    current = word
                        else:
                            current = line
            else:
                current = para

    if current:
        parts.append(current)

    return parts
