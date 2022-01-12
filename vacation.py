import os
from datetime import datetime
import requests
from json import loads
import sqlite3
import pandas as pd

DB_FILE = 'vacation.db'

LIVE_URL = os.environ['LIVE_URL']
API_KEY = os.environ['API_KEY']

this_year = datetime.today().strftime('%Y')

# iter_month = '10'
# get_timeline = 'timeline?department_id=&team_id=&date=' + '%s' % year + '%2F' + '%s&q=' % iter_month
# print

# from html.parser import HTMLParser
#
#
# class MyHTMLParser(HTMLParser):
#
#     def handle_starttag(self, tag, attrs):
#         print("Encountered a start tag:", tag)
#
#     def handle_endtag(self, tag):
#         print("Encountered an end tag :", tag)
#
#     def handle_data(self, data):
#         print("Encountered some data  :", data)
#
#
# parser = MyHTMLParser()


def vacations() -> dict:
    """берет из API отпуска за текущий год"""
    live3 = requests.Session()
    live3.params = {'api_key': API_KEY}
    api_path = '/api/users/vacation'
    get_vacations = live3.get(LIVE_URL + api_path)
    vacations_this_year = dict()
    if get_vacations.status_code == 200:
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


get_data = vacations()
search_date = (datetime.today() + pd.DateOffset(months=1)).strftime("%d-%m-%Y")
pass