import os
import signal
import sys
import time

import flask
import requests
from dotenv import load_dotenv
from flask import Flask

import shoper_rest_client as sc

PORT = 5421
app = Flask(__name__)


def start_tunnel(port: int) -> None:
    print('Opening tunnel')
    load_dotenv()
    ngrok = os.environ.get('NGROK')
    os.system(f'{ngrok} http -bind-tls=true {port} > /dev/null &')


def get_public_url():
    print('Getting public URL')
    time.sleep(5)
    response = requests.get('http://localhost:4040/api/tunnels')
    return response.json()['tunnels'][0]['public_url']


def close_app(*args):
    print('\nClosing tunnel...')
    os.system('killall ngrok')
    print('Goodbye!')
    sys.exit(0)


@app.route("/", methods=['POST'])
def webhook_receive():
    print("I've got something!")
    return flask.Response(status=200)


def main():
    start_tunnel(PORT)
    signal.signal(signal.SIGINT, close_app)
    sc.start()
    sc.update_webhook_url(get_public_url())
    print('Runnning...')


if __name__ == "__main__":
    from waitress import serve

    main()
    serve(app, host="0.0.0.0", port=PORT)
