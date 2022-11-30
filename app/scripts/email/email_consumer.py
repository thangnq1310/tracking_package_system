import os

from consumer import ConsumerKafka


class EmailConsumer(ConsumerKafka):
    def __init__(self):
        super().__init__()
        self.topic = os.getenv('EMAIL_TOPIC', 'email_topic')
        self.group = os.getenv('EMAIL_GROUP', 'email_group')
        self.brokers = os.getenv('BOOTSTRAP_SERVERS', 'kafka1:9092,kafka2:9093,kafka3:9094')

    def process_message(self, raw_msg):
        # call email service
        pass