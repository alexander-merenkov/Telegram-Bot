from telebot.custom_filters import StateFilter
from loader import bot


bot.add_custom_filter(StateFilter(bot))

bot.infinity_polling()