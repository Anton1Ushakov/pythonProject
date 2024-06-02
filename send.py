import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import asyncio
from datetime import datetime, timedelta

conn = sqlite3.connect('users.db')
cursor = conn.cursor()
conn.commit()

BOT_TOKEN = '7316832069:AAE8kM2fPRVWHfRi0VvFa4EDiEnwzmQd1C4'
# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

async def send_message(user_id, message):
    await bot.send_message(chat_id=user_id, text=message)

async def main():
    while True:
        cursor = conn.cursor()
        # Получаем города, даты слотов и время последнего обновления из таблицы cities
        cursor.execute("SELECT city, dates, last_update FROM cities")
        cities = cursor.fetchall()

        current_time = datetime.now()
        user_id_for_notification = 773600126

        for city in cities:
            city_name = city[0]
            slots = city[1]
            last_update_str = city[2]

            # Проверяем время последнего обновления
            if last_update_str:
                last_update = datetime.strptime(last_update_str, '%Y-%m-%d %H:%M:%S')
                time_difference = current_time - last_update
                if time_difference > timedelta(hours=5):
                    message = f"Слоты в городе {city_name} не обновлялись более 5 часов."
                    await send_message(user_id_for_notification, message)

            # Проверяем наличие слотов
            if slots != str([]) and slots != None:
                slots_string = ', '.join(slots.strip("[]'").split(", "))
                message = f"В городе {city_name} появились слоты: {slots_string}"

                # Получаем всех пользователей
                cursor.execute("SELECT user_id FROM users WHERE status = 1")
                users = cursor.fetchall()

                for user in users:
                    user_id = user[0]
                    # Отправляем сообщение каждому пользователю
                    await send_message(user_id, message)

        conn.commit()
        await asyncio.sleep(1800)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())