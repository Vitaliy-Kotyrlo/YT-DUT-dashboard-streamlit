# 13. Замовлення корму для тварин
import telebot

bot = telebot.TeleBot('--')

@bot.message_handler(commands=['start'])
def main(message):
    bot.send_message(message.chat.id, message)

@bot.message_handler(commands=['main'])
def main(message):
    bot.send_message(message.chat.id, message)

bot.infinity_polling()
