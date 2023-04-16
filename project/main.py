import telebot

bot = telebot.TeleBot('5708841963:AAGKHWT1WD2M9VfIQj6XMgqEi6pTjhrW8Ao')
command_dict = {'/start': 'Запуск бота',
				'/hello_world': 'Бот расскажет о себе',
				'/help': 'Описание доступных команд (вы только что это ввели)',
				'/lowprice': 'Узнать топ самых дешёвых отелей в городе',
				'/highprice': 'Узнать топ самых дорогих отелей в городе',
				'/bestdeal': 'Узнать топ отелей, наиболее подходящих по цене и расположению от центра ',
				'/history': 'Узнать историю поиска отелей'
				}
command = ''
city = ''
count = ''
Photo = False


def get_price(message):
	get_price.command = message.text
	bot.send_message(message.from_user.id, f"Привет, {message.from_user.first_name} {message.from_user.last_name}, в каком городе будем искать?")
	bot.register_next_step_handler(message, get_city)


def get_city(message):
	if message.text.isdigit():
		bot.send_message(message.from_user.id, 'Неверно указан город\nВ каком городе будем искать?')
		return bot.register_next_step_handler(message, get_city)
	get_city.city = message.text
	if get_price.command == '/lowprice' or get_price.command == '/highprice':
		bot.send_message(message.from_user.id, 'Сколько отелей вывести?')
		bot.register_next_step_handler(message, get_hotels_count)
	else:
		bot.send_message(message.from_user.id, 'Какой диапазон цен?')
		bot.register_next_step_handler(message, price_values)


def get_hotels_count(message):
	if not message.text.isdigit():
		bot.send_message(message.from_user.id, 'Неверное количество\nСколько отелей вывести?')
		return bot.register_next_step_handler(message, get_hotels_count)
	get_hotels_count.count = message.text
	bot.send_message(message.from_user.id, 'Вывести фото?')
	bot.register_next_step_handler(message, get_photo)


def get_photo(message):
	if message.text.lower() == 'да':
		get_photo.photo = True
	elif message.text.lower() == 'нет':
		get_photo.photo = False
	else:
		bot.send_message(message.from_user.id, 'Я так и не понял, да или нет?(')
		return bot.register_next_step_handler(message, get_photo)
	bot.send_message(message.from_user.id, f'{get_city.city} {get_hotels_count.count} {get_photo.photo} ')


def price_values(message):
	price_values.values = message.text
	bot.send_message(message.from_user.id, 'Какое расстояние от центра?')
	bot.register_next_step_handler(message, get_distance)


def get_distance(message):
	if not message.text.isdigit():
		bot.send_message(message.from_user.id, 'Неверное расстояние\nКакое расстояние от центра?')
		return bot.register_next_step_handler(message, get_distance)
	get_distance.distance = message.text
	bot.send_message(message.from_user.id, 'Сколько отелей вывести?')
	bot.register_next_step_handler(message, get_hotels_count)

@bot.message_handler(content_types=['text'])
def send_welcome(message):
	if message.text == '/start':
		bot.send_message(message.from_user.id, 'Учебный бот запущен!')
	elif message.text == '/hello_world':
		bot.send_message(message.from_user.id, 'Привет, меня зовут Merenkov_DPO_bot, я учебный бот!\nНадеюсь я вам понравлюсь, иначе я не получу диплом')
	elif message.text == '/help':
		help_answer = ''
		for key, value in sorted(command_dict.items()):
			help_answer += key + '  ->  ' + value + '\n'
		bot.send_message(message.from_user.id, help_answer)

	elif message.text in ('/lowprice', '/highprice', '/bestdeal'):
		get_price(message)

	else:
		bot.reply_to(message, 'Я вас не понимаю(')








@bot.message_handler(func=lambda message: True)
def echo_all(message):
	bot.reply_to(message, 'Я не понимаю вас(')


bot.infinity_polling()