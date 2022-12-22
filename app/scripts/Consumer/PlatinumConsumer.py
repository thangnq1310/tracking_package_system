import os

from scripts.consumer import AsyncConsumerKafka


class PlatinumConsumer(AsyncConsumerKafka):
    def __init__(self):
        super().__init__()
        self.topic = os.getenv('PLATINUM_TOPIC', 'platinum_topic')
        self.group = os.getenv('PLATINUM_GROUP', 'platinum_group')