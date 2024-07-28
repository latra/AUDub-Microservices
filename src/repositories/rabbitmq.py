import pika
from typing import Any

class RabbitMQConnector:
    def __init__(self, config: dict) -> None:
        self.host = config['rabbitmq']['host']
        self.user = config['rabbitmq']['username']
        self.password = config['rabbitmq']['password']
        self.job_queue =  config['rabbitmq']['job_queue']
        self.status_queue =  config['rabbitmq']['status_queue']
        self.credentials = pika.PlainCredentials(self.user, self.password)

    def subscribe(self, callback: function):
        subscription_connection = pika.BlockingConnection(pika.ConnectionParameters(self.host, credentials=self.credentials))
        channel = subscription_connection.channel()

        channel.queue_declare(queue=self.job_queue)
        channel.basic_consume(queue=self.job_queue, on_message_callback=lambda ch, method, properties, body: callback(ch, method, properties, body),
                          auto_ack=True)
        channel.start_consuming()
        
    def send_message(self, message: bytes) -> str:
        publish_connection = pika.BlockingConnection(pika.ConnectionParameters(self.host, credentials=self.credentials))
        channel = publish_connection.channel()

        channel.queue_declare(queue=self.status_queue)
        channel.basic_publish(exchange='',
                          routing_key=self.status_queue,
                          body=message)
        publish_connection.close()