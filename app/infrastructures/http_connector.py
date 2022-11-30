import os

import dotenv
import requests
import ujson as json

dotenv.load_dotenv()


class HTTPConnectorService:
    def __init__(self, params, url, method='POST'):
        self.method = method
        self.params = params
        self.headers = {}
        self.request = {}
        self.response = {}
        self.files = None
        self.auth = None
        self.service_name = ""
        self.timeout = 20
        self.base_url = os.getenv('WEBHOOK_URL', '')
        self.url = self.base_url + url

    def do_request(self):
        print(self.url)
        try:
            if self.method == 'GET':
                self.response = requests.get(self.url, params=self.params, headers=self.headers, timeout=self.timeout)
            elif self.method == 'POST':
                if self.files is None:
                    self.response = requests.post(
                        self.url,
                        json=json.dumps(self.params)
                    )
                else:
                    self.response = requests.post(self.url, json=json.dumps(self.params), files=self.files, headers=self.headers,
                                                  timeout=self.timeout)
            elif self.method == 'PUT':
                self.response = requests.put(self.url, data=self.params, headers=self.headers, timeout=self.timeout)
            print("[RESPONSE]: Response when do request to " + self.url,
                  str(self.response.text))
        except Exception as e:
            print("[ERROR]: Error when do request to " + str(self.url) + ': ' + str(e))

            return {
                'success': False,
                'message': ''
            }
        return self.format_response()

    def format_response(self):
        return json.loads(self.response.text)
