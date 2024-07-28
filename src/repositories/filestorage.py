import os
"""
Se utiliza como intermediario. Ahora mismo es una clase inútil porque todo se guarda en local.
Está por si el dia de mañana se mueve a cloud o algo, será transparente al resto de módulos y funciones.
"""
class FileManager:
    def __init__(self, config: dict) -> None:
        self.path = config['filestorage']['path']
        pass

    def save_file(self, file_name: str, file_data: bytes) -> str:
        file = open(os.path.join(self.path, file_name), "wb")
        file.write(file_data)
        return file_name
    
    def get_file(self, uri: str) -> bytes:
        file = open(os.path.join(self.path, uri), "rb")
        return file.read()
