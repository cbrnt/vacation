from typing import Any

import os
from datetime import datetime
import requests
import json

from json import loads
import sqlite3
import pandas as pd
import logging
import argparse

class GetSlackIDError(Exception):
    def __init__(self, *args):
        if args:
            logging.error('Не нашел юзера %s по почте', args)

parser = argparse.ArgumentParser()
parser.add_argument('--log', metavar='DEBUG',
                    dest='loglevel',
                    help='уровень логирования')
args = parser.parse_args()
if args.loglevel:
    LOGLEVEL = args.loglevel
else:
    LOGLEVEL = ''
# выставляем уровень логирования
log_file = 'vacation.log'
numeric_level = getattr(logging, LOGLEVEL.upper(), None)
if not isinstance(numeric_level, int):
    logging.basicConfig(filename='%s' % log_file, level=logging.WARNING)
else:
    logging.basicConfig(filename='%s' % log_file, level=numeric_level)

DB_FILE = 'vacation.db'

LIVE_URL = os.environ['LIVE_URL']
API_KEY = os.environ['API_KEY']

this_year = datetime.today().strftime('%Y')
channel_to_post = 'test-out-hooks-1'


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


class Slack:
    bot_token = os.environ['SLACK_BOT_TOKEN_TOCHKAK']
    user_token = os.environ['SLACK_USER_TOKEN_TOCHKAK']
    session = requests.Session()
    session.headers = {'Authorization': 'Bearer %s' % bot_token,
                       'Content-type': 'application/x-www-form-urlencoded'}
    session.timeout = 10

    @staticmethod
    def get_name(user_id_list: list) -> list:
        """Получаает slack user id и возвращает список из кортежей"""
        get_list = session.post('https://slack.com/api/users.list', timeout=10)
        if get_list.status_code == 200 and get_list.ok:
            users_list = get_list.json()
            name_list = []
            if users_list.get('ok'):
                for user_id in user_id_list:
                    for user in users_list['members']:
                        if user.get('id') == user_id:
                            name_list.append((user.get('id'), user.get('real_name')))
                return name_list
        return False

    @staticmethod
    def post_to_channel(message_text: str, channel_id: str, username: str):
        data = {"channel": "%s" % channel_id,
                "text": "%s" % message_text,
                "username": "%s" % username,
                "icon_emoji": ":palm_tree:"
                }
        request = Slack.session.post('https://slack.com/api/chat.postMessage',
                                     data=data, timeout=10)
        result = json.loads(request.text)
        if not result['ok']:
            logging.debug("Ошибка при посте в slack: %s" % str(result['error']))

    @staticmethod
    def get_user_by_email(mail) -> str:
        """Получает данные юзера по email"""
        data = {"email": mail}
        request = Slack.session.post('https://slack.com/api/users.lookupByEmail', timeout=10, data=data)
        result = json.loads(request.text)
        if not request.ok or not result['ok']:
            raise GetSlackIDError(mail)
        get_id = request.json()
        return get_id


def get_employees() -> dict:
    employees_func = dict()
    api_string = 'api/users'
    request_live3 = requests.Session()
    request_live3.params = {'api_key': API_KEY}
    request_data = request_live3.get(LIVE_URL + api_string)
    request_data_json = request_data.json()
    if request_data.ok:
        for empl in request_data_json:
            employees_func[empl['id']] = {}
            employees_func[empl['id']]['email'] = empl['email']
            employees_func[empl['id']]['fired'] = empl['work']['fired']
    return employees_func


def get_name(func_id: int, func_employees: dict) -> str:
    if func_id in func_employees:
        return func_employees[func_id]


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


def main():
    got_vacations = vacations()
    # ищем у кого отпуск через начнется месяц
    search_date = datetime.today().date() + pd.DateOffset(months=1)
    search_date_str = (datetime.today() + pd.DateOffset(months=1)).strftime("%d-%m-%Y")
    who_take_vacation = dict()
    for employee in got_vacations:
        # находим границы отпуска
        first_day = ''
        last_day = ''
        day_before_search = search_date - pd.DateOffset(days=1)
        for date in got_vacations[employee]:
            # если дня перед искомой датой нет в списке дней отпуска сотрудника - значит первый день отпуска
            if date.strftime("%d-%m-%Y") == search_date_str:
                if day_before_search not in got_vacations[employee]:
                    first_day = date
                    subdate = first_day
                    while subdate in got_vacations[employee]:
                        subdate = subdate + pd.DateOffset(days=1)
                    last_day = subdate - pd.DateOffset(days=1)
        if not who_take_vacation.get(employee) and first_day and last_day:
            who_take_vacation[employee] = list()
        if first_day and last_day:
            who_take_vacation[employee].append((first_day, last_day))

    employees = get_employees()
    who_post_to_slack = dict()
    for mate in who_take_vacation:
        dt = who_take_vacation[mate]
        name = get_name(mate, employees)
        start_vac = dt[0][0].strftime("%d.%m")
        end_vac = dt[0][1].strftime("%d.%m")
        days_diff = dt[0][1] - dt[0][0]
        # добавляю 1 день так как при подсчете разницы в днях
        # предполгаю, что последний день не учитывеатся из-за того что не перешел границу времени 23:59
        diff = days_diff.days + 1
        who_post_to_slack[mate] = (name, start_vac, end_vac, diff)



    for dude in who_post_to_slack:
        emp = who_post_to_slack[dude]
        to_slack = Slack
        if not emp[0]['fired']:
            get_employee_id = to_slack.get_user_by_email(emp[0]['email'])
            employee_slack_id = get_employee_id['user']['id']
            message = "У <@{employee_id}> приближается запланированный отпуск на {days} дней с {start} по {end}".format(
                employee_id=employee_slack_id, start=emp[1], end=emp[2], days=emp[3])

            result = to_slack.post_to_channel(message, 'C02LPT3GBU7', 'Пора в отпуск')



if __name__ == '__main__':
    main()
