from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📎Показать команды", callback_data="show_commands")]
    ])

def commands_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋список мероприятий", callback_data="list_events")],
        [InlineKeyboardButton(text="📋мои мероприятия", callback_data="personal_list")],
        [InlineKeyboardButton(text="️📝создать мероприятие", callback_data="create_event")]
    ])

def home_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠Домой", callback_data="home")]
    ])

def event_navigation_keyboard(event_index, events, is_subscribed, event_link):
    keyboard = [
        [InlineKeyboardButton(text="❌Отписаться" if is_subscribed else "✍️Записаться", callback_data=f"{'unsubscribe' if is_subscribed else 'subscribe'}_{events[event_index]['event_id']}")],
        [InlineKeyboardButton(text="🔗Ссылка", url=event_link)]
    ]
    navigation_buttons = []
    if event_index > 0:
        navigation_buttons.append(InlineKeyboardButton(text="Предыдущее", callback_data=f"prev_{event_index}"))
    if event_index < len(events) - 1:
        navigation_buttons.append(InlineKeyboardButton(text="Следующее", callback_data=f"next_{event_index}"))
    keyboard.append([InlineKeyboardButton(text="🏠Домой", callback_data="home")])
    if navigation_buttons:
        keyboard.append(navigation_buttons)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def personal_event_navigation_keyboard(event_index, events):
    keyboard = [
        [InlineKeyboardButton(text="✏️Редактировать", callback_data=f"edit_{events[event_index]['event_id']}")],
        [InlineKeyboardButton(text="🗑️Удалить", callback_data=f"delete_{events[event_index]['event_id']}")],
        [InlineKeyboardButton(text="🏠Домой", callback_data="home")]
    ]
    navigation_buttons = []
    if event_index > 0:
        navigation_buttons.append(InlineKeyboardButton(text="Предыдущее", callback_data=f"personal_prev_{event_index}"))
    if event_index < len(events) - 1:
        navigation_buttons.append(InlineKeyboardButton(text="Следующее", callback_data=f"personal_next_{event_index}"))
    if navigation_buttons:
        keyboard.append(navigation_buttons)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
