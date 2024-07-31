from utils.config import load_config, Collections, Queues
from repositories.mongodb import MongoConnection
from repositories.rabbitmq import RabbitMQConnector
from repositories.filestorage import FileManager
from schemas.task import TaskTypes, task_classes, TTSTask, TaskStatus
from schemas.microservice import Microservice
from schemas.video import Video
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import torch
from TTS.api import TTS
from pycountry import languages
import numpy as np


class TTSService(Microservice):
    def __init__(self, config_path) -> None:
        super().__init__(config_path, Queues.tts_queue)

        self.start_model()
    def start(self):
        self.rabbitmq_connection.subscribe(task_classes[TaskTypes.TEXT_TO_SPEECH], self.callback)
        pass

    def start_model(self):

        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)


    def callback(self, task_request: TTSTask):
        status = TaskStatus(task_uuid=task_request.task_uuid, status=False, message="")
        video_data: Video = self.mongodb_connection.get_video(task_request.video_id)
        voice_data = None
        if video_data:
            text_to_say = video_data.transcriptions[task_request.target_language].transcription[task_request.timestamp_key]
            self.tts.tts_to_file(text=text_to_say, language= languages.get(name=task_request.target_language).alpha_2, speaker="Daisy Studious", file_path=f"temporal_{task_request.task_uuid}.wav")
            self.filestorage.upload_partial_audio(video_data.video_id, task_request.target_language, task_request.timestamp_key, open(f"temporal_{task_request.task_uuid}.wav", "rb").read())
            
            Microservice.remove_files([f"temporal_{task_request.task_uuid}.wav"])
            pass
        self.rabbitmq_connection.send_message(status.to_bytes())
        

service = TTSService("config/config.yaml")
service.start()
