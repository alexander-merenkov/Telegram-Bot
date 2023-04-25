import telebot, requests, json, datetime, os
from typing import Any
from states.bot_states import UserInfoState
from project.loader import bot
from project.hotel_api import hotel_api as api
from project.loader import API_HOST
from project.loader import API_KEY


@bot.message_handler(content_types=['text'])
def send_welcome(message: telebot.types.Message) -> Any:
    """
    Функция обработки сообщений из Telegram
    """
    if message.text == '/start':
        start(message)
    elif message.text == '/hello_world':
        bot.send_message(message.from_user.id,
                         'Привет, меня зовут Merenkov_DPO_bot, я учебный бот!\nНадеюсь я вам понравлюсь, иначе я не получу диплом')
    elif message.text == '/help':
        help_answer = ''
        command_dict: dict = {'/start': 'Запуск бота',
                              '/hello_world': 'Бот расскажет о себе',
                              '/help': 'Описание доступных команд (вы только что это ввели)',
                              '/lowprice': 'Узнать топ самых дешёвых отелей в городе',
                              '/guest_rating': 'Узнать топ самых популярных отелей в городе',
                              '/bestdeal': 'Узнать топ отелей, наиболее подходящих по цене и расположению от центра ',
                              '/history': 'Узнать историю поиска отелей'
                              }
        for key, value in sorted(command_dict.items()):
            help_answer += key + '  ->  ' + value + '\n'
        bot.send_message(message.from_user.id, help_answer)

    elif message.text in ('/lowprice', '/guest_rating', '/bestdeal'):
        get_command(message)

    elif message.text == '/history':
        history(message)

    else:
        bot.reply_to(message, 'Я вас не понимаю(')


@bot.message_handler(func=lambda message: True)
def echo_all(message: telebot.types.Message) -> Any:
    """
    Функция обработки неизвестных сообщений из Telegram
    """
    bot.reply_to(message, 'Я не понимаю вас(')


def start(message: telebot.types.Message) -> None:
	""""
	Функция для команды /start
	Приветствует пользователя и обнуляет историю поиска
	"""
	bot.set_state(message.from_user.id, UserInfoState.start, message.chat.id)
	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		if data.get('history'):
			data['history'] = []
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

		bot.send_message(message.from_user.id, 'Пошел искать! Пожалуйста, ожидайте.')
		response(message)

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

def response(message: telebot.types.Message) -> Any:
	""""
	Основная функция вывода запроса пользователя
	"""

	hotel_api = api.HotelAPI(api_key=API_KEY, api_host=API_HOST)

	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		response_for_get_request = hotel_api.get_hotel_data_by_city(city=data['city'])

	city_id = None
	if response_for_get_request:
		city_id = response_for_get_request.get('sr')
		if city_id and len(city_id) > 0:
			city_id = response_for_get_request.get('sr')[0].get('gaiaId')

	if city_id:
		with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
			if data['command'] == '/lowprice':
				sort = 'PRICE_LOW_TO_HIGH'
			elif data['command'] == '/guest_rating':
				sort = 'REVIEW'
			elif data['command'] == '/bestdeal':
				sort = 'DISTANCE'

			count = data['hotels_count']
			min_price = 1
			max_price = 999
			hotels_for_history = []

			if data['command'] == '/bestdeal':
				count = 30
				max_price = data['price_values'][1]
				min_price = data['price_values'][0]

			date_in = data['register_date_in']
			date_out = data['register_date_out']

		response_for_post_request = hotel_api.post_request(id=city_id, sort=sort, count=count, min_price=min_price, max_price=max_price, date_in=date_in, date_out=date_out)

		if response_for_post_request:

			response_properties = api.get_properties(response_for_post_request)

			if response_properties:

				hotel_list = []
				with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
					if data['command'] == '/bestdeal':
						response_properties = api.filter_by_distance(response=response_properties, distance=data['distance'])
						response_properties = api.sort_by_price(response_properties)
						response_properties = response_properties[:data['hotels_count']]

				for property_in_request in response_properties:
					hotel_details = api.hotel_details_request(property_in_request['id'])
					hotel_image_list = api.get_images(hotel_details)
					if hotel_details:
						hotel_list.append({property_in_request['name']: {'price': property_in_request['price']['lead']['amount'],
								'address': api.get_address_text(hotel_details),
								'distance': property_in_request['destinationInfo']['distanceFromDestination']['value'],
								'id': property_in_request['id'],
								'photo': hotel_image_list}})

						hotels_for_history.append(property_in_request['name'])

				with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
					timedelta_date = data['register_date_out'] - data['register_date_out']

				for hotel_dict in hotel_list:
					for key, value in hotel_dict.items():
							bot_answer_string = f"{key} \nАдрес: {value['address']}\nРасстояние до центра: {str(value['distance'])} км.\nЦена за ночь: {str(round(value['price'], 2))} USD. Полная цена за {str(timedelta_date.days + 1)} дней: {str(round((timedelta_date.days + 1) * value['price'], 2))} \n\n"
							with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
								if data['photo']:
									media = []
									caption = bot_answer_string
									if data['photo_count'] == 1:
										caption = None

									for photo in value['photo'][:data['photo_count']]:
										media.append(telebot.types.InputMediaPhoto(media=photo['image']['url'], caption=caption))

							bot.send_message(message.from_user.id, bot_answer_string)
							with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
								if data['photo']:
									bot.send_media_group(chat_id=message.chat.id, media=media)

				with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
					if data.get('history'):
						data['history'].append({'command': data['command'], 'date': datetime.datetime.now(), 'hotels': hotels_for_history})
					else:
						data['history'] = [{'command': data['command'], 'date': datetime.datetime.now(), 'hotels': hotels_for_history}]

			else:
				bot.send_message(message.from_user.id, 'Ничего не найдено')

		else:
			bot.send_message(message.from_user.id, 'Ничего не найдено')

	else:
		bot.send_message(message.from_user.id, 'Ничего не найдено')