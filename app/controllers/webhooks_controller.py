from flask import Blueprint, request, jsonify

webhooks_routes = Blueprint('webhooks_routes', __name__)


@webhooks_routes.route('/ping', methods=['GET'])
def ping():
    return 'pong'


@webhooks_routes.route('/apple', methods=['POST'])
def apple_webhook():
    req_data = request.json if request.json else {}
    print(req_data, "APPLE")

    return 'Apple'


@webhooks_routes.route('/shopee', methods=['POST'])
def shopee_webhook():
    req_data = request.json if request.json else {}
    print(req_data, "SHOPEE")

    return 'Shopee'


@webhooks_routes.route('/tiktok', methods=['POST'])
def tiktok_webhook():
    req_data = request.json if request.json else {}
    print(req_data, "TIKTOK")

    return 'Tiktok'