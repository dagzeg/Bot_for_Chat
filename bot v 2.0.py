import datetime as dt  # для расчета дней до опеределенной даты
import re  # для обработки регулярных выражений
import calendar
import time

import numpy as np  # для расчета рабочих дней
import telebot  # на чем работает сам бот
import logging  # прописывать логи
import random  # случайная мудрость
import requests  # запрос погоды
import os
import threading

from telebot.types import ReplyKeyboardRemove
from config import TOKEN_BOT, host, user, password, db_name
from recoginazer import Сonvect  # класс для расшифровки сообщений
from Button import dice_kb, kb # Кнопки для функции football
from telebot import types  # types.Message
from parsers import pars_date_tour, pars_rfpl_tabl

bot = telebot.TeleBot(TOKEN_BOT, skip_pending=True)  # токен бота + пропуск предыдущих сообщений

log = logging.getLogger()  # логи

# доступные команды

Help = """
/help - список команд 
/weather - узнать погоду в городе
/wisdom - добавить мудрость
/football - сыграть в футбол в чате #394
/dr - счетчик дней рождений
/rfpl - Расписание на ближайший тур РФПЛ и ссылка на турнирную таблицу
/who - фирменный опрос
/chat - отправить от имени бота свое сообщение

Расшифрую голосовуху
Мудрость - поделюсь мудростью с тобой
Да - Гифка
Нет - Стикер

@isremember_Bot - Бот - напоминалка и таймер

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
    file_id = message.voice.file_id  # Получаем id сообщения
    file_info = bot.get_file(file_id)  # извлекаем файл
    downloaded_file = bot.download_file(file_info.file_path)  # скачиваем файл
    file_name = str(message.message_id) + '.ogg'  # имя с расширением ogg для конвертации в wav
    name = message.chat.first_name if message.chat.first_name else 'Unicorm_dude'  # для логов
    log.info(f'Chat {name} (ID: {message.chat.id}) download file {file_name} ')  # строка лога

    with open(file_name, 'wb') as new_file:  # создаем новый файл
        new_file.write(downloaded_file)
    convecter = Сonvect(file_name)  # конвертируем с помощью созданного класса
    os.remove(file_name)  # удаление первоначального файла с расширением ogg
    message_text = convecter.audio_to_text()  # перевод в текст
    del convecter  # удаляем файл с расширением wav
    bot.reply_to(message, message_text)


# Добавление "Мудрости" от пользователя в файл, для дальнейшего вывода в чат
@bot.message_handler(commands=['wisdom'])
def add_wisdom(message: types.Message):
    bot.delete_message(message.chat.id, message.id)
    send = bot.send_message(message.from_user.id, 'Делись мудростью своей со мной')
    bot.register_next_step_handler(send, new_wisdom)  # ожидание ввода сообщения


def new_wisdom(message: types.Message):
    write_wisdom = message.text.capitalize()  # Запись сообщения и преобразование в текст с первой заглавной буквой

    with open('wisdom.txt', 'r+') as f:  # открытие файла с "Мудростями" и распаковка их в лист
        new_list = [i for i in f if len(i) != 0]

        # Проверка наличия введенной "Мудрости" и добавление в файл, или вывод сообщения, что такая уже есть.
        if write_wisdom not in new_list:
            f.write(f'\n{write_wisdom}')
            wisdom_list.append(write_wisdom)
            bot.send_message(message.from_user.id,
                             f'Мудрость хорошая, приму мудрость твою \n \n <em> Твоя мудрость:</em> {write_wisdom}',
                             parse_mode='html')
        else:
            bot.send_message(message.from_user.id,
                             f' <b>Мудрость - {write_wisdom}</b> \n \n Уже знаю \n Есть еще-что нибудь?',
                             parse_mode='html')


# Вывод "Мудрости" в чат
@bot.message_handler(regexp=r'Мудрость')
def wisdom_choice(message: types.Message):
    if message.text.count(' ') < 1:
        try:
            bot.send_message(message.chat.id, random.choice(wisdom_list))
        except:
            bot.send_message(message.chat.id, random.choice(wisdom_list))

# Получение информации о сообщении(chat, username, id)
@bot.message_handler(commands=['message'])
def message_info(message: types.Message):
    bot.send_message(message.from_user.id, message)
    bot.delete_message(message.chat.id, message.id)


# игра в футбол с помощью эмодзи в чате
@bot.message_handler(commands=['football'])
def football(message: types.Message):
    bot.delete_message(message.chat.id, message.id)  # Удаление сообщения с командой
    send = bot.send_message(message.from_user.id,
                            'Сколько ударов надо?(выбери на клавиатуре)',
                            reply_markup=dice_kb)  # вывод клавиатуры в личный чат
    bot.register_next_step_handler(send, dice)  # Ожидание следующего сообщения для выполнения след. def


def dice(message: types.Message):
    recevid_message = message.text.lower()
    if recevid_message == 'Три' or recevid_message == 'Два':
        bot.delete_message(message.chat.id, message.chat.id)
        # Обработка исключения если нет username
        try:
            bot.send_message(chat_id=***********, text=f'Бьет @{message.from_user.username}')
        except TypeError:
            bot.send_message(chat_id=***********,
                             text=f'Бьет {message.from_user.first_name} {message.from_user.last_name}')
        # отправка эмодзи
        finally:
            if recevid_message == 'три':
                for ball in range(3):
                    bot.send_dice(chat_id=***********,
                                  emoji="⚽")
                bot.send_dice(chat_id=-***********,
                              emoji="🎲")
            elif recevid_message == 'два':
                for ball in range(2):
                    bot.send_dice(chat_id=***********,
                                  emoji="⚽")
                bot.send_dice(chat_id=***********,
                              emoji="🎲")


# Показывает погоду в городе на выбор
@bot.message_handler(commands=['weather'])
def weather_reqest(message: types.Message):
    bot.delete_message(message.chat.id, message.id)
    send = bot.send_message(message.from_user.id, f' Погоду в каком городе хочешь узнaть? \n\n'
                                                  f' Если нет нужного города, напиши в чате', reply_markup=kb)
    bot.register_next_step_handler(send, weather_info)


def weather_info(message: types.Message):
    if message.text == 'Москва':
        city = 'Москва'
    elif message.text == 'Cанкт-Петербург':
        city = 'Cанкт-Петербург'
    elif message.text == 'Тбилиси':
        city = 'Тбилиси'
    elif message.text == 'Батуми':
        city = 'Батуми'
    elif message.text == 'Ташкент':
        city = 'Ташкент'
    elif message.text == 'Ереван':
        city = 'Ереван'
    else:
        city = message.text.capitalize()

    url = f'https://wttr.in/{city}'  # сайт с погодой для разработчиков

    weater_parameters = {
        'O': '',
        'T': '',
        'M': '',
        'format': 2
    }  # Параметры для вывода информации

    request_headers = {'Accept-Language': 'ru'}  # Язык вывода информации о погоде

    response = requests.get(url, headers=request_headers,
                                params=weater_parameters)  # запрос для вывода с параметрами

    ikb = types.InlineKeyboardMarkup(row_width=1)
    ikb1 = types.InlineKeyboardButton(text='Сайт', url=f'https://wttr.in/{city}')
    ikb.add(ikb1)

    bot.send_message(message.from_user.id, f'Погода в городе {city} - {response.text}', reply_markup=ReplyKeyboardRemove())
    bot.send_message(message.from_user.id, '<b>Можешь проверить, просто нажми на кнопку ниже.</b>', parse_mode='html',
                                                                                                    reply_markup=ikb)
    bot.delete_message(message.chat.id, message.id)


# Остаток дней до отпуска 
@bot.message_handler(commands=['date', 'work'])
def date(message: types.Message):
    day_x = dt.date(2023, 3, 27)  # cтатичная дата до которой нужно посчитать дни
    holiday = [dt.date(2023, 2, 23), dt.date(2023, 2, 24), dt.date(2023, 2, 25), dt.date(2023, 3, 8)]
    day = dt.date.today()  # Получение актуальной даты
    # Вывод в зависимости от команды
    if message.text == '/date':
        go_away = day_x - day
        bot.send_message(message.chat.id,
                         f'<b>календарных дней</b> <em>до отпуска осталось:</em> \n<b>{go_away.days}</b>',
                         parse_mode='html')
    else:
        go_away = np.busday_count(day, day_x, holidays=holiday)  # timedelta для рабочих дней
        bot.send_message(message.chat.id, f' Дней еще работать  -  <b>{go_away}</b>',
                         parse_mode='html')


# Отсчет дней до дня рождения
@bot.message_handler(commands=['dr'])
def happy_birthday(message: types.Message):
    bot.delete_message(message.chat.id, message.id)

    DATABASE = {
        "***********,": '2022-01-07',
        "***********,": '2022-02-13',
        "***********,": '2022-02-20',
        "***********,": '2022-04-24',
        "***********,": '2022-05-30',
        "***********,": '2022-09-01',
        "***********,": '2022-10-22',
        "***********,": '2022-12-03'
    }

    msg = '<u><b>Дней до дня рождения осталось:\n\n</b></u>'
    dr = list()
    for name in DATABASE:  # Перебор ключей словаря

        day_x = dt.datetime.strptime(DATABASE[name], '%Y-%m-%d').date()  # Преобразование значения в дату
        day = dt.date.today()  # Текущий день
        year_now = day.year  # Текущий год - для проверки, високосный год или нет
        # Проверка -  день рождения в этом году или нет
        if day < day_x:
            tdelta = day_x - day



        while day > day_x:
            # Получение правильного количества дней в году
            if calendar.isleap(year_now) == False:  # невисокосный год
                day_x = day_x + dt.timedelta(days=365)

            else:  # Високосный год
                day_x = day_x + dt.timedelta(days=366)

            tdelta = day_x - day

        if day == day_x:  # Если даты совпадают
            bot.send_message(message.from_user.id, 'Cегодня!')

        dr.append((name, day_x, tdelta.days))

    for i in range(len(dr)):
        if dr[i][2] < dr[i-1][2]:
            dr[i-1], dr[i] = dr[i], dr[i-1]

    for elements in dr:

        space_one = ' ' * (7-len(elements[0]))


        msg +='<em>{}</em> {} <b>{}</b>'.format(elements[0], space_one,
        elements[1].strftime('%d.%m.%Y')) + '  ' +  '--' +'  ' + str(elements[2])+'\n'

    bot.send_message(message.from_user.id, '<code>{}</code>'.format(msg), parse_mode='html')


# Функции для админов чата

# Писать от имени бота капслоком
@bot.message_handler(commands=['rc'])
def red_caps(message: types.Message):
    mess = list(message.text.split())
    mess.pop(0)
    mess = ' '.join(mess)
    mess = mess.upper()
    bot.send_message(chat_id=***********, text=f'<b>{mess}</b> ',
                     parse_mode='html')
    bot.delete_message(message.chat.id, message.id)


# Писать сообщение от имени бота через команду
@bot.message_handler(commands=['r'])
def red_caps(message: types.Message):
    mess = list(message.text.split())
    mess.pop(0)
    mess = ' '.join(mess)
    mess = mess.capitalize()
    bot.send_message(chat_id=***********, text=mess)
    bot.delete_message(message.chat.id, message.id)


# Писать обычные сообщение от имени бота через чат
@bot.message_handler(commands=['chat'],
                     content_types=['text', 'photo', 'stiker', 'video', 'emoji', 'voice', 'video_note'])
def rat_voce(message: types.Message):
    bot.delete_message(message.chat.id, message.id)
    send = bot.send_message(message.from_user.id, 'Просто пришли мне(или напиши, что ты хочешь отправить)')
    bot.send_message(message.from_user.id, "Я умею отправлять:\n"
                                           "- Текст\n "
                                           "- Фото\n "
                                           "- Видео\n "
                                           "- Стикеры\n "
                                           "- Смайлики\n "
                                           "- Голосовые сообщения\n "
                                           "- Видеосообщения")
    bot.register_next_step_handler(send, bot_voice)


def bot_voice(message: types.Message):
     bot.copy_message(chat_id=***********, from_chat_id=message.from_user.id, message_id=message.id)

@bot.message_handler(commands=['who'])
def pool(message):
    names = ['***********', '***********', '***********', '***********', '***********', '***********', '***********', '***********']
    bot.send_poll(chat_id=***********,
                  question='Кто пидор?',
                  options=names,
                  is_anonymous=True)

    bot.send_message(chat_id=***********, text='Все, конечно, знают <b>ПРАВИЛЬНЫЙ</b> ответ', parse_mode='html')
    bot.delete_message(message.chat.id, message.id)


@bot.message_handler(regexp='пидора')
@bot.message_handler(regexp='пидор')
def pidor(message):
    bot.send_audio(message.chat.id, 'AwACAgIAAxkBAAISyGOgQEcYEbzEJRtOBGfBnvviCUCoAALgIwACbw4BSdWIYzC_qQVtLAQ')


# реакция бота на определенные сообщения в чате
@bot.message_handler(regexp=r'Да')
@bot.message_handler(regexp=r'da')
@bot.message_handler(regexp=r'дa')
@bot.message_handler(regexp=r'д a')
@bot.message_handler(regexp=r'Да')
@bot.message_handler(regexp=r'd a')
@bot.message_handler(regexp=r'Нет')
@bot.message_handler(regexp=r'Нeт')
@bot.message_handler(regexp=r'Почему')
@bot.message_handler(regexp='как')
@bot.message_handler(regexp=r'no')
@bot.message_handler(regexp=r'nо')
@bot.message_handler(regexp=r'n o')
@bot.message_handler(regexp=r'n о')
@bot.message_handler(regexp=r'yes')
@bot.message_handler(regexp=r'yеs')
@bot.message_handler(regxp=r'y e s')
@bot.message_handler(regexp=r'y е s')
@bot.message_handler(regexp=r'Д@')
@bot.message_handler(regexp=r'd@')
@bot.message_handler(regexp=r'д а')
@bot.message_handler(regexp=r'н e т')
@bot.message_handler(regexp=r'd @')
@bot.message_handler(regexp=r'Д @')
@bot.message_handler(regexp=r'н е т')
def get_answer(message: types.Message):
    yes = 'CgACAgIAAxkBAAIEoWN02hOt6_BDH_M59N5AQyF4dL4RAAJ4DgACg2WxSWvB91qjxq6CKwQ'
    no = 'CAACAgIAAxkBAAEGkS9jgnvwXqZRV39_t8DpiecLMzQj2QACxwEAAnngUC8VnEmMhisfUCsE'
    why = 'BAACAgIAAxkBAAIKyGOAk2E7csc4AAFE91uvNI4FI3qI0QACjiMAAo8JAAFIPXGse2Y3wAorBA'
    answer = message.text.lower()
    match = re.search(pattern=r'([~@!#$%^&*()-_=+,."№;%:?*/bcf-z ]\s*)+', string=answer)  # Проверка символов в строке

    if match == False:
        answer = answer
    else:
        answer = re.sub('[~!@#$%^&*()-_=+,."№;:?/]+', '', answer)  # удаление символов
    da = ['da', 'дa', 'д а', 'd a', 'да', 'd a', 'd а', 'д a', 'd', 'д', 'd @', 'д @', 'д ', 'd ']
    net = ['нет', 'н е т ', 'н e т', 'нeт', 'н е т', 'н   т']
    if answer in da:
        bot.send_animation(message.chat.id, yes)
    elif answer in net:
        bot.send_sticker(message.chat.id, no)
    elif answer == "почему":
        bot.send_video(message.chat.id, why)
    elif answer == 'как' and len(answer) < 4:
        bot.send_message(message.chat.id, 'Через КУТАК')
    elif answer == 'no' or answer == 'nо' or answer == 'n o ' or answer == 'n о':
        bot.send_message(message.chat.id, '<em> Хуем по лбу дано</em>',
                         parse_mode='html')
    elif answer == 'yes' or answer == 'yеs' or answer == 'y e s' or answer == 'y е s':
        bot.send_message(message.chat.id,
                         f'{message.from_user.first_name} {message.from_user.last_name}<b> В залупу залез</b>',
                         parse_mode='html')


@bot.message_handler(commands=['rfpl'])
def rfpl_tour(message):

    bot.delete_message(message.chat.id, message.id)

    tour = pars_date_tour()
    tabl = pars_rfpl_tabl()
    tornament_tabl = '<b>ТУРНИРНАЯ ТАБЛИЦА</b> \n\n'
    one_tour = 'РАСПИСАНИЕ МАТЧЕЙ ТУРА \n\n'

    ikb_tabl = types.InlineKeyboardButton(text='Таблица', url='https://premierliga.ru/tournament-table/')
    ikb_matchday = types.InlineKeyboardButton(text='Расписание тура', url='https://premierliga.ru/calendar/')

    ikb_rfpl = types.InlineKeyboardMarkup(row_width=2)
    ikb_rfpl.add(ikb_tabl, ikb_matchday)


    for i in tabl[1:]:
        if i[1] == 'Зенит':
            i[1] = 'Бомжи'
        elif i[1] == 'ПФК ЦСКА':
            i[1] = 'Команда гондонов'
        elif i[1] == 'Локомотив':
            i[1] = 'Шлюхомоты'
        elif i[1] == 'Динамо':
            i[1] = 'Мусоришки'

        space = 25 - len(i[1])
        tornament_tabl += i[1] + ' ' * space + ' ' + i[7] + '\n'

    bot.send_message(message.from_user.id, '<code>{}</code>'.format(tornament_tabl), parse_mode='html')


    for i in range(len(tour)):
        one_tour += '<b>{}</b>'.format(tour[i][0]) + '\n' + '<u>{}</u>'.format(tour[i][1]) + '\n'

    bot.send_message(message.from_user.id, one_tour, parse_mode='html', reply_markup=ikb_rfpl)





@bot.message_handler()
def info_message_for_edit(message):
    chat = message.chat.id
    id_msg = message.id
    nick = message.from_user.username
    sending = message.text

    print(f'CHAT: {chat}, ID MESSAGE: {id_msg} USERNAME: {nick}, TEXT: {sending}')



#
# @bot.message_handler(content_types = ['photo'])
# def photo_id(message: types.Message):
# 	bot.send_message(message.from_user.id, message.photo.file_id)


#
# @bot.message_handler(content_types = ['animation'])
# def animation_id(message: types.Message):
# 	bot.send_message(message.from_user.id, message.animation.file_id)
#
# @bot.message_handler(content_types = ['stiker'])
# def animation_id(message: types.Message):
# 	bot.send_message(message.from_user.id, message.stiker.file_id)
#
# @bot.message_handler(content_types = ['video'])
# def video_id(message: types.Message):
# 	bot.send_message(message.from_user.id, message.video.file_id)

# @bot.message_handler(content_types = ['voice'])
# def video_id(message: types.Message):
# 	bot.send_message(message.from_user.id, message)

def simple_wisdom():
    hour = dt.datetime.now().hour
    if hour > 8 and hour < 10:
        bot.send_message(chat_id=***********,
                         text='<b>Мудростью на сегодняшний день, делюсь с Вами я!</b>\n\n' + f'<i>{random.choice(wisdom_list)}</i>',
                         parse_mode='html')
        threading.Timer(60*60*24, simple_wisdom).start()

def weather_today():
    hour = dt.datetime.now().hour
    if  hour > 6 and hour < 8:
        today = '<b>Погода на сегодня:</b>\n\n'
        cities = ['Москва', 'Тбилиси']
        for city in cities:
            url = f'https://wttr.in/{city}'  

            weater_parameters = {
                'O': '',
                'T': '',
                'M': '',
                'format': 2
            }  

            request_headers = {'Accept-Language': 'ru'}  

            response = requests.get(url, headers=request_headers,
                                        params=weater_parameters)
            today += '{}  \n{}'.format(city, response.text) + '\n'
        bot.send_message(chat_id=***********, text=today, parse_mode='html')
        threading.Timer(60 * 60 * 24, weather_today).start()


if __name__ == '__main__':
    with open('wisdom.txt', 'r') as f:
        wisdom_list = [i for i in f if len(i) != 0]

    print(wisdom_list)
    log.info('работаю')
    while True:
        simple_wisdom()
        weather_today()
        bot.infinity_polling(skip_pending=True)