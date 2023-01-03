import os

from scripts.BaseConsumer.AsyncConsumer import AsyncConsumer


# python worker.py Consumer PlatinumConsumer
class PlatinumConsumer(AsyncConsumer):
    def __init__(self):
        super().__init__()