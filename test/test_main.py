import pytest
import asyncio
from aiogram import types
from unittest.mock import AsyncMock, patch
from src.main import start_command, create_event, join_event, on_startup, on_shutdown, db_connection


@pytest.fixture
async def message():
    return types.Message(message_id=1, from_user=types.User(id=12345, is_bot=False, first_name="Test"),
                         chat=types.Chat(id=12345, type="private"), date=types.datetime.datetime.now(), text="/start")


@pytest.fixture
async def db_mock():
    with patch("main.db_connection") as mock:
        yield mock


@pytest.mark.asyncio
async def test_start_command(message):
    message.answer = AsyncMock()
    await start_command(message)
    message.answer.assert_called_once()
    assert "Привет! Я бот для создания и управления мероприятиями." in message.answer.call_args[0][0]


@pytest.mark.asyncio
async def test_create_event(message, db_mock):
    message.text = "/create"
    message.answer = AsyncMock()

    db_mock.cursor.return_value.__enter__.return_value = AsyncMock()

    await create_event(message)
    message.answer.assert_called_once_with(
        f'Мероприятие создано! Ключ доступа: {hash(message.chat.id + message.message_id)}')


@pytest.mark.asyncio
async def test_join_event_success(message, db_mock):
    message.text = "/join 123456"
    message.answer = AsyncMock()

    db_mock.cursor.return_value.__enter__.return_value.fetchone.return_value = {"event_key": "123456"}

    await join_event(message)
    message.answer.assert_called_once_with('Вы успешно присоединились к мероприятию!')


@pytest.mark.asyncio
async def test_join_event_invalid_format(message):
    message.text = "/join"
    message.answer = AsyncMock()

    await join_event(message)
    message.answer.assert_called_once_with('Используйте команду в формате: /join [ключ]')


@pytest.mark.asyncio
async def test_join_event_not_found(message, db_mock):
    message.text = "/join 123456"
    message.answer = AsyncMock()

    db_mock.cursor.return_value.__enter__.return_value.fetchone.return_value = None

    await join_event(message)
    message.answer.assert_called_once_with('Мероприятие с данным ключом не найдено.')


@pytest.mark.asyncio
async def test_join_event_db_error(message, db_mock):
    message.text = "/join 123456"
    message.answer = AsyncMock()

    db_mock.cursor.return_value.__enter__.side_effect = Exception("Database error")

    await join_event(message)
    message.answer.assert_called_once_with("Произошла ошибка при присоединении к мероприятию.")