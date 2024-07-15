from telethon.sync import TelegramClient  # Импортируем необходимые библиотеки
from telethon.tl.functions.messages import GetHistoryRequest
import telebot
from telebot import types
import asyncio
from datetime import datetime
from datetime import date
import json

# Открываем файл config.json и загружаем данные
f = open('config.json')
config = json.load(f)

# Инициализируем переменные для api_id, api_hash и token
api_id = config["api_id"]
api_hash = config["api_hash"]
token = config["bot_token"]
user = {}
bot = telebot.TeleBot(token)


# Функция для подсчета количества сообщений с ключевым словом в канале за определенное время
async def test(c, d, w, id):
    try:
        async with TelegramClient('session', api_id, api_hash,
                                  system_version='4.16.30-vxCUSTOM') as client:  # Подключаемся к TelegramClient
            channel_username = c
            keyword = w
            date = d
            channel_entity = await client.get_entity(channel_username)
            messages = await client(GetHistoryRequest(
                peer=channel_entity,
                limit=100000000,  # максимальное количество сообщений для получения
                offset_date=0,
                offset_id=0,
                max_id=0,
                min_id=0,
                add_offset=0,
                hash=0,
            ))
            col = 0

            for message in messages.messages:  # Перебираем сообщения и проверяем наличие ключевого слова и соответствие дате
                if keyword in str(message.message):
                    d = str(message.date).split(" ")[0]

                    current_date = datetime.now().strftime('%Y-%m-%d')
                    start_date = datetime.strptime(date, '%Y-%m-%d')
                    end_date = datetime.strptime(current_date, '%Y-%m-%d')

                    date_to_check = datetime.strptime(d, '%Y-%m-%d')
                    if start_date <= date_to_check <= end_date:
                        print(message.message)
                        col += 1
            bot.send_message(id,
                             f"С ключевым словом '{keyword}' в канале '{channel_username}' найдено {col} совпадений")  # Отправляем результат количества найденных сообщений пользователю
    except ValueError:
        bot.send_message(id, f"Произошла ошибка, проверьте корректность данных. ")


@bot.message_handler(commands=['start'])  # Обработчик команды /start
def start_message(message):
    # Отправляем приветственное сообщение и создаем клавиатуру для пользователя
    bot.send_message(message.chat.id,
                     "Здравствуйте, я вам помогу подсчитать количество сообщений за определённое время с ключевыми словами")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    bt1 = types.KeyboardButton("подсчитать количество сообщений")
    markup.add(bt1)
    bot.send_message(message.chat.id,
                     'Нажмите кнопку подсчитать количество сообщений',
                     reply_markup=markup)


@bot.message_handler(content_types=["text"])  # Обработчик текстовых сообщений
def handle_text(message):
    try:
        if message.text.strip() == 'подсчитать количество сообщений':
            # При запросе "подсчитать количество сообщений" запрашиваем у пользователя название канала
            msg = bot.send_message(message.from_user.id, 'Введите название канала в таком виде @ChannelMY: ',
                                   reply_markup=types.ReplyKeyboardRemove(), parse_mode='Markdown')
            bot.register_next_step_handler(msg, channel)
        if message.text.strip() == 'Всё верно':
            # При подтверждении правильности запроса отправляем результат подсчета сообщений
            bot.send_message(message.chat.id, "Ожидайте...")
            try:
                asyncio.run(test(user[message.from_user.id]["channel"], user[message.from_user.id]["date"], user[message.from_user.id]["world"], int(message.from_user.id)))
            except ValueError:
                bot.send_message(message.from_user.id, f"Произошла ошибка, проверьте корректность данных. ")

        elif message.text.strip() == 'Переписать запрос':
            # При запросе на переписывание запроса создаем клавиатуру для пользователя
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            bt1 = types.KeyboardButton("подсчитать количество сообщений")
            markup.add(bt1)
            bot.send_message(message.chat.id,
                             'Нажмите кнопку подсчитать количество сообщений',
                             reply_markup=markup)
    except ValueError:
        bot.send_message(message.from_user.id, f"Произошла ошибка, проверьте корректность данных. ")


# Функция для получения названия канала от пользователя
def channel(message):
    user[message.from_user.id] = {}
    user[message.from_user.id]["channel"] = str(
        message.text)  # Сохраняем название канала в словаре user и запрашиваем у пользователя дату
    current_date = datetime.now().strftime('%Y-%m-%d')
    msg = bot.send_message(message.from_user.id,
                           f'Введите дату до которой я буду проверять сообщения ГОД-МЕСЯЦ-ДЕНЬ, пример: {current_date}')
    bot.register_next_step_handler(msg, date)  # Переходим к следующему шагу для получения даты


# Функция для получения даты от пользователя
def date(message):
    user[message.from_user.id]["date"] = str(
        message.text)  # Сохраняем дату в словаре user и запрашиваем у пользователя ключевое слово
    msg = bot.send_message(message.from_user.id,
                           f'Введите ключевое слово по которому будет осуществляться поиск')
    bot.register_next_step_handler(msg, world)  # Переходим к следующему шагу для получения ключевого слова


# Функция для получения ключевого слова от пользователя
def world(message):
    user[message.from_user.id]["world"] = str(
        message.text)  # Сохраняем ключевое слово в словаре user и отправляем пользователю сформированный запрос
    current_date = datetime.now().strftime('%Y-%m-%d')
    bot.send_message(message.chat.id,
                     f"Канал: {user[message.from_user.id]['channel']} \n\nДиапозон дат с {user[message.from_user.id]['date']} по {current_date} \n\nКлючевое слово {user[message.from_user.id]['world']}")
    bt1 = types.KeyboardButton("Всё верно")  # Пользователь может подтвердить запрос
    bt2 = types.KeyboardButton("Переписать запрос")  # или запросить переписать
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(bt1)
    markup.add(bt2)
    bot.send_message(message.chat.id,
                     "Запрос сформирован проверти корректность, если всё верно нажмите 'Всё верно', если нет нажмите 'Переписать запрос'",
                     reply_markup=markup)


bot.polling(none_stop=True)  # Запуск бота в режиме ожидания сообщений от пользователей