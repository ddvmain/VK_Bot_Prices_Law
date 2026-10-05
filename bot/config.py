"""Загрузка конфигурации из переменных окружения."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Config:
    vk_group_token: str
    group_id: int
    company_name: str
    manager_vk_id: int | None
    manager_notify_peer_id: int | None
    work_hours_text: str | None


def load_config() -> Config:
    load_dotenv(BASE_DIR / ".env")

    token = os.getenv("VK_GROUP_TOKEN", "").strip()
    if not token:
        raise RuntimeError("VK_GROUP_TOKEN не задан в .env")

    group_id_raw = os.getenv("VK_GROUP_ID", "").strip()
    if not group_id_raw:
        raise RuntimeError("VK_GROUP_ID не задан в .env")

    manager_vk_raw = os.getenv("MANAGER_VK_ID", "").strip()
    manager_notify_raw = os.getenv("MANAGER_NOTIFY_PEER_ID", "").strip()

    return Config(
        vk_group_token=token,
        group_id=int(group_id_raw),
        company_name=os.getenv("COMPANY_NAME", "БутиК «Ваш личный Советник»").strip(),
        manager_vk_id=int(manager_vk_raw) if manager_vk_raw else None,
        manager_notify_peer_id=int(manager_notify_raw) if manager_notify_raw else None,
        work_hours_text=os.getenv("WORK_HOURS_TEXT", "").strip() or None,
    )
