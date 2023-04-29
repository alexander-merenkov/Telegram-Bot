from telebot.types import Message
from loader import bot
from config_data.config import DEFAULT_COMMANDS


@bot.message_handler(commands=["help"])
def help_func(message: Message) -> None:
    """"
    Функция для команды /help
    """
    bot.set_state(message.from_user.id, None, message.chat.id)
    bot_string = ''
    for command, message_text in DEFAULT_COMMANDS:
        bot_string += f'/{command} - {message_text}\n'

    bot.send_message(message.from_user.id, bot_string)