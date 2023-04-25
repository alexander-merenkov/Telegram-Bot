import telebot, requests, json, datetime, os
from typing import Any
from . import telegram_logic


def response(message: telebot.types.Message) -> Any:
	""""
	Основная функция вывода запроса пользователя
	"""
	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		response_for_get_request = get_request(city=data['city'])

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

		response_for_post_request = post_request(id=city_id, sort=sort, count=count, min_price=min_price, max_price=max_price, message=message)

		if response_for_post_request:

			response_properties = get_properties(response_for_post_request)

			if response_properties:

				hotel_list = []
				with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
					if data['command'] == '/bestdeal':
						response_properties = filter_by_distance(response_properties)
						response_properties = sort_by_price(response_properties)
						response_properties = response_properties[:get_hotels_count.count]

				for property_in_request in response_properties:
					hotel_details = hotel_details_request(property_in_request['id'])
					hotel_image_list = get_images(hotel_details)
					if hotel_details:
						hotel_list.append({property_in_request['name']: {'price': property_in_request['price']['lead']['amount'],
								'address': get_address_text(hotel_details),
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


def filter_by_distance(response: list) -> list:
	"""
	Функиция, которая фильтрует список методом sort_method
	:param response: list
	:return: list
	"""
	filtered_list = list(filter(sort_method, response))
	return filtered_list


def sort_method(elem_to_sort: json) -> bool:
	"""
	Функция - метод сортировки.
	:param elem_to_sort: list
	:return:
	True, если значение дистанции в json файле меньше или равна заявленной пользователем
	False, если значение дистанции в json файле больше заявленной пользователем
	"""
	if elem_to_sort['destinationInfo']['distanceFromDestination']['value'] <= get_distance.distance:
		return True
	else:
		return False


def sort_by_price(hotel_list: list) -> list:
	"""
	Сортирует список по значению цены в json файле
	"""
	return sorted(hotel_list, key=lambda hotel: int(hotel['price']['lead']['amount']))


"""Функции, для получения из post запроса по ID"""


def get_data(response: json) -> json:
	"""
	Функция получения 'data' из json файла
	"""
	if response:
		return response.get('data')


def get_property_search(response: json) -> json:
	"""
	Функция получения 'propertySearch' из json файла
	"""
	data = get_data(response)
	if data:
		return data.get('propertySearch')


def get_properties(response: json) -> json:
	"""
	Функция получения 'properties' из json файла
	"""
	data = get_property_search(response)
	if data:
		return data.get('properties')


"""Функции, для получения из post запроса hotel details"""


def get_property_info(response: json) -> json:
	"""
	Функция получения 'propertyInfo' из json файла
	"""
	data = get_data(response)
	if data:
		return data.get('propertyInfo')


def get_summary(response: json) -> json:
	"""
	Функция получения 'propertyInfo' из json файла
	"""
	data = get_property_info(response)
	if data:
		return data.get('summary')


def get_location(response: json) -> json:
	"""
	Функция получения 'location' из json файла
	"""
	data = get_summary(response)
	if data:
		return data.get('location')


def get_address(response: json) -> json:
	"""
	Функция получения 'address' из json файла
	"""
	data = get_location(response)
	if data:
		return data.get('address')


def get_address_text(response: json) -> json:
	"""
	Функция получения 'addressLine' из json файла
	"""
	data = get_address(response)
	if data:
		return data.get('addressLine')


def get_property_gallery(response: json) -> json:
	"""
	Функция получения 'propertyGallery' из json файла
	"""
	data = get_property_info(response)
	if data:
		return data.get('propertyGallery')


def get_images(response: json) -> json:
	"""
	Функция получения 'images' из json файла
	"""
	data = get_property_gallery(response)
	if data:
		return data.get('images')

######################################


@bot.message_handler(content_types=['text'])
def send_welcome(message: telebot.types.Message) -> Any:
	"""
	Функция обработки сообщений из Telegram
	"""
	if message.text == '/start':
		start(message)
	elif message.text == '/hello_world':
		bot.send_message(message.from_user.id, 'Привет, меня зовут Merenkov_DPO_bot, я учебный бот!\nНадеюсь я вам понравлюсь, иначе я не получу диплом')
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

	elif message.text =='/history':
		history(message)

	else:
		bot.reply_to(message, 'Я вас не понимаю(')


@bot.message_handler(func=lambda message: True)
def echo_all(message: telebot.types.Message) -> Any:
	"""
	Функция обработки неизвестных сообщений из Telegram
	"""
	bot.reply_to(message, 'Я не понимаю вас(')


def get_request(city: str) -> json:
	"""
	Get запрос API по ключевому слову city
	"""

	params = {'q': city, 'locale': 'ru_RU'}

	url = f"https://hotels4.p.rapidapi.com/locations/v3/search"

	try:
		response = requests.request("GET", url, headers=token, params=params, timeout=15)

		if response.status_code == requests.codes.ok:
			return response.json()

	except Exception:
		return False


def post_request(id: int, sort: str, count: int, min_price: int, max_price: int, message: telebot.types.Message):
	"""
	Post запрос API по ID города, полученного из get запроса
	:param id: Идентификатор отеля
	:param sort: Метод сортировки результата
	:param count: Количество выводимой информации
	:param min_price: Минимальная цена для поиска
	:param max_price: Максимальная цена для поиска
	:return: json ответ на запрос
	"""
	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		day_in = data['register_date_in'].day
		month_in = data['register_date_in'].month
		year_in = data['register_date_in'].year
		day_out = data['register_date_in'].day
		month_out = data['register_date_in'].month
		year_out = data['register_date_in'].year

	url = "https://hotels4.p.rapidapi.com/properties/v2/list"
	try:

		payload = {
			"currency": "USD",
			"eapid": 1,
			"locale": "ru_RU",
			"siteId": 300000001,
			"destination": {"regionId": id},
			"checkInDate": {
				"day": day_in,
				"month": month_in,
				"year": year_in
			},
			"checkOutDate": {
				"day": day_out,
				"month": month_out,
				"year": year_out
			},
			"rooms": [
				{
					"adults": 1}
			],
			"resultsStartingIndex": 0,
			"resultsSize": count,
			"sort": sort,
			"filters": {"price": {
				"max": max_price,
				"min": min_price
			}}
		}

		response = requests.request("POST", url, json=payload, headers=token, timeout=15)

		if response.status_code == requests.codes.ok:
			return response.json()
	except Exception:
		return False


def hotel_details_request(id: int) -> json:
	"""
	Post запрос API для по ID отеля, для подробной информации о нем
	:param id: Идентификатор отеля
	:return: json ответ на запрос
	"""

	url = "https://hotels4.p.rapidapi.com/properties/v2/detail"
	try:
		payload = {
			"currency": "USD",
			"eapid": 1,
			"locale": "ru_RU",
			"siteId": 300000001,
			"propertyId": id
		}

		response = requests.request("POST", url, json=payload, headers=token, timeout=15)
		if response.status_code == requests.codes.ok:
			return response.json()

	except Exception:
		return False


bot.infinity_polling()