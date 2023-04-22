import telebot, requests, json, datetime

bot = telebot.TeleBot('5708841963:AAGKHWT1WD2M9VfIQj6XMgqEi6pTjhrW8Ao')
# token = {"X-RapidAPI-Key": "bba960687bmsh07b83e8768fc6f4p12c285jsnab9156e7acdc",
# 		"X-RapidAPI-Host": "hotels4.p.rapidapi.com"}

token = {"X-RapidAPI-Key": "8735a00919msh53cca4ab1530e22p14f9c0jsn62e41d6bf842",
	"X-RapidAPI-Host": "hotels4.p.rapidapi.com"}


command_dict = {'/start': 'Запуск бота',
				'/hello_world': 'Бот расскажет о себе',
				'/help': 'Описание доступных команд (вы только что это ввели)',
				'/lowprice': 'Узнать топ самых дешёвых отелей в городе',
				'/guest_rating': 'Узнать топ самых популярных отелей в городе',
				'/bestdeal': 'Узнать топ отелей, наиболее подходящих по цене и расположению от центра ',
				'/history': 'Узнать историю поиска отелей'
				}


def start(message):
	start.history = {}
	bot.send_message(message.from_user.id, f'Привет, {message.from_user.first_name} {message.from_user.last_name}, я учебный бот!')


def register_date_in(message):
	date = date_check(message.text)
	if date:
		register_date_in.date = date
		bot.send_message(message.from_user.id, 'Какая дата выселения? (dd-mm-yyyy)')
		bot.register_next_step_handler(message, register_date_out)

	else:
		bot.send_message(message.from_user.id, 'Неверная дата заселения, повторите пожалуйста')
		return bot.register_next_step_handler(message, register_date_in)


def register_date_out(message):
	date = date_check(message.text)
	if date:
		register_date_out.date = date
		response(message)

	else:
		bot.send_message(message.from_user.id, 'Неверная дата выселения, повторите пожалуйста')
		return bot.register_next_step_handler(message, register_date_out)


def date_check(date_str):
	date_format = '%d-%m-%Y'
	today = datetime.datetime.now()
	try:
		dateObject = datetime.datetime.strptime(date_str, date_format)
		if dateObject.date() >= today.date():
			return dateObject
	except ValueError:
		return False


def get_command(message):
	get_command.command = message.text
	bot.send_message(message.from_user.id, f"Привет, {message.from_user.first_name} {message.from_user.last_name}, в каком городе будем искать?")
	bot.register_next_step_handler(message, get_city)


def get_city(message):
	if message.text.isdigit():
		bot.send_message(message.from_user.id, 'Неверно указан город\nВ каком городе будем искать?')
		return bot.register_next_step_handler(message, get_city)
	get_city.city = message.text
	if get_command.command == '/lowprice' or get_command.command == '/guest_rating':
		bot.send_message(message.from_user.id, 'Сколько отелей вывести?')
		bot.register_next_step_handler(message, get_hotels_count)
	elif get_command.command == '/bestdeal':
		bot.send_message(message.from_user.id, 'Какой диапазон цен? (min-max)')
		bot.register_next_step_handler(message, price_values)


def get_hotels_count(message):
	if not message.text.isdigit():
		bot.send_message(message.from_user.id, 'Неверное количество\nСколько отелей вывести?')
		return bot.register_next_step_handler(message, get_hotels_count)
	get_hotels_count.count = int(message.text)
	bot.send_message(message.from_user.id, 'Вывести фото?')
	bot.register_next_step_handler(message, get_photo)


def price_values(message):
	prices = message.text.split('-')
	if len(prices) == 2:
		if not prices[0].isdigit or not prices[1].isdigit:
			bot.send_message(message.from_user.id, 'Неверный диапазон цен, повторите. (min-max)')
			return bot.register_next_step_handler(message, price_values)
		else:
			price_values.values = prices
			bot.send_message(message.from_user.id, 'Какое расстояние от центра?')
			bot.register_next_step_handler(message, get_distance)
	else:
		bot.send_message(message.from_user.id, 'Неверный диапазон цен, повторите. (min-max)')
		return bot.register_next_step_handler(message, price_values)


def get_distance(message):
	if not message.text.isdigit():
		bot.send_message(message.from_user.id, 'Неверное расстояние\nКакое расстояние от центра?')
		return bot.register_next_step_handler(message, get_distance)
	get_distance.distance = int(message.text)
	bot.send_message(message.from_user.id, 'Сколько отелей вывести?')
	bot.register_next_step_handler(message, get_hotels_count)


def get_photo(message):
	if message.text.lower() == 'да':
		get_photo.photo = True
	elif message.text.lower() == 'нет':
		get_photo.photo = False
	else:
		bot.send_message(message.from_user.id, 'Я так и не понял, да или нет?(')
		return bot.register_next_step_handler(message, get_photo)



	bot.send_message(message.from_user.id, 'Какая дата заселения? (dd-mm-yyyy)')
	bot.register_next_step_handler(message, register_date_in)


def response(message):
	response_for_get_request = get_request(city=get_city.city)
	city_id = None

	if response_for_get_request.get('sr'):
		city_id = response_for_get_request.get('sr')[0].get('gaiaId')

	if city_id:

		if get_command.command == '/lowprice':
			sort = 'PRICE_LOW_TO_HIGH'
		elif get_command.command == '/guest_rating':
			sort = 'REVIEW'
		elif get_command.command == '/bestdeal':
			sort = 'DISTANCE'

		count = get_hotels_count.count
		min_price = 1
		max_price = 999

		if get_command.command == '/bestdeal':
			count = 30
			max_price = price_values.values[1]
			min_price = price_values.values[0]

		response_for_post_request = post_request(id=city_id, sort=sort, count=count, min_price=min_price, max_price=max_price)

		if response_for_post_request:

			response_properties = get_properties(response_for_post_request)

			if response_properties:

				hotel_list = []

				if get_command.command == '/bestdeal':
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


				timedelta_date = register_date_out.date - register_date_in.date

				for hotel_dict in hotel_list:
					for key, value in hotel_dict.items():
							bot_answer_string = f"{key} \nАдрес: {value['address']}\nРасстояние до центра: {str(value['distance'])} км.\nЦена за ночь: {str(round(value['price'], 2))} USD. Полная цена за {str(timedelta_date.days + 1)} дней: {str(round((timedelta_date.days + 1) * value['price'], 2))} \n\n"

							if get_photo.photo:
								media = []
								for photo in value['photo'][:3]:
									media.append(telebot.types.InputMediaPhoto(media=photo['image']['url'], caption=bot_answer_string))

							bot.send_message(message.from_user.id, bot_answer_string)

							if get_photo.photo:
								bot.send_media_group(chat_id=message.chat.id, media=media)
			else:
				bot.send_message(message.from_user.id, 'Ничего не найдено')

		else:
			bot.send_message(message.from_user.id, 'Ничего не найдено')

	else:
		bot.send_message(message.from_user.id, 'Ничего не найдено')


def filter_by_distance(response):
	filtered_list = list(filter(sort_method, response))
	return filtered_list


def sort_method(elem_to_sort):
	if elem_to_sort['destinationInfo']['distanceFromDestination']['value'] <= get_distance.distance:
		return True
	else:
		return False


def sort_by_price(hotel_list):
	return sorted(hotel_list, key=lambda hotel: int(hotel['price']['lead']['amount']))


def get_data(response):
	return response.get('data')


def get_property_search(response):
	data = get_data(response)
	if data:
		return data.get('propertySearch')


def get_properties(response):
	data = get_property_search(response)
	if data:
		return data.get('properties')


## for hotel details
def get_property_info(response):
	data = get_data(response)
	if data:
		return data.get('propertyInfo')


def get_summary(response):
	data = get_property_info(response)
	if data:
		return data.get('summary')


def get_location(response):
	data = get_summary(response)
	if data:
		return data.get('location')

def get_address(response):
	data = get_location(response)
	if data:
		return data.get('address')


def get_address_text(response):
	data = get_address(response)
	if data:
		return data.get('addressLine')


def get_property_gallery(response):
	data = get_property_info(response)
	if data:
		return data.get('propertyGallery')


def get_images(response):
	data = get_property_gallery(response)
	if data:
		return data.get('images')


@bot.message_handler(content_types=['text'])
def send_welcome(message):
	if message.text == '/start':
		start(message)
	elif message.text == '/hello_world':
		bot.send_message(message.from_user.id, 'Привет, меня зовут Merenkov_DPO_bot, я учебный бот!\nНадеюсь я вам понравлюсь, иначе я не получу диплом')
	elif message.text == '/help':
		help_answer = ''
		for key, value in sorted(command_dict.items()):
			help_answer += key + '  ->  ' + value + '\n'
		bot.send_message(message.from_user.id, help_answer)

	elif message.text in ('/lowprice', '/guest_rating', '/bestdeal'):
		get_command(message)

	else:
		bot.reply_to(message, 'Я вас не понимаю(')




@bot.message_handler(func=lambda message: True)
def echo_all(message):
	bot.reply_to(message, 'Я не понимаю вас(')


def get_request(city):

	params = {'q': city, 'locale': 'ru_RU'}

	url = f"https://hotels4.p.rapidapi.com/locations/v3/search"

	try:
		response = requests.request("GET", url, headers=token, params=params, timeout=15)
		if response.status_code == requests.codes.ok:
			return response.json()

	except Exception:
		return False


def post_request(id, sort, count, min_price, max_price):

	url = "https://hotels4.p.rapidapi.com/properties/v2/list"
	try:

		payload = {
			"currency": "USD",
			"eapid": 1,
			"locale": "ru_RU",
			"siteId": 300000001,
			"destination": {"regionId": id},
			"checkInDate": {
				"day": register_date_in.date.day,
				"month": register_date_in.date.month,
				"year": register_date_in.date.year
			},
			"checkOutDate": {
				"day": register_date_out.date.day,
				"month": register_date_out.date.month,
				"year": register_date_out.date.year
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


def hotel_details_request(id):

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