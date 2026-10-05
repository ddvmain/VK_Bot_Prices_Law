"""Все пользовательские тексты бота.

Заказчик может править этот файл без изменения логики.
"""

WELCOME_TEMPLATE = (
    "Здравствуйте! Это бот компании {company_name}. "
    "Здесь можно посмотреть услуги, цены и связаться с менеджером.\n\n"
    "Выберите раздел:"
)

BTN_SERVICES = "📋 Список услуг"
BTN_PRICE = "💰 Прайс-лист"
BTN_MANAGER = "👤 Связаться с менеджером"
BTN_HOME = "🏠 Главное меню"
BTN_BACK_TO_SECTIONS = "⬅️ К разделам"
BTN_BACK_TO_SECTION = "⬅️ Назад к разделу"
BTN_ORDER_MANAGER = "👤 Заказать / уточнить у менеджеру"
BTN_FULL_PRICE = "Весь прайс-лист"
BTN_WRITE_MANAGER = "Написать менеджеру"

SECTION_SERVICES_TEMPLATE = "{emoji} {title}\n\nУслуг в разделе: {count}"

SERVICE_CARD_TEMPLATE = (
    "{emoji} {title}\n\n"
    "{description}\n\n"
    "💰 Стоимость: {price}\n"
    "{price_note}\n\n"
    "{disclaimer}"
)

SERVICE_CARD_REGIONAL_TEMPLATE = (
    "{emoji} {title}\n\n"
    "{description}\n\n"
    "💰 Стоимость (за заседание):\n"
    "• Нижний Новгород — {nn_price}\n"
    "• Москва, СПб, иные города — {other_price}\n"
    "{price_note}\n\n"
    "{disclaimer}"
)

SERVICE_CARD_REGIONAL_TURNKEY_TEMPLATE = (
    "{emoji} {title}\n\n"
    "{description}\n\n"
    "💰 Стоимость:\n"
    "• Нижний Новгород — {nn_price}\n"
    "• Москва, СПб — {other_price}\n"
    "{price_note}\n\n"
    "{disclaimer}"
)

SERVICE_CARD_HOURS_TEMPLATE = (
    "{emoji} {title}\n\n"
    "{description}\n\n"
    "💰 Стоимость: {price}\n"
    "🗓 Включено часов в месяц: {hours}\n"
    "{price_note}\n\n"
    "{disclaimer}"
)

DISCLAIMER_FULL = "Не является публичной офертой. Точная стоимость фиксируется в договоре."
DISCLAIMER_SHORT = "Не является публичной офертой."

PRICE_SECTION_HEADER = "{emoji} {title}"
PRICE_LINE = "• {title} — {price}"
PRICE_NOTE = "Примечание: {note}"

PRICE_FOOTER = (
    "Условия:\n"
    "1. Цены указаны в рублях РФ, НДС не облагается. Государственные пошлины, "
    "нотариальные, почтовые расходы и стоимость экспертиз в цену не входят.\n"
    "2. Точная стоимость фиксируется в договоре после ознакомления с материалами. "
    "По имущественным спорам возможна модель «низкий фикс + гонорар успеха»: "
    "фиксированная часть по нижней границе прейскуранта + 10% от фактически "
    "взысканной суммы.\n"
    "3. Срочное выполнение (менее 5 рабочих дней) — коэффициент 1,5; работа "
    "в выходные и праздничные дни — коэффициент 2,0.\n"
    "4. Не является публичной офертой."
)

MANAGER_REPLY = (
    "Менеджер свяжется с вами в рабочее время (10:00–18:00). "
    "Чтобы не ждать, можно написать ему напрямую:"
)

MANAGER_NOTIFY_TEMPLATE = (
    "Новый запрос от клиента\n"
    "Профиль: https://vk.com/id{user_id}\n"
    "Время: {time}\n"
    "Услуга: {service_title}"
)

UNKNOWN_INPUT = "Не совсем понял. Выберите раздел в меню:"
ERROR_MESSAGE = "Произошла ошибка. Попробуйте ещё раз или выберите раздел в меню."
