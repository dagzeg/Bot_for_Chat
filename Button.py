from telebot import types


ikb = types.InlineKeyboardMarkup(row_width=1)
ikb1 = types.InlineKeyboardButton(text = 'Сайт', url = f'https://wttr.in/')

ikb.add(ikb1)


ikp_rfpl = types.InlineKeyboardMarkup(row_width=2)
ikb_tabl = types.InlineKeyboardButton(text='Таблица', url='https://premierliga.ru/tournament-table/')
ikb_matchday = types.InlineKeyboardButton(text='Расписание тура', url='https://premierliga.ru/calendar/')

ikp_rfpl.add(ikb_tabl, ikb_matchday)


kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)

k1 = types.KeyboardButton(text= 'Москва')
k2 = types.KeyboardButton(text='Санкт-Петербург')
k3 = types.KeyboardButton(text='Тбилиси')
k4 = types.KeyboardButton(text ='Батуми')
k5 = types.KeyboardButton(text = 'Ташкент')
k6 = types.KeyboardButton(text= 'Ереван')

kb.add(k1, k2, k3, k4, k5, k6)


dice_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True) # создание клавиатуры
dice_kb1 = types.KeyboardButton(text ='Три') # назначение кнопки 1
dice_kb2 = types.KeyboardButton(text = 'Два') # назначение кнопки 2
dice_kb.add(dice_kb1, dice_kb2) # создание клавиатуры

