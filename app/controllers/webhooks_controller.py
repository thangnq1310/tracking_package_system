from flask import Blueprint, request
from scripts.email_kafka.EmailProducer import EmailProducer

webhooks_routes = Blueprint('webhooks_routes', __name__)


@webhooks_routes.route('/ping', methods=['GET'])
def ping():
    return 'pong'


@webhooks_routes.route('/apple', methods=['POST'])
def apple_webhook():
    req_data = request.json if request.json else {}
    print("Params Apple:", req_data)
    email_producer = EmailProducer()
    email_producer.send_message(req_data)

    return {
        'success': True,
        'message': 'Apple receive message successfully!'
    }


@webhooks_routes.route('/shopee', methods=['POST'])
def shopee_webhook():
    req_data = request.json if request.json else {}
    print("Params Shopee:", req_data)

    return {
        'success': True,
        'message': 'Shopee receive message successfully!',
    }


@webhooks_routes.route('/tiktok', methods=['POST'])
def tiktok_webhook():
    req_data = request.json if request.json else {}
    print("Params Tiktok:", req_data)

    return {
        'success': True,
        'message': 'Tiktok receive message successfully!',
    }
