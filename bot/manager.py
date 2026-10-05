"""Логика связи с менеджером: уведомления и антиспам."""
from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Any

from vkbottle import API

from . import texts

logger = logging.getLogger(__name__)

NOTIFY_COOLDOWN_SECONDS = 600  # 10 минут


class ManagerNotifier:
    """Отправляет уведомления менеджеру с антиспамом по пользователям."""

    def __init__(self, api: API, notify_peer_id: int | None) -> None:
        self._api = api
        self._notify_peer_id = notify_peer_id
        self._last_notify: dict[int, float] = {}

    def can_notify(self, user_id: int) -> bool:
        """Проверяет, прошло ли 10 минут с последнего уведомления."""
        last = self._last_notify.get(user_id)
        if last is None:
            return True
        return (time.time() - last) >= NOTIFY_COOLDOWN_SECONDS

    async def notify(
        self,
        user_id: int,
        service_title: str | None = None,
    ) -> None:
        """Отправляет уведомление менеджеру.

        Если отправка не удалась — залогировать ошибку, клиенту не сообщать.
        """
        if not self._notify_peer_id:
            return
        if not self.can_notify(user_id):
            logger.info("Антиспам: пропуск уведомления для user_id=%s", user_id)
            return

        now = datetime.now().strftime("%d.%m.%Y %H:%M")
        service = service_title or "не указана"
        message = texts.MANAGER_NOTIFY_TEMPLATE.format(
            user_id=user_id,
            time=now,
            service_title=service,
        )

        try:
            await self._api.messages.send(
                peer_id=self._notify_peer_id,
                message=message,
                random_id=0,
            )
            self._last_notify[user_id] = time.time()
            logger.info("Уведомление менеджеру отправлено для user_id=%s", user_id)
        except Exception as exc:
            logger.error("Не удалось отправить уведомление менеджеру: %s", exc)
