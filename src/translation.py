from utils.config import load_config, Queues
from repositories.mongodb import MongoConnection
from repositories.rabbitmq import RabbitMQConnector
from repositories.filestorage import FileManager
from schemas.task import TaskTypes, task_classes, TranslationTask, TaskStatus
from schemas.microservice import Microservice
from schemas.video import VideoTranscription, TranscriptionStatus
from ollama import Client
import re

class TranslationService(Microservice):
    def __init__(self, config_path) -> None:
        super().__init__(config_path, Queues.translation_queue)

        self.ollama_client = Client(self.config["ollama"]["host"])
        self.ollama_client.create("translation-model", "config/Modelfile")

    def start(self):
        self.rabbitmq_connection.subscribe(task_classes[TaskTypes.TRANSLATION], self.callback)
        pass

    def callback(self, task_request: TranslationTask):
        status = TaskStatus(task_uuid=task_request.task_uuid, status=False, message="")
        video_data = self.mongodb_connection.get_video(task_request.video_id)
        if video_data:
            promp = f"""
The original language of the video is {video_data.original_language} and you must translate it to {task_request.target_language}.
The script of the original video is:
{video_data.original_script}
{video_data.transcriptions[video_data.original_language]}
"""
            response = self.ollama_client.chat(model='translation-model', messages=[
            {
                'role': 'user',
                'content': promp,
            },
            ])
            video_data.transcriptions[task_request.target_language] =  VideoTranscription(status= TranscriptionStatus.PROCESSED,transcription= get_translated_dict(response['message']['content']))
            self.mongodb_connection.save_video(video_data)

            status.status = True
        self.rabbitmq_connection.send_message(status.to_bytes())
        

def get_translated_dict(response: str):

# Expresión regular para extraer los datos
    pattern = r'\- \(([\d.,]+), ([\d.,]+)\): "*(.*)"*'
    # Buscar todas las coincidencias
    matches = re.findall(pattern, response)

    # Crear el diccionario
    transcription_dict = {f"({start}, {end})": text for start, end, text in matches}

    return transcription_dict

def format_transcription(transcription):
    result = {}
    for transc in transcription:
        result[str(transc["timestamp"])] = transc["text"]
    return result

service = TranslationService("config/config.yaml")
service.start()
