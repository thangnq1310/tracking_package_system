import time

from flask import Blueprint, request

webhooks_routes = Blueprint('webhooks_routes', __name__)


@webhooks_routes.route('/ping', methods=['GET'])
def ping():
    return 'pong'


@webhooks_routes.route('/alpha', methods=['POST'])
def alpha_webhook():
    # req_data = request.json if request.json else {}
    # print("Params Alpha:", req_data)
    time.sleep(2)

    return {
        'success': True,
        'message': 'Alpha receive message successfully!'
    }


@webhooks_routes.route('/beta', methods=['POST'])
def beta_webhook():
    # req_data = request.json if request.json else {}
    # print("Params Beta:", req_data)
    time.sleep(5)

    return {
        'success': True,
        'message': 'Beta receive message successfully!',
    }


@webhooks_routes.route('/gamma', methods=['POST'])
def gamma_webhook():
    # req_data = request.json if request.json else {}
    # print("Params Gamma:", req_data)
    time.sleep(10)

    return {
        'success': True,
        'message': 'Gamma receive message successfully!',
    }
