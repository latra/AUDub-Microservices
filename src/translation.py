from utils.config import load_config
from repositories.mongodb import MongoConnection
from repositories.rabbitmq import RabbitMQConnector
from repositories.filestorage import FileManager
from repositories.youtube import download_video
from schemas.task import TaskTypes, task_classes, TranslationTask, VideoSource, TaskStatus
from schemas.microservice import Microservice
from schemas.video import Video, VideoMetadata, AudioMetadata
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import ollama
import ffmpeg
import numpy as np


class TranslationService(Microservice):
    def __init__(self, config_path) -> None:
        self.config: dict = load_config(config_path)
        self.mongodb_connection: MongoConnection = MongoConnection(self.config)
        self.rabbitmq_connection: RabbitMQConnector = RabbitMQConnector(self.config)
        self.filestorage: FileManager = FileManager(self.config)


    def start(self):
        self.rabbitmq_connection.subscribe(task_classes[TaskTypes.TRANSLATION], self.callback)
        pass

    def callback(self, task_request: TranslationTask):
        status = TaskStatus(task_uuid=task_request.task_uuid, status=False, message="")
        video_data = Video.from_dict(self.mongodb_connection.get_item(task_request.video_id))
        if video_data:
            #TODO hay que seguir jugando y probando esto
            promp = 'Target Language:\n{}\nOriginal transcription:\n{}'.format(task_request.target_language, video_data.transcriptions["en"]) 
            promp += '\nNotice that the original video is about {}'.format(task_request.additional_info) if task_request.additional_info else ''
            promp += '\nMake sure that the translated output has sense'
            promp += '\nIMPORTANT: Make sure to provide ONLY the JSON with the timestamps and the translation sentence.'
            print(promp)
            response = ollama.chat(model='translation-model', messages=[
            {
                'role': 'user',
                'content': promp,
            },
            ])
            print(response['message']['content'])
            status.status = True
        self.rabbitmq_connection.send_message(status.to_bytes())
        

def format_transcription(transcription):
    result = {}
    for transc in transcription:
        result[str(transc["timestamp"])] = transc["text"]
    return result

def read(file_uri, normalized=False):
    """MP3 to numpy array using ffmpeg"""
    try:
        out, err = (
            ffmpeg.input(file_uri)
            .output('pipe:', format='wav')
            .run(capture_stdout=True, capture_stderr=True)
        )
        a = np.frombuffer(out, np.int16)

        if normalized:
            return np.float32(a) / 2**15
        else:
            return a
    except ffmpeg.Error as e:
        print("ffmpeg error:", e.stderr.decode('utf8'))
        raise

service = TranslationService("config/config.yaml")
service.start()
