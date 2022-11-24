import os
import time
from kafka import KafkaConsumer
import ujson as json
import dotenv
import requests

dotenv.load_dotenv()

class CustomerWorker():
    def __init__(self):
        self.topic = os.getenv('CUSTOMER_TOPIC', 'dbserver1.sakila.customers')
        self.group = os.getenv('CUSTOMER_GROUP', 'customer_group')
        self.brokers = os.getenv('BOOTSTRAP_SERVERS', 'kafka1:9092,kafka2:9093,kafka3:9094')
        self.webhook_url = os.getenv('WEBHOOK_URL', 'https://webhook.site/16ee7df2-0643-4759-aa89-447bc283f06f')

    
    def connect_kafka(self):
        print('CONSUMER TOPIC: ' + self.topic)
        print('CONSUMER GROUP: ' + self.group)
        print('CONSUMER BROKERS: ' + self.brokers)

        brokers = self.brokers.split(',')
        return KafkaConsumer(
            self.topic, 
            bootstrap_servers=brokers,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='customers_group',
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
            res = requests.post(self.webhook_url, data=json.dumps(raw_msg), headers={'Content-Type': 'application/json'})
            print(res)
        except Exception as e:
            print('[EXCEPTION] Has an error when updating shop contacts ' + str(e))



kafka_consumer = CustomerWorker()
kafka_consumer.run()