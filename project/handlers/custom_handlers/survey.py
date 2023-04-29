from loader import bot
from states.bot_states import UserInfoState
from telebot.types import Message
import datetime
from hotel_api.hotel_api import response
from telebot.types import InputMediaPhoto


@bot.message_handler(commands=['hello_world'])
def hello_world(message: Message) -> None:
	""""
	Функция для регистрации команд /hello_world
	"""
	bot.send_message(message.from_user.id,
					 'Привет, меня зовут Merenkov_DPO_bot, я учебный бот!\nНадеюсь я вам понравлюсь, иначе я не получу диплом')


@bot.message_handler(commands=['lowprice'])
def low_pirce(message: Message) -> None:
	""""
	Функция для регистрации команд /lowprice
	"""
	bot.set_state(message.from_user.id, UserInfoState.command, message.chat.id)
	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		data['command'] = '/lowprice'

	bot.set_state(message.from_user.id, UserInfoState.city, message.chat.id)
	bot.send_message(message.from_user.id, f"Привет, {message.from_user.first_name}, в каком городе будем искать?")


@bot.message_handler(commands=['bestdeal'])
def best_deal(message: Message) -> None:
	""""
	Функция для регистрации команд /bestdeal
	"""
	bot.set_state(message.from_user.id, UserInfoState.command, message.chat.id)
	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		data['command'] = '/bestdeal'

	bot.set_state(message.from_user.id, UserInfoState.city, message.chat.id)
	bot.send_message(message.from_user.id, f"Привет, {message.from_user.first_name}, в каком городе будем искать?")


@bot.message_handler(commands=['guest_rating'])
def guest_rating(message: Message) -> None:
	""""
	Функция для регистрации команд /guest_rating
	"""
	bot.set_state(message.from_user.id, UserInfoState.command, message.chat.id)
	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		data['command'] = '/guest_rating'

	bot.set_state(message.from_user.id, UserInfoState.city, message.chat.id)
	bot.send_message(message.from_user.id, f"Привет, {message.from_user.first_name}, в каком городе будем искать?")


@bot.message_handler(state=UserInfoState.city)
def get_city(message: Message) -> None:
	""""
	Функция для регистрации города
	"""

	if message.text.isdigit():
		bot.send_message(message.from_user.id, 'Неверно указан город\nВ каком городе будем искать?')
		bot.set_state(message.from_user.id, UserInfoState.city, message.chat.id)

	else:
		with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
			data['city'] = message.text

			if data['command'] == '/lowprice' or data['command'] == '/guest_rating':
				bot.send_message(message.from_user.id, 'Сколько отелей вывести?')
				bot.set_state(message.from_user.id, UserInfoState.hotels_count, message.chat.id)

			elif data['command'] == '/bestdeal':
				bot.send_message(message.from_user.id, 'Какой диапазон цен за ночь в USD? (min-max)')
				bot.set_state(message.from_user.id, UserInfoState.price_values, message.chat.id)


@bot.message_handler(state=UserInfoState.hotels_count)
def get_hotels_count(message: Message) -> None:
	"""
	Функция для регистрации количества отелей
	"""
	if not message.text.isdigit():
		bot.send_message(message.from_user.id, 'Неверное количество\nСколько отелей вывести?')
		bot.set_state(message.from_user.id, UserInfoState.hotels_count, message.chat.id)
	else:
		with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
			if int(message.text) > 10:
				data['hotels_count'] = int(message.text)
			else:
				data['hotels_count'] = int(message.text)

		bot.send_message(message.from_user.id, 'Вывести фото?')
		bot.set_state(message.from_user.id, UserInfoState.photo, message.chat.id)


@bot.message_handler(state=UserInfoState.photo)
def get_photo(message: Message) -> None:
	""""
	Функция для регистрации необходимости вывода фото
	"""

	if message.text.lower() == 'да':
		with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
			data['photo'] = True
		bot.send_message(message.from_user.id, 'Сколько вывести фото?')
		bot.set_state(message.from_user.id, UserInfoState.photo_count, message.chat.id)
	elif message.text.lower() == 'нет':
		with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
			data['photo'] = False
		bot.send_message(message.from_user.id, 'Какая дата заселения? (дд-мм-гггг)')
		bot.set_state(message.from_user.id, UserInfoState.register_date_in, message.chat.id)
	else:
		bot.send_message(message.from_user.id, 'Я так и не понял, да или нет?(')
		bot.set_state(message.from_user.id, UserInfoState.photo, message.chat.id)


@bot.message_handler(state=UserInfoState.photo_count)
def get_photo_count(message: Message) -> None:
	""""
	Функция для регистрации количества фото для вывода
	"""
	if message.text.isdigit():
		with bot.retrieve_data(message.from_user.id, message.chat.id) as data:

			if int(message.text) > 5:
				data['photo_count'] = 5
			else:
				data['photo_count'] = int(message.text)
			bot.send_message(message.from_user.id, 'Какая дата заселения? (дд-мм-гггг)')
			bot.set_state(message.from_user.id, UserInfoState.register_date_in, message.chat.id)
	else:
		bot.send_message(message.from_user.id, 'Неверное количество, повторите')
		bot.set_state(message.from_user.id, UserInfoState.photo_count, message.chat.id)


@bot.message_handler(state=UserInfoState.register_date_in)
def register_date_in(message: Message) -> None:
	""""
	Функция для регистрации даты заселения
	"""
	date = date_check(message.text)
	if date:
		with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
			data['register_date_in'] = date

		bot.send_message(message.from_user.id, 'Какая дата выселения? (дд-мм-гггг)')
		bot.set_state(message.from_user.id, UserInfoState.register_date_out, message.chat.id)

	else:
		bot.send_message(message.from_user.id, 'Неверная дата заселения, повторите пожалуйста')
		bot.set_state(message.from_user.id, UserInfoState.register_date_in, message.chat.id)


@bot.message_handler(state=UserInfoState.register_date_out)
def register_date_out(message: Message) -> None:
	""""
	Функция для регистрации даты выселения
	"""
	date = date_check(message.text)
	if date:
		with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
			data['register_date_out'] = date

			bot.send_message(message.from_user.id, 'Пошел искать! Пожалуйста, ожидайте.')
			bot.set_state(message.from_user.id, None, message.chat.id)
			answer(message, data)

	else:
		bot.send_message(message.from_user.id, 'Неверная дата выселения, повторите пожалуйста')
		bot.set_state(message.from_user.id, UserInfoState.register_date_out, message.chat.id)


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


@bot.message_handler(state=UserInfoState.price_values)
def price_values(message: Message) -> None:
	""""
	Функция для регистрации диапазона цен
	"""
	prices = message.text.split('-')
	if len(prices) == 2:
		if not prices[0].isdigit or not prices[1].isdigit:
			bot.send_message(message.from_user.id, 'Неверный диапазон цен, повторите. (min-max)')
			bot.set_state(message.from_user.id, UserInfoState.price_values, message.chat.id)

		else:
			with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
				data['price_values'] = prices
			bot.send_message(message.from_user.id, 'Какое расстояние от центра в км?')
			bot.set_state(message.from_user.id, UserInfoState.distance, message.chat.id)

	else:
		bot.send_message(message.from_user.id, 'Неверный диапазон цен, повторите. (min-max)')
		bot.set_state(message.from_user.id, UserInfoState.price_values, message.chat.id)


@bot.message_handler(state=UserInfoState.distance)
def get_distance(message: Message) -> None:
	""""
	Функция для регистрации отдаления от центра
	"""
	if not message.text.isdigit():
		bot.send_message(message.from_user.id, 'Неверное расстояние\nКакое расстояние от центра в км?')
		bot.set_state(message.from_user.id, UserInfoState.price_values, message.chat.id)
	else:
		with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
			data['distance'] = int(message.text)

	bot.send_message(message.from_user.id, 'Сколько отелей вывести?')
	bot.set_state(message.from_user.id, UserInfoState.hotels_count, message.chat.id)



history_requests: list = []
def history_update(command: str, hotels_list: list, message: Message) -> None:
	""""
	Функция добавляет в список, содержащий историю поиска, текущие данные запроса пользователя
	"""
	history_requests.append({message.from_user.id: {'command': command, 'date': datetime.datetime.now(), 'hotels': hotels_list}})


def answer(message: Message, data: dict) -> None:
	""""
	Функция запуска и вывода ответа на запрос
	"""
	api_response = response(data)
	if not api_response:
		bot.send_message(message.from_user.id, 'Ничего не найдено')
		return

	timedelta_date = data['register_date_out'] - data['register_date_out']
	hotels_for_history = []
	for hotel_dict in api_response:
		for key, value in hotel_dict.items():
			bot_answer_string = f"{key} \nАдрес: {value['address']}\nРасстояние до центра: {str(value['distance'])} км.\nЦена за ночь: {str(round(value['price'], 2))} USD. Полная цена за {str(timedelta_date.days + 1)} дней: {str(round((timedelta_date.days + 1) * value['price'], 2))} \n\n"

			hotels_for_history.append(key)
			if data['photo']:
				media = []
				caption = bot_answer_string
				if data['photo_count'] == 1:
					caption = None

				for photo in value['photo'][:data['photo_count']]:
					media.append(InputMediaPhoto(media=photo['image']['url'], caption=caption))

			bot.send_message(message.from_user.id, bot_answer_string)
			if data['photo']:
				bot.send_media_group(chat_id=message.chat.id, media=media)

	history_update(command=data.get('command'), hotels_list=hotels_for_history, message=message)

