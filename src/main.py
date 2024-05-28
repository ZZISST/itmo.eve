import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command, CommandStart
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from configparser import ConfigParser

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv('TOKEN')
#DATABASE_URL = os.getenv('DATABASE_URL')
DATABASE_URL = f"postgresql+psycopg2://{os.environ.get('DATABASE_USER')}:{os.environ.get('DATABASE_PASSWORD')}@" \
              f"{os.environ.get('DATABASE_HOST')}:{os.environ.get('DATABASE_PORT')}/{os.environ.get('DATABASE_NAME')}"
logger.info("DATABASE-URLabbbbbbbbbbbbbbbbb"+str(DATABASE_URL)+"   "+str(TOKEN))


bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()

def load_config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)

    # get section, default to postgresql
    config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

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

db_connection = None

async def on_startup():
    global db_connection
    db_connection = create_db_connection()

async def on_shutdown():
    if db_connection:
        db_connection.close()
        logger.info("Подключение к базе данных закрыто")


@router.message(CommandStart())
async def start_command(message: types.Message):
    commands_info = (
        "/start - Начать взаимодействие с ботом\n"
        "/create - Создать новое мероприятие и получить ключ доступа\n"
        "/join [ключ] - Присоединиться к существующему мероприятию по ключу\n"
    )
    await message.answer(
        "Привет! Я бот для создания и управления мероприятиями.\n\n"
        "Вот список доступных команд:\n\n"
        f"{commands_info}"
    )


@router.message(Command("create"))
async def create_event(message: types.Message):
    event_key = str(hash(message.chat.id + message.message_id))
    try:
        cursor = db_connection.cursor()
        cursor.execute(
            "INSERT INTO events (event_key, creator_id) VALUES (%s, %s)",
            (event_key, message.from_user.id)
        )
        db_connection.commit()
        cursor.close()
        await message.answer(f'Мероприятие создано! Ключ доступа: {event_key}')
    except psycopg2.Error as e:
        logger.error(f"Ошибка при создании мероприятия: {e}")
        await message.answer("Произошла ошибка при создании мероприятия.")


@router.message(Command("join"))
async def join_event(message: types.Message):
    try:
        command, event_key = message.text.split()
        cursor = db_connection.cursor()
        cursor.execute("SELECT * FROM events WHERE event_key = %s", (event_key,))
        event = cursor.fetchone()
        if event:
            cursor.execute(
                "INSERT INTO participants (event_key, user_id) VALUES (%s, %s)",
                (event_key, message.from_user.id)
            )
            db_connection.commit()
            await message.answer('Вы успешно присоединились к мероприятию!')
        else:
            await message.answer('Мероприятие с данным ключом не найдено.')
        cursor.close()
    except ValueError:
        await message.answer('Используйте команду в формате: /join [ключ]')
    except psycopg2.Error as e:
        logger.error(f"Ошибка при присоединении к мероприятию: {e}")
        await message.answer("Произошла ошибка при присоединении к мероприятию.")


async def main():
    dp.include_router(router)
    await on_startup()
    try:
        await dp.start_polling(bot)
    finally:
        await on_shutdown()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())