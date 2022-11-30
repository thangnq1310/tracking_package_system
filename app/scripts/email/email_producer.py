import ujson as json
import os

from kafka import KafkaProducer
from services.email_service import EmailService


class EmailProducer:
    def __init__(self):
        self.brokers = os.getenv('BOOTSTRAP_SERVERS', 'kafka1:9092,kafka2:9093,kafka3:9094')
        self.topic = os.getenv('EMAIL_TOPIC', 'email_topic')
        self.producer = KafkaProducer(bootstrap_servers=self.brokers)

    def send_message(self, data):
        self.producer.send(self.topic, str(json.encode(data)).encode('utf-8'))