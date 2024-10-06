# 13. Замовлення корму для тварин
import telebot

bot = telebot.TeleBot('8144619073:AAFwHqP_4mDDvcX0WUhptDjEJ7b1cACAIz4')

@bot.message_handler(commands=['start'])
def main(message):
    bot.send_message(message.chat.id, message)

@bot.message_handler(commands=['main'])
def main(message):
    bot.send_message(message.chat.id, message)

bot.infinity_polling()
