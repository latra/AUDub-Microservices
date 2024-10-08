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
import wave

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
        def get_wav_duration(file_path):
            with wave.open(file_path, 'r') as wav_file:
                # Get the number of frames and frame rate
                frames = wav_file.getnframes()
                rate = wav_file.getframerate()
                duration = frames / float(rate)
                return duration
        max_audio_time = task_request.max_target_time
        time = max_audio_time + 1
        status = TaskStatus(task_uuid=task_request.task_uuid, status=False, message="")
        speed = task_request.voice_speed
        if task_request.voice_target_id:
            voices = self.save_temporal_folder("voice", "ogg" ,self.filestorage.download_voice(voice_id=task_request.voice_target_id))
        text_to_say = task_request.text
        while time > max_audio_time:
            if not task_request.voice_target_id:
                self.tts.tts_to_file(text=text_to_say, language= languages.get(name=task_request.target_language).alpha_2, speaker="Daisy Studious", file_path=self.get_temporal_path(f"temporal_{task_request.task_uuid}.wav"), speed=speed)
            else:
                self.tts.tts_to_file(text=text_to_say, language= languages.get(name=task_request.target_language).alpha_2, speaker_wav=voices, file_path=self.get_temporal_path(f"temporal_{task_request.task_uuid}.wav"), speed=speed)

            time = get_wav_duration(self.get_temporal_path(f"temporal_{task_request.task_uuid}.wav"))
            speed += 0.5
            if speed >= 2:
                break
        self.filestorage.upload_partial_audio(task_request.media_id, task_request.target_language, task_request.voice_target_id, task_request.task_uuid, open(self.get_temporal_path(f"temporal_{task_request.task_uuid}.wav"), "rb").read())
        self.remove_files([f"temporal_{task_request.task_uuid}.wav"])
        self.remove_files(voices, True)
        self.rabbitmq_connection.send_message(status.to_bytes())
        

service = TTSService("config/config.yaml")
service.start()
