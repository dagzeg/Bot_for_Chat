import requests
from bs4 import BeautifulSoup as bs
import datetime as dt
import re
from functools import lru_cache
import time

@lru_cache(None)
def pars_rfpl_tabl():
    site = requests.get('https://premierliga.ru/tournament-table/').text
    pars = bs(site, 'lxml')
    teams = pars.find_all('td')
    teams = [teams[i].text for i in range(len(teams))]
    teams = teams[21:]
    s = ''
    for i in range(len(teams)):
        for m in teams[i]:
            if m != '\n':
                s += m
        teams.append(s)
        s = ''
    t = teams[360:]
    groups = [t[0:7], t[8:30], t[30:52],t[52:74], t[74:96], t[96:118], t[118:140], t[140:162], t[162:184], t[184:206], t[206:228], t[228:250],
              t[250:272], t[272:294], t[294:316], t[316:338], t[338:]]

    for i in groups[1:]:
        i.pop(-1)
        i.pop(2)
        i.remove('\xa0')
        i.remove('\xa0')
        i.remove('\xa0')
        i.pop(12)

    groups[0].pop(-2)
    groups[0].remove('\xa0')
    groups[0].remove('\xa0')
    groups[0].remove('\xa0')

    return groups



@lru_cache(None)
def pars_date_tour():
    site = requests.get('https://premierliga.ru/calendar/').text
    pars = bs(site, 'lxml')
    day = pars.find_all('p')
    day = day[9:41]
    rasp_day = [[day[i-3].text, day[i-2].text, day[i-1].text, day[i].text] for i in range(3,len(day),4)]
    day = [[i[2], i[0]] for i in rasp_day]
    for i in day:
        teams = i[1].split()
        if 'Зенит' in teams:
            teams[teams.index('Зенит')] = 'Бомжи'
        elif 'ПФК' and 'ЦСКА' in teams:
            teams[teams.index('ПФК')] = 'Команда'
            teams[teams.index('ЦСКА')] = 'гондонов'
        elif 'Локомотив' in teams:
            teams[teams.index('Локомотив')] = 'Шлюхомоты'
        elif 'Динамо' in teams:
            teams[teams.index('Динамо')] = 'Мусоришки'
        teams = ' '.join(teams)
        i[1] = teams
    return day

