from utils.config import load_config
from repositories.mongodb import MongoConnection
from repositories.rabbitmq import RabbitMQConnector
from repositories.filestorage import FileManager
from repositories.youtube import download_video
from schemas.task import TaskTypes, task_classes, PreprocessingTask, VideoSource, TaskStatus
from schemas.microservice import Microservice
from schemas.video import Video, VideoMetadata, AudioMetadata
import ffmpeg

class PreprocessingService(Microservice):
    def __init__(self, config_path) -> None:
        self.config: dict = load_config(config_path)
        self.mongodb_connection: MongoConnection = MongoConnection(self.config)
        self.rabbitmq_connection: RabbitMQConnector = RabbitMQConnector(self.config)
        self.filestorage: FileManager = FileManager(self.config)

    def start(self):
        self.rabbitmq_connection.subscribe(task_classes[TaskTypes.PREPROCESSING], self.callback)
        pass

    def callback(self, task_request: PreprocessingTask):
        video_name = None
        status = TaskStatus(task_uuid=task_request.task_uuid, status=False, message="")
        isolated_files = (f'video-{task_request.video_id}.mp4', f'audio-{task_request.video_id}.mp3')

        if task_request.video_source == VideoSource.YOUTUBE:
            video_name = download_video(task_request.video_id, task_request.video_uri)
        
        if video_name:
            ffmpeg.input(video_name).output(isolated_files[0], vcodec='copy', an=None).run()

            # Extraer la pista de audio
            ffmpeg.input(video_name).output(isolated_files[1], ac=1, ar=16000).run()

            # Aquí puedes agregar el procesamiento adicional y guardado en MongoDB si es necesario
            video_info = ffmpeg.probe(isolated_files[0])
            audio_info = ffmpeg.probe(isolated_files[1])

            video_uri = self.filestorage.save_file(isolated_files[0], open(isolated_files[0], 'rb').read())
            audio_uri = self.filestorage.save_file(isolated_files[1], open(isolated_files[1], 'rb').read())
            self.remove_files(isolated_files)

            new_video = Video(video_id=task_request.video_id, video_metadata=VideoMetadata.from_video_info(video_uri, video_info),
                              audio_metadata=AudioMetadata.from_audio_info(audio_uri, audio_info), transcriptions={})
            self.mongodb_connection.save_item(video_id=task_request.video_id, key=None, content=new_video.model_dump())
            status.status = True
        self.rabbitmq_connection.send_message(status.to_bytes())

service = PreprocessingService("config/config.yaml")
service.start()
