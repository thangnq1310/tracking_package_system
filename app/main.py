import os

from flask import Flask
from controllers.webhooks_controller import webhooks_routes

app = Flask(__name__)

# Routes
app.register_blueprint(webhooks_routes)

API_HANDLE_HOST = os.getenv('API_HANDLE_HOST', '0.0.0.0')
API_HANDLE_PORT = os.getenv('API_HANDLE_PORTT', 8000)

if __name__ == '__main__':
    app.run(host=API_HANDLE_HOST, port=API_HANDLE_PORT, debug=True, threaded=False, processes=3)
