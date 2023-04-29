from config_data.config import X_RapidAPI_Key, X_RapidAPI_Host
import requests
import json
import datetime
from typing import Any


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
			user_count: int,
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
					"day": date_in.day,
					"month": date_in.month,
					"year": date_in.year,
				},
				"checkOutDate": {
					"day": date_out.day,
					"month": date_out.month,
					"year": date_out.year,
				},
				"rooms": [
					{
						"adults": 1}
				],
				"resultsStartingIndex": 0,
				"resultsSize": user_count,
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


def filter_by_distance(response: list, distance: int) -> list:
	"""
	Функиция, которая фильтрует список методом sort_method
	:param response: list
	:return: list
	"""
	filtered_list = list(filter(lambda seq: sort_method(seq, distance), response))
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


def response(data: dict) -> Any:
	""""
	Основная функция вывода запроса пользователя
	"""
	hotel_api = HotelAPI(api_key=X_RapidAPI_Key, api_host=X_RapidAPI_Host)

	response_for_get_request = hotel_api.get_hotel_data_by_city(city=data['city'])

	city_id = None
	if response_for_get_request:
		city_id = response_for_get_request.get('sr')
		if city_id and len(city_id) > 0:
			city_id = response_for_get_request.get('sr')[0].get('gaiaId')

	if city_id:
		if data['command'] == '/lowprice':
			sort = 'PRICE_LOW_TO_HIGH'
		elif data['command'] == '/guest_rating':
			sort = 'REVIEW'
		elif data['command'] == '/bestdeal':
			sort = 'DISTANCE'

		user_count = data['hotels_count']
		min_price = 1
		max_price = 999

		if data['command'] == '/bestdeal':
			user_count = 30
			max_price = data['price_values'][1]
			min_price = data['price_values'][0]

		date_in = data['register_date_in']
		date_out = data['register_date_out']

		response_for_post_request = hotel_api.post_request(id=city_id, sort=sort, user_count=user_count, min_price=min_price, max_price=max_price, date_in=date_in, date_out=date_out)

		if response_for_post_request:

			response_properties = get_properties(response_for_post_request)

			if response_properties:

				hotel_data = []

				if data['command'] == '/bestdeal':
					response_properties = filter_by_distance(response=response_properties, distance=data['distance'])
					response_properties = sort_by_price(response_properties)
					response_properties = response_properties[:data['hotels_count']]

				for property_in_request in response_properties:
					hotel_details = hotel_api.hotel_details_request(property_in_request['id'])
					hotel_image_list = get_images(hotel_details)
					if hotel_details:
						hotel_data.append({property_in_request['name']: {'price': property_in_request['price']['lead']['amount'],
								'address': get_address_text(hotel_details),
								'distance': property_in_request['destinationInfo']['distanceFromDestination']['value'],
								'id': property_in_request['id'],
								'photo': hotel_image_list}})

				return hotel_data
			else:
				return False
		else:
			return False
	else:
		return False
