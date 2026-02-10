from locust import HttpUser, between, task


class KafkaProducerUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task
    def send_batch_messages(self):
        self.client.post("/producers/person?number_of_people=1")
