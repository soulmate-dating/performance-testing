import uuid

from locust import HttpUser, TaskSet, task, between, User
from locust.contrib.fasthttp import FastHttpUser
import faker


fake_gen = faker.Faker()

user_id_1 = fake_gen.uuid4()
user_id_2 = fake_gen.uuid4()


class MessageApiUser(TaskSet):

    @task(1)
    def send_message_1(self):
        user_id = user_id_1
        recipient_id = user_id_2
        message_data = {
            "recipient_id": recipient_id,
            "content": fake_gen.sentence()
        }
        self.client.post(f"/users/{user_id}/messages", json=message_data)

    @task(1)
    def send_message_2(self):
        user_id = user_id_2
        recipient_id = user_id_1
        message_data = {
            "recipient_id": recipient_id,
            "content": fake_gen.sentence()
        }
        self.client.post(f"/users/{user_id}/messages", json=message_data)

    @task(1)
    def get_messages_1(self):
        user_id = user_id_1
        companion_id = user_id_2
        params = {
            "companion_id": companion_id,
            "page": fake_gen.random_int(1, 100),
            "size": fake_gen.random_int(10, 14)
        }
        self.client.get(f"/users/{user_id}/messages", params=params)

    @task(1)
    def get_messages_2(self):
        user_id = user_id_2
        companion_id = user_id_1
        params = {
            "companion_id": companion_id,
            "page": fake_gen.random_int(1, 100),
            "size": fake_gen.random_int(10, 14)
        }
        self.client.get(f"/users/{user_id}/messages", params=params)


class WebsiteUser(FastHttpUser):
    network_timeout = 5.0
    connection_timeout = 5.0
    tasks = [MessageApiUser]
    wait_time = between(0.01, 0.02)
