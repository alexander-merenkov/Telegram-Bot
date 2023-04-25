import telebot, requests, json, datetime, os
from telebot.custom_filters import StateFilter
from typing import Any
from dotenv import load_dotenv
from states.bot_states import UserInfoState


load_dotenv()

bot_id = os.getenv('bot_token')
api_key = os.getenv('X-RapidAPI-Key')
api_host = os.getenv('X-RapidAPI-Host')

token = {'X-RapidAPI-Key': api_key, 'X-RapidAPI-Host': api_host}

bot = telebot.TeleBot(bot_id)

bot.add_custom_filter(StateFilter(bot))


def start(message: telebot.types.Message) -> None:
	""""
	Функция для команды /start
	Приветствует пользователя и обнуляет историю поиска
	"""
	bot.set_state(message.from_user.id, UserInfoState.start, message.chat.id)

	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		if data.get('history'):
			data['history'] = ()
	bot.send_message(message.from_user.id, f'Привет, {message.from_user.first_name}, я учебный бот!')


def history(message: telebot.types.Message) -> None:
	""""
	Функция для команды /history. Выводит историю поиска
	"""
	bot.set_state(message.from_user.id, UserInfoState.history, message.chat.id)
	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		if not data.get('history'):
			bot.send_message(message.from_user.id, 'История поиска пустая')
		else:
			bot_string = ''
			for history in data['history']:
				bot_string += f'{history.get("command")}:\n{history.get("date").strftime("%Y-%m-%d %H:%M:%S")}, {", ".join(history.get("hotels"))} \n\n'

			bot.send_message(message.from_user.id, bot_string)


def register_date_in(message: telebot.types.Message) -> None:
	""""
	Функция для регистрации даты заселения
	"""
	date = date_check(message.text)
	if date:

		bot.set_state(message.from_user.id, UserInfoState.register_date_in, message.chat.id)
		with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
			data['register_date_in'] = date

		bot.send_message(message.from_user.id, 'Какая дата выселения? (дд-мм-гггг)')
		bot.register_next_step_handler(message, register_date_out)

	else:
		bot.send_message(message.from_user.id, 'Неверная дата заселения, повторите пожалуйста')
		return bot.register_next_step_handler(message, register_date_in)


def register_date_out(message: telebot.types.Message) -> None:
	""""
	Функция для регистрации даты выселения
	"""
	date = date_check(message.text)
	if date:

		bot.set_state(message.from_user.id, UserInfoState.register_date_out, message.chat.id)
		with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
			data['register_date_out'] = date
            data['flag'] = True

		bot.send_message(message.from_user.id, 'Пошел искать! Пожалуйста, ожидайте.')


	else:
		bot.send_message(message.from_user.id, 'Неверная дата выселения, повторите пожалуйста')
		return bot.register_next_step_handler(message, register_date_out)


def date_check(date_str: str) -> datetime:
	""""
	Функция для проверки даты из строки.
	:return: Объект datetime
	"""
	date_format = '%d-%m-%Y'
	today = datetime.datetime.now()
	try:
		dateObject = datetime.datetime.strptime(date_str, date_format)
		if dateObject.date() >= today.date():
			return dateObject
	except ValueError:
		return False


def get_command(message: telebot.types.Message) -> None:
	""""
	Функция для регистрации команд /lowprice, /bestdeal, /guest_rating
	"""
	bot.set_state(message.from_user.id, UserInfoState.command, message.chat.id)
	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		data['command'] = message.text


	bot.send_message(message.from_user.id, f"Привет, {message.from_user.first_name}, в каком городе будем искать?")
	bot.register_next_step_handler(message, get_city)


def get_city(message: telebot.types.Message) -> Any:
	""""
	Функция для регистрации города
	"""

	if message.text.isdigit():
		bot.send_message(message.from_user.id, 'Неверно указан город\nВ каком городе будем искать?')
		return bot.register_next_step_handler(message, get_city)

	bot.set_state(message.from_user.id, UserInfoState.city, message.chat.id)
	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		data['city'] = message.text

		if data['command'] == '/lowprice' or data['command'] == '/guest_rating':
			bot.send_message(message.from_user.id, 'Сколько отелей вывести?')
			bot.register_next_step_handler(message, get_hotels_count)

		elif data['command'] == '/bestdeal':
			bot.send_message(message.from_user.id, 'Какой диапазон цен за ночь в USD? (min-max)')
			bot.register_next_step_handler(message, price_values)


def get_hotels_count(message: telebot.types.Message) -> Any:
	""""
	Функция для регистрации количества отелей
	"""
	if not message.text.isdigit():
		bot.send_message(message.from_user.id, 'Неверное количество\nСколько отелей вывести?')
		return bot.register_next_step_handler(message, get_hotels_count)

	bot.set_state(message.from_user.id, UserInfoState.hotels_count, message.chat.id)
	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		if int(message.text) > 10:
			data['hotels_count'] = int(message.text)
		else:
			data['hotels_count'] = int(message.text)

	bot.send_message(message.from_user.id, 'Вывести фото?')
	bot.register_next_step_handler(message, get_photo)


def price_values(message: telebot.types.Message) -> Any:
	""""
	Функция для регистрации диапазона цен
	"""
	prices = message.text.split('-')
	if len(prices) == 2:
		if not prices[0].isdigit or not prices[1].isdigit:
			bot.send_message(message.from_user.id, 'Неверный диапазон цен, повторите. (min-max)')
			return bot.register_next_step_handler(message, price_values)
		else:

			bot.set_state(message.from_user.id, UserInfoState.price_values, message.chat.id)
			with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
				data['price_values'] = prices

			bot.send_message(message.from_user.id, 'Какое расстояние от центра в км?')
			bot.register_next_step_handler(message, get_distance)
	else:
		bot.send_message(message.from_user.id, 'Неверный диапазон цен, повторите. (min-max)')
		return bot.register_next_step_handler(message, price_values)


def get_distance(message: telebot.types.Message) -> Any:
	""""
	Функция для регистрации отдаления от центра
	"""
	if not message.text.isdigit():
		bot.send_message(message.from_user.id, 'Неверное расстояние\nКакое расстояние от центра в км?')
		return bot.register_next_step_handler(message, get_distance)

	bot.set_state(message.from_user.id, UserInfoState.distance, message.chat.id)
	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		data['distance'] = int(message.text)


	bot.send_message(message.from_user.id, 'Сколько отелей вывести?')
	bot.register_next_step_handler(message, get_hotels_count)


def get_photo(message: telebot.types.Message) -> Any:
	""""
	Функция для регистрации необходимости вывода фото
	"""
	bot.set_state(message.from_user.id, UserInfoState.photo, message.chat.id)

	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		if message.text.lower() == 'да':
			data['photo'] = True
			bot.send_message(message.from_user.id, 'Сколько вывести фото?')
			bot.register_next_step_handler(message, get_photo_count)
		elif message.text.lower() == 'нет':
			data['photo'] = False
			bot.send_message(message.from_user.id, 'Какая дата заселения? (дд-мм-гггг)')
			bot.register_next_step_handler(message, register_date_in)
		else:
			bot.send_message(message.from_user.id, 'Я так и не понял, да или нет?(')
			return bot.register_next_step_handler(message, get_photo)


def get_photo_count(message: telebot.types.Message) -> Any:
	""""
	Функция для регистрации количества фото для вывода
	"""
	bot.set_state(message.from_user.id, UserInfoState.photo_count, message.chat.id)
	if message.text.isdigit():
		with bot.retrieve_data(message.from_user.id, message.chat.id) as data:

			if int(message.text) > 5:
				data['photo_count'] = 5
			else:
				data['photo_count'] = int(message.text)
	else:
		bot.send_message(message.from_user.id, 'Неверное количество, повторите')
		return bot.register_next_step_handler(message, get_photo_count)

	bot.send_message(message.from_user.id, 'Какая дата заселения? (дд-мм-гггг)')
	bot.register_next_step_handler(message, register_date_in)