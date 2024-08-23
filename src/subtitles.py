
from schemas.task import TaskTypes, task_classes, SubtitlesTask, TaskStatus
from schemas.microservice import Microservice
from utils.config import Types, Queues
from schemas.video import Video, VideoTranscription, TranscriptionStatus
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import torch
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip
import ffmpeg
from pycountry import languages
import numpy as np

def split_text(text, max_width, font_size, font):
    """
    Divide el texto en varias líneas basadas en el ancho máximo permitido.
    """
    import textwrap
    # Este cálculo es aproximado, depende de la fuente usada.
    char_width = font_size * 0.5  # Aproximadamente, ajusta si es necesario
    max_chars = int(max_width // char_width)
    return "\n".join(textwrap.wrap(text, width=max_chars))
def calculate_text_height(text, fontsize, video_width, line_spacing=1.2):
    """
    Calcula la altura requerida para el texto dado en función del número de líneas.
    """
    lines = text.count('\n') + 1
    return int(lines * fontsize * line_spacing)
class SubtitlesService(Microservice):
    def __init__(self, config_path) -> None:
        super().__init__(config_path, Queues.subtitles_queue)

    def start(self):
        self.rabbitmq_connection.subscribe(task_classes[TaskTypes.SUBTITLES], self.callback)
        pass

    def callback(self, task_request: SubtitlesTask):
        def convert_timing(timing_str):
            start, end = timing_str.strip("()").split(",")
            if "None" in end:
                return (float(start), None)

            return (float(start), float(end))
        def second_to_str(segundos):
            horas = segundos // 3600
            minutos = (segundos % 3600) // 60
            segundos = segundos % 60
            return f"{int(horas):02}:{int(minutos):02}:{int(segundos):02},000"

        status = TaskStatus(task_uuid=task_request.task_uuid, status=False, message="")
        video_data = self.mongodb_connection.get_video(task_request.video_id)
        if video_data:
            if task_request.language in video_data.transcriptions:
                transcription_dict = video_data.transcriptions[task_request.language].transcription
                print(transcription_dict)
                with open(self.get_temporal_path("subtitles.srt"), 'w') as archivo_srt:
                    for i, (time, frase) in enumerate(transcription_dict.items(), start=1):
                        (inicio, fin) = convert_timing(time)
                        if not fin:
                            fin=video_data.video_duration
                        inicio_srt = second_to_str(inicio)
                        fin_srt = second_to_str(fin)
                        archivo_srt.write(f"{i}\n")
                        archivo_srt.write(f"{inicio_srt} --> {fin_srt}\n")
                        archivo_srt.write(f"{frase}\n\n")
                self.filestorage.upload_subtitles(task_request.video_id, task_request.language, open(self.get_temporal_path("subtitles.srt"), "rb").read())
                self.remove_files(["subtitles.srt"])
        self.rabbitmq_connection.send_message(status.to_bytes())
        
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

service = SubtitlesService("config/config.yaml")
service.start()
