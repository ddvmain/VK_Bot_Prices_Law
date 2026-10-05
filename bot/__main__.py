"""Точка входа для запуска бота."""
import logging

from vkbottle import API

from .catalog import load_catalog
from .config import load_config
from .handlers import init
from .manager import ManagerNotifier


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    cfg = load_config()
    catalog = load_catalog()
    api = API(token=cfg.vk_group_token)
    notifier = ManagerNotifier(api=api, notify_peer_id=cfg.manager_notify_peer_id)
    bot = init(cfg=cfg, cat=catalog, ntfr=notifier)
    logging.info("Запуск бота для сообщества %s", cfg.group_id)
    bot.run_forever()


if __name__ == "__main__":
    main()
