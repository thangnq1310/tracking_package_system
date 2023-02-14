import json

from locust import HttpUser, TaskSet, task

class Message(HttpUser):
    @task
    def get_alpha(self):
        self.client.post('/alpha', data={'message': 1})

    @task
    def get_beta(self):
        self.client.post('/beta', data={'message': 1})

    @task
    def get_gamma(self):
        self.client.post('/gamma', data={'message': 1})