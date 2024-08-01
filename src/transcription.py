
from schemas.task import TaskTypes, task_classes, STTTask, TaskStatus
from schemas.microservice import Microservice
from utils.config import Types, Queues
from schemas.video import Video, VideoTranscription, TranscriptionStatus
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import torch
import ffmpeg
from pycountry import languages
import numpy as np


class TranscriptionService(Microservice):
    def __init__(self, config_path) -> None:
        super().__init__(config_path, Queues.transcription_queue)

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
        video_data = self.mongodb_connection.get_video(task_request.video_id)
        if video_data:
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


            self.save_temporal_file(f"audio-{video_data.video_id}.mp3", self.filestorage.download_original(video_data.video_id, Types.voice))
            audio_array = read(self.get_temporal_path(f"audio-{video_data.video_id}.mp3"), normalized=True)
            sample = {"array": audio_array, "sampling_rate": 16000}

            if task_request.video_language:
                generate_kwargs={"task": "translate", "return_timestamps": True, "language": languages.get(name=task_request.video_language).alpha_2}
            else:
                generate_kwargs={"task": "translate", "return_timestamps": True}

            result = self.pipe(sample, generate_kwargs=generate_kwargs)
            timestamped_dict = format_transcription(result["chunks"])

            video_data.transcriptions["english"] = VideoTranscription(status = TranscriptionStatus.TRANCRIPTED, transcription= timestamped_dict)
            video_data.original_language = "english"
            video_data.original_script = result["text"]
            self.mongodb_connection.save_video(video_data)
            self.remove_files((f"audio-{video_data.video_id}.mp3",))
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
            .output('pipe:', format='wav', ac=1, ar=16000)
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
