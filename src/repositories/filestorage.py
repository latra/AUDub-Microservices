import os
from utils.config import Collections, Types
"""
Se utiliza como intermediario. Ahora mismo es una clase inútil porque todo se guarda en local.
Está por si el dia de mañana se mueve a cloud o algo, será transparente al resto de módulos y funciones.
"""
class FileManager:
    def __init__(self, config: dict) -> None:
        self.path = config['filestorage']['path']
        pass

    def upload_original(self, video_id: str, file_type: Types, file_data: bytes) -> str:
        return self._save_file(os.path.join(self.path, "videos", video_id), file_type.value, file_data)

    def upload_partial_audio(self, video_id: str, language: str, voice_id: str, task_uuid: str, file_data: bytes) -> str:
        return self._save_file(os.path.join(self.path, "videos", video_id, language, voice_id), task_uuid + ".mp3", file_data)

    def upload_translation_audio(self, video_id: str, language: str, file_data: bytes) -> str:
        return self._save_file(os.path.join(self.path, "videos", video_id, language), "tranlsated.mp4", file_data)

    def upload_subtitles(self, video_id: str, language: str, file_data: bytes) -> str:
        return self._save_file(os.path.join(self.path, "videos", video_id),  f"{language}.srt", file_data)

    def upload_voice(self, voice_id: str, file_data: bytes) -> str:
        return self._save_file(os.path.join(self.path, "voices"), voice_id + ".mp3", file_data)

    def download_original(self, video_id: str, file_type: Types) -> bytes:
        return self._get_file(os.path.join(self.path, "videos", video_id, file_type.value))
    
    def download_partials(self, video_id: str, language: str, timestamp: str) -> bytes:
        return self._get_file(os.path.join(self.path, "videos", video_id, language, "partial", timestamp + ".mp3"))
    
    def download_voice(self, voice_id: str) -> list[bytes]:
        array_de_bytes = []
    
        # Recorre todos los archivos en la carpeta especificada
        for nombre_fichero in os.listdir(os.path.join(self.path, "voices", voice_id)):
            ruta_completa = os.path.join(self.path, "voices", voice_id, nombre_fichero)
            # Verifica si es un archivo (ignora carpetas)
            if os.path.isfile(ruta_completa):
                with open(ruta_completa, 'rb') as fichero:
                    # Lee el archivo y añade los bytes a la lista
                    array_de_bytes.append(fichero.read())
        return array_de_bytes
        # return self._get_file(os.path.join(self.path, "voices", voice_id + ".mp3"))
    
    def download_subtitles(self, video_id: str, language: str) -> bytes:
        return self._get_file(os.path.join(self.path, "videos", video_id, f"{language}.srt"))

    def _save_file(self, path: str, file_name: str, file_data: bytes) -> str:
        os.makedirs(path, exist_ok= True)
        file = open(os.path.join(path, file_name), "wb")
        file.write(file_data)

        return os.path.join(path, file_name)

    def _get_file(self, file_path: str) -> bytes:
        file = open(os.path.join(file_path), "rb")
        return file.read()
