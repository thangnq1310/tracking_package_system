import os

from scripts.BaseConsumer.AsyncConsumer import AsyncConsumer


# python worker.py Consumer PlatinumConsumer
class PlatinumConsumer(AsyncConsumer):
    def __init__(self):
        super().__init__()
        self.topic = os.getenv('PLATINUM_TOPIC', 'platinum_topic')
        self.group = os.getenv('PLATINUM_GROUP', 'platinum_group')