import asyncio
import aiohttp
import os
import time

from kafka import KafkaConsumer
from dotenv import load_dotenv
import ujson as json
import sys


from models.model import Customers, Packages, Shops, Stations

import constants

sys.path.append('../')
from models.base import session
from models.model import *

load_dotenv()


# python worker.py consumer ConsumerKafka
class ConsumerKafka:
    __slots__ = ['ts_ms', 'list_msg', 'topic', 'brokers', 'group', 'limit_msg', 'raw_package_data', 'package_data']

    def __init__(self):
        self.topic = os.getenv('PACKAGE_TOPIC', 'connector.logistic.packages')
        self.group = os.getenv('PACKAGE_GROUP', 'package_group')
        self.brokers = os.getenv('BOOTSTRAP_SERVERS', 'kafka1:9092,kafka2:9093,kafka3:9094')
        self.ts_ms = None
        self.raw_package_data = None
        self.package_data = None

    def run(self):
        self.listen_message()

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
            max_poll_records=10
        )
        for message in client:
            start_time = time.time()
            self.process_msg(message)
            time_metrics = time.time() - start_time
            print("TIME PROCESS MSG WEBHOOK: ", time_metrics)

    def process_msg(self, msg):
        start_time = time.time()
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

        time_metrics = time.time() - start_time
        print("TIME PROCESS MSG WEBHOOK: ", time_metrics)

    def format_message(self):
        package_data = self.raw_package_data['after']

        before_data = {
            'package_status_id': None
        }
        # if 'before' in self.raw_package_data and self.raw_package_data['before'] is not None:
        #     if self.raw_package_data['before']['status'] != self.raw_package_data['after']['status']:
        #         return False
        #
        #     before_data = {
        #         'package_status_id': self.raw_package_data['before']['status']
        #     }

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

    def process_message(self, package_data):
        try:
            webhook_url = session.query(Shops.webhook_url).filter(Shops.id == package_data['shop_id']).first()

            self.package_data['webhook_url'] = str(webhook_url[0])


            # alpha - package status is shipped
            # if after['status'] == constants.PKG_STATUS['SHIPPED'] and shop_id == 1:
            #     customer = session.query(Customers.name, Customers.email). \
            #         join(Packages).filter(Packages.id == pkg_id).first()
            #     shop = session.query(Shops.name, Shops.email).join(Packages).filter(Packages.id == pkg_id).first()
            #     if customer and shop:
            #         params = {
            #             'status': after['status'],
            #             'pkg_order': after['pkg_order'],
            #             'customer': dict(customer),
            #             'shop': dict(shop)
            #         }
            #         email_producer = EmailProducer()
            #         email_producer.send_message(params)
            #         res = requests.post(url=f'{base_url}/alpha', json=json.dumps(params))
            #         print("RESPONSE: ", res.text, ", TOTAL TIME:", res.elapsed.total_seconds())
            #
            # # beta - when package is in station 2
            # if after['current_station_id'] == 2 and shop_id == 2:
            #     station_name = session.query(Stations.name). \
            #         join(Stations.packages).filter(Packages.id == pkg_id).first()
            #     if station_name:
            #         params = {
            #             'status': after['status'],
            #             'station_name': str(station_name),
            #             'pkg_order': after['pkg_order']
            #         }
            #         res = requests.post(url=f'{base_url}/beta', json=json.dumps(params))
            #         print("RESPONSE: ", res.text, ", TOTAL TIME:", res.elapsed.total_seconds())
            #
            # # gamma - customer in Ha Noi order
            # customer_id = after['customer_id']
            # customer = session.query(Customers.name, Customers.email) \
            #     .join(Packages) \
            #     .filter(Customers.id == customer_id) \
            #     .filter(Customers.address_id == 29) \
            #     .filter(Packages.id == pkg_id).first()
            #
            # if customer:
            #     params = {
            #         'status': after['status'],
            #         'pkg_order': after['pkg_order'],
            #         'customer': dict(customer)
            #     }
            #
            #     res = requests.post(url=f'{base_url}/gamma', json=json.dumps(params))
            #     print("RESPONSE: ", res.text, "TOTAL TIME:", res.elapsed.total_seconds())

        except Exception as e:
            print('[EXCEPTION] Has an error when post to webhook: ' + str(e))

    def get_tasks(self, session):
        tasks = []
        base_url = os.getenv('WEBHOOK_URL')
        for msg in self.list_msg:
            url = base_url + msg['url']
            tasks.append(session.post(url, ssl=False))

        return tasks


# python worker.py consumer AsyncConsumerKafka
class AsyncConsumerKafka:
    __slots__ = ['ts_ms', 'list_msg', 'topic', 'brokers', 'group', 'limit_msg', 'raw_package_data', 'package_data']

    def __init__(self):
        self.topic = os.getenv('PACKAGE_TOPIC', 'connector.logistic.packages')
        self.group = os.getenv('PACKAGE_GROUP', 'package_group_async')
        self.brokers = os.getenv('BOOTSTRAP_SERVERS', 'kafka1:9092,kafka2:9093,kafka3:9094')
        self.list_msg = []
        self.limit_msg = 50
        self.ts_ms = None
        self.raw_package_data = None
        self.package_data = None

    def run(self):
        asyncio.run(self.listen_message())

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
                    tasks = self.get_tasks(session)
                    responses = await asyncio.gather(*tasks)
                    for response in responses:
                        res = await response.json()
                        print(res)

                    self.list_msg = []
                    time_metrics = time.time() - start_time
                    print("TIME PROCESS MSG WEBHOOK: ", time_metrics)

    def process_msg(self, msg):
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
            if self.raw_package_data['before']['status'] != self.raw_package_data['after']['status']:
                return False

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

    def process_message(self, package_data):
        try:
            webhook_url = session.query(Shops.webhook_url).filter(Shops.id == package_data['shop_id']).first()

            self.package_data['webhook_url'] = str(webhook_url[0])
            # alpha - package status is shipped
            # if package_data['status'] == constants.PKG_STATUS['SHIPPED'] and shop_id == 1:
            #     customer = session.query(Customers.name, Customers.email). \
            #         join(Packages).filter(Packages.id == pkg_id).first()
            #     shop = session.query(Shops.name, Shops.email).join(Packages).filter(Packages.id == pkg_id).first()
            #     if customer and shop:
            #         params = {
            #             'status': after['status'],
            #             'pkg_order': after['pkg_order'],
            #             'customer': dict(customer),
            #             'shop': dict(shop)
            #         }
            #
            # # beta - when package is in station 2
            # if after['current_station_id'] == 2 and shop_id == 2:
            #     station_name = session.query(Stations.name). \
            #         join(Stations.packages).filter(Packages.id == pkg_id).first()
            #     if station_name:
            #         params = {
            #             'status': after['status'],
            #             'station_name': str(station_name),
            #             'pkg_order': after['pkg_order']
            #         }
            #         res = requests.post(url=f'{base_url}/beta', json=json.dumps(params))
            #         print("RESPONSE: ", res.text, ", TOTAL TIME:", res.elapsed.total_seconds())
            #
            # # gamma - customer in Ha Noi order
            # customer_id = after['customer_id']
            # customer = session.query(Customers.name, Customers.email) \
            #     .join(Packages) \
            #     .filter(Customers.id == customer_id) \
            #     .filter(Customers.address_id == 29) \
            #     .filter(Packages.id == pkg_id).first()
            #
            # if customer:
            #     params = {
            #         'status': after['status'],
            #         'pkg_order': after['pkg_order'],
            #         'customer': dict(customer)
            #     }
            #
            #     res = requests.post(url=f'{base_url}/gamma', json=json.dumps(params))
            #     print("RESPONSE: ", res.text, "TOTAL TIME:", res.elapsed.total_seconds())

        except Exception as e:
            print('[EXCEPTION] Has an error when post to webhook: ' + str(e))

    def get_tasks(self, session):
        tasks = []
        base_url = os.getenv('WEBHOOK_URL')
        for msg in self.list_msg:
            url = base_url + msg['webhook_url']
            params = {
                'pkg_code': msg['pkg_code'],
                'package_status_id': msg['package_status_id'],
            }
            tasks.append(session.post(url, json=params, ssl=False))

        return tasks
