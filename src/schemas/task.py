from enum import Enum
from pydantic import BaseModel


class TaskTypes(str, Enum):
    PREPROCESSING = "PREPROCESSING"
    SPEECH_TO_TEXT = "SPEECH_TO_TEXT"
    TRANSLATION = "TRANSLATION"
    TEXT_TO_SPEECH = "TEXT_TO_SPEECH"
    VOICE_CLONNING = "VOICE_CLONNING"
    VOICE_PROCESSING = "VOICE_PROCESSING"

class VideoSource(str, Enum):
    YOUTUBE = "YOUTUBE"
    PLATFORM = "PLATFORM"

class Task(BaseModel):
    task_type: TaskTypes
    task_uuid: str

    @classmethod
    def from_json(cls, json_data: dict):
        return cls.parse_obj(json_data)

    def to_json(self) -> dict:
        return self.dict()

class PreprocessingTask(Task):
    video_id: str
    video_source: VideoSource
    video_uri: str

class STTTask(Task):
    video_id: str

class TranslationTask(Task):
    video_id: str
    target_language: str