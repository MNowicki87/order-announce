from os import environ

import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()
REST_URL = environ.get('SHOPER_REST_URL')
CLIENT_ID = environ.get('SHOPER_CLIENT_ID')
CLIENT_SECRET = environ.get('SHOPER_CLIENT_SECRET')
WEBHOOK_ID = environ.get('SHOPER_WEBHOOK_ID')

auth_url = f'{REST_URL}auth/'
webhook_url = f'{REST_URL}webhooks/{WEBHOOK_ID}'

bearer_token = ''
headers = ''


def get_token() -> str:
    auth = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    response = requests.post(url=auth_url, auth=auth)
    return "Bearer " + response.json()["access_token"]


def update_headers():
    global headers
    headers = {'Authorization': get_token()}


def update_webhook_url(url: str):
    print(f'Updating Webhook url to: {url}')
    body = '{"url": "%s"}' % url
    with requests.put(webhook_url, data=body, headers=headers) as response:
        if response.status_code != 200:
            print('Something went wrong, close app and debug')


def get_exchange_rate() -> float:
    with requests.get(f'{REST_URL}currencies/3', headers=headers) as response:
        if response.status_code != 200:
            print('Something went wrong, close app and debug')
    return float(response.json()['rate'])


def start():
    update_headers()
