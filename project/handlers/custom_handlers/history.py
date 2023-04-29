from loader import bot
from states.bot_states import UserInfoState
from telebot.types import Message
from handlers.custom_handlers.survey import history_requests


@bot.message_handler(commands=['history'])
def history(message: Message) -> None:
	""""
	Функция для команды /history. Выводит историю поиска
	"""
	bot.set_state(message.from_user.id, None, message.chat.id)

	if history_requests:
		if len(history_requests) == 0:
			bot.send_message(message.from_user.id, 'История поиска пустая')
		else:
			bot_string = ''
			for history_for_user in history_requests:
				history = history_for_user.get(message.from_user.id)
				if history:
					bot_string += f'{history.get("command")}:\n{history.get("date").strftime("%Y-%m-%d %H:%M:%S")}, {", ".join(history.get("hotels"))} \n\n'

			bot.send_message(message.from_user.id, bot_string)

	else:
		bot.send_message(message.from_user.id, 'История поиска пустая')
