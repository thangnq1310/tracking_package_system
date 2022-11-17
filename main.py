import os
import time
from kafka import KafkaConsumer
import ujson as json


class KafkaConsumer():
    def __init__(self):
        self.topic = os.getenv('INVENTORY_CUSTOMER_TOPIC', 'dbserver1.inventory.customers')
        self.group = os.getenv('INVENTORY_CUSTOMER_GROUP', 'inventory_group')
        self.brokers = os.getenv('BOOTSTRAP_BROKERS', 'kafka1:9092,kafka2:9093,kafka3:9094')

    
    def connect_kafka(self):
        print('CONSUMER TOPIC: ' + self.topic)
        print('CONSUMER GROUP: ' + self.group)
        print('CONSUMER BROKERS: ' + self.brokers)

        brokers = self.brokers.split(',')
        return KafkaConsumer(
            self.topic, 
            bootstrap_servers=brokers,
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id=self.group_id,
            max_poll_records=1000
        )