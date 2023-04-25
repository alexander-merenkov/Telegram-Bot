import telebot, os
from dotenv import load_dotenv

load_dotenv()

BOT_ID = os.getenv('bot_token')
API_KEY = os.getenv('X-RapidAPI-Key')
API_HOST = os.getenv('X-RapidAPI-Host')


bot = telebot.TeleBot(BOT_ID)