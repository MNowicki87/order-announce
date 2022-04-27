import hashlib
from os import environ

from dotenv import load_dotenv
from flask import Request

from notification_service import NotificationService


class RequestHandler:
    _EVENTS = (
        'order.create',
        'order.paid',
        'order.status',
    )

    def __init__(self):
        load_dotenv()
        self._secret = environ.get('SHOPER_WEBHOOK_SECRET')
        self.notifier = NotificationService()

    # noinspection InsecureHash
    def validate(self, req: Request) -> bool:
        headers = req.headers.environ
        webhook_id = headers.get('HTTP_X_WEBHOOK_ID')
        webhook_data = req.data.decode('UTF-8')
        webhook_sha = req.headers.environ.get('HTTP_X_WEBHOOK_SHA1', '')
        checksum = hashlib.sha1(f'{webhook_id}:{self._secret}:{webhook_data}'.encode('utf-8'))
        return True if checksum.hexdigest() == webhook_sha else False

    def process_request(self, req: Request):
        event = req.headers.environ.get('HTTP_X_WEBHOOK_NAME')
        if event in self._EVENTS:
            self.notifier.notify(event)
