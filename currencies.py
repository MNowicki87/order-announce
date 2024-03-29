from math import floor
from os import environ
from time import sleep

import dotenv
import requests
from apscheduler.schedulers.background import BackgroundScheduler

import shoper_rest_client as shoper
from notification_service import NotificationService


class CurrencyApiClient:
    def __init__(self):
        dotenv.load_dotenv()
        self.url: str = environ.get('CURRENCY_API_URL')

    def update_currency_rates(self) -> dict:
        response = requests.get(self.url)
        if response.status_code != 200:
            raise Exception('Error: API request failed')
        rates = response.json()['rates']
        return {k: float(v) for k, v in rates.items()}


class CurrencyService:
    def __init__(self):
        self.client = CurrencyApiClient()
        self.notifier = NotificationService()
        self.exchange_rates: dict[str, float] = self.client.update_currency_rates()
        dotenv.load_dotenv()
        self.MIN_MARKUP = int(environ.get('MIN_MARKUP'))
        self.MAX_MARKUP = int(environ.get('MAX_MARKUP'))
        self.attention_counter = 0

    def _get_rate(self, currency_code: str) -> float:
        try:
            return self.exchange_rates[currency_code]
        except KeyError:
            raise Exception('Error: Currency code not found')

    def update(self):
        self.exchange_rates = self.client.update_currency_rates()

    def get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        if from_currency == 'USD':
            return self._get_rate(to_currency)
        elif to_currency == 'USD':
            return 1 / self._get_rate(from_currency)
        else:
            return self._get_rate(to_currency) / self._get_rate(from_currency)

    def compare_exchange_rates(self) -> None:
        shoper_rate = shoper.get_exchange_rate()
        global_rate = self.get_exchange_rate("EUR", "PLN")
        ints = int(floor(global_rate))
        decimals = int(round((global_rate - ints) * 100))
        markup = (shoper_rate / global_rate - 1) * 100
        if self.MIN_MARKUP <= markup <= self.MAX_MARKUP:
            return
        elif markup < self.MIN_MARKUP:
            self.notifier.notify('rate.low')
            self.notifier.speak(f'Euro po {ints},{decimals} zł. Podnieś kurs w sklepie!')
        else:
            self.notifier.notify('rate.high')
            self.notifier.speak(f'Euro po {ints},{decimals} zł. Obniż kurs w sklepie!')

        self.attention_counter += 1
        if self.attention_counter > 1:
            correct_rate = global_rate * (1 + ((self.MIN_MARKUP + self.MAX_MARKUP) / 2) / 100)
            message = f'Kurs euro: {global_rate:.4f} zł\n' \
                      f'Kurs w sklepie: {shoper_rate:.4f} zł\n' \
                      f'Prawidłowy kurs: {correct_rate:.4f} zł'

            self.notifier.push('Zmień KURS W SKLEPIE', message)
            self.notifier.send_sms(message)

        sleep(120)
        return self.compare_exchange_rates()

    def init_values(self):
        self.notifier.speak(f'Kurs w sklepie: {shoper.get_exchange_rate():.2f} zł')
        self.notifier.speak(f'Kurs globalny: {self.get_exchange_rate("EUR", "PLN"):.2f} zł')


class CurrencyCheckScheduler:
    def __init__(self, currency_service: CurrencyService):
        self._service = currency_service
        self._scheduler = BackgroundScheduler(
            job_defaults={
                'misfire_grace_time': 60,
                'coalesce': True
            }, timezone='Europe/Warsaw')
        self._service.update()
        self._service.compare_exchange_rates()
        self._service.init_values()

    def schedule_jobs(self):
        self._scheduler.add_job(self._service.update, trigger='cron', hour='9-22')
        self._scheduler.add_job(self._service.compare_exchange_rates, trigger='cron', hour='9-22', minute='15')
        self._scheduler.start()
