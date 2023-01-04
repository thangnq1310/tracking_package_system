import asyncio
import aiohttp
import os
import time

import redis
from confluent_kafka import Producer
from kafka import KafkaConsumer
from dotenv import load_dotenv
import ujson as json

import constants
from models.base import session as db
from models.model import Shops

load_dotenv()


# python worker.py BaseConsumer AsyncConsumer
class AsyncConsumer:
    __slots__ = ['list_msg', 'topic', 'brokers', 'group', 'limit_msg', 'raw_package_data', 'ts_ms', 'cache',
                 'package_data', 'timeout_msg', 'timeout_request', 'producer']

    def __init__(self):
        self.brokers = os.getenv('BOOTSTRAP_SERVERS', 'kafka1:9092,kafka2:9093,kafka3:9094')
        self.topic = os.getenv('PACKAGE_TOPIC', 'connector.logistic.packages')
        self.group = os.getenv('PACKAGE_GROUP', 'package_group')
        self.list_msg = []
        self.limit_msg = 50
        self.timeout_msg = 5000
        self.timeout_request = 3
        self.package_data = None
        self.raw_package_data = None
        self.ts_ms = None
        self.cache = None
        self.producer = None

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
                            current_topic = self.decode_message(message)
                            if not current_topic:
                                continue
                            self.list_msg.append(self.package_data)

                if len(self.list_msg) >= self.limit_msg \
                        or is_timeout and len(self.list_msg) > 0:
                    async with aiohttp.ClientSession() as session:
                        start_time = time.time()
                        tasks = [self.get_task(session, task) for task in self.list_msg]
                        await asyncio.gather(*tasks)

                        self.list_msg = []
                        time_metrics = time.time() - start_time
                        print("TIME PROCESS MSG WEBHOOK: ", time_metrics)
            except Exception as e:
                print('Timeout message ' + str(e))

    async def get_task(self, session, msg):
        base_url = os.getenv('WEBHOOK_URL')
        url = base_url + msg['webhook_url']
        params = {
            'pkg_code': msg['pkg_code'],
            'package_status_id': msg['package_status_id'],
        }

        try:
            async with session.post(url, json=params, ssl=False, timeout=self.timeout_request) as response:
                response_webhook = await response.json()

                print(response_webhook)
        except Exception as e:
            self.switch_topic(self.package_data)
            print("Exception timeout " + str(e))

    def decode_message(self, msg):
        try:
            self.raw_package_data = json.loads(msg.value.decode('utf-8'))
            if 'payload' in self.raw_package_data:
                self.raw_package_data = self.raw_package_data['payload']

            self.ts_ms = str(self.raw_package_data['source']['ts_ms'])

            rs = self.format_message()
            if rs is False:
                print('No need process message because status does not change')

            current_topic = self.cache_message(self.package_data)

            print("Package with code:", self.package_data['pkg_code'],
                  "and status:", self.package_data['package_status_id'])

            return current_topic
        except Exception as e:
            print("Cannot parse message -> Invalid format" + str(e))

    def format_message(self):
        package_data = self.raw_package_data['after']

        before_data = {
            'package_status_id': None
        }
        if 'before' in self.raw_package_data and self.raw_package_data['before'] is not None:
            before_data = {
                'package_status_id': self.raw_package_data['before']['status']
            }

        self.package_data = {
            'id': package_data['id'],
            'pkg_code': package_data['pkg_order'],
            'package_status_id': package_data['status'],
            'shop_id': package_data['shop_id'],
            'customer_id': package_data['customer_id'],
            'current_station_id': package_data['current_station_id'],
            'before_data': before_data,
            'ts_ms': self.ts_ms,
            'op': self.raw_package_data['op']
        }
        return True

    def cache_message(self, package_data):
        try:
            # cache shop
            shop_response_time = self.cache.get(package_data['shop_id'])
            shop_response_time = json.loads(shop_response_time) if shop_response_time else None

            package_data['webhook_url'] = shop_response_time['webhook_url'] if shop_response_time else None

            if shop_response_time is None:
                shop = db.query(Shops.webhook_url, Shops.name)\
                                    .filter(Shops.id == package_data['shop_id']).first()
                shop = dict(shop)
                shop_name = shop['name']
                if shop_name == 'Alpha':
                    shop['cache_time'] = 2
                elif shop_name == 'Beta':
                    shop['cache_time'] = 10
                else:
                    shop['cache_time'] = 5

                package_data['webhook_url'] = shop['webhook_url']
                self.cache.set(package_data['shop_id'], json.dumps(shop))

                return True

            cache_time = shop_response_time['cache_time']

            if 5 > cache_time >= 2:
                print('Message in current topic')
                return True
            elif 5 <= cache_time < 10:
                print('Switch message to', constants.RANK_TOPIC[1])
                self.producer_topic(constants.RANK_TOPIC[1], package_data)
            else:
                print('Switch message to', constants.RANK_TOPIC[2])
                self.producer_topic(constants.RANK_TOPIC[2], package_data)

            return False

        except Exception as e:
            print('[EXCEPTION] Has an error when caching: ' + str(e))

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
            print('[EXCEPTION] Has an error when producer to topic: ' + str(e))
