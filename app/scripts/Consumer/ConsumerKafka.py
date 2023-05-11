import os

import requests
import logging
from kafka import KafkaConsumer
from dotenv import load_dotenv
from retry_webhook import RetryWebhook

from models.base import session as db
from models.model import *
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
            'pkg_code': package_data['pkg_code'],
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

            msg = f"[PROCESSING] Processing package of shop code: {shop['shop_id']} with pkg_code: " \
                  f"{msg['pkg_code']} and status: {msg['package_status_id']}"

            self.produce_logstash(msg, msg['pkg_code'])

            response = requests.post(url, data=params)
            response_time = response.elapsed.total_seconds()
            response_log = f"[RESPONSE] Response {response.text}: Receive package {msg['pkg_code']} " \
                               f"within {str(response_time)} seconds"
            self.produce_logstash(response_log, pkg_code=msg['pkg_code'])

        except requests.exceptions.Timeout as e:
            logging.error('[EXCEPTION] Timeout when sending webhook' + str(e))
            
            retry_webhook = RetryWebhook(topic=self.topic, brokers=self.brokers)
            message = f'[RETRY]: Retry sending package {msg["pkg_code"]} because of getting error server ' \
                        f'response'
            self.produce_logstash(message, msg['pkg_code'])
            retry_webhook.retry(msg['pkg_code'], response.status_code, msg)

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


consumer_kafka = ConsumerKafka()
consumer_kafka.run()
