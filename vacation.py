import os
from datetime import datetime
# import pandas as pd

import requests
from base64 import b64encode
import base64
from json import loads

LIVE_URL = os.environ['LIVE_URL']
API_KEY = os.environ['API_KEY']




this_year = datetime.today().strftime('%Y')

iter_month = '10'
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














pass