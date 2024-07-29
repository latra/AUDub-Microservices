import os
from utils.config import Collections
"""
Se utiliza como intermediario. Ahora mismo es una clase inútil porque todo se guarda en local.
Está por si el dia de mañana se mueve a cloud o algo, será transparente al resto de módulos y funciones.
"""
class FileManager:
    def __init__(self, config: dict) -> None:
        self.path = config['filestorage']['path']
        pass

    def save_file(self, collection: Collections, entity_id: str, file_name: str, file_data: bytes) -> str:
        file_route = "/".join([collection, entity_id, file_name])
        file_path = os.path.join(self.path, collection, entity_id)
        os.makedirs(file_path, exist_ok= True)
        file = open(os.path.join(self.path, collection, entity_id, file_name), "wb")
        file.write(file_data)
        return file_route
    
    def get_file(self, uri: str) -> bytes:
        file = open(os.path.join(self.path, uri), "rb")
        return file.read()
