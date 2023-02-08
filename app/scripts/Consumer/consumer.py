import os

import requests
from kafka import KafkaConsumer
from dotenv import load_dotenv

from models.base import session as db
from models.model import *
import constants
import ujson as json

load_dotenv()


class ConsumerKafka:
    def __init__(self):
        self.topic = os.getenv('PACKAGE_TOPIC', 'connector.logistic.packages')
        self.group = os.getenv('PACKAGE_GROUP', 'package_group')
        self.brokers = os.getenv('BOOTSTRAP_SERVERS', 'kafka1:9092,kafka2:9093,kafka3:9094')
        self.raw_msg = None
        self.msg = None
        self.ts_ms = None

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
            group_id=self.group,
            max_poll_records=1000
        )

    def run(self):
        consumer = self.connect_kafka()
        for msg in consumer:
            self.raw_msg = json.loads(msg.value)
            if 'payload' in self.raw_msg.keys():
                self.raw_msg = self.raw_msg['payload']
            self.ts_ms = str(self.raw_msg['source']['ts_ms'])
            self.format_message()
            self.process_message(self.msg)

    def format_message(self):
        package_data = self.raw_msg['after']
        before_data = {
            'package_status_id': None
        }
        if 'before' in self.raw_msg and self.raw_msg['before'] is not None:
            before_data = {
                'package_status_id': self.raw_msg['before']['status']
            }
        self.msg = {
            'id': package_data['id'],
            'pkg_code': package_data['pkg_order'],
            'package_status_id': package_data['status'],
            'shop_id': package_data['shop_id'],
            'customer_id': package_data['customer_id'],
            'current_station_id': package_data['current_station_id'],
            'before_data': before_data,
            'ts_ms': self.ts_ms,
            'op': self.raw_msg['op']
        }
        return True

    def process_message(self, msg):
        try:
            params = {
                'pkg_code': msg['pkg_code'],
                'status': msg['package_status_id']
            }

            shop = db.query(Shops.webhook_url).filter(Shops.id == msg['shop_id']).first()
            shop = dict(shop)
            webhook_url = shop['webhook_url']
            url = os.getenv('WEBHOOK_URL') + webhook_url

            response = requests.post(url, data=params)
            print("RESPONSE:", response)

        except Exception as e:
            print('[EXCEPTION] Has an error when post to webhook: ' + str(e))


consumer_kafka = ConsumerKafka()
consumer_kafka.run()
