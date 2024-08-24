import pika
from typing import Any

import pika.credentials
from schemas.task import TaskTypes, Task
import json


class RabbitMQConnector:
    def __init__(self, config: dict, queue: str) -> None:
        self.host = config['rabbitmq']['host']
        self.port = config['rabbitmq']['port']
        self.user = config['rabbitmq']['username']
        self.password = config['rabbitmq']['password']
        self.job_queue =  config['rabbitmq'][queue]
        self.status_queue =  config['rabbitmq']['status_queue']
        self.credentials = pika.credentials.PlainCredentials(self.user, self.password)

    def subscribe(self, task_type: Task, callback):
        subscription_connection = pika.BlockingConnection(pika.ConnectionParameters(self.host, credentials=self.credentials))
        channel = subscription_connection.channel()

        channel.queue_declare(queue=self.job_queue)
        channel.basic_consume(queue=self.job_queue, on_message_callback=lambda ch, method, properties, body: self.callback(ch, method, properties, body, task_type, callback),
                          auto_ack=False)
        channel.start_consuming()
    
    def callback(self, ch, method, properties, body, type_target, function_callback):
        ch.basic_ack(delivery_tag=method.delivery_tag)

        task_request = Task.from_json(json.loads(body))
        if type(task_request) == type_target:
            print("Task...")
            print(task_request)
            function_callback(task_request)
        
    def send_message(self, message: bytes) -> str:
        publish_connection = pika.BlockingConnection(pika.ConnectionParameters(self.host, credentials=self.credentials))
        channel = publish_connection.channel()

        channel.queue_declare(queue=self.status_queue)
        channel.basic_publish(exchange='', 
                          routing_key=self.status_queue,
                          body=message)
        publish_connection.close()