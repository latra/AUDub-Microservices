from utils.config import load_config
from repositories.mongodb import MongoConnection
from repositories.rabbitmq import RabbitMQConnector
from repositories.filestorage import FileManager
from repositories.youtube import download_video
from schemas.task import TaskTypes, task_classes, STTTask, VideoSource, TaskStatus
from schemas.microservice import Microservice
from schemas.video import Video, VideoMetadata, AudioMetadata
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import torch
import ffmpeg
import numpy as np


class TranscriptionService(Microservice):
    def __init__(self, config_path) -> None:
        self.config: dict = load_config(config_path)
        self.mongodb_connection: MongoConnection = MongoConnection(self.config)
        self.rabbitmq_connection: RabbitMQConnector = RabbitMQConnector(self.config)
        self.filestorage: FileManager = FileManager(self.config)
        model, processor, torch_dtype, device = self.start_model()


        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            max_new_tokens=128,
            chunk_length_s=30,
            batch_size=16,
            return_timestamps=True,
            torch_dtype=torch_dtype,
            device=device,
        )


    def start_model(self):
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        model_id = "openai/whisper-large-v3"

        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
        )
        model.to(device)

        processor = AutoProcessor.from_pretrained(model_id)
        return model, processor, torch_dtype, device
    
    def start(self):
        self.rabbitmq_connection.subscribe(task_classes[TaskTypes.SPEECH_TO_TEXT], self.callback)
        pass

    def callback(self, task_request: STTTask):
        status = TaskStatus(task_uuid=task_request.task_uuid, status=False, message="")
        video_data = Video.from_dict(self.mongodb_connection.get_item(task_request.video_id))
        if video_data:
            Microservice.save_temporal_file(f"audio-{video_data.video_id}.mp3", self.filestorage.get_file(video_data.audio_metadata.uri))
            audio_array = read(f"audio-{video_data.video_id}.mp3", normalized=True)
            sample = {"array": audio_array, "sampling_rate": 16000}
            result = self.pipe(sample, generate_kwargs={"task": "translate", "return_timestamps": True})
            timestamped_dict = format_transcription(result["chunks"])
            self.mongodb_connection.save_item(video_id=video_data.video_id, key="transcriptions.en", content=timestamped_dict)
            Microservice.remove_files((f"audio-{video_data.video_id}.mp3",))
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

service = TranscriptionService("config/config.yaml")
service.start()
