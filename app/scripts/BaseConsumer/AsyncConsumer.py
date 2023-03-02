import asyncio
import aiohttp
import os
import time
import logging
from functools import reduce

import redis
from confluent_kafka import Producer
from kafka import KafkaConsumer
from dotenv import load_dotenv
import ujson as json

import constants
from retry_webhook import RetryWebhook
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
            host=os.getenv('REDIS_HOST', 'redis'),
            port=os.getenv('REDIS_PORT', 6379)
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
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id=self.group,
            max_poll_records=constants.LIMIT_MSG
        )

        while True:
            try:
                messages = client.poll(constants.TIMEOUT_MSG)

                is_timeout = False
                if not messages:
                    is_timeout = True
                else:
                    for _, raw_message in messages.items():
                        for message in raw_message:
                            self.decode_message(message)
                            is_current_topic = self.cache_message(self.package_data)

                            if not is_current_topic:
                                continue
                            self.list_msg.append(self.package_data)

                if len(self.list_msg) >= constants.LIMIT_MSG \
                        or is_timeout and len(self.list_msg) > 0:
                    async with aiohttp.ClientSession() as session:
                        start_time = time.time()
                        tasks = [self.get_task(session, task) for task in self.list_msg]
                        await asyncio.gather(*tasks)

                        self.list_msg = []
                        time_metrics = time.time() - start_time
                        print(f"TOTAL TIME FOR PROCESSING MESSAGES TO WEBHOOK: ", time_metrics)
            except (TimeoutError, Exception):
                logging.error(f"Timeout because not getting any message after {constants.TIMEOUT_MSG}", exc_info=True)

    def decode_message(self, msg):
        try:
            self.raw_package_data = json.loads(msg.value.decode('utf-8'))
            if 'payload' in self.raw_package_data:
                self.raw_package_data = self.raw_package_data['payload']

            self.ts_ms = str(self.raw_package_data['source']['ts_ms']) if 'source' \
                                in self.raw_package_data.keys() else self.raw_package_data['ts_ms']

            rs = self.format_message()
            if rs is False:
                print('No need to process message because status does not change')

            print("Package with code:", self.package_data['pkg_code'], "and status:",
                  self.package_data['package_status_id'])
        except (ValueError, Exception):
            logging.error("Cannot parse message because invalid format", exc_info=True)

    def format_message(self):
        is_retry = self.raw_package_data['is_retry'] if 'is_retry' in self.raw_package_data.keys() else 0
        if is_retry:
            package_data = self.raw_package_data['package_data']
            self.package_data = {
                'id': package_data['id'],
                'pkg_code': package_data['pkg_code'],
                'package_status_id': package_data['package_status_id'],
                'shop_id': package_data['shop_id'],
                'customer_id': package_data['customer_id'],
                'before_data': package_data['before_data'],
                'current_station_id': package_data['current_station_id'],
                'ts_ms': package_data['ts_ms'],
                'op': package_data['op']
            }
            return True
        else:
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
            shop_cached = self.cache.get(package_data['shop_id'])
            shop_cached = json.loads(shop_cached) if shop_cached else None

            package_data['webhook_url'] = shop_cached['webhook_url'] if shop_cached else None

            if shop_cached is None:
                shop = db.query(Shops.webhook_url).filter(Shops.id == package_data['shop_id']).first()
                package_data['webhook_url'] = shop[0] if shop else None
                payload = {'webhook_url': package_data['webhook_url'], 'time_responses': [], 'avg_response': None}
                self.cache.set(package_data['shop_id'], json.dumps(payload))
                return True

            cache_time = shop_cached['avg_response']

            if cache_time:
                if 3 > cache_time:
                    print(f'This message has been cached and will stay in {self.topic} topic')
                    return True
                elif 3 <= cache_time < 10:
                    print('This message has been cached, switch message to', constants.RANK_TOPIC[1])
                    self.producer_topic(constants.RANK_TOPIC[1], package_data)
                else:
                    print('This message has been cached, switch message to', constants.RANK_TOPIC[2])
                    self.producer_topic(constants.RANK_TOPIC[2], package_data)
                return False

            return True

        except (ValueError, Exception):
            logging.error('Has an error when caching', exc_info=True)

    def calculate_avg_response(self, shop_id, response_time):
        shop_cached = json.loads(self.cache.get(shop_id))
        time_responses = shop_cached['time_responses'] if 'time_responses' in shop_cached.keys() else []
        total_responses = shop_cached['total_responses'] if 'total_responses' in shop_cached.keys() else None

        if shop_cached:
            time_responses.append(response_time)
            if len(time_responses) < constants.LIMIT_REDIS_MSG:
                total_responses = reduce(lambda x, y: x + y, time_responses)
            else:
                first_response = time_responses.pop(0)
                total_responses = total_responses - first_response + response_time

            recalculated = total_responses / len(time_responses)
            shop_cached['time_responses'] = time_responses
            shop_cached['total_responses'] = total_responses
            shop_cached['avg_response'] = recalculated
            self.cache.set(shop_id, json.dumps(shop_cached))

    async def get_task(self, session, msg):
        base_url = os.getenv('WEBHOOK_URL')
        url = base_url + msg['webhook_url']
        shop_id = msg['shop_id']
        params = {
            'pkg_code': msg['pkg_code'],
            'package_status_id': msg['package_status_id'],
        }

        try:
            start_request = time.time()
            async with session.post(url, json=params, ssl=False, timeout=constants.TIMEOUT_REQUEST) as response:
                response_status = response.status
                if response_status in constants.STATUS_ALLOW:
                    retry_webhook = RetryWebhook(topic=self.topic, brokers=self.brokers)
                    retry_webhook.retry(msg['pkg_code'], response_status, msg)
                response_webhook = await response.json()
                end_result = time.time()
                response_time = round(end_result - start_request, 2)
                response_log = f"[INFO] Response: {response_webhook} within {str(response_time)} seconds"
                self.produce_logstash(response_log, pkg_code=params['pkg_code'])
                self.calculate_avg_response(shop_id, response_time)

        except (TimeoutError, Exception) as e:
            self.switch_topic(msg)
            print("Timeout for waiting for response, this request will be switched to alternative topic", e)

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

    def produce_logstash(self, msg, pkg_code):
        try:
            topic = os.getenv("LOG_STASH_TOPIC", "logstash_topic")
            self.producer.produce(topic, json.dumps(msg).encode('utf-8'), key=pkg_code)
            self.producer.poll(10)
            self.producer.flush()
        except Exception as e:
            logging.error('Has an error when producer to topic log stash: ' + str(e))
