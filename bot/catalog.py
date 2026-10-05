"""Загрузка и валидация каталога услуг."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
CATALOG_PATH = BASE_DIR / "data" / "catalog.json"

REQUIRED_SERVICE_FIELDS = {"id", "section", "short_title", "title", "emoji", "description", "price"}
VALID_PRICE_KINDS = {"range", "from", "free", "regional"}
VALID_UNITS = {"rub", "rub_per_hour", "rub_per_month", "rub_per_session"}


class CatalogError(Exception):
    pass


def load_catalog(path: Path | None = None) -> dict[str, Any]:
    """Загружает и валидирует catalog.json.

    Возвращает словарь с ключами 'sections' и 'services'.
    При ошибке валидации бросает CatalogError.
    """
    catalog_path = path or CATALOG_PATH
    raw = json.loads(catalog_path.read_text(encoding="utf-8"))

    sections = raw.get("sections", [])
    services = raw.get("services", [])

    section_ids = [s["id"] for s in sections]
    if len(section_ids) != len(set(section_ids)):
        raise CatalogError("Дублирующиеся id разделов")

    service_ids = [s["id"] for s in services]
    if len(service_ids) != len(set(service_ids)):
        raise CatalogError("Дублирующиеся id услуг")

    for svc in services:
        missing = REQUIRED_SERVICE_FIELDS - svc.keys()
        if missing:
            raise CatalogError(f"Услуга {svc.get('id', '?')}: отсутствуют поля {missing}")
        if svc["section"] not in section_ids:
            raise CatalogError(f"Услуга {svc['id']}: неизвестный раздел {svc['section']}")
        _validate_price(svc["id"], svc["price"])

    logger.info("Каталог загружен: %d разделов, %d услуг", len(sections), len(services))
    return raw


def _validate_price(service_id: str, price: dict[str, Any]) -> None:
    kind = price.get("kind")
    if kind not in VALID_PRICE_KINDS:
        raise CatalogError(f"Услуга {service_id}: неизвестный kind {kind!r}")
    unit = price.get("unit")
    if unit not in VALID_UNITS:
        raise CatalogError(f"Услуга {service_id}: неизвестный unit {unit!r}")
    if kind == "range":
        if "from" not in price or "to" not in price:
            raise CatalogError(f"Услуга {service_id}: range требует from и to")
    elif kind == "from":
        if "from" not in price:
            raise CatalogError(f"Услуга {service_id}: from требует поле from")
    elif kind == "regional":
        for key in ("nn", "other"):
            if key not in price:
                raise CatalogError(f"Услуга {service_id}: regional требует {key}")
            sub = price[key]
            if sub.get("kind") not in ("range", "from"):
                raise CatalogError(f"Услуга {service_id}: невалидный подтип regional.{key}")


def get_sections(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    return catalog["sections"]


def get_services(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    return catalog["services"]


def get_services_by_section(catalog: dict[str, Any], section_id: str) -> list[dict[str, Any]]:
    return [s for s in catalog["services"] if s["section"] == section_id]


def get_service_by_id(catalog: dict[str, Any], service_id: str) -> dict[str, Any] | None:
    for s in catalog["services"]:
        if s["id"] == service_id:
            return s
    return None


def get_section_by_id(catalog: dict[str, Any], section_id: str) -> dict[str, Any] | None:
    for s in catalog["sections"]:
        if s["id"] == section_id:
            return s
    return None
