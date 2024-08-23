from enum import Enum
from typing import Optional
from pydantic import BaseModel
import json

class TaskTypes(str, Enum):
    PREPROCESSING = "PREPROCESSING"
    SPEECH_TO_TEXT = "SPEECH_TO_TEXT"
    TRANSLATION = "TRANSLATION"
    TEXT_TO_SPEECH = "TEXT_TO_SPEECH"
    MOUNT_AUDIO = "MOUNT_AUDIO"
    VOICE_PROCESSING = "VOICE_PROCESSING"
    SUBTITLES = "SUBTITLES"

class VideoSource(str, Enum):
    YOUTUBE = "YOUTUBE"
    PLATFORM = "PLATFORM"

class TaskStatus(BaseModel):
    task_uuid: str
    status: bool
    message: str
    def to_json(self) -> dict:
        return self.model_dump()
    def to_bytes(self) -> bytes:
        return json.dumps(self.to_json())

class Task(BaseModel):
    task_type: TaskTypes
    task_uuid: str

    @classmethod
    def from_json(cls, json_data: dict):
        task_type = json_data.get("task_type")
        if task_type:
            task_cls = task_classes.get(TaskTypes(task_type))
            if task_cls:
                return task_cls.model_validate(json_data)
        return None

    def to_json(self) -> dict:
        return self.model_dump()

class PreprocessingTask(Task):
    video_id: str
    video_source: VideoSource
    video_uri: str

class STTTask(Task):
    video_id: str
    video_language: str

class TranslationTask(Task):
    video_id: str
    target_language: str

class TTSTask(Task):
    video_id: str
    timestamp_key: str
    target_language: str
    voice_target_id: str

class MountTask(Task):
    video_id: str
    target_language: str

class SubtitlesTask(Task):
    video_id: str
    language: str

task_classes = {
    TaskTypes.PREPROCESSING: PreprocessingTask,
    TaskTypes.SPEECH_TO_TEXT: STTTask,
    TaskTypes.TRANSLATION: TranslationTask,
    TaskTypes.TEXT_TO_SPEECH: TTSTask,
    TaskTypes.MOUNT_AUDIO: MountTask,
    TaskTypes.SUBTITLES: SubtitlesTask,
}