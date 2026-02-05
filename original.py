import sqlite3
import telebot
import types from telebot

bot = telebot.TeleBot("api")

user_data = {}


@‌bot.message_handler(content_types = ['text'])
def occupy_table(message):
chat_id = message.chat.id
table = message.text

connection = sqlite3.connect("restaurant.db")
cursor = connection.cursor()

cursor.execute("SELECT is_free FROM tables WHERE id = ?", (table,))
result = cursor.fetchone()
if not result:
bot.send_message(chat_id, "Стол занят")

cursor.execute("UPDATE tables SET is_free = 0 WHERE id = ?", (table,))
connection.commit()
connection.close()

bot.send_message(chat_id, "Стол забронірован")


def rest_db():
connection = sqlite3.connect("restaurant.db")
cursor = connection.cursor()



cursor.execute("""CREATE TABLE IF NOT EXISTS users (tg_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)""")
connection.commit()
cursor.execute("""CREATE TABLE IF NOT EXISTS tables (id INTEGER PRIMARY KEY AUTOINCREMENT, is_free INTEGER)""")
connection.commit()
cursor.execute("""CREATE TABLE IF NOT EXISTS orders (user_id INTEGER PRIMARY KEY AUTOINCREMENT, table_id INTEGER, order_text TEXT)""")


@bot.message_handler(commands=["start"])
def add_user(message):

    user_id = message.chat.id
    user_name = message.from_user.username

    db("""
        INSERT INTO users (tg_id, name)
        VALUES (?,?)
        """,(user_id, user_name)
        )

    bot.send_message(user_id,"ti zapisan")

from telebot import types

@bot.message_handler(func=lambda message: message.text == 'Menu/Order')
def start(message):

    menu = {
        'cake' : 40,
        'pizza' : 100,
        'icecreame' : 30,
        'water' : 300
    }

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for key, price in menu.items():
      keyboard.add(
          types.KeyboardButton(f'{key}-{price}')
      )
    keyboard.add(types.KeyboardButton('Exit'))

    bot.send_message(
      message.chat.id,
      'Select an action: ',
      reply_markup=keyboard
    )
import telebot
import random


@bot.message_handler(func=lambda message: message.text == 'Оплатить')
def get_card(message):
    card = message.text.strip()

    if not card.isdigit() or len(card) != 12:
        bot.send_message(
            message.chat.id,
            'Номер карты должен состоять из 12 цифр. Попробуйте ещё раз'
        )
        bot.register_next_step_handler(message, get_card)
        return

    user_data[message.chat.id] = {}
    bot.send_message(message.chat.id, 'Enter a card number: ')
    bot.register_next_step_handler(message, get_cvv)

def get_cvv(message):

    cvv = message.text.strip()

    if not cvv.isdigit() or len(cvv) != 3:
        bot.send_message(
            message.chat.id,
            'CVV должен состоять из 3 цифр. Попробуйте ещё раз'
        )
        bot.register_next_step_handler(message, get_cvv)
        return

    bot.send_message(message.chat.id, 'Enter a cvv number: ')
    bot.register_next_step_handler(message, pay_verif)

def pay_verif(message):
    if random.random() < 0.5:
      bot.send_message(message.chat.id,  "Проверка...Оплата прошла успешно!")
    else:
      bot.send_message(message.chat.id,  "Проверка...Оплата не прошла")

@‌bot.message_handler(commands=['хочу столик'])
def want_table(message):
connection = sqlite3.connect("restaurant.db")
cursor = connection.cursor()
chat_id = message.chat.id



cursor.execute("SELECT id FROM tables WHERE is_free = 1")
tables_av = cursor.fetchall()
if tables_av == 0:
    bot.send_message(chat_id, "Мест нет")
    return
markup = types.InlineKeyboardMarkup()
for i in tables_av:
    table_id = i[0]
    markup.add(types.InlineKeyboardButton(text=f"Стол {table_id}",callback_data=f"table_{table_id}"))

from telebot import types

@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    keyboard.add(
        types.KeyboardButton('Reserve a table'),
        types.KeyboardButton('Menu/Order'),
        types.KeyboardButton('My orders')
    )
    keyboard.add(types.KeyboardButton('Exit'))

    bot.send_message(
        message.chat.id,
        'Select an action: ',
        reply_markup=keyboard
    )

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):

    if message.text == 'Reserve a table':
        bot.send_message(message.chat.id, 'Select an available table')
        reserve(chat_id)

    elif message.text == 'Menu/Order':
        bot.send_message(message.chat.id, 'Our menu')
        menu()

    elif message.text == 'My orders':
        bot.send_message(message.chat.id, 'Your orders')
        orders(chat_id)

    elif message.text == 'Exit':
        bot.send_message(message.chat.id, 'We look forward to your return')

bot.polling()

