import os

from scripts.BaseConsumer.AsyncConsumer import AsyncConsumer


# python worker.py Consumer GoldConsumer
class GoldConsumer(AsyncConsumer):
    def __init__(self):
        super().__init__()
        self.topic = os.getenv('GOLD_TOPIC', 'gold_topic')
        self.group = os.getenv('GOLD_GROUP', 'gold_group')