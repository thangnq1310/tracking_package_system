import os

from scripts.consumer import AsyncConsumerKafka


class GoldConsumer(AsyncConsumerKafka):
    def __init__(self):
        super().__init__()
        self.topic = os.getenv('GOLD_TOPIC', 'gold_topic')
        self.group = os.getenv('GOLD_GROUP', 'gold_group')