from utils.config import load_config, Queues
from repositories.mongodb import MongoConnection
from repositories.rabbitmq import RabbitMQConnector
from repositories.filestorage import FileManager
from schemas.task import Task
from os import remove, path, makedirs

class Microservice:
    def __init__(self, config_path, task_queue) -> None:
        self.config: dict = load_config(config_path)
        self.localstorage: str = self.config['microservice']['localstorage']
        self.mongodb_connection: MongoConnection = MongoConnection(self.config)
        self.rabbitmq_connection: RabbitMQConnector = RabbitMQConnector(self.config, task_queue)
        self.filestorage: FileManager = FileManager(self.config)
        makedirs(self.localstorage, exist_ok= True)

    def callback(self, task_request: Task):
        raise NotImplementedError()

    def remove_files(self, files_to_remove: tuple[str]):
        for file in files_to_remove:
            remove(path.join(self.localstorage, file))

    def save_temporal_file(self, file_name:str, file_data:bytes):
        tmp_file = open(path.join(self.localstorage, file_name), "wb")
        tmp_file.write(file_data)
        tmp_file.close()
        return path.join(self.localstorage, file_name)

    def get_temporal_path(self, file_name: str) -> str:
        return path.join(self.localstorage, file_name)