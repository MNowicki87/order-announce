from flask import Request

from request_handler import RequestHandler

if __name__ == '__main__':
    handler = RequestHandler()

    request_create = Request({'HTTP_X_WEBHOOK_NAME': 'order.create'})
    request_paid = Request({'HTTP_X_WEBHOOK_NAME': 'order.paid'})

    handler.process_request(request_create)
    handler.process_request(request_paid)
