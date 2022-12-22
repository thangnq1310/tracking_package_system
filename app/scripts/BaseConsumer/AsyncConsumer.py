import asyncio
import aiohttp
import os
import time

from kafka import KafkaConsumer
from dotenv import load_dotenv
import ujson as json
import sys

load_dotenv()


# python worker.py Consumer AsyncConsumer
class AsyncConsumer:
    __slots__ = ['list_msg', 'topic', 'brokers', 'group', 'limit_msg', 'package_data']

    def __init__(self):
        self.brokers = os.getenv('BOOTSTRAP_SERVERS', 'kafka1:9092,kafka2:9093,kafka3:9094')
        self.topic = None
        self.group = None
        self.list_msg = []
        self.limit_msg = 50
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
            self.package_data = json.loads(msg.decode('utf-8'))
        except Exception as e:
            print("Cannot parse message -> Invalid format" + str(e))

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
