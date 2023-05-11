from confluent_kafka import Producer
import os
import ujson as json


class RetryWebhook:
    def __init__(self, topic, brokers):
        self.topic = topic
        self.brokers = brokers
        self.producer = Producer({'bootstrap.servers': brokers})
        self.response = {}

    def retry(self, package_order, status_id, package_data: dict):
        data = {
            **package_data,
            'is_retry': 1,
            'ts_ms': package_data['ts_ms'] if 'ts_ms' in package_data.keys() else None,
            'status_code': status_id
        }
        self.producer.poll(0)
        msg = json.dumps(data).encode('utf-8')
        self.producer.produce(self.topic, msg, callback=self.build_response, key=package_order)
        self.producer.flush()

        return self.response

    def build_response(self, err, msg):
        if err is not None:
            print("[ERROR]: Error when retry send webhook:", str(err))
            self.response = {
                'success': False,
                'message': 'Error when push to webhook' + str(err),
                'data': None
            }
        else:
            print("Retry send webhook successfully!")
            self.response = {
                'success': True,
                'message': 'Retry send webhook successfully!',
                'data': {
                    'topic': msg.topic(),
                    'partition': msg.partition()
                }
            }
