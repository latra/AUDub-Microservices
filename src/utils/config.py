import yaml
from enum import Enum

class Types(str, Enum):
    voice = "voice.mp3"
    background = "background.mp3"
    video = "video.mp4"

class Collections(str, Enum):
    videos = "video_collection"
    voices = "voice_collection"

class Queues(str, Enum):
    video_queue= "video_queue"
    transcription_queue= "transcription_queue"
    translation_queue= "translation_queue"
    tts_queue= "tts_queue"
    mount_queue= "mount_queue"
    subtitles_queue= "subtitles_queue"

def load_config(config_path: str) -> dict:
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)