from math import floor
from time import sleep

from apscheduler.schedulers.background import BackgroundScheduler
import requests
import dotenv
from os import environ


import shoper_rest_client as shoper
from notification_service import NotificationService


class CurrencyApiClient:
    def __init__(self):
        dotenv.load_dotenv()
        self.url: str = environ.get('CURRENCY_API_URL')

    def update_currency_rates(self) -> dict[str, float]:
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
        cc_rate = self.get_exchange_rate('EUR', 'PLN')
        ints = int(floor(cc_rate))
        decimals = int(round((cc_rate - ints) * 100))
        markup = (shoper_rate / cc_rate - 1) * 100
        if self.MIN_MARKUP <= markup <= self.MAX_MARKUP:
            return
        elif markup < self.MIN_MARKUP:
            print(f'Markup too low: {markup:.2f}%')
            self.notifier.notify('rate.low')
            self.notifier.speak(f'Euro po {ints} {decimals}; Podnieś kurs w sklepie')
        else:
            print(f'Markup too high: {markup:.2f}%')
            self.notifier.notify('rate.high')
            self.notifier.speak(f'Euro po {ints} {decimals}; Obniż kurs w sklepie')

        sleep(120)
        return self.compare_exchange_rates()


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

    def schedule_jobs(self):
        self._scheduler.add_job(self._service.update(), trigger='cron', hour='9-22')
        self._scheduler.add_job(self._service.compare_exchange_rates(), trigger='cron', hour='9-22', minute='15')
        self._scheduler.start()
