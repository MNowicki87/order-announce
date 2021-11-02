import os, sys
import signal
import time

import requests
from flask import Flask

app = Flask(__name__)
PORT = 5421


def start_tunnel(port: int) -> None:
    os.system(f'ngrok http -bind-tls=true {port} > /dev/null &')


start_tunnel(PORT)


def get_public_url():
    time.sleep(2)
    response = requests.get('http://localhost:4040/api/tunnels')
    return response.json()['tunnels'][0]['public_url']


url = get_public_url()

print(f'Tunnel URL: {url}')


def signal_handler(sig, frame):
    print('\nClosing tunnel...')
    os.system('killall ngrok')
    print('Goodbye!')
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


@app.route("/")
def hello_world():
    return '<p>OK!</p>'


if __name__ == "__main__":
    from waitress import serve

    serve(app, host="0.0.0.0", port=PORT)
