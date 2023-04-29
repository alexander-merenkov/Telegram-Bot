from telebot.types import Message
from loader import bot

@bot.message_handler(commands=["start"])
def start(message: Message) -> None:
	""""
	Функция для команды /start
	"""
	bot.set_state(message.from_user.id, None, message.chat.id)
	bot.send_message(message.from_user.id, f'Привет, {message.from_user.first_name}, я учебный бот!')