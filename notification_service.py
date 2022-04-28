import os
from datetime import datetime
from time import sleep

import pygame.mixer
from dotenv import load_dotenv
from gtts import gTTS
from pushbullet import Pushbullet
from pushbullet.errors import PushError, PushbulletError


class NotificationService:
    SOUNDS = {
        'order.create': 'order.mp3',
        'order.paid': 'payment.mp3',
        'order.status': 'chime.mp3',
        'rate.high': 'chime.mp3',
        'rate.low': 'chime.mp3',
    }

    def __init__(self):
        load_dotenv()
        api_key = os.environ.get('PUSHBULLET_API_KEY')
        self.pb = Pushbullet(api_key)
        self.pb_device = self.pb.devices[0]
        self.phone_number = os.environ.get('PHONE_NUMBER')

    def notify(self, event):
        self._play_sound(self.SOUNDS[event])

    @staticmethod
    def _play_sound(sound):
        pygame.mixer.init()
        pygame.mixer.music.load(sound)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            sleep(.3)
            continue
        pygame.mixer.quit()

    def speak(self, message):
        tts = gTTS(message, lang='pl', tld='pl')
        file = f'temp{datetime.now().strftime("%H%M%S%f")}.mp3'
        tts.save(file)
        self._play_sound(file)
        os.remove(file)

    def push(self, title, body):
        try:
            self.pb.push_note(title, body)
        except PushError:
            self.speak(f'Błąd wysyłania powiadomienia: {title}')

    def send_sms(self, message):
        try:
            self.pb.push_sms(self.pb_device, self.phone_number, message)
        except PushbulletError:
            self.speak('Błąd wysyłania SMS')
