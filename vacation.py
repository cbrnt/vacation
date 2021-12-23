import os
from datetime import datetime
# import pandas as pd

import requests

LIVE_URL = os.environ['LIVE_URL']
API_KEY = os.environ['API_KEY']




year = datetime.today().strftime('%Y')

iter_month = '10'
get_timeline = 'timeline?department_id=&team_id=&date=' + '%s' % year + '%2F' + '%s&q=' % iter_month
print

from html.parser import HTMLParser


class MyHTMLParser(HTMLParser):

    def handle_starttag(self, tag, attrs):
        print("Encountered a start tag:", tag)

    def handle_endtag(self, tag):
        print("Encountered an end tag :", tag)

    def handle_data(self, data):
        print("Encountered some data  :", data)


parser = MyHTMLParser()

# parser.feed('<html><head><title>Test</title></head>')
authParam = {'api_key': API_KEY}
api_param = ''


get_live_page = requests.get('http://test.live3.dcp24.ru/timeline', headers=authParam)
headers = {'Content-Type': 'application/json', 'Authorization': 'Basic %s' % Jira.JIRA_CREDENTIALS_BASE64}
jira_credentials = 'vigerin:wantt0Know'
jira_credentials_bytes = jira_credentials.encode('ascii')
JIRA_CREDENTIALS_BASE64 = base64.b64encode(jira_credentials_bytes).decode('ascii')



pass