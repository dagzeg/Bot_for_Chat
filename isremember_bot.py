import threading
import logging
import datetime as dt
import telebot

from config import RememberBot
from SQL_Class import SQL
from telebot import types

corr_yes = types.KeyboardButton(text='да')
corr_no = types.KeyboardButton(text='нет')
corr_keyword = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)


keyword_time = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=4)
time_zones = [str(i) for i in range(12)]
keyword_time.add(*time_zones)

corr_keyword.add(corr_yes, corr_no)

bot = telebot.TeleBot(RememberBot, skip_pending=True)

log = logging.getLogger()




@bot.message_handler(commands=['start'])
def start(message):
    start = 'Я бот-напоминалка, напиши мне что тебе нужно напомнить.\n' \
            'Напоминаю в установленную дату, за час и в установленное время\n' \
            'Что-бы создать напоминания напиши: <b>напомни</b> \n' \
            'Так же могу показать все твои напоминания, просто напиши <u><b>покажи</b></u>\n' \
            'так же могу удалить ненужные напоминания, подробнее в /help',

    bot.send_message(message.from_user.id, start, parse_mode='html')


@bot.message_handler(commands=['help'])
def help(message):
    help = 'Для создания напоминания напиши: <b>напомни*</u>\n' \
           'Напоминанием может быть любое текстовое сообщение(в том числе цифры и ссылки)\n' \
           'Время задается в формате ЧЧ:ММ или ЧЧ ММ (например 10:30 или 10 30)\n' \
           'Дата задается в формате дд.мм.гг или дд мм гг (например 20.04.23 или 20 04 23)\n' \
           'После каждого шага, будет проверочное сообщение <b>"Верно?"</b> с клавиатурой внизу. Выбери "да" или "нет".\n' \
           'Если напомнить надо сегодня, можно после вопроса <b>"Сегодня?"</b> выбрать "да"\n' \
           'Обращаю внимание. Возможно скорректировать значение только 1 раз, после придется начать сначала!\n\n' \
           'Для просмотра всех созданных напоминаний, напиши <u>покажи</u>\n\n' \
           'Для удаления ненужного напоминания, сделай reply сообщения после <u>покажи</u> и напиши к нему <u>удали</u>'

    bot.send_message(message.from_user.id, help, parse_mode='html')


@bot.message_handler()
def remember_for_user(message):
    text = message.text
    user_id = message.from_user.id


    if 'напомни' in text.lower():


        values = [user_id] # Cписок для передачи значений (user_id, remember_text, row_id, time, remember_day)
        bot.send_message(values[0], 'Что напомнить?')
        bot.register_next_step_handler(message, check_new, values)

    if text == 'покажи':
        select = sql.user_select(f'select * from remember_bot where user_id = {user_id}')
        for row in select:
            print(select[row])
            show_remember = f'Напоминание: <b>{select[row]["remember_text"]}</b>\n' \
                            f'Время: <i>{select[row]["remember_time"]}</i>\n' \
                            f'Дата: <u>{select[row]["remember_date"]}</u>'
            bot.send_message(user_id, show_remember, parse_mode='html')

    if text == 'удали':
        bot.send_message(user_id, f'<b>ты хочешь удалить</b>\n{message.reply_to_message.text}', parse_mode='html')
        bot.send_message(user_id, 'Верно?', reply_markup=corr_keyword)
        print(message.reply_to_message.text)
        if 'None' in message.reply_to_message.text:
            message.reply_to_message.text.replace('None', 'Null')
        delete_message = message.reply_to_message.text.split('\n')
        bot.register_next_step_handler(message, check_delete, delete_message, user_id)


def check_new(message, values):

    values.append(message.text)
    user_list = []
    time_zone = []
    check_time_zone = sql.select_all('users_time_zone')

    if len(check_time_zone) != 0:

        for row in check_time_zone:
            user_list.append(check_time_zone[row]['user_id'])
            time_zone.append(check_time_zone[row]['time_zone'])
            print(check_time_zone)
        print(user_list)
        print(time_zone)

        if values[0] in user_list and time_zone[user_list.index(values[0])] != None:
            bot.send_message(values[0], f'Твое напоминание: <b>{values[1]}</b>', parse_mode='html')
            bot.send_message(values[0], 'Верно?', reply_markup=corr_keyword)
            bot.register_next_step_handler(message, new_remember, values)

        else:
            sql.insert_into(table='users_time_zone', columns='user_id', values=[[values[0]]])
            bot.send_message(values[0], 'Выбери часовой пояс', reply_markup=keyword_time)
            bot.register_next_step_handler(message, check_location, values)

    else:
        sql.insert_into(table='users_time_zone', columns='user_id', values=[[values[0]]])
        bot.send_message(values[0], 'Выбери часовой пояс', reply_markup=keyword_time)
        bot.register_next_step_handler(message, check_location, values)



def new_remember(message, values):

    if message.text.lower() == 'да':
        sql.insert_into(table='remember_bot',
                        columns='user_id remember_text',
                        values=[values])
        bot.send_message(values[0], f'Напоминание: <b>{values[1]}</b>\n\n'
                                    f'Добавлено', parse_mode='html')

        select = sql.select_all('remember_bot')
        for row in select:
            remember_id = select[row]['id'] # получаем id записи в таблице remember_bot
        values.append(remember_id)

        bot.send_message(values[0], 'Введи время в формате ЧЧ:ММ или ЧЧ ММ')
        bot.register_next_step_handler(message, new_time, values)

    if message.text.lower() =='нет':
        bot.send_message(values[0], 'Напиши правильное напоминание')
        bot.register_next_step_handler(message, edit_remember, values)

def edit_remember(message, values):

    values[1] = message.text
    sql.insert_into(table='remember_bot',
                    columns='user_id remember_text',
                    values=[values])
    bot.send_message(values[0], f'Твое напоминание: <b>{values[1]}</b>\n\n'
                                f'Добавлено', parse_mode='html')

    select = sql.select_all('remember_bot')
    for row in select:
        remember_id = select[row]['id']
    values.append(remember_id)

    bot.send_message(values[0], 'Введи время в формате ЧЧ:ММ или ЧЧ ММ')
    bot.register_next_step_handler(message, new_time, values)


def check_location(message, values):

    td = int(message.text)
    td = td - 3

    sql.user_update(f'UPDATE users_time_zone set time_zone = {td} where user_id = {values[0]}')
    bot.send_message(values[0], f'Твое напоминание: <b>{values[1]}</b>', parse_mode='html')
    bot.send_message(values[0], 'Верно?', reply_markup=corr_keyword)
    bot.register_next_step_handler(message, new_remember, values)

def new_time(message, values):

    if len(message.text) == 5:
        time = message.text
        if ':' in time:
            time = time.split(':')
        elif ' ' in time:
            time = time.split()

        else:
            bot.send_message(values[0], 'Введенное время не подходит под формат ЧЧ:ММ или ЧЧ ММ\n'
                                        'Напиши время в формате ЧЧ:ММ или ЧЧ ММ')
            bot.register_next_step_handler(message, correct_time, values)
            return
        bot.send_message(values[0], f'Напомнить в <b>{time[0]} часов {time[1]} минут</b>', parse_mode='html')
        bot.send_message(values[0], 'Верно?', reply_markup=corr_keyword)
        bot.register_next_step_handler(message, check_time, values, time)

    else:
        bot.send_message(values[0], 'Введенное время не подходит под формат ЧЧ:ММ или ЧЧ ММ\n'
                                    'Напиши время в формате ЧЧ:ММ или ЧЧ ММ')
        bot.register_next_step_handler(message, correct_time, values)


def correct_time(message, values):

    if len(message.text) == 5:
        time = message.text

        if ' ' in time:
            time = time.split()
        elif ':' in time:
            time = time.split(':')

        bot.send_message(values[0], f'Напомнить в <b>{time[0]} часов {time[1]} минут</b>', parse_mode='html')
        bot.send_message(values[0], 'Верно?', reply_markup=corr_keyword)
        bot.register_next_step_handler(message, check_time, values, time)
    else:
        bot.send_message(values[0], 'Формат времени не подходит. Начни сначала')


def check_time(message, values, time):

    if message.text.lower() == 'да':
        time = ' '.join(time)
        sql.user_update(f'UPDATE remember_bot set remember_time = "{time}" where id = {values[2]}')
        bot.send_message(values[0], 'Время записано')
        values.append(time)
        bot.send_message(values[0], 'Напомнить сегодня?', reply_markup=corr_keyword)
        bot.register_next_step_handler(message, check_date_today, values)
    else:
        bot.send_message(values[0], 'Время сброшено. Начни сначала')
        sql.delete_where(table='remember_bot', where=f'id = {values[2]}')




def check_date_today(message, values):

    remember_day = dt.date.today()
    select = sql.user_select(f'select time_zone from users_time_zone where user_id = {values[0]}')
    td = select[1]['time_zone']

    if message.text.lower() == 'да':
        time = [int(i) for i in values[3].split()]
        check_date = dt.datetime(remember_day.year, remember_day.month, remember_day.day, time[0], time[1], 0)


        if check_date >= dt.datetime.now() + dt.timedelta(hours=td):
            sql.user_update(
                    f'UPDATE remember_bot set remember_date = "{remember_day}" where id = {values[2]}')
            write_remember = f'Ты попросил напомнить:\n' \
                                 f'Напоминание: <b>{values[1]}</b>\n' \
                                 f'Время: <i>{time[0]}:{time[1]}</i>\n' \
                                 f'Дата: <u>{remember_day.strftime("%d.%m.%Y")}</u>'
            bot.send_message(values[0], write_remember, parse_mode='html')
        else:
            bot.send_message(values[0], 'Не могу поставить напоминание в прошлое, пожалуйста напиши другую дату')
            bot.send_message(values[0], 'Напиши дату в формате: дд.мм.гг или дд мм гг')
            values.append(td)
            bot.register_next_step_handler(message, remember_date, values)

    else:
        bot.send_message(values[0], 'Напиши дату в формате: дд.мм.гг или дд мм гг')
        values.append(td)
        bot.register_next_step_handler(message, remember_date, values)


def remember_date(message, values):
    remember_day = message.text
    if '.' in remember_day:
        remember_day = remember_day.split('.')
    elif ' ' in remember_day:
        remember_day = remember_day.split()
    else:
        bot.send_message(values[0], 'Напиши дату корректную дату в формате: дд.мм.гг или дд мм гг')
        bot.register_next_step_handler(message, correct_date, values)

    if len(remember_day[2]) == 2:
        remember_day[2] = f'20{remember_day[2]}'
        remember_day = [int(i) for i in remember_day]
        time = [int(i) for i in values[3].split()]

    remember_day = dt.datetime(remember_day[2], remember_day[1], remember_day[0], time[0], time[1])

    if remember_day >= dt.datetime.now() + dt.timedelta(hours=values[4]):
        bot.send_message(values[0], f'Дата для напоминания: <b>{remember_day.strftime("%d.%m.%Y")}</b>',
                         parse_mode='html')
        bot.send_message(values[0], 'Верно?', reply_markup=corr_keyword)
        values.append(remember_day)
        bot.register_next_step_handler(message, check_date, values)
    else:
        bot.send_message(values[0], 'Не могу поставить напоминание в прошлое, пожалуйста напиши другую дату')
        bot.send_message(values[0], 'Напиши дату в формате: дд.мм.гг или дд мм гг')
        bot.register_next_step_handler(message, correct_date, values)



def correct_date(message, values):

    remember_day = message.text
    if ' ' in remember_day:
        remember_day = remember_day.split()
    elif '.' in remember_day:
        remember_day = remember_day.split('.')

    if len(remember_day[2]) == 2:
        remember_day[2] = int(f'20{remember_day[2]}')

    remember_day = dt.date(remember_day[2], remember_day[1], remember_day[0])

    bot.send_message(values[0], f'Дата для напоминания: <b>{remember_day.strftime("%d.%m.%Y")}</b>', parse_mode='html')
    bot.send_message(values[0], 'Верно?', reply_markup=corr_keyword)
    values.append(remember_day)
    bot.register_next_step_handler(message, check_date, values)

def check_date(message, values):

    print(values)

    if message.text.lower() == 'да':
        if values[5] >= dt.datetime.now():
            sql.user_update(
                f'UPDATE remember_bot set remember_date = "{values[5]}" where id = {values[2]}')
            time = values[3].split()
            write_remember = f'Ты попросил напомнить:\n' \
                             f'Напоминание: <b>{values[1]}</b>\n' \
                             f'Время: <i>{time[0]}:{time[1]}</i>\n' \
                             f'Дата: <u>{values[5].strftime("%d.%m.%Y")}</u>'
            bot.send_message(values[0], write_remember, parse_mode='html')
        else:
            bot.send_message(values[0], '<b>В прошлое не могу напомнить.</b>\n'
                                      'Напиши корректную дату в формате: дд.мм.гг или дд мм гг ', parse_mode='html')
            values.pop()
            bot.register_next_step_handler(message, one_more_time_date, values)
    else:
        bot.send_message(values[0], 'Напиши дату корректную дату в формате: дд.мм.гг или дд мм гг')
        values.pop()
        bot.register_next_step_handler(message, one_more_time_date, values)

def one_more_time_date(message, values):

    remember_day = message.text

    if ' ' in remember_day:
        remember_day = [int(i) for i in remember_day.split()]
    elif '.' in remember_day:
        remember_day = [int(i) for i in remember_day.split('.')]
    else:
        bot.send_message(values[0], 'Некорректный формат даты. Начни сначала')
        sql.delete_where(table= 'remember_bot', where=f'id = {values[2]}')

    if len(remember_day[2]) == 2:
        remember_day[2] = int(f'20{remember_day[2]}')

    remember_day = dt.date(remember_day[2], remember_day[1], remember_day[0])
    if remember_day >= dt.date.today():
        sql.user_update(f'UPDATE remember_bot set remember_date = {remember_day} where id = {values[1]}')

        write_remember = f'Ты попросил напомнить:\n' \
                         f'Напоминание: <b>{values[1]}</b>\n' \
                         f'Время: <i>{time[0]}:{time[1]}</i>\n' \
                         f'Дата: <u>{remember_day.strftime("%d.%m.%Y")}</u>'
        bot.send_message(values[0], write_remember, parse_mode='html')

    else:
        bot.send_message(values[0], 'Не могу поставить напоминание в прошлое. Начни сначала.')
        sql.delete_where(table='remember_bot', where=f'id= {values[2]}')






def check_delete(message, delete_message, user_id):
    message_for_user = "\n".join(delete_message)
    if message.text.lower() == 'да':
        msg = list()
        for i in delete_message:
            i = i.split(':')
            msg.append(i)
        print(msg)
        msg = [i[1].strip() for i in msg]
        print(msg)
        if msg[0] != 'None':
            remember_text = msg[0]
        else:
            remember_text = 'Null'
        if msg[1] != 'None':
            time = msg[1]
        else:
            time = 'Null'
        if msg[2] != 'None':
            remember_date = msg[2]
        else:
            remember_date = 'Null'

        if remember_text == 'Null' and time == 'Null' and remember_date == 'Null':
            sql.delete_where(table='remember_bot',
                             where=f'user_id = {user_id} and remember_text is Null and remember_time is Null and remember_date is Null')

        elif remember_text == 'Null' and time == 'Null':
            sql.delete_where(table='remember_bot',
                             where=f'user_id = {user_id} and remember_text is Null and remember_time is Null and remember_date = "{remember_date}"')

        elif remember_text == 'Null' and remember_date == 'Null':
            sql.delete_where(table='remember_bot',
                             where=f'user_id = {user_id} and remember_text is Null and remember_time = "{time}" and remember_date is Null')

        elif time == 'Null' and remember_date == 'Null':
            sql.delete_where(table='remember_bot',
                             where=f'user_id = {user_id} and remember_text = "{remember_text}" and remember_time is Null and remember_date is Null')

        elif remember_text == 'Null':
            sql.delete_where(table='remember_bot',
                             where=f'user_id = {user_id} and remember_text is Null and remember_time = "{time}" and remember_date = "{remember_date}"')

        elif time == 'Null':
            sql.delete_where(table='remember_bot',
                             where=f'user_id = {user_id} and remember_text = "{remember_text}" and remember_time is Null and remember_date = "{remember_date}"')

        elif remember_date == 'Null':
            sql.delete_where(table='remember_bot',
                             where=f'user_id = {user_id} and remember_text = "{remember_text}" and remember_time = "{time}" and remember_date is Null')

        else:
            sql.delete_where(table='remember_bot',
                             where=f'user_id = {user_id} and remember_text = "{remember_text}" and remember_time = "{time}" and remember_date = "{remember_date}"')

        bot.send_message(message.from_user.id, f'Напоминание: \n\n{message_for_user}\n\n<b>Удалено!</b>',
                         parse_mode='html')
    else:
        bot.send_message(message.from_user.id,
                         f'Хорошо, <b>не буду</b> удалять напоминание:\n\n{message_for_user}')


def check_remember_today():
    select = sql.select_all('remember_bot')

    for row in select:
        if select[row]['remember_date'] == dt.date.today():
            msg_remember = f'Напоминаю, сегодня у тебя запланировано:\n' \
                           f'<b>{select[row]["remember_text"]}</b>\n' \
                           f'Время - {select[row]["remember_time"]}'
            user_id = int(select[row]['user_id'])
            bot.send_message(chat_id=user_id, text=msg_remember, parse_mode='html')

    t = threading.Timer(3600 * 24, check_remember_today)
    t.start()


def check_remember_one_hour_left():
    select = sql.select_all('remember_bot')
    tz = sql.select_all('users_time_zone')
    time = dt.datetime.now()
    time_now = dt.datetime.now()
    time_zone = {}


    for row in select:
        user_id = select[row]['user_id']

        for r in tz:
            user = tz[r]['user_id']
            td = tz[r]['time_zone']
            time_zone[user] = td
        check_time = dt.datetime(time_now.year, time_now.month, time_now.day,
                                 time_now.hour + time_zone[user_id], time_now.minute, 0)
        if select[row]['remember_date'] == dt.date.today():
            day_today = dt.date.today()
            time = select[row]['remember_time'].split()
            time = [int(i) for i in time]
            time = dt.datetime(day_today.year, day_today.month, day_today.day, time[0], time[1], 0)

        if time.hour == (check_time + dt.timedelta(hours=1)).hour and time.minute == (check_time + dt.timedelta(hours=1)).minute:

            bot.send_message(chat_id=user_id, text=f'Напоминаю, через час у тебя запланировано:\n'
                                                   f'{select[row]["remember_text"]}\n'
                                                   f'Время - {select[row]["remember_time"]}')

        if time == check_time:

            bot.send_message(chat_id=user_id, text=f'Напоминаю, сейчас у тебя запланировано:\n'
                                                   f'{select[row]["remember_text"]}\n')


            sql.delete_where(table='remember_bot',
                             where=f'remember_text = "{select[row]["remember_text"]}"' \
                                   f' and remember_time = "{select[row]["remember_time"]}"' \
                                   f'and user_id = {select[row]["user_id"]}' \
                                   f' and remember_date = "{dt.date.today()}"'
                                   f'and id = {select[row]["id"]}')

        if time < check_time:
            sql.delete_where(table='remember_bot',
                             where=f'remember_text = "{select[row]["remember_text"]}"' \
                                   f' and remember_time = "{select[row]["remember_time"]}"' \
                                   f'and user_id = {select[row]["user_id"]}' \
                                   f' and remember_date = "{dt.date.today()}"')

    t = threading.Timer(60, check_remember_one_hour_left)
    t.start()


def check_Null():
    select = sql.select_all('remember_bot')

    if len(select) != 0:
        for row in select:
            if select[row]['remember_text'] == None or\
                select[row]['remember_time'] == None or\
                select[row]['remember_date'] == None:
                delete = select[row]['id']
                sql.delete_where(table='remember_bot', where=f'id = {delete}')
            else:
                print('Not Null')
    t = threading.Timer(3600*24, check_Null)
    t.start()



if __name__ == '__main__':

    log.info('INFO')

    sql = SQL()

    users_time_zone = {}
    while True:
        # check_remember_today()
        # check_remember_one_hour_left()
        # check_Null()

        bot.infinity_polling(skip_pending=True)