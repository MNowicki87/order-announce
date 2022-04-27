from time import sleep

import pygame


class NotificationService:
    SOUNDS = {
        'order.create': 'order.mp3',
        'order.paid': 'payment.mp3',
        'rate.high': 'hi-rate.mp3',
        'rate.low': 'lo-rate.mp3',
    }

    def notify(self, event):
        pygame.mixer.init()
        pygame.mixer.music.load(self.SOUNDS[event])
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            sleep(.3)
            continue
