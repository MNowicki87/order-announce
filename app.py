import os
import signal
import sys
import time

import flask
import requests
from dotenv import load_dotenv
from flask import Flask, request

import shoper_rest_client as sc
from currencies import CurrencyCheckScheduler, CurrencyService
from notification_service import NotificationService
from request_handler import RequestHandler

PORT = 5421
app = Flask(__name__)
handler = RequestHandler()


def start_tunnel(port: int) -> None:
    """
    Starts ngrok.
    A command to run ngrok must be passed as ENV var. I couldn't get it to run with command alias on RPi.

    :param port: port number for the tunnel to be opened - same as Flask APP
    """
    print('Opening tunnel')
    load_dotenv()
    ngrok = os.environ.get('NGROK')
    os.system(f'{ngrok} http -bind-tls=true {port} > /dev/null &')


def get_public_url():
    print('Getting public URL')
    time.sleep(2)
    try:
        response = requests.get('http://localhost:4040/api/tunnels')
    except ConnectionError:
        time.sleep(1)
        return get_public_url()
    return response.json()['tunnels'][0]['public_url']


def close_app(*args):
    print('\nClosing tunnel...')
    os.system('killall ngrok')
    print('Goodbye!')
    sys.exit(0)


@app.route("/", methods=['POST'])
def webhook_receive():
    print("I've got something!")
    if handler.validate(request):
        handler.process_request(request)
        return flask.Response(status=200)

    return flask.Response(status=401)


def main():
    notifier = NotificationService()
    notifier.speak('Dzień dobry!')

    start_tunnel(PORT)
    signal.signal(signal.SIGINT, close_app)
    sc.start()
    sc.update_webhook_url(get_public_url())
    notifier.speak('Tunel otwarty!')

    currency_service = CurrencyService()
    currency_scheduler = CurrencyCheckScheduler(currency_service)
    currency_scheduler.schedule_jobs()
    notifier.speak('Monitorowanie kursów walut uruchomione!')
    notifier.push('Monitor kursu walut', 'Monitorowanie kursów walut uruchomione!')


if __name__ == "__main__":
    from waitress import serve

    main()
    serve(app, host="0.0.0.0", port=PORT)
