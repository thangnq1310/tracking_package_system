import os
import sys
import ujson as json

sys.path.append('../../')
from scripts.consumer import ConsumerKafka
from services.email_service import EmailService


# python worker.py email_kafka EmailConsumer
class EmailConsumer(ConsumerKafka):
    def __init__(self):
        super().__init__()
        self.topic = os.getenv('EMAIL_TOPIC', 'email_topic')
        self.group = os.getenv('EMAIL_GROUP', 'email_group')
        self.brokers = os.getenv('BOOTSTRAP_SERVERS', 'kafka1:9092,kafka2:9093,kafka3:9094')

    def process_message(self, raw_msg):
        # call email service
        sender = raw_msg['shop']['email']
        recipient = raw_msg['customer']['email']
        email_service = EmailService(sender, recipient, raw_msg)
        email_service.send_email()
