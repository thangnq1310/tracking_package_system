import asyncio
import aiohttp
import os
import time
import logging

from confluent_kafka import Producer
from kafka import KafkaConsumer
from dotenv import load_dotenv
import ujson as json

import constants
from retry_webhook import RetryWebhook

load_dotenv()


# python worker.py Consumer AsyncConsumer
class AsyncConsumer:
    __slots__ = ['list_msg', 'topic', 'brokers', 'group', 'limit_msg', 'package_data', 'producer', 'base_url']

    def __init__(self):
        self.brokers = os.getenv('BOOTSTRAP_SERVERS', 'kafka1:9092,kafka2:9093,kafka3:9094')
        self.topic = None
        self.group = None
        self.list_msg = []
        self.limit_msg = 50
        self.package_data = None
        self.producer = None
        self.base_url = os.getenv('WEBHOOK_URL')

    def run(self):
        self.init_producer()
        asyncio.run(self.listen_message())

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
            max_poll_records=100
        )

        for message in client:
            self.process_msg(message)
            self.list_msg.append(self.package_data)

            if len(self.list_msg) >= self.limit_msg:
                async with aiohttp.ClientSession() as session:
                    start_time = time.time()
                    tasks = [self.get_task(session, task) for task in self.list_msg]
                    await asyncio.gather(*tasks)
                    
                    self.list_msg = []
                    time_metrics = time.time() - start_time
                    print(f"[METRIC] Metric time for processing messages to webhook: ", round(time_metrics, 2))

    def process_msg(self, msg):
        try:
            self.package_data = json.loads(msg.value.decode('utf-8'))
            self.format_message()

            msg = f"[PROCESSING] Processing package of shop code: {self.package_data['shop_id']} with pkg_code: " \
                  f"{self.package_data['pkg_code']} and status: {self.package_data['package_status_id']}"
            
            self.produce_logstash(msg, self.package_data['pkg_code'])
        except Exception as e:
            print("Cannot parse message -> Invalid format" + str(e))

    def format_message(self):
        package_data = self.raw_msg['after']
        before_data = {
            'package_status_id': None
        }
        if 'before' in self.raw_msg and self.raw_msg['before'] is not None:
            before_data = {
                'package_status_id': self.raw_msg['before']['status']
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
            'op': self.raw_msg['op']
        }

    async def get_task(self, session, msg):
        url = self.base_url + msg['webhook_url']
        params = {
            'pkg_code': msg['pkg_code'],
            'package_status_id': msg['package_status_id'],
        }

        start_request = time.time()
        async with session.post(url, json=params, ssl=False) \
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
            self.produce_logstash(response_log, pkg_code=params['pkg_code'])

    def produce_logstash(self, msg, pkg_code):
        try:
            topic = os.getenv("LOG_STASH_TOPIC", "logstash_topic")
            self.producer.produce(topic, json.dumps(msg).encode('utf-8'), key=pkg_code)
            self.producer.poll(10)
            self.producer.flush()
        except Exception as e:
            logging.error('Has an error when producer to topic log stash: ' + str(e))
