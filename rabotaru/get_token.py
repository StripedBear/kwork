import codecs
import configparser
from datetime import date, datetime
import requests


config = configparser.ConfigParser()
config.read_file(codecs.open("config.ini", 'r', 'utf8'))

url = 'https://api.rabota.ru/v6/login.json'
today = str(date.today())

USER = config['Main']['USER']
PASSWORD = config['Main']['PASSWORD']

headers = {
    'Content-Type': 'application/json',
    }
data = {
    "request": {
        "login": USER,
        "password": PASSWORD,
        "recaptcha_response": ""
    },
    "user_tags": [
        {
            "id": None,
            "name": "",
            "add_date": today,
            "campaign_key": None
        }
    ],
    "rabota_ru_id": "",
    "cache_control_max_age": 0
}

print(datetime.now().time(), ': Отправляю запрос')
result = requests.post(url, headers=headers, json=data)
token = result.json()['response']['token']
print(datetime.now().time(), f': Получен токен: {token}')

config.set("Main", "TOKEN", token)
with codecs.open("config.ini", 'w', 'utf8') as config_file:
    config.write(config_file)

print(datetime.now().time(), f'Токен записан')