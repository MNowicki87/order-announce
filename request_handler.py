import hashlib
from os import environ

import pygame
from dotenv import load_dotenv
from flask import Request

SOUNDS = {
    'order.create': 'order.mp3',
    'order.paid': 'payment.mp3',
    # 'order.status': 'order.mp3', # For testing purposes
}


class RequestHandler:
    def __init__(self):
        load_dotenv()
        self._secret = environ.get('SHOPER_WEBHOOK_SECRET')

    # noinspection InsecureHash
    def validate(self, req: Request) -> bool:
        headers = req.headers.environ
        webhook_id = headers.get('HTTP_X_WEBHOOK_ID')
        webhook_data = req.data.decode('UTF-8')
        webhook_sha = req.headers.environ.get('HTTP_X_WEBHOOK_SHA1', '')
        checksum = hashlib.sha1(f'{webhook_id}:{self._secret}:{webhook_data}'.encode('utf-8'))
        return True if checksum.hexdigest() == webhook_sha else False

    # @staticmethod
    def process_request(self, req: Request):
        event = req.headers.environ.get('HTTP_X_WEBHOOK_NAME')
        # os.system(f'omxplayer {SOUNDS[event]}')
        self.play_sound(event)

    def play_sound(self, event):
        pygame.mixer.init()
        pygame.mixer.music.load(SOUNDS[event])
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue
