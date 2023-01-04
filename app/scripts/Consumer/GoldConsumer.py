import os

from scripts.BaseConsumer.AsyncConsumerLow import AsyncConsumerLow


# python worker.py Consumer GoldConsumer
class GoldConsumer(AsyncConsumerLow):
    def __init__(self):
        super().__init__()
        self.topic = os.getenv('GOLD_TOPIC', 'gold_topic')
        self.group = os.getenv('GOLD_GROUP', 'gold_group')
        self.timeout_request = 6
