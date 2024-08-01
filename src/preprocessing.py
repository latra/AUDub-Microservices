from utils.config import load_config, Collections, Types, Queues
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
        super().__init__(config_path, Queues.video_queue)

    def start(self):
        self.rabbitmq_connection.subscribe(task_classes[TaskTypes.PREPROCESSING], self.callback)
        pass

    def callback(self, task_request: PreprocessingTask):
        video_name = None
        status = TaskStatus(task_uuid=task_request.task_uuid, status=False, message="")
        isolated_files = (f'video-{task_request.video_id}.mp4', f'audio-{task_request.video_id}.mp3')

        if task_request.video_source == VideoSource.YOUTUBE:
            video_name = download_video(task_request.video_id, task_request.video_uri, self.localstorage)
        
        if video_name:
            ffmpeg.input(video_name).output(self.get_temporal_path(isolated_files[0]), vcodec='copy', an=None).run()
            video_info = ffmpeg.probe(self.get_temporal_path(isolated_files[0]))

            # Extraer la pista de audio
            ffmpeg.input(video_name).output(self.get_temporal_path(isolated_files[1])).run()
            audio_info = ffmpeg.probe(self.get_temporal_path(isolated_files[1]))

            # Aquí puedes agregar el procesamiento adicional y guardado en MongoDB si es necesario

            video_uri = self.filestorage.upload_original(task_request.video_id, Types.video, open(self.get_temporal_path(isolated_files[0]), 'rb').read())
            audio_uri = self.filestorage.upload_original(task_request.video_id, Types.voice, open(self.get_temporal_path(isolated_files[1]), 'rb').read())
            self.remove_files(isolated_files)

            new_video = Video(video_id=task_request.video_id, video_metadata=VideoMetadata.from_video_info(video_info),
                              audio_metadata=AudioMetadata.from_audio_info(audio_info), transcriptions={}, original_script= None, original_language=None)
            self.mongodb_connection.save_video(new_video)
            status.status = True
        self.rabbitmq_connection.send_message(status.to_bytes())

service = PreprocessingService("config/config.yaml")
service.start()
