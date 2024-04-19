import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command

# Замените 'YOUR_TOKEN' на ваш токен
TOKEN = '7167280571:AAHbRH6IhYDYwusbufpWy6q9zHdXuCmOdFc'

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Словарь для хранения созданных мероприятий с ключами
events = {}

# Обработчик команды /start для вывода информации о боте и командах
@dp.message(Command("start"))
async def start(message: types.Message):
    commands_info = (
        "/start - Начать взаимодействие с ботом\n"
        "/create - Создать новое мероприятие и получить ключ доступа\n"
        "/join [ключ] - Присоединиться к существующему мероприятию по ключу\n"
    )
    await message.answer(
        "Привет! Я бот для создания и управления мероприятиями в ИТМО.\n\n"
        "Вот список доступных команд:\n\n"
        f"{commands_info}"
    )

# Обработчик команды /create для создания мероприятия с уникальным ключом
@dp.message(Command("create"))
async def create_event(message: types.Message):
    # Генерация уникального ключа для мероприятия
    event_key = str(hash(message.chat.id + message.message_id))
    events[event_key] = {'creator': message.from_user.id, 'participants': []}
    await message.answer(f'Мероприятие создано! Ключ доступа: {event_key}')

# Обработчик команды /join для подключения к мероприятию по ключу
@dp.message(Command("join"))
async def join_event(message: types.Message):
    try:
        command, event_key = message.text.split()
        if event_key in events:
            events[event_key]['participants'].append(message.from_user.id)
            await message.answer('Вы успешно присоединились к мероприятию!')
        else:
            await message.answer('Мероприятие с данным ключом не найдено.')
    except ValueError:
        await message.answer('Используйте команду в формате: /join [ключ]')

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
