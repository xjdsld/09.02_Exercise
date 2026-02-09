import sqlite3
import telebot
from telebot import types
import random

bot = telebot.TeleBot("")

user_data = {}

@bot.message_handler(content_types=['text'])
def occupy_table(message):
    chat_id = message.chat.id
    table = message.text

    connection = sqlite3.connect("restaurant.db")
    cursor = connection.cursor()

    cursor.execute("SELECT is_free FROM tables WHERE id = ?", (table,))
    result = cursor.fetchone()

    if not result:
        bot.send_message(chat_id, "Стол занят")
        connection.close()
        return

    cursor.execute("UPDATE tables SET is_free = 0 WHERE id = ?", (table,))
    connection.commit()
    connection.close()

    bot.send_message(chat_id, "Стол забронірован")

def rest_db():
    connection = sqlite3.connect("restaurant.db")
    cursor = connection.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS users (tg_id INTEGER PRIMARY KEY, name TEXT)""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS tables (id INTEGER PRIMARY KEY AUTOINCREMENT, is_free INTEGER)""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS orders (user_id INTEGER, table_id INTEGER, order_text TEXT)""")

    connection.commit()

rest_db()

@bot.message_handler(commands=["start"])
def add_user(message):
    user_id = message.chat.id
    user_name = message.from_user.username

    connection = sqlite3.connect("restaurant.db")
    cursor = connection.cursor()

    cursor.execute("INSERT OR IGNORE INTO users (tg_id, name) VALUES (?, ?)", (user_id, user_name))

    connection.commit()

    bot.send_message(user_id, "ti zapisan")

@bot.message_handler(func=lambda message: message.text == 'Menu/Order')
def start_menu(message):

    menu = {
        'cake': 40,
        'pizza': 100,
        'icecreame': 30,
        'water': 300
    }

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for key, price in menu.items():
        keyboard.add(types.KeyboardButton(f'{key}-{price}'))

    keyboard.add(types.KeyboardButton('Exit'))

    bot.send_message(
        message.chat.id,
        'Select an action:',
        reply_markup=keyboard
    )

@bot.message_handler(func=lambda message: message.text == 'Оплатить')
def get_card(message):
    bot.send_message(message.chat.id, 'Enter a card number:')
    bot.register_next_step_handler(message, check_card)

def check_card(message):
    card = message.text.strip()

    if not card.isdigit() or len(card) != 12:
        bot.send_message(
            message.chat.id,
            'Номер карты должен состоять из 12 цифр. Попробуйте ещё раз'
        )
        bot.register_next_step_handler(message, check_card)
        return

    bot.send_message(message.chat.id, 'Enter a cvv number:')
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

    pay_verif(message)

def pay_verif(message):
    if random.random() < 0.5:
        bot.send_message(message.chat.id, "Проверка...Оплата прошла успешно!")
    else:
        bot.send_message(message.chat.id, "Проверка...Оплата не прошла")

@bot.message_handler(commands=['хочу столик'])
def want_table(message):
    connection = sqlite3.connect("restaurant.db")
    cursor = connection.cursor()
    chat_id = message.chat.id

    cursor.execute("SELECT id FROM tables WHERE is_free = 1")
    tables_av = cursor.fetchall()

    if not tables_av:
        bot.send_message(chat_id, "Мест нет")
        connection.close()
        return

    markup = types.InlineKeyboardMarkup()
    for i in tables_av:
        table_id = i[0]
        markup.add(types.InlineKeyboardButton(text=f"Стол {table_id}", callback_data=f"table_{table_id}"))
    bot.send_message(chat_id, "Выберите стол:", reply_markup=markup)

@bot.message_handler(commands=['start_menu'])
def main_menu(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    keyboard.add(
        types.KeyboardButton('Reserve a table'),
        types.KeyboardButton('Menu/Order'),
        types.KeyboardButton('My orders')
    )
    keyboard.add(types.KeyboardButton('Exit'))

    bot.send_message(
        message.chat.id,
        'Select an action:',
        reply_markup=keyboard
    )

@bot.message_handler(commands=['add_table'])
def add_table(message):
    chat_id = message.chat.id

    connection = sqlite3.connect("restaurant.db")
    cursor = connection.cursor()

    cursor.execute("INSERT INTO tables (is_free) VALUES (1)")

    cursor.execute("SELECT COUNT(*) FROM tables")
    total_tables = cursor.fetchone()[0]

    connection.commit()
    bot.send_message(chat_id, f"Стол добавлен. Всего: {total_tables}")

bot.polling()
