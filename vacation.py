import os
from datetime import datetime
import requests
import json

from json import loads
import sqlite3
import pandas as pd
import logging

DB_FILE = 'vacation.db'

LIVE_URL = os.environ['LIVE_URL']
API_KEY = os.environ['API_KEY']

this_year = datetime.today().strftime('%Y')


def vacations() -> dict:
    """берет из API отпуска за текущий год"""
    live3 = requests.Session()
    live3.params = {'api_key': API_KEY}
    api_path = 'api/users/vacation'
    get_vacations = live3.get(LIVE_URL + api_path)
    vacations_this_year = dict()
    if get_vacations.status_code == 200:
        vacations_all = json.loads(get_vacations.content)
        vacations_all = loads(get_vacations.content)
        for vacation in vacations_all:
            vacation_date = datetime.strptime(vacation['date'], '%Y-%m-%d')
            if vacation_date.year == int(this_year):
                if vacation['reason'] == 'vacation':
                    if not vacations_this_year.get(vacation['user_id']):
                        vacations_this_year[vacation['user_id']] = []
                    vacations_this_year[vacation['user_id']].append(vacation_date)
    return vacations_this_year


class Db:
    def __init__(self):
        self.db_connect = sqlite3.connect(DB_FILE)
        self.set_cursor = self.db_connect.cursor()
        # создаем таблицу, если не существует
        self.set_cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="vacations"')
        if not self.set_cursor.fetchall():
            self.set_cursor.execute('''CREATE TABLE vacations
                                (user_id text, name text, vacation_dates text)''')

    def read(self, user_id='all'):
        # todo добавь выборку по полю id пользователя
        self.setCursor.execute('SELECT * FROM vacations ORDER BY vacation_dates')
        return self.setCursor.fetchall()


    def write(self):
        self.setCursor.execute("INSERT INTO vacations VALUES ('%s', '%s', '%s')" % ('1302', 'Edward', '2021-10-03'))
        self.dbConnect.commit()
        self.dbConnect.close()


def post_to_slack(name, message_text):
    payload_text = {
        'username': 'Пора в отпуск',
        'text': '%s' % message_text,
        'icon_emoji': ':palm_tree:'
    }
    hook_url = 'https://hooks.slack.com/services/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'
    slack = requests.post(url=hook_url, data=json.dumps(payload_text))
    if slack.status_code == 200 and slack.text == 'ok':
        return True
    else:
        logging.debug('Не получилось отправить сообщение. Ошибка: %s' % slack.text)
        return False


def get_employees() -> dict:
    employees = dict()
    api_string = 'api/users/who_is_in_office'
    request_live3 = requests.Session()
    request_live3.params = {'api_key': API_KEY}
    request_data = request_live3.get(LIVE_URL + api_string)
    request_data_json = request_data.json()
    if request_data.ok == True:
        for empl in request_data_json:
            employees[empl['id']] = empl['name']
    return employees


def get_name(func_id: int, func_employees: dict) -> str:
    if func_id in func_employees:
        return func_employees[func_id]


got_vacations = vacations()
# ищем у кого отпуск через начнется месяц
search_date = (datetime.today() + pd.DateOffset(months=1)).strftime("%d-%m-%Y")
who_take_vacation = dict()
for employee in got_vacations:
    # находим границы отпуска
    first_day = ''
    for date in got_vacations[employee]:
        prev_day = (date - pd.DateOffset(days=1)).strftime("%d-%m-%Y")
        # если прошлого дня нет в списке дней отпуска - значит первый день
        if date.strftime("%d-%m-%Y") == search_date and prev_day not in got_vacations[employee]:
            first_day = date.strftime("%d-%m-%Y")
            continue
        else:
            next_day = (date + pd.DateOffset(days=1)).strftime("%d-%m-%Y")
            if next_day not in got_vacations[employee]:
                last_day = date.strftime("%d-%m-%Y")
                break
    if first_day:
        who_take_vacation[employee] = (first_day, last_day)
    if employee == 924:
        pass

employees = get_employees()
for mate in who_take_vacation:
    text = '{name} идет в отпуск с {search_date} по {last}'
pass