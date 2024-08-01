from utils.config import load_config, Collections, Queues, Types
from repositories.mongodb import MongoConnection
from repositories.rabbitmq import RabbitMQConnector
from repositories.filestorage import FileManager
from repositories.youtube import download_video
from schemas.task import TaskTypes, task_classes, MountTask, VideoSource, TaskStatus
from schemas.microservice import Microservice
from schemas.video import Video, VideoMetadata, AudioMetadata
from pydub import AudioSegment
import librosa
import numpy as np
from moviepy.editor import VideoFileClip, AudioFileClip

class MountAudioService(Microservice):
    def __init__(self, config_path) -> None:
        super().__init__(config_path,  Queues.mount_queue)

    def start(self):
        self.rabbitmq_connection.subscribe(task_classes[TaskTypes.MOUNT_AUDIO], self.callback)
        pass

    def callback(self, task_request: MountTask):
        video_name = None
        status = TaskStatus(task_uuid=task_request.task_uuid, status=False, message="")
        video = self.mongodb_connection.get_video(task_request.video_id)
        partial_audios = {}
        for timestamp in video.transcriptions[task_request.target_language].transcription:
            partial_audios[timestamp] = self.save_temporal_file(timestamp + ".mp3", self.filestorage.download_partials(task_request.video_id, task_request.target_language, timestamp))
        combined_file = combine_audios(partial_audios.values(), partial_audios)
        combined_file.export(self.get_temporal_path("combined_audio.mp3"), format="mp3")
        self.save_temporal_file("video.mp4",self.filestorage.download_original(task_request.video_id, Types.video))
        add_audio_to_video(self.get_temporal_path("video.mp4"), self.get_temporal_path("combined_audio.mp3"), self.get_temporal_path("output.mp4"))
        self.filestorage.upload_translation_audio(task_request.video_id, task_request.target_language, open(self.get_temporal_path("output.mp4"), "rb").read())

def combine_audios(audio_files, timings):
    def convert_timing(timing_str):
        start, end = timing_str.strip("()").split(",")
        return (float(start), float(end))
    
    timings = [convert_timing(timing) for timing in timings]
    combined = AudioSegment.silent(duration=max([end for _, end in timings]) * 1000)
    
    for i, (audio_file, (start, end)) in enumerate(zip(audio_files, timings)):
        print(f"{start},{end} - {audio_file}")

        audio = AudioSegment.from_file(audio_file)
        duration = (end - start) * 1000  # convertir a milisegundos
        if len(audio) > duration:
            speed = len(audio) / duration
            audio =  audio #change_speed_without_pitch(audio, speed)
        combined = combined.overlay(audio, position=start * 1000)

    return combined

def change_speed_without_pitch(audio, speed=1.0):
    # Convert AudioSegment to numpy array
    samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
    print("Original samples dtype:", samples.dtype)
    samples = samples / 32768  # Normalize the audio
    sample_rate = audio.frame_rate

    print("Sample rate:", sample_rate)
    print("Samples shape:", samples.shape)
    print("Speed:", speed)
    samples = samples.astype(np.float64)

    # Use librosa to change the speed without changing the pitch
    new_samples = librosa.effects.time_stretch(y=samples, rate=speed)
    print("New samples dtype after time stretch:", new_samples.dtype)

    # Convert back to AudioSegment
    new_samples = (new_samples * 32768).astype(np.int16)  # Denormalize the audio
    print("New samples dtype after denormalization:", new_samples.dtype)
    new_audio = AudioSegment(
        new_samples.tobytes(), 
        frame_rate=sample_rate,
        sample_width=audio.sample_width, 
        channels=audio.channels
    )
    return new_audio

def change_speed(audio, speed=1.0):
    # Cambiar la velocidad del audio
    sound_array = np.array(audio.get_array_of_samples())
    sample_rate = audio.frame_rate
    
    # Usar scipy para cambiar la velocidad
    sound_array = np.interp(
        np.arange(0, len(sound_array), speed),
        np.arange(0, len(sound_array)),
        sound_array
    ).astype(np.int16)
    
    new_audio = AudioSegment(
        sound_array.tobytes(), 
        frame_rate=int(sample_rate * speed),
        sample_width=audio.sample_width, 
        channels=audio.channels
    )
    return new_audio
def add_audio_to_video(video_file, audio_file, output_file):
    # Asegurarse de que el audio se guarda en un formato compatible
    audio = AudioFileClip(audio_file)
    video = VideoFileClip(video_file)
    
    # Ajustar la duración del audio para que coincida con la duración del video
    if audio.duration > video.duration:
        audio = audio.subclip(0, video.duration)
    elif audio.duration < video.duration:
        video = video.subclip(0, audio.duration)
    
    video = video.set_audio(audio)
    video.write_videofile(output_file, codec='libx264', audio_codec='aac')


service = MountAudioService("config/config.yaml")
service.start()
