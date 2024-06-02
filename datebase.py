import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram.types import ParseMode, ReplyKeyboardMarkup, KeyboardButton
# Установка токена бота
API_TOKEN = '7316832069:AAE8kM2fPRVWHfRi0VvFa4EDiEnwzmQd1C4'

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Подключение к базе данных SQLite
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Создание таблицы users, если она не существует

conn.commit()

# Обработчик команды /subscribe
@dp.message_handler(commands=['subscribe'])
async def subscribe(message: types.Message):
    user_id = str(message.from_user.id)
    cursor.execute("SELECT status FROM users WHERE user_id = ?", (user_id,))
    user_status = cursor.fetchone()

    if user_status is None:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        await message.reply("Вы успешно подписались на уведомления.")
    elif user_status[0] == 1:
        await message.reply("Вы уже подписаны.")
    else:
        cursor.execute("UPDATE users SET status = 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        await message.reply("Вы успешно подписались на уведомления.")

# Обработчик команды /unsubscribe
@dp.message_handler(commands=['unsubscribe'])
async def unsubscribe(message: types.Message):
    user_id = str(message.from_user.id)
    cursor.execute("SELECT status FROM users WHERE user_id = ?", (user_id,))
    user_status = cursor.fetchone()

    if user_status is None:
        await message.reply("Вы еще не подписаны.")
    elif user_status[0] == 0:
        await message.reply("Вы уже отписаны.")
    else:
        cursor.execute("UPDATE users SET status = 0 WHERE user_id = ?", (user_id,))
        conn.commit()
        await message.reply("Вы успешно отписались от уведомлений.")

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = str(message.from_user.id)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    subscribe_button = KeyboardButton('/subscribe')
    unsubscribe_button = KeyboardButton('/unsubscribe')
    keyboard.add(subscribe_button, unsubscribe_button)
    await message.reply("Добро пожаловать! Выберите действие:", reply_markup=keyboard)

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)