"""
Load testing script to validate handling of 5K+ concurrent alerts
Run with: locust -f load_test.py --host=http://localhost:8000
"""

from locust import HttpUser, task, between
import random
import string


def generate_alert_id():
    """Generate random alert ID"""
    return f"ALERT-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"


class MarketSupervisionUser(HttpUser):
    """Simulated user for load testing"""
    wait_time = between(0.1, 0.5)  # Rapid requests for stress testing
    
    @task(3)
    def get_statistics(self):
        """Test statistics endpoint with caching"""
        self.client.get("/api/alerts/statistics/")
    
    @task(2)
    def get_risk_trends(self):
        """Test risk trends endpoint"""
        self.client.get("/api/alerts/risk_trends/")
    
    @task(2)
    def get_top_companies(self):
        """Test top companies endpoint with denormalized data"""
        self.client.get("/api/alerts/top_companies/")
    
    @task(1)
    def list_alerts(self):
        """Test alert listing with filters"""
        severity = random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'])
        self.client.get(f"/api/alerts/?severity={severity}")
    
    @task(1)
    def batch_process_alerts(self):
        """Test Celery batch processing with concurrent alerts"""
        # Generate batch of alert IDs
        batch_size = random.randint(100, 500)  # Simulate batches
        alert_ids = [generate_alert_id() for _ in range(batch_size)]
        
        self.client.post(
            "/api/alerts/batch_process/",
            json={"alert_ids": alert_ids}
        )


class HighLoadUser(HttpUser):
    """Extreme load user for 5K+ concurrent simulation"""
    wait_time = between(0.01, 0.1)  # Very aggressive
    
    @task
    def rapid_statistics(self):
        """Rapidly hit cached statistics endpoint"""
        self.client.get("/api/alerts/statistics/")


# To run load test validating 5K+ concurrent:
# locust -f load_test.py --host=http://localhost:8000 -u 5000 -r 100 --run-time 60s
# This spawns 5000 users at rate of 100/sec for 60 seconds
