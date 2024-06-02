import requests
import time
from DrissionPage import ChromiumPage
import datetime
import sqlite3

while True:
    try:
        url = 'https://ru.almaviva-visa.services/'

        page = ChromiumPage()
        page.get(url)

        a = page.cookies(url)
        cf_clearance = a.get('cf_clearance')

        cookie_string = ""
        for key, value in a.items():
            cookie_string += f"{key}={value}; "

        cookie_string = cookie_string.rstrip("; ") + '"'
        print(cf_clearance)

        token_url = "https://ru.almaviva-visa.services/api/login"
        token_data = {
            "email": "ushakovrea@gmail.com",
            "password": "Au04071997!"
        }
        headers1 = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "authorization": "Bearer",
            "content-type": "application/json",
            "cookie": f"cf_clearance={cf_clearance}",
            "origin": "https://ru.almaviva-visa.services",
            "priority": "u=1, i",
            "referer": "https://ru.almaviva-visa.services/",
            "sec-ch-ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            "sec-ch-ua-arch": "x86",
            "sec-ch-ua-bitness": "64",
            "sec-ch-ua-full-version": "125.0.6422.113",
            "sec-ch-ua-full-version-list": '"Google Chrome";v="125.0.6422.113", "Chromium";v="125.0.6422.113", "Not.A/Brand";v="24.0.0.0"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-model": "",
            "sec-ch-ua-platform": "Windows",
            "sec-ch-ua-platform-version": "10.0.0",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        }

        # Получение токена
        token_response = requests.post(token_url, json=token_data, headers=headers1)
        if token_response.status_code != 200:
            print(f"Ошибка получения токена: {token_response.status_code}")
            time.sleep(60)
            continue  # Перезапуск цикла while
        token = token_response.json()["accessToken"]
        cookies = token_response.cookies.get_dict()

        # Список различных siteId
        site_ids = [7, 8, 9, 10, 11, 12, 14, 16]
        current_date = datetime.datetime.now()

        page.quit(timeout=7)

        for site_id in site_ids:
            # Подключение к базе данных
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()

            all_missing_dates = []  # Переменная для хранения всех пропущенных дат

            for month_offset in range(1, 3):  # Проверка на следующий месяц и через месяц
                # Получаем первый день следующего месяца
                target_month_first_day = (current_date.replace(day=1) + datetime.timedelta(days=32 * month_offset)).replace(day=1)
                # Получаем последний день текущего месяца
                last_day_current_month = (target_month_first_day + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)

                # Форматируем даты в строковый формат
                start_date = target_month_first_day.strftime('%d/%m/%Y')
                end_date = last_day_current_month.strftime('%d/%m/%Y')

                dates_url = 'https://ru.almaviva-visa.services/api/sites/disabled-dates/'
                dates_params = {
                    'start': start_date,
                    'end': end_date,
                    'siteId': site_id,
                    'persons': 1
                }
                dates_headers = {
                    "Host": "ru.almaviva-visa.services",
                    "cookie": f"cf_clearance={cf_clearance}",
                    "sec-ch-ua": "\"Google Chrome\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
                    "sec-ch-ua-mobile": "?0",
                    "authorization": f"Bearer {token}",
                    "sec-ch-ua-arch": "\"x86\"",
                    "sec-ch-ua-full-version": "\"125.0.6422.113\"",
                    "accept": "application/json, text/plain, */*",
                    "sec-ch-ua-platform-version": "\"10.0.0\"",
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                    "sec-ch-ua-full-version-list": "\"Google Chrome\";v=\"125.0.6422.113\", \"Chromium\";v=\"125.0.6422.113\", \"Not.A/Brand\";v=\"24.0.0.0\"",
                    "sec-ch-ua-bitness": "\"64\"",
                    "sec-ch-ua-model": "\"\"",
                    "sec-ch-ua-platform": "\"Windows\"",
                    "sec-fetch-site": "same-origin",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-dest": "empty",
                    "referer": "https://ru.almaviva-visa.services/appointment",
                    "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                    "priority": "u=1, i"
                }

                dates_response = requests.get(dates_url, params=dates_params, headers=dates_headers)
                if dates_response.status_code != 200:
                    print(f"Ошибка получения слотов для siteId={site_id} на {start_date} - {end_date}: {dates_response.status_code}")
                    time.sleep(60)
                    continue  # Перезапуск цикла while

                dates_data = dates_response.json()
                print(f"Данные для siteId={site_id} на {start_date} - {end_date}:")
                print(dates_data)
                all_dates_target_month = [target_month_first_day.replace(day=day).strftime('%Y-%m-%d') for day in range(1, last_day_current_month.day + 1)]

                dates_from_response = [data['date'] for data in dates_data]
                missing_dates = [date for date in all_dates_target_month if date in dates_from_response]

                all_missing_dates.extend(missing_dates)  # Добавляем пропущенные даты в общий список

            # Сохраняем пропущенные даты и время последнего обновления в базу данных
            all_missing_dates_str = str(all_missing_dates)
            last_update = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('UPDATE cities SET dates = ?, last_update = ? WHERE alt_number = ?', (all_missing_dates_str, last_update, site_id,))
            print(f"Пропущенные даты для siteId={site_id}: {all_missing_dates_str}")
            print(f"Последнее обновление для siteId={site_id}: {last_update}")
            conn.commit()
            time.sleep(4)

        time.sleep(5)

    except Exception as e:
        print(f"Произошла ошибка: {e}. Перезапуск через 60 секунд.")
        time.sleep(60)