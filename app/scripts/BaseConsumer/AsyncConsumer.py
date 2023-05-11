import os

import requests
import logging
import redis
from kafka import KafkaConsumer
from confluent_kafka import Producer
from dotenv import load_dotenv

import ujson as json

from models.base import session
from models.model import Shops

load_dotenv()


class AsyncConsumer:
    def __init__(self):
        self.topic = os.getenv('PACKAGE_TOPIC', 'connector.logistic.packages')
        self.group = os.getenv('PACKAGE_GROUP', 'package_group')
        self.brokers = os.getenv('BOOTSTRAP_SERVERS', 'kafka1:9092,kafka2:9093,kafka3:9094')
        self.raw_msg = None
        self.msg = None
        self.ts_ms = None
        self.cache = redis.Redis(
            host='redis',
            port=6379
        )
        self.producer = Producer(**{'bootstrap.servers': self.brokers})

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

            self.format_message(self.raw_msg)
            self.process_message(self.msg)

    def format_message(self, package_data):
        self.msg = {
            'id': package_data['id'],
            'pkg_code': package_data['pkg_code'],
            'package_status_id': package_data['package_status_id'],
            'shop_id': package_data['shop_id'],
            'customer_id': package_data['customer_id'],
            'current_station_id': package_data['current_station_id'],
        }
        return True

    def process_message(self, msg):
        try:
            params = {
                'pkg_code': msg['pkg_code'],
                'package_status_id': int(msg['package_status_id'])
            }

            cache_key = 'S' + str(msg['shop_id'])
            shop_response_time = self.cache.get(cache_key)
            shop_response_time = json.loads(shop_response_time) if shop_response_time else None
            
            webhook_url = shop_id = cache_time = None
            if shop_response_time is None:
                shop = session.query(Shops.webhook_url, Shops.id)\
                                    .filter(Shops.id == msg['shop_id']).first()
                webhook_url, shop_id = shop
            else:
                webhook_url, cache_time, shop_id = shop_response_time['webhook_url'], \
                                            shop_response_time['cache_time'], msg['shop_id']
            
            url = os.getenv('WEBHOOK_URL') + webhook_url

            message = f"[PROCESSING] Processing package of shop code: {shop_id} with pkg_code: " \
                  f"{msg['pkg_code']} and status: {msg['package_status_id']}"

            self.produce_logstash(message, msg['pkg_code'])

            response = requests.post(url, json=params)
            response_time = response.elapsed.total_seconds()
            if not cache_time:
                cache_time = response_time
                self.cache.set(cache_key, json.dumps({
                    'webhook_url': webhook_url,
                    'cache_time': cache_time
                }))

            response_log = f"[RESPONSE] Response {response.text}: Receive package {msg['pkg_code']} " \
                               f"within {str(response_time)} seconds"
            self.produce_logstash(response_log, pkg_code=msg['pkg_code'])

        except Exception as e:
            logging.error('[EXCEPTION] Has an error when post to webhook: ' + str(e))

    def produce_logstash(self, msg, pkg_code):
        try:
            topic = os.getenv("LOG_STASH_TOPIC", "logstash_topic")
            self.producer.produce(topic, json.dumps(msg).encode('utf-8'), key=pkg_code)
            self.producer.poll(10)
            self.producer.flush()
        except Exception as e:
            logging.error('Has an error when producer to topic log stash: ' + str(e))