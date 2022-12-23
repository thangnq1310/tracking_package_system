import os

from scripts.BaseConsumer.AsyncConsumer import AsyncConsumer


# python worker.py Consumer SilverConsumer
class SilverConsumer(AsyncConsumer):
    def __init__(self):
        super().__init__()
        self.topic = os.getenv('SILVER_TOPIC', 'silver_topic')
        self.group = os.getenv('SILVER_GROUP', 'silver_group')