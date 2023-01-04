import os

from scripts.BaseConsumer.AsyncConsumerLow import AsyncConsumerLow


# python worker.py Consumer SilverConsumer
class SilverConsumer(AsyncConsumerLow):
    def __init__(self):
        super().__init__()
        self.topic = os.getenv('SILVER_TOPIC', 'silver_topic')
        self.group = os.getenv('SILVER_GROUP', 'silver_group')
        self.timeout_request = 11
