import os
from datetime import datetime
from time import sleep

import pygame
from gtts import gTTS


class NotificationService:
    SOUNDS = {
        'order.create': 'order.mp3',
        'order.paid': 'payment.mp3',
        'order.status': 'chime.mp3',
        'rate.high': 'chime.mp3',
        'rate.low': 'chime.mp3',
    }

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
