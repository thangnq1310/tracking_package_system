import os

import logging
import asyncio
import aiohttp
import redis
from kafka import KafkaConsumer
from confluent_kafka import Producer
from dotenv import load_dotenv
import constants
import time

import ujson as json

from retry_webhook import RetryWebhook
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
        self.cache = None
        self.producer = None
        self.list_msg = []

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
        self.cache = redis.Redis(
            host='redis',
            port=6379
        )
        self.producer = Producer(**{'bootstrap.servers': self.brokers})
        asyncio.run(self.listen_message())

    async def listen_message(self):
        consumer = self.connect_kafka()
        for msg in consumer:
            self.raw_msg = json.loads(msg.value)

            self.format_message(self.raw_msg)
            self.list_msg.append(self.msg)
            if len(self.list_msg) >= constants.LIMIT_MSG and len(self.list_msg) > 0:
                async with aiohttp.ClientSession() as session:
                    start_time = time.time()
                    tasks = [self.get_task(session, task) for task in self.list_msg]
                    await asyncio.gather(*tasks)

                    self.list_msg = []
                    time_metrics = time.time() - start_time
                    print(f"[METRIC] Metric time for processing messages to webhook: ", round(time_metrics, 2))

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

    async def get_task(self, session, msg):
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

            start_request = time.time()
            async with session.post(url, json=params, ssl=False, timeout=constants.PLATINUM_TIMEOUT_REQUEST) \
                    as response:
                response_status = response.status
                if response_status in constants.STATUS_ALLOW:
                    retry_webhook = RetryWebhook(topic=self.topic, brokers=self.brokers)
                    message = f'[RETRY]: Retry sending package {msg["pkg_code"]} because of getting error server ' \
                            f'response'
                    self.produce_logstash(message, msg['pkg_code'])
                    retry_webhook.retry(msg['pkg_code'], response_status, msg)
                end_result = time.time()
                response_time = round(end_result - start_request, 2)
                response_log = f"[RESPONSE] Response {response}: Receive package {params['pkg_code']} " \
                            f"within {str(response_time)} seconds"
                self.produce_logstash(response_log, pkg_code=msg['pkg_code'])

                if not cache_time:
                    cache_time = response_time
                    self.cache.set(cache_key, json.dumps({
                        'webhook_url': webhook_url,
                        'cache_time': cache_time
                    }))

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