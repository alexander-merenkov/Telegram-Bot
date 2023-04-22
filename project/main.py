import telebot, requests, json, datetime

bot = telebot.TeleBot('5708841963:AAGKHWT1WD2M9VfIQj6XMgqEi6pTjhrW8Ao')
token = {"X-RapidAPI-Key": "bba960687bmsh07b83e8768fc6f4p12c285jsnab9156e7acdc",
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
	get_distance.distance = message.text
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
	answer_for_get_request = get_request(city=get_city.city)
	bot_answer_string = ''

	if check_request(answer_for_get_request):

		city_id = answer_for_get_request['sr'][0]['gaiaId']

		if get_command.command == '/lowprice':
			sort = 'PRICE_LOW_TO_HIGH'
		elif get_command.command == '/guest_rating':
			sort = 'REVIEW'
		elif get_command.command == '/bestdeal':
			sort = 'DISTANCE'


		answer_for_post_request = post_request(id=city_id, sort=sort)

		if answer_for_post_request:

			answer_properties = get_properties(answer_for_post_request)

			hotel_list = []
			if get_command.command in ('/lowprice', '/guest_rating'):
				answer_properties = answer_properties[:get_hotels_count.count]

			elif get_command.command == '/bestdeal':
				answer_properties = sort_by_distance(answer_properties)

			for property_in_request in answer_properties:
				hotel_list.append({property_in_request['name']: {'price': property_in_request['price']['lead']['amount'],
						 'id': property_in_request['id']}})


			timedelta_date = register_date_out.date - register_date_in.date

			for hotel_dict in hotel_list:
				for key, value in hotel_dict.items():
						bot_answer_string += key + '. Цена за ночь: ' + str(round(value['price'], 2)) + ' USD. Полная цена за ' + str(timedelta_date.days) + ' дней: ' + str(round((timedelta_date.days + 1) * value['price'], 2)) + '\n'

	else:
		bot_answer_string = 'Ничего не найдено'
	bot.send_message(message.from_user.id, bot_answer_string)


def sort_by_distance(response):
	return filter(sort_method, response)


def sort_method(list_to_sort):
	for i_elem in list_to_sort:
		for key, value in i_elem.items():
			if value['destinationInfo']['distanceFromDestination']['value'] > get_distance.distance:
				return True
			else:
				return False




# def sort_by_price(hotel_list):
	# for hotel in hotel_list:



def check_request(answer):

	if answer['sr'] == []:
		return False
	else:
		return True


def get_data(response):
	if response.get('data'):
		data = response['data']
		return data


def get_property_search(response):
	data = get_data(response)
	if data.get('propertySearch'):
		return data['propertySearch']


def get_properties(response):
	data = get_property_search(response)
	if data.get('properties'):
		return data['properties']


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

	except:
		pass


def post_request(id, sort):

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
			"resultsSize": 200,
			"sort": sort,
			"filters": {'availableFilter': 'SHOW_AVAILABLE_ONLY'}
		}
		headers = token

		response = requests.request("POST", url, json=payload, headers=headers, timeout=15)
		if response.status_code == requests.codes.ok:
			return response.json()
	except:
		pass




bot.infinity_polling()