from telebot.handler_backends import State, StatesGroup


class UserInfoState(StatesGroup):
    command = State()
    register_date_in = State()
    register_date_out = State()
    city = State()
    hotels_count = State()
    price_values = State()
    distance = State()
    photo = State()
    photo_count = State()
    history = State()
    start = State()