"""Обработчики команд и payload бота."""
from __future__ import annotations

import logging
from typing import Any

from vkbottle.bot import Bot, Message

from . import keyboards, render, texts
from .catalog import (
    get_section_by_id,
    get_sections,
    get_service_by_id,
    get_services_by_section,
)
from .config import Config
from .manager import ManagerNotifier

logger = logging.getLogger(__name__)

catalog: dict[str, Any] = {}
config: Config | None = None
notifier: ManagerNotifier | None = None
bot: Bot | None = None


def init(cfg: Config, cat: dict[str, Any], ntfr: ManagerNotifier) -> Bot:
    """Инициализация глобального состояния бота. Возвращает инстанс Bot."""
    global catalog, config, notifier, bot
    catalog = cat
    config = cfg
    notifier = ntfr
    bot = Bot(token=cfg.vk_group_token)
    _register_handlers(bot)
    return bot


TEXT_COMMANDS = {"начать", "меню", "/start"}


def _register_handlers(bot: Bot) -> None:
    """Регистрация единого обработчика сообщений на инстансе бота."""

    @bot.on.message()
    async def message_handler(message: Message) -> None:
        """Диспетчер: payload кнопок → текстовые команды → неизвестный ввод."""
        try:
            payload = message.get_payload_json()
            if isinstance(payload, dict) and payload.get("cmd"):
                await _dispatch_payload(message, payload)
                return

            text = (message.text or "").strip().lower()
            if text in TEXT_COMMANDS:
                await _send_main_menu(message)
                return

            logger.info("Неизвестный ввод от user_id=%s", message.from_id)
            await message.answer(texts.UNKNOWN_INPUT, keyboard=keyboards.main_menu_keyboard())
        except Exception as exc:
            logger.error(
                "Ошибка обработки сообщения от user_id=%s: %s", message.from_id, exc, exc_info=True
            )
            try:
                await message.answer(texts.ERROR_MESSAGE, keyboard=keyboards.main_menu_keyboard())
            except Exception:
                logger.error("Не удалось отправить сообщение об ошибке", exc_info=True)


async def _dispatch_payload(message: Message, payload: dict[str, Any]) -> None:
    """Диспетчеризация команд, пришедших в payload кнопки."""
    cmd = payload.get("cmd", "")
    logger.info("Команда от user_id=%s: %s", message.from_id, cmd)

    try:
        if cmd == "menu_services":
            await _show_sections(message)
        elif cmd == "menu_price":
            await _show_price_menu(message)
        elif cmd == "menu_manager":
            await _show_manager(message)
        elif cmd == "menu_home":
            await _send_main_menu(message)
        elif cmd == "section":
            await _show_section_services(message, payload.get("id", ""))
        elif cmd == "service":
            await _show_service_card(message, payload.get("id", ""))
        elif cmd == "back_sections":
            await _show_sections(message)
        elif cmd == "back_section":
            await _back_to_section(message, payload.get("id", ""))
        elif cmd == "price_full":
            await _show_full_price(message)
        elif cmd == "price_section":
            await _show_price_section(message, payload.get("id", ""))
        elif cmd == "order_manager":
            await _show_manager(message, service_id=payload.get("id"))
        else:
            logger.info("Неизвестная команда от user_id=%s: %s", message.from_id, cmd)
            await message.answer(texts.UNKNOWN_INPUT, keyboard=keyboards.main_menu_keyboard())
    except Exception as exc:
        logger.error("Ошибка обработки команды %s: %s", cmd, exc, exc_info=True)
        await message.answer(texts.ERROR_MESSAGE, keyboard=keyboards.main_menu_keyboard())


async def _send_main_menu(message: Message) -> None:
    """Отправляет главное меню."""
    assert config is not None
    welcome = texts.WELCOME_TEMPLATE.format(company_name=config.company_name)
    await message.answer(welcome, keyboard=keyboards.main_menu_keyboard())


async def _show_sections(message: Message) -> None:
    """Показывает список разделов каталога."""
    sections = get_sections(catalog)
    await message.answer(
        "Выберите раздел:",
        keyboard=keyboards.sections_keyboard(sections),
    )


async def _show_section_services(message: Message, section_id: str) -> None:
    """Показывает список услуг раздела."""
    section = get_section_by_id(catalog, section_id)
    if not section:
        await message.answer(texts.UNKNOWN_INPUT, keyboard=keyboards.main_menu_keyboard())
        return

    services = get_services_by_section(catalog, section_id)
    header = texts.SECTION_SERVICES_TEMPLATE.format(
        emoji=section["emoji"],
        title=section["title"],
        count=len(services),
    )
    await message.answer(header, keyboard=keyboards.section_services_keyboard(services))


async def _show_service_card(message: Message, service_id: str) -> None:
    """Показывает карточку услуги."""
    service = get_service_by_id(catalog, service_id)
    if not service:
        await message.answer(texts.UNKNOWN_INPUT, keyboard=keyboards.main_menu_keyboard())
        return

    section = get_section_by_id(catalog, service["section"])
    section_note = section.get("note") if section else None

    card_text = render.render_service_card(service, section_note)
    parts = render.split_message(card_text)

    # Первое сообщение с клавиатурой
    await message.answer(parts[0], keyboard=keyboards.service_card_keyboard(service_id))
    # Остальные части — без клавиатуры
    for part in parts[1:]:
        await message.answer(part)


async def _back_to_section(message: Message, service_id: str) -> None:
    """Возвращает к списку услуг раздела (из карточки)."""
    service = get_service_by_id(catalog, service_id)
    if not service:
        await _show_sections(message)
        return
    await _show_section_services(message, service["section"])


async def _show_price_menu(message: Message) -> None:
    """Показывает меню прайс-листа."""
    sections = get_sections(catalog)
    await message.answer("Прайс-лист:", keyboard=keyboards.price_menu_keyboard(sections))


async def _show_full_price(message: Message) -> None:
    """Показывает весь прайс-лист по разделам."""
    messages = render.render_price_full(catalog)
    for i, text in enumerate(messages):
        parts = render.split_message(text)
        for j, part in enumerate(parts):
            is_last = i == len(messages) - 1 and j == len(parts) - 1
            if is_last:
                await message.answer(part, keyboard=keyboards.price_footer_keyboard())
            else:
                await message.answer(part)


async def _show_price_section(message: Message, section_id: str) -> None:
    """Показывает прайс-лист для одного раздела."""
    section = get_section_by_id(catalog, section_id)
    if not section:
        await message.answer(texts.UNKNOWN_INPUT, keyboard=keyboards.main_menu_keyboard())
        return

    services = get_services_by_section(catalog, section_id)
    text = render.render_price_section(section, services)
    parts = render.split_message(text)

    for i, part in enumerate(parts):
        is_last = i == len(parts) - 1
        if is_last:
            await message.answer(part, keyboard=keyboards.price_footer_keyboard())
        else:
            await message.answer(part)


async def _show_manager(message: Message, service_id: str | None = None) -> None:
    """Показывает контакт менеджера и отправляет уведомление."""
    assert config is not None

    service_title = None
    if service_id:
        service = get_service_by_id(catalog, service_id)
        if service:
            service_title = service["title"]

    if config.manager_vk_id:
        await message.answer(
            texts.MANAGER_REPLY,
            keyboard=keyboards.manager_link_keyboard(config.manager_vk_id),
        )
    else:
        await message.answer(texts.MANAGER_REPLY)

    if notifier:
        await notifier.notify(message.from_id, service_title)
