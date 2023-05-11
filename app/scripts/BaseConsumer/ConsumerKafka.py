import time

from confluent_kafka import Producer
from kafka import KafkaConsumer
import ujson as json
import os
import dotenv
import redis
import constants

from models.base import session
from models.model import Shops

dotenv.load_dotenv()


# python worker.py BaseConsumer ConsumerKafka
class ConsumerKafka:
    __slots__ = ['ts_ms', 'topic', 'brokers', 'group', 'raw_package_data', 'package_data', 'cache', 'producer']

    def __init__(self):
        self.topic = os.getenv('PACKAGE_TOPIC', 'connector.logistic.packages')
        self.group = os.getenv('PACKAGE_GROUP', 'package_group')
        self.brokers = os.getenv('BOOTSTRAP_SERVERS', 'kafka1:9092,kafka2:9093,kafka3:9094')
        self.ts_ms = None
        self.raw_package_data = None
        self.package_data = None
        self.cache = None
        self.producer = None

    def run(self):
        self.init_redis()
        self.init_producer()
        self.listen_message()

    def init_redis(self):
        self.cache = redis.Redis(
            host='redis',
            port=6379
        )

    def init_producer(self):
        producer_conf = {'bootstrap.servers': self.brokers}
        self.producer = Producer(**producer_conf)

    def listen_message(self):
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
            max_poll_records=1000
        )

        for message in client:
            self.decode_message(message)

    def decode_message(self, msg):
        try:
            self.raw_package_data = json.loads(msg.value.decode('utf-8'))
            if 'payload' in self.raw_package_data:
                self.raw_package_data = self.raw_package_data['payload']

            self.ts_ms = str(self.raw_package_data['source']['ts_ms'])

            rs = self.format_message()
            if rs is False:
                print('No need process message because status does not change')

            self.process_message(self.package_data)
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
            'pkg_code': package_data['code'],
            'package_status_id': package_data['status'],
            'shop_id': package_data['shop_id'],
            'customer_id': package_data['customer_id'],
            'current_station_id': package_data['current_station_id'],
            'before_data': before_data,
            'ts_ms': self.ts_ms,
            'op': self.raw_package_data['op']
        }
        return True

    def process_message(self, package_data):
        try:
            # cache shop
            cache_key = 'S' + str(package_data['shop_id'])
            shop_response_time = self.cache.get(cache_key)
            shop_response_time = json.loads(shop_response_time) if shop_response_time else None

            if shop_response_time is None:
                self.producer_topic(constants.RANK_TOPIC[0], package_data)
                return

            webhook_url = shop_response_time['webhook_url']
            cache_time = shop_response_time['cache_time']
            package_data['webhook_url'] = webhook_url

            if constants.PLATINUM_TIMEOUT_REQUEST > cache_time:
                msg = f"[CACHED] This package {package_data['pkg_code']} of shop code {package_data['shop_id']} " \
                          f"has been cached, switch message to {constants.RANK_TOPIC[0]}"
                self.produce_logstash(msg, package_data['pkg_code'])
                self.producer_topic(constants.RANK_TOPIC[0], package_data)
            elif constants.PLATINUM_TIMEOUT_REQUEST < cache_time < constants.GOLD_TIMEOUT_REQUEST:
                msg = f"[CACHED] This package {package_data['pkg_code']} of shop code {package_data['shop_id']} " \
                          f"has been cached, switch message to {constants.RANK_TOPIC[1]}"
                self.produce_logstash(msg, package_data['pkg_code'])
                self.producer_topic(constants.RANK_TOPIC[1], package_data)
            else:
                msg = f"[CACHED] This package {package_data['pkg_code']} of shop code {package_data['shop_id']} " \
                          f"has been cached, switch message to {constants.RANK_TOPIC[2]}"
                self.produce_logstash(msg, package_data['pkg_code'])
                self.producer_topic(constants.RANK_TOPIC[2], package_data)

        except Exception as e:
            print('[EXCEPTION] Has an error when post to webhook: ' + str(e))

    def producer_topic(self, topic, package_data):
        try:
            pkg_code = package_data['pkg_code']
            self.producer.produce(topic, json.dumps(package_data).encode('utf-8'), key=pkg_code)
            self.producer.poll(0)
        except Exception as e:
            print('[EXCEPTION] Has an error when producer to topic: ' + str(e))

    def produce_logstash(self, msg, pkg_code):
        try:
            topic = os.getenv("LOG_STASH_TOPIC", "logstash_topic")
            self.producer.produce(topic, json.dumps(msg).encode('utf-8'), key=pkg_code)
            self.producer.poll(10)
            self.producer.flush()
        except Exception as e:
            print('Has an error when producer to topic log stash: ' + str(e))

