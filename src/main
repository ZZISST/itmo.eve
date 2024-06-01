import asyncio
import logging
import os
import re
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from configparser import ConfigParser
from datetime import datetime

# Импортируем функции клавиатур
from keyboard import main_menu_keyboard, commands_keyboard, home_button, event_navigation_keyboard, personal_event_navigation_keyboard

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv('TOKEN')
DATABASE_URL = f"postgresql://{os.environ.get('DATABASE_USER')}:{os.environ.get('DATABASE_PASSWORD')}@" \
               f"{os.environ.get('DATABASE_HOST')}:{os.environ.get('DATABASE_PORT')}/{os.environ.get('DATABASE_NAME')}"
logger.info("DATABASE-URL" + str(DATABASE_URL) + "   " + str(TOKEN))

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()

# Функции для работы с базой данных
def load_config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)

    config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} not found in the {filename} file')

    return config

def create_db_connection():
    try:
        config = load_config()
        connection = psycopg2.connect(**config, cursor_factory=RealDictCursor)
        logger.info("Подключение к базе данных установлено")
        return connection
    except psycopg2.Error as e:
        logger.error(f"Ошибка при подключении к базе данных: {e}")
        return None

conn = None

async def on_startup():
    global conn
    conn = create_db_connection()

async def on_shutdown():
    if conn:
        conn.close()
        logger.info("Подключение к базе данных закрыто")

# Удаление сообщения безопасно
async def delete_message_safe(chat_id, message_id):
    try:
        await bot.delete_message(chat_id, message_id)
    except Exception as e:
        logger.error(f"Ошибка при удалении сообщения: {e}")

# Команда /start
@router.message(CommandStart())
async def start_command(message: types.Message):
    user_id = message.from_user.id
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (user_id) VALUES (%s) ON CONFLICT (user_id) DO NOTHING",
            (user_id,)
        )
        conn.commit()
        cursor.close()
        logger.info(f"User {user_id} inserted into database.")
    except psycopg2.Error as e:
        logger.error(f"Ошибка при вставке user_id в базу данных: {e}")
        conn.rollback()

    keyboard = main_menu_keyboard()
    await message.answer("Привет! Я бот для создания и управления мероприятиями.", reply_markup=keyboard)

# Показать команды
@router.callback_query(lambda c: c.data == 'show_commands')
async def show_commands(callback_query: types.CallbackQuery):
    await delete_message_safe(callback_query.message.chat.id, callback_query.message.message_id)
    keyboard = commands_keyboard()
    await callback_query.message.answer("Вот список доступных команд:", reply_markup=keyboard)

# Определение состояний
class EventCreation(StatesGroup):
    waiting_for_event_name = State()
    waiting_for_event_description = State()
    waiting_for_event_date = State()
    waiting_for_event_location = State()
    waiting_for_event_links = State()

class EventEdit(StatesGroup):
    waiting_for_event_name = State()
    waiting_for_event_description = State()
    waiting_for_event_date = State()
    waiting_for_event_location = State()
    waiting_for_event_links = State()

# Функция для начала процесса создания мероприятия
async def start_event_creation(message_or_callback, state: FSMContext):
    keyboard = home_button()
    if isinstance(message_or_callback, types.Message):
        await message_or_callback.answer("Введите название мероприятия:", reply_markup=keyboard)
    else:
        await delete_message_safe(message_or_callback.message.chat.id, message_or_callback.message.message_id)
        await message_or_callback.message.answer("Введите название мероприятия:", reply_markup=keyboard)
    await state.set_state(EventCreation.waiting_for_event_name)

# Команда /create
@router.message(Command("create"))
async def create_event_command(message: types.Message, state: FSMContext):
    await start_event_creation(message, state)

# Инлайн-кнопка создать мероприятие
@router.callback_query(lambda c: c.data == 'create_event')
async def create_event_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await start_event_creation(callback_query, state)

@router.message(EventCreation.waiting_for_event_name)
async def handle_event_name(message: types.Message, state: FSMContext):
    await state.update_data(event_name=message.text)
    keyboard = home_button()
    await message.answer("Введите описание мероприятия:", reply_markup=keyboard)
    await state.set_state(EventCreation.waiting_for_event_description)

@router.message(EventCreation.waiting_for_event_description)
async def handle_event_description(message: types.Message, state: FSMContext):
    await state.update_data(event_description=message.text)
    keyboard = home_button()
    await message.answer("Введите дату мероприятия (дд.мм.гггг чч:мм):", reply_markup=keyboard)
    await state.set_state(EventCreation.waiting_for_event_date)

def validate_date(date_text):
    try:
        datetime.strptime(date_text, "%d.%m.%Y %H:%M")
        return True
    except ValueError:
        return False

def convert_date_format(date_text):
    return datetime.strptime(date_text, "%d.%m.%Y %H:%M").strftime("%Y-%m-%d %H:%M:%S")

@router.message(EventCreation.waiting_for_event_date)
async def handle_event_date(message: types.Message, state: FSMContext):
    date_text = message.text
    if validate_date(date_text):
        formatted_date = convert_date_format(date_text)
        await state.update_data(event_date=formatted_date)
        keyboard = home_button()
        await message.answer("Введите место проведения мероприятия:", reply_markup=keyboard)
        await state.set_state(EventCreation.waiting_for_event_location)
    else:
        await message.answer("Неправильный формат даты. Пожалуйста, введите дату в формате дд.мм.гггг чч:мм:")

@router.message(EventCreation.waiting_for_event_location)
async def handle_event_location(message: types.Message, state: FSMContext):
    await state.update_data(event_location=message.text)
    keyboard = home_button()
    await message.answer("Введите ссылку на мероприятие:", reply_markup=keyboard)
    await state.set_state(EventCreation.waiting_for_event_links)

def validate_url(url):
    url_regex = re.compile(r'^(https?://)?(www\.)?([a-zA-Z0-9]+(\.[a-zA-Z0-9]+)+.*)$')
    return re.match(url_regex, url) is not None

@router.message(EventCreation.waiting_for_event_links)
async def handle_event_links(message: types.Message, state: FSMContext):
    url = message.text
    if validate_url(url):
        user_data = await state.get_data()
        event_name = user_data['event_name']
        event_description = user_data['event_description']
        event_date = user_data['event_date']
        event_location = user_data['event_location']
        event_links = url
        user_id = message.from_user.id

        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO events (user_id, title, description, event_date, location, useful_links) VALUES (%s, %s, %s, %s, %s, %s)",
                (user_id, event_name, event_description, event_date, event_location, event_links)
            )
            conn.commit()
            cursor.close()
            await message.answer('Мероприятие создано!')
            # Перенаправление на старт после создания мероприятия
            await start_command(message)
        except Exception as e:
            logger.error(f"Ошибка при создании мероприятия: {e}")
            conn.rollback()
            await message.answer("Произошла ошибка при создании мероприятия. Убедитесь, что формат данных правильный.")

        await state.clear()
    else:
        await message.answer("Неправильный формат ссылки. Пожалуйста, введите ссылку на мероприятие (начинающуюся с http:// или https://):")

# Функция для отображения событий
async def show_events(user_id, message_or_callback):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events")
        events = cursor.fetchall()

        if events:
            event_index = 0
            event = events[event_index]
            cursor.execute("SELECT * FROM participants WHERE event_id = %s AND user_id = %s", (event['event_id'], user_id))
            participant = cursor.fetchone()

            is_subscribed = participant is not None
            keyboard = event_navigation_keyboard(event_index, events, is_subscribed, event['useful_links'])

            response_text = (
                f"📝 Название: {event['title']}\n"
                f"📖 Описание: {event['description']}\n"
                f"📅 Дата: {event['event_date']}\n"
                f"📍 Место: {event['location']}\n"
            )

            if isinstance(message_or_callback, types.Message):
                await message_or_callback.answer(response_text, reply_markup=keyboard)
            else:
                await delete_message_safe(message_or_callback.message.chat.id, message_or_callback.message.message_id)
                await message_or_callback.message.answer(response_text, reply_markup=keyboard)
        else:
            response_text = "Нет доступных мероприятий."
            if isinstance(message_or_callback, types.Message):
                await message_or_callback.answer(response_text)
            else:
                await message_or_callback.message.answer(response_text)
        cursor.close()
    except psycopg2.Error as e:
        logger.error(f"Ошибка при получении списка мероприятий: {e}")
        error_text = "Произошла ошибка при получении списка мероприятий."
        if isinstance(message_or_callback, types.Message):
            await message_or_callback.answer(error_text)
        else:
            await message_or_callback.message.answer(error_text)

# Функция для отображения личных событий
async def show_personal_events(user_id, message_or_callback):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events WHERE user_id = %s", (user_id,))
        events = cursor.fetchall()

        if events:
            event_index = 0
            event = events[event_index]

            keyboard = personal_event_navigation_keyboard(event_index, events)

            response_text = (
                f"📝 Название: {event['title']}\n"
                f"📖 Описание: {event['description']}\n"
                f"📅 Дата: {event['event_date']}\n"
                f"📍 Место: {event['location']}\n"
            )

            if isinstance(message_or_callback, types.Message):
                await message_or_callback.answer(response_text, reply_markup=keyboard)
            else:
                await delete_message_safe(message_or_callback.message.chat.id, message_or_callback.message.message_id)
                await message_or_callback.message.answer(response_text, reply_markup=keyboard)
        else:
            response_text = "Нет доступных мероприятий."
            if isinstance(message_or_callback, types.Message):
                await message_or_callback.answer(response_text)
            else:
                await message_or_callback.message.answer(response_text)
        cursor.close()
    except psycopg2.Error as e:
        logger.error(f"Ошибка при получении списка мероприятий: {e}")
        error_text = "Произошла ошибка при получении списка мероприятий."
        if isinstance(message_or_callback, types.Message):
            await message_or_callback.answer(error_text)
        else:
            await message_or_callback.message.answer(error_text)

# Команда /list
@router.message(Command("list"))
async def list_events_command(message: types.Message, state: FSMContext):
    await show_events(message.from_user.id, message)

@router.callback_query(lambda c: c.data == 'list_events')
async def list_events_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await show_events(callback_query.from_user.id, callback_query)

# Команда /personal_list
@router.message(Command("personal_list"))
async def personal_list_command(message: types.Message, state: FSMContext):
    await show_personal_events(message.from_user.id, message)

@router.callback_query(lambda c: c.data == 'personal_list')
async def personal_list_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await show_personal_events(callback_query.from_user.id, callback_query)

@router.callback_query(lambda c: c.data.startswith('prev_') or c.data.startswith('next_'))
async def switch_event(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    direction, event_index_str = callback_query.data.split('_')
    event_index = int(event_index_str)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events")
    events = cursor.fetchall()

    if direction == 'next':
        event_index += 1
    elif direction == 'prev':
        event_index -= 1

    event = events[event_index]
    cursor.execute("SELECT * FROM participants WHERE event_id = %s AND user_id = %s", (event['event_id'], user_id))
    participant = cursor.fetchone()

    is_subscribed = participant is not None
    keyboard = event_navigation_keyboard(event_index, events, is_subscribed, event['useful_links'])

    await callback_query.message.edit_text(
        f"📝 Название: {event['title']}\n"
        f"📖 Описание: {event['description']}\n"
        f"📅 Дата: {event['event_date']}\n"
        f"📍 Место: {event['location']}\n",
        reply_markup=keyboard
    )
    cursor.close()

@router.callback_query(lambda c: c.data.startswith('personal_prev_') or c.data.startswith('personal_next_'))
async def switch_personal_event(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    data = callback_query.data.split('_')
    direction = data[1]
    event_index = int(data[2])

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events WHERE user_id = %s", (user_id,))
    events = cursor.fetchall()
    cursor.close()

    # Проверка на выход за пределы списка
    if direction == 'next' and event_index < len(events) - 1:
        event_index += 1
    elif direction == 'prev' and event_index > 0:
        event_index -= 1
    else:
        await callback_query.answer("Нет доступных событий в этом направлении.", show_alert=True)
        return

    event = events[event_index]

    keyboard = personal_event_navigation_keyboard(event_index, events)

    response_text = (
        f"📝 Название: {event['title']}\n"
        f"📖 Описание: {event['description']}\n"
        f"📅 Дата: {event['event_date']}\n"
        f"📍 Место: {event['location']}\n"
    )

    new_reply_markup = keyboard

    # Преобразование текущей и новой клавиатуры в строки для сравнения
    current_message_text = callback_query.message.text
    current_reply_markup = callback_query.message.reply_markup

    if current_message_text == response_text and str(current_reply_markup) == str(new_reply_markup):
        await callback_query.answer()  # Просто ответить на callback_query, чтобы убрать часы
    else:
        await callback_query.message.edit_text(
            response_text,
            reply_markup=new_reply_markup
        )

@router.callback_query(lambda c: c.data.startswith('edit_'))
async def edit_event_callback(callback_query: types.CallbackQuery, state: FSMContext):
    event_id = int(callback_query.data.split('_')[1])
    await state.update_data(event_id=event_id)
    await start_event_edit(callback_query, state)

async def start_event_edit(callback_query: types.CallbackQuery, state: FSMContext):
    keyboard = home_button()
    await delete_message_safe(callback_query.message.chat.id, callback_query.message.message_id)
    await callback_query.message.answer("Введите новое название мероприятия:", reply_markup=keyboard)
    await state.set_state(EventEdit.waiting_for_event_name)

@router.message(EventEdit.waiting_for_event_name)
async def handle_edit_event_name(message: types.Message, state: FSMContext):
    await state.update_data(event_name=message.text)
    keyboard = home_button()
    await message.answer("Введите новое описание мероприятия:", reply_markup=keyboard)
    await state.set_state(EventEdit.waiting_for_event_description)

@router.message(EventEdit.waiting_for_event_description)
async def handle_edit_event_description(message: types.Message, state: FSMContext):
    await state.update_data(event_description=message.text)
    keyboard = home_button()
    await message.answer("Введите новую дату мероприятия (дд.мм.гггг чч:мм):", reply_markup=keyboard)
    await state.set_state(EventEdit.waiting_for_event_date)

@router.message(EventEdit.waiting_for_event_date)
async def handle_edit_event_date(message: types.Message, state: FSMContext):
    date_text = message.text
    if validate_date(date_text):
        formatted_date = convert_date_format(date_text)
        await state.update_data(event_date=formatted_date)
        keyboard = home_button()
        await message.answer("Введите новое место проведения мероприятия:", reply_markup=keyboard)
        await state.set_state(EventEdit.waiting_for_event_location)
    else:
        await message.answer("Неправильный формат даты. Пожалуйста, введите дату в формате дд.мм.гггг чч:мм:")

@router.message(EventEdit.waiting_for_event_location)
async def handle_edit_event_location(message: types.Message, state: FSMContext):
    await state.update_data(event_location=message.text)
    keyboard = home_button()
    await message.answer("Введите новую ссылку на мероприятие:", reply_markup=keyboard)
    await state.set_state(EventEdit.waiting_for_event_links)

@router.message(EventEdit.waiting_for_event_links)
async def handle_edit_event_links(message: types.Message, state: FSMContext):
    url = message.text
    if validate_url(url):
        user_data = await state.get_data()
        event_id = user_data['event_id']
        event_name = user_data['event_name']
        event_description = user_data['event_description']
        event_date = user_data['event_date']
        event_location = user_data['event_location']
        event_links = url

        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE events SET title = %s, description = %s, event_date = %s, location = %s, useful_links = %s WHERE event_id = %s",
                (event_name, event_description, event_date, event_location, event_links, event_id)
            )
            conn.commit()
            cursor.close()
            await message.answer('Мероприятие обновлено!')
            await start_command(message)
        except Exception as e:
            logger.error(f"Ошибка при обновлении мероприятия: {e}")
            conn.rollback()
            await message.answer("Произошла ошибка при обновлении мероприятия. Убедитесь, что формат данных правильный.")

        await state.clear()
    else:
        await message.answer("Неправильный формат ссылки. Пожалуйста, введите ссылку на мероприятие (начинающуюся с http:// или https://):")

@router.callback_query(lambda c: c.data.startswith('delete_'))
async def delete_event_callback(callback_query: types.CallbackQuery, state: FSMContext):
    event_id = int(callback_query.data.split('_')[1])
    try:
        cursor = conn.cursor()
        # Сначала удаляем все записи из таблицы participants, которые ссылаются на удаляемое мероприятие
        cursor.execute("DELETE FROM participants WHERE event_id = %s", (event_id,))
        # Затем удаляем само мероприятие
        cursor.execute("DELETE FROM events WHERE event_id = %s", (event_id,))
        conn.commit()
        cursor.close()
        await callback_query.message.answer('Мероприятие удалено!')
        await delete_message_safe(callback_query.message.chat.id, callback_query.message.message_id)
        await show_personal_events(callback_query.from_user.id, callback_query)
    except psycopg2.Error as e:
        logger.error(f"Ошибка при удалении мероприятия: {e}")
        await callback_query.message.answer("Произошла ошибка при удалении мероприятия.")

# Подписка на мероприятие
@router.callback_query(lambda c: c.data.startswith('subscribe_'))
async def subscribe_event(callback_query: types.CallbackQuery, state: FSMContext):
    event_id = int(callback_query.data.split('_')[1])
    user_id = callback_query.from_user.id
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO participants (event_id, user_id) VALUES (%s, %s)",
            (event_id, user_id)
        )
        conn.commit()
        cursor.close()
        await delete_message_safe(callback_query.message.chat.id, callback_query.message.message_id)
        await show_events(user_id, callback_query)  # Обновить список мероприятий
    except psycopg2.Error as e:
        logger.error(f"Ошибка при подписке на мероприятие: {e}")
        await callback_query.message.answer("Произошла ошибка при подписке на мероприятие.")

# Отписка от мероприятия
@router.callback_query(lambda c: c.data.startswith('unsubscribe_'))
async def unsubscribe_event(callback_query: types.CallbackQuery, state: FSMContext):
    event_id = int(callback_query.data.split('_')[1])
    user_id = callback_query.from_user.id
    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM participants WHERE event_id = %s AND user_id = %s",
            (event_id, user_id)
        )
        conn.commit()
        cursor.close()
        await delete_message_safe(callback_query.message.chat.id, callback_query.message.message_id)
        await show_events(user_id, callback_query)  # Обновить список мероприятий
    except psycopg2.Error as e:
        logger.error(f"Ошибка при отписке от мероприятия: {e}")
        await callback_query.message.answer("Произошла ошибка при отписке от мероприятия.")

# Кнопка "Домой"
@router.callback_query(lambda c: c.data == "home")
async def home_callback(callback_query: types.CallbackQuery):
    await delete_message_safe(callback_query.message.chat.id, callback_query.message.message_id)
    await start_command(callback_query.message)

# Обработчик для всех остальных сообщений
@router.message()
async def handle_text(message: types.Message):
    response = "Вы не использовали команду. Чтобы просмотреть команды, Вы можете воспользоваться кнопкой меню."
    await message.answer(response)

# Основная функция
async def main():
    dp.include_router(router)
    await on_startup()
    try:
        await dp.start_polling(bot)
    finally:
        await on_shutdown()

if __name__ == '__main__':
    asyncio.run(main())
