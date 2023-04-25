import telebot, requests, json, datetime, os
from telebot.custom_filters import StateFilter
from typing import Any
from dotenv import load_dotenv
from states.bot_states import UserInfoState

class HotelAPI:
	def __init__(self, api_key, api_host):
		self.token = {'X-RapidAPI-Key': api_key, 'X-RapidAPI-Host': api_host}

	def get_hotel_data_by_city(self, city: str) -> json:
		"""
		Get запрос API по ключевому слову city
		"""

		params = {'q': city, 'locale': 'ru_RU'}

		url = f"https://hotels4.p.rapidapi.com/locations/v3/search"

		try:
			response = requests.request("GET", url, headers=self.token, params=params, timeout=15)

			if response.status_code == requests.codes.ok:
				return response.json()

		except Exception:
			return False

	def post_request(
			self,
			id: int,
			sort: str,
			count: int,
			min_price: int,
			max_price: int,
			date_in: datetime,
			date_out: datetime
	):
		"""
		Post запрос API по ID города, полученного из get запроса
		:param id: Идентификатор отеля
		:param sort: Метод сортировки результата
		:param count: Количество выводимой информации
		:param min_price: Минимальная цена для поиска
		:param max_price: Максимальная цена для поиска
		:return: json ответ на запрос
		"""

		url = "https://hotels4.p.rapidapi.com/properties/v2/list"
		try:

			payload = {
				"currency": "USD",
				"eapid": 1,
				"locale": "ru_RU",
				"siteId": 300000001,
				"destination": {"regionId": id},
				"checkInDate": {
					"day": date_in.day(),
					"month": date_in.month(),
					"year": date_in.year(),
				},
				"checkOutDate": {
					"day": date_out.day(),
					"month": date_out.month(),
					"year": date_out.year(),
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

			response = requests.request("POST", url, json=payload, headers=self.token, timeout=15)

			if response.status_code == requests.codes.ok:
				return response.json()
		except Exception:
			return False

	def hotel_details_request(self, id: int) -> json:
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

			response = requests.request("POST", url, json=payload, headers=self.token, timeout=15)
			if response.status_code == requests.codes.ok:
				return response.json()

		except Exception:
			return False


def filter_by_distance(response: list) -> list:
	"""
	Функиция, которая фильтрует список методом sort_method
	:param response: list
	:return: list
	"""
	filtered_list = list(filter(sort_method, response))
	return filtered_list


def sort_method(elem_to_sort: json, distance: int) -> bool:
	"""
	Функция - метод сортировки.
	:param elem_to_sort: list
	:return:
	True, если значение дистанции в json файле меньше или равна заявленной пользователем
	False, если значение дистанции в json файле больше заявленной пользователем
	"""
	if elem_to_sort['destinationInfo']['distanceFromDestination']['value'] <= distance:
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