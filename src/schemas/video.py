from pydantic import BaseModel


class VideoMetadata(BaseModel):
    uri: str
    format: str
    bitrate: int
    width: int
    height: int
    duration: float

    @classmethod
    def from_video_info(cls, video_uri: str, video_info: dict):
        return cls(
            uri=video_uri,
            format=video_info['streams'][0]['codec_name'],
            bitrate=int(video_info['streams'][0]['bit_rate']),
            width=int(video_info['streams'][0]['width']),
            height=int(video_info['streams'][0]['height']),
            duration=float(video_info['streams'][0]['duration'])
        )

class AudioMetadata(BaseModel):
    uri: str
    format: str
    bitrate: int
    sample_rate: int
    @classmethod
    def from_audio_info(cls, audio_uri: str, audio_info: dict):
        return cls(
            uri=audio_uri,
            format=audio_info['streams'][0]['codec_name'],
            bitrate=int(audio_info['streams'][0]['bit_rate']),
            sample_rate=int(audio_info['streams'][0]['sample_rate']),
        )
    
class Video(BaseModel):
    video_id: str
    video_metadata: VideoMetadata
    audio_metadata: AudioMetadata
    transcriptions: dict

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            video_id=data['video_id'],
            video_metadata=VideoMetadata(**data['video_metadata']),
            audio_metadata=AudioMetadata(**data['audio_metadata']),
            transcriptions=data['transcriptions']
        )