import os

import requests
from kafka import KafkaConsumer
from dotenv import load_dotenv

from infrastructures.http_connector import HTTPConnectorService
from services.email_service import *
from models.base import session
from models.model import *
import constants

load_dotenv()


class ConsumerKafka:
    def __init__(self):
        self.topic = os.getenv('PACKAGE_TOPIC', 'connector.logistic.packages')
        self.group = os.getenv('PACKAGE_GROUP', 'package_group')
        self.brokers = os.getenv('BOOTSTRAP_SERVERS', 'kafka1:9092,kafka2:9093,kafka3:9094')

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
            raw_msg = json.loads(msg.value)
            if 'payload' in raw_msg:
                raw_msg = raw_msg['payload']

            self.process_message(raw_msg)

    def process_message(self, raw_msg):
        try:
            after = raw_msg['after']
            pkg_id = after['id']
            # apple - package status is shipped
            if after['status'] == constants.PKG_STATUS['SHIPPED']:
                customer = session.query(Customers.name, Customers.email). \
                                join(Packages).filter(Packages.id == pkg_id).first()
                shop = session.query(Shops.name, Shops.email).join(Packages).filter(Packages.id == pkg_id).first()
                if customer and shop:
                    params = {
                        'status': after['status'],
                        'pkg_order': after['pkg_order'],
                        'customer': dict(customer),
                        'shop': dict(shop)
                    }
                    print(params, "PARAMS")
                    # res = requests.post(url='http://localhost:5000/webhooks/tiktok', json=json.dumps(params))
                    #
                    # print(res.text)
                    apple_service = HTTPConnectorService(params=params, url='/apple')
                    apple_service.do_request()

            # shopee - when package is in station 2
            if after['current_station_id'] == 2:
                station_name = session.query(Stations.name). \
                                   join(Stations.packages).filter(Packages.id == pkg_id).filter(
                    Stations.id == 2).first()
                if station_name:
                    params = {
                        'status': after['status'],
                        'station_name': str(station_name),
                        'pkg_order': after['pkg_order']
                    }
                    print(station_name, "shopee")
                    shopee_service = HTTPConnectorService(params=params, url='/shopee')
                    shopee_service.do_request()

            # tiktok - customer in Ha Noi order
            customer_id = after['customer_id']
            customer = session.query(Customers.name, Customers.email) \
                            .join(Packages) \
                            .filter(Customers.id == customer_id) \
                            .filter(Customers.address_id == 29) \
                            .filter(Packages.id == pkg_id).first()

            if customer:
                params = {
                    'status': after['status'],
                    'pkg_order': after['pkg_order'],
                    'customer': dict(customer)
                }
                print(customer, "tiktok")

                # res = requests.post(url='http://localhost:5000/webhooks/tiktok', data=params)
                #
                # print(res)

        except Exception as e:
            print('[EXCEPTION] Has an error when post to webhook: ' + str(e))


consumer_kafka = ConsumerKafka()
consumer_kafka.run()
