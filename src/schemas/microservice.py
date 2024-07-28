from schemas.task import Task
from os import remove

class Microservice:
    def callback(self, task_request: Task):
        raise NotImplementedError()

    @staticmethod  
    def remove_files(files_to_remove: tuple[str]):
        for file in files_to_remove:
            remove(file)

    @staticmethod
    def save_temporal_file(file_name:str, file_data:bytes):
        tmp_file = open(file_name, "wb")
        tmp_file.write(file_data)
        tmp_file.close()