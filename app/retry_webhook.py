from confluent_kafka import Producer
import os
import ujson as json


class RetryWebhook:
    def __init__(self):
        self.topic = os.getenv('HANDLE_KAFKA_TOPIC_JSON', 'cs_webhook_handle_json_topic_local')
        self.brokers = os.getenv('HANDLE_KAFKA_BROKERS', '10.120.80.37:9092,10.120.80.38:9092,10.120.80.39:9092')
        self.producer = Producer({'bootstrap.servers': self.brokers})
        self.response = {}

    def retry(self, package_order, status_id, package_data: dict):
        data = dict(
            pkg_order=package_order,
            status_id=status_id,
            package_data=package_data,
            retry=1,
            ts_ms=package_data['ts_ms'] if 'ts_ms' in package_data.keys() else None
        )
        self.producer.poll(0)
        msg = json.dumps(data).encode('utf-8')
        self.producer.produce(self.topic, msg, callback=self.build_response)
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
