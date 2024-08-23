from pydantic import BaseModel
from typing import Optional
from enum import Enum

class TranscriptionStatus(int, Enum):
    PENDING = 0
    TRANCRIPTED = 1
    PROCESSED = 2



class VideoTranscription(BaseModel):
    status: TranscriptionStatus
    transcription: dict


class VideoMetadata(BaseModel):
    format: str
    bitrate: int
    width: int
    height: int
    duration: float

    @classmethod
    def from_video_info(cls, video_info: dict):
        return cls(
            format=video_info['streams'][0]['codec_name'],
            bitrate=int(video_info['streams'][0]['bit_rate']),
            width=int(video_info['streams'][0]['width']),
            height=int(video_info['streams'][0]['height']),
            duration=float(video_info['streams'][0]['duration'])
        )

class AudioMetadata(BaseModel):
    format: str
    bitrate: int
    sample_rate: int
    @classmethod
    def from_audio_info(cls, audio_info: dict):
        return cls(
            format=audio_info['streams'][0]['codec_name'],
            bitrate=int(audio_info['streams'][0]['bit_rate']),
            sample_rate=int(audio_info['streams'][0]['sample_rate']),
        )
    
class Video(BaseModel):
    video_id: str
    video_duration: float
    video_metadata: VideoMetadata
    audio_metadata: AudioMetadata
    original_script: Optional[str]
    original_language: Optional[str]
    transcriptions: dict[str, VideoTranscription]

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            video_id=data['video_id'],
            video_duration=data['video_duration'],
            video_metadata=VideoMetadata(**data['video_metadata']),
            audio_metadata=AudioMetadata(**data['audio_metadata']),
            transcriptions=data['transcriptions'],
            original_language=data['original_language'],
            original_script=data['original_script']
        )