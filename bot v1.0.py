
import datetime as dt # для расчета дней до опеределенной даты
import re # для обработки регулярных выражений

import numpy as np # для расчета рабочих дней
import telebot # на чем работает сам бот
import logging # прописывать логи
import random # случайная мудрость
import requests # запрос погоды
import os
from config import TOKEN_BOT
from recoginazer import Сonvect # класс для расшифровки сообщений
from Button import dice_kb #Кнопки для функции football
from telebot import types  # types.Message

bot = telebot.TeleBot(TOKEN_BOT, skip_pending=True)
#токен бота + пропуск предыдущих сообщений

log = logging.getLogger() #логи





# доступные команды
Help = """
/help - список команд 
/weather - узнать погоду в городе
/wisdom - добавить мудрость
/football - сыграть в футбол в чате #394
/dr - счетчик дней рождений

Расшифрую голосовуху
Мудрость - поделюсь мудростью с тобой
Да - Гифка
Нет - Стикер

"""

# Приветственная функция
@bot.message_handler(commands=['start'])
def send_welcome(message):
	bot.reply_to(message, "Поприветстуй сенсея, напиши /help")
# Подсказки по командам и умениям
@bot.message_handler(commands=['help'])
def info_from_bot(message: types.Message):
	bot.reply_to(message, Help)


# Расшифровка голосовых сообщений(перевод в текст)
@bot.message_handler(content_types=['voice'])
def get_audio(message: types.Message):
	file_id = message.voice.file_id # Получаем id сообщения
	file_info = bot.get_file(file_id) # извлекаем файл
	downloaded_file = bot.download_file(file_info.file_path) # скачиваем файл
	file_name = str(message.message_id) + '.ogg'
# имя с расширением ogg для конвертации в wav
	name = message.chat.first_name if message.chat.first_name else 'Unicorm_dude' # для отображения логов
	log.info(f'Chat {name} (ID: {message.chat.id}) download file {file_name} ')
# строка лога

	with open(file_name, 'wb') as new_file: # создаем новый файл
		new_file.write(downloaded_file)
	convecter = Сonvect(file_name) # конвертируем с помощью созданного класса
	os.remove(file_name) # удаление первоначального файла с расширением ogg
	message_text = convecter.audio_to_text() # перевод в текст
	del convecter # удаляем файл с расширением wav
	bot.reply_to(message, message_text)


# Добавление "Мудрости" от пользователя в файл, для дальнейшего вывода в чат
@bot.message_handler(commands=['wisdom'])
def add_wisdom(message: types.Message):
	bot.delete_message(message.chat.id, message.id)
	send = bot.send_message(message.from_user.id,
		   'Делись мудростью своей со мной')
	bot.register_next_step_handler(send, new_wisdom) # ожидание ввода сообщения

def new_wisdom(message: types.Message):
#Запись сообщения и преобразование в текст с первой заглавной буквой
	write_wisdom = message.text.capitalize()
# открытие файла с "Мудростями" и распаковка их в лист
	f = open('wisdom.txt', 'r+')
	new_list = []
	for i in f:
		new_list.append(i)
# Проверка наличия введенной "Мудрости" и добавление в файл, или вывод сообщения, что такая уже есть.
	if write_wisdom not in new_list:
		f.write(f'\n{write_wisdom}')

		bot.send_message(message.from_user.id,f'Мудрость хорошая, приму мудрость твою \n \n <em> Твоя мудрость:</em> {write_wisdom}',
							       parse_mode='html')
	else:
		bot.send_message(message.from_user.id,f' <b>Мудрость - {write_wisdom}</b> \n \n Уже знаю \n Есть еще-что нибудь?',
							parse_mode='html')
	f.close() # закрытие файла

# Вывод "Мудрости" в чат
@bot.message_handler(regexp= r'Мудрость')
def wisdom_chioce(message: types.Message):
	wisdom_list = []
	if message.text.count(' ') < 1:  # Реакция только на слово «Мудрость»
		file_wisdom = open('wisdom.txt', 'r')
		for i in file_wisdom:
			wisdom_list.append(i) # Наполнение списка из файла
		file_wisdom.close()
	print(wisdom_list) # Отображение списка для контроля внесенных фраз
	bot.send_message(message.chat.id, random.choice(wisdom_list))


# Получение информации о сообщении(chat, username, id)
@bot.message_handler(commands=['message'])
def message_info(message: types.Message):
	bot.send_message(message.from_user.id, message)

	bot.delete_message(message.chat.id, message.id)


# игра в футбол с помощью эмодзи в чате
@bot.message_handler(commands=['football'])
def only_dice_command(message: types.Message):
	bot.delete_message(message.chat.id, message.id) # Удаление команды из чата
	send = bot.send_message(message.from_user.id,
					'Сколько ударов надо?(выбери на клавиатуре)',
									      reply_markup=dice_kb) # вывод клавиатуры в личный чат
	bot.register_next_step_handler(send, dice)
# Ожидание следующего сообщения для выполнения след. def

def dice(message: types.Message):
	bot.delete_message(message.chat.id, message.id)
	recevid_message = message.text.lower()
	#Обработка исключения если нет username
    try:
	    bot.send_message(chat_id=******************, text=f'Бьет @{message.from_user.username}')
    except TypeError:
	    bot.send_message(chat_id=******************, text=f'Бьет {message.from_user.first_name} {message.from_user.last_name}')
	# отправка эмодзи
	finally:
		if recevid_message == 'три' or recevid_message == 'два':
			if recevid_message == 'три':
				for ball in range(3):
					bot.send_dice(chat_id=******************,
								  	   emoji="⚽")
				bot.send_dice(chat_id=******************,
							  	   emoji="🎲")
			elif recevid_message == 'два':
				for ball in range(2):
					bot.send_dice(chat_id=******************,
								  	   emoji="⚽")
				bot.send_dice(chat_id=******************,
							  	   emoji="🎲")


# Показывает погоду в городе на выбор
@bot.message_handler(commands=['weather'])
def weather_reqest(message: types.Message):
	bot.delete_message(message.chat.id, message.id)
	send = bot.send_message(message.from_user.id,
               'Погоду в каком городе хочешь узнaть?')

	bot.register_next_step_handler(send, weather_info)

def weather_info(message: types.Message):
	city = message.text.capitalize()

	url = f'https://wttr.in/{city}' # сайт с погодой для разработчиков

	weater_parameters = {
		'O': '',
		'T': '',
		'M': '',
		'format': 2
	} # Параметры для вывода информации


	request_headers = {'Accept-Language': 'ru'}
# Язык вывода информации о погоде


	response = requests.get(url, headers=request_headers,
				          params=weater_parameters)
# запрос для вывода с параметрами

	bot.send_message(message.from_user.id, f' Погода в городе {city.capitalize()} - {response.text}')

	bot.delete_message(message.chat.id, message.id)

# Остаток дней до отпуска для Марины
@bot.message_handler(commands=['date', 'work'])
def date(message: types.Message):
	day_x = dt.date(2022, 12, 24)
# Cтатичная дата до которой нужно посчитать дни

	day = dt.date.today()  # Получение актуальной даты
	# Расчет в зависимости от команды
	if message.text == '/date':
		go_away = day_x - day
		bot.send_message(message.chat.id,
						 f'<b>календарных дней</b> <em>до отпуска осталось:</em> \n<b>{go_away.days}</b>',
						 																parse_mode='html')
	else:
		go_away = np.busday_count(day, day_x)  # timedelta для рабочих дней
		bot.send_message(message.chat.id, f' Дней еще работать - <b>{go_away}</b>',parse_mode='html')

# Отсчет дней до дня рождения
@bot.message_handler(commands='dr')
def happy_birthday(message: types.Message):
	bot.delete_message(message.chat.id, message.id)

	bot.send_message(message.from_user.id, '<b>Дней до дня рождения осталось:</b>',parse_mode='html')
	DATABASE = {
		"*******": '2022-01-07',
		"*******": '2022-02-13',
		"*******": '2022-02-20',
		"*******": '2022-04-24',
		"*******": '2022-05-30',
		"*******": '2022-09-01',
		"*******": '2022-10-22',
		"*******": '2022-12-03'
	}
	for name in DATABASE:  # Перебор ключей словаря
		day_x = dt.datetime.strptime(DATABASE[name], '%Y-%m-%d').date()            		# Преобразование значения в дату
		day = dt.date.today()  # Текущий день
		year_now = day.year
	# Текущий год - для проверки, високосный год или нет

		# Проверка -  день рождения в этом году или нет
		if day < day_x:
			tdelta = day_x - day

		elif day > day_x:
			# Получение правильного количества дней в году
			while day > day_x:

				if year_now % 4 != 0 or year_now % 400 != 0:
					day_x = day_x + dt.timedelta(days=365)

				else:  # Високосный год
					day_x = day_x + dt.timedelta(days=366)

			tdelta = day_x - day

		else:  # Если даты совпадают
			bot.send_message(message.from_user.id, 'Cегодня!')
		bot.send_message(message.from_user.id, f'<em>{name}</em> <b>{tdelta.days}</b>',parse_mode='html')

#Функции для админов чата

#Писать от имени бота жирным капслоком
@bot.message_handler(commands=['caps'])
def red_caps(message: types.Message):
	mess = list(message.text.split())
	mess.pop(0)
	mess = ' '.join(mess)
	mess = mess.upper()
	bot.send_message(chat_id= **************, text = f'<b>{mess}</b> '				 						    parse_mode='html')
	bot.delete_message(message.chat.id, message.id)

#Писать сообщение от имени бота через команду
@bot.message_handler(commands=['v'])
def red_caps(message: types.Message):
	mess = list(message.text.split())
	mess.pop(0)
	mess = ' '.join(mess)
	mess = mess.capitalize()
	bot.send_message(chat_id= ***************, text = mess)
	bot.delete_message(message.chat.id, message.id)

#Писать обычные сообщение от имени бота через чат
@bot.message_handler(commands=['chat'])
def rat_voce(message: types.Message):
	bot.delete_message(message.chat.id, message.id)
	send = bot.send_message(message.from_user.id, 'Начнем')
	bot.send_message(message.from_user.id, 'Что ты хочешь чтоб я сказал?')
	bot.register_next_step_handler(send, bot_voice)

def bot_voice(message: types.Message):
	mess = message.text.capitalize()
	bot.send_message(chat_id= *****************, text = mess)

# реакция бота на определенные сообщения в чате
@bot.message_handler(regexp=r'Да')
@bot.message_handler(regexp=r'Нет')
@bot.message_handler(regexp= r'Да[~!@#$%^&*()-_=+."№;:?]+')
@bot.message_handler(regexp= r'Нет[~!@#$%^&*()-_=+."№;:?]+')

def get_answer(message: types.Message):

    yes='CgACAgIAAxkBAAIEoWN02hOt6_BDH_M59N5AQyF4dL4RAAJ4DgACg2WxSWvB91qjxq6CKwQ'

    no='CAACAgIAAxkBAAEGfphje6YT62vnUk72cCeVSRzHXbWzOgACSgADB7vYFPnWGPVMp7GzKwQ'

    answer = message.text.lower()
    match = re.search(pattern = r'[~!@#$%^&*()-_=+,."№;%:?*/]+', string=answer) # Проверка символов в строке
    if match == False:
		answer = answer
    else:
		answer = re.sub('[~!@#$%^&*()-_=+,."№;:?/]+', '', answer)
# удаление символов

	if answer == 'да':
		bot.send_animation(message.chat.id, yes )
	elif answer == 'нет':
		bot.send_sticker(message.chat.id, no )

if __name__ == '__main__':
	log.info('работаю')
	bot.infinity_polling()
# Запрос к серверу telegram, проверка полученных сообщений




