import asyncio
import logging
from functools import reduce

import aiohttp
import os
import time

import redis
from confluent_kafka import Producer
from kafka import KafkaConsumer
from dotenv import load_dotenv
import ujson as json

import constants

load_dotenv()


# python worker.py BaseConsumer AsyncConsumerLow
class AsyncConsumerLow:
    __slots__ = ['list_msg', 'topic', 'brokers', 'group', 'limit_msg',
                 'package_data', 'timeout_msg', 'timeout_request', 'producer', 'cache']

    def __init__(self):
        self.brokers = os.getenv('BOOTSTRAP_SERVERS', 'kafka1:9092,kafka2:9093,kafka3:9094')
        self.topic = None
        self.group = None
        self.list_msg = []
        self.limit_msg = 50
        self.timeout_msg = 5000
        self.timeout_request = 5
        self.package_data = None
        self.producer = None
        self.cache = None

    def run(self):
        self.init_producer()
        self.init_redis()
        asyncio.run(self.listen_message())

    def init_redis(self):
        self.cache = redis.Redis(
            host='redis',
            port=6379
        )

    def init_producer(self):
        producer_conf = {'bootstrap.servers': self.brokers}
        self.producer = Producer(**producer_conf)

    async def listen_message(self):
        print('CONSUMER TOPIC: ' + self.topic)
        print('CONSUMER GROUP: ' + self.group)
        print('CONSUMER BROKERS: ' + self.brokers)

        brokers = self.brokers.split(',')
        client = KafkaConsumer(
            self.topic,
            bootstrap_servers=brokers,
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id=self.group,
            max_poll_records=self.limit_msg
        )

        while True:
            try:
                messages = client.poll(self.timeout_msg)

                is_timeout = False
                if not messages:
                    is_timeout = True
                else:
                    for _, raw_message in messages.items():
                        for message in raw_message:
                            self.process_msg(message)
                            self.list_msg.append(self.package_data)

                if len(self.list_msg) >= self.limit_msg \
                        or is_timeout and len(self.list_msg) > 0:
                    async with aiohttp.ClientSession() as session:
                        start_time = time.time()
                        tasks = [self.get_task(session, task) for task in self.list_msg]
                        await asyncio.gather(*tasks)

                        self.list_msg = []
                        time_metrics = time.time() - start_time
                        print(f"TOTAL TIME FOR PROCESSING MESSAGES TO WEBHOOK: ", time_metrics)
            except (TimeoutError, Exception):
                logging.error(f"Timeout because not getting any message after {self.timeout_msg}", exc_info=True)

    def process_msg(self, msg):
        try:
            self.package_data = json.loads(msg.value.decode('utf-8'))

            print("Package with code:", self.package_data['pkg_code'],
                  "and status:", self.package_data['package_status_id'])
        except (ValueError, Exception):
            logging.error("Cannot parse message because invalid format", exc_info=True)

    async def get_task(self, session, msg):
        base_url = os.getenv('WEBHOOK_URL')
        url = base_url + msg['webhook_url']
        shop_id = msg['shop_id']
        params = {
            'pkg_code': msg['pkg_code'],
            'package_status_id': msg['package_status_id'],
        }

        try:
            async with session.post(url, json=params, ssl=False, timeout=self.timeout_request) as response:
                response_webhook = await response.json()
                response_time = round(response_webhook.elapsed.total_seconds(), 2)

                shop_cached = json.loads(self.cache.get(shop_id))
                time_responses = shop_cached['time_responses']

                if shop_cached:
                    time_responses.append(response_time)
                    recalculated = reduce(lambda x, y: x + y, time_responses) / len(time_responses)
                    shop_cached['time_responses'] = time_responses
                    shop_cached['avg_response'] = recalculated
                    self.cache.set(shop_id, json.dumps(shop_cached))
        except (TimeoutError, Exception):
            self.switch_topic(self.package_data)
            print("Timeout for waiting for response, this request will be switched to alternative topic")

    def switch_topic(self, message):
        rank_topic = constants.RANK_TOPIC
        for index, topic in enumerate(rank_topic):
            if topic == self.topic and index != len(rank_topic) - 1:
                self.producer_topic(rank_topic[index + 1], message)

    def producer_topic(self, topic, package_data):
        try:
            pkg_code = package_data['pkg_code']
            self.producer.produce(topic, json.dumps(package_data).encode('utf-8'), key=pkg_code)
            self.producer.poll(0)
            self.producer.flush()
        except Exception as e:
            logging.error('Has an error when producer to topic: ' + str(e))
