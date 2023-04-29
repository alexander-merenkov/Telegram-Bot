import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
X_RapidAPI_Key = os.getenv("X_RapidAPI_Key")
X_RapidAPI_Host = os.getenv("X_RapidAPI_Host")
DEFAULT_COMMANDS = (
    ('start', "Запустить бота"),
    ('help', "Вывести справку"),
    ('hello_world', 'Бот расскажет о себе'),
    ('lowprice', 'Узнать топ самых дешёвых отелей в городе'),
    ('guest_rating', 'Узнать топ самых популярных отелей в городе'),
    ('bestdeal', 'Узнать топ отелей, наиболее подходящих по цене и расположению от центра '),
    ('history', 'Узнать историю поиска отелей'),
)