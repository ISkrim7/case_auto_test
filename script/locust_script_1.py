
from locust import HttpUser, task, between
import json

class DynamicUser(HttpUser):
    wait_time = between(1, 2.5)

    @task
    def test_api(self):
        headers = {}
        body = {}
        method = "get"
        if method == "get":
            self.client.get("", headers=headers)
        elif method == "post":
            self.client.post("", json=body, headers=headers)
        elif method == "put":
            self.client.put("", json=body, headers=headers)
        elif method == "delete":
            self.client.delete("", headers=headers)
