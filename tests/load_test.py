import locust
from locust import HttpUser, task, between
import random

class HRSystemUser(HttpUser):
    wait_time = between(1, 5)
    
    @task(3)
    def view_dashboard(self):
        self.client.get("/dashboard", headers={
            "Authorization": f"Bearer {self.token}"
        })

    @task(2) 
    def submit_activity(self):
        self.client.post("/api/activities", json={
            "user_id": f"user_{random.randint(1,1000)}",
            "activity_type": random.choice(["coding", "meeting", "research"]),
            "duration": random.randint(5, 120)
        }, headers={
            "Authorization": f"Bearer {self.token}"
        })

    @task(1)
    def get_analytics(self):
        self.client.get("/api/analytics/trends", params={
            "time_window": random.choice(["day", "week", "month"]),
            "department": random.choice(["eng", "product", "design"])
        }, headers={
            "Authorization": f"Bearer {self.token}"
        })

    def on_start(self):
        # Authenticate and store token
        response = self.client.post("/api/auth/login", json={
            "username": "load_tester",
            "password": "testpassword123"
        })
        self.token = response.json()["token"]

# Test Configuration
if __name__ == "__main__":
    import os
    os.system("locust -f load_test.py --headless -u 1000 -r 100 --host http://localhost:8080 --run-time 30m")
