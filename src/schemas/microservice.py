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

    def remove_files(self, files_to_remove: tuple[str], add_localpath = False):
        for file in files_to_remove:
            if not add_localpath:
                remove(path.join(self.localstorage, file))
            else:
                print(file)
                remove(file)

    def save_temporal_file(self, file_name:str, file_data:bytes):
        tmp_file = open(path.join(self.localstorage, file_name), "wb")
        tmp_file.write(file_data)
        tmp_file.close()
        return path.join(self.localstorage, file_name)

    def save_temporal_folder(self, folder_name:str, extension, files_data:list[bytes]):
        print(len(files_data))
        voices_paths = []
        makedirs(path.join(self.localstorage, folder_name), exist_ok= True)
        for index in range(0, len(files_data)):
            tmp_file = open(path.join(self.localstorage, folder_name, str(index) + "." + extension), "wb")
            tmp_file.write(files_data[index])
            tmp_file.close()
            voices_paths.append(path.join(self.localstorage, folder_name, str(index) + "." + extension))
        return voices_paths

    def get_temporal_path(self, file_name: str) -> str:
        return path.join(self.localstorage, file_name)