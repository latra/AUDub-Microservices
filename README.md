# AU-DUB

AU-DUB is an advanced platform designed for the automatic dubbing of videos, utilizing various AI tools and algorithms to transcribe, translate, dub, and clone voices from provided videos. This platform aims to streamline and automate the entire dubbing process, ensuring high-quality results with minimal human intervention.

## Features

## Installation and Running
### Local Development
#### Prerequisites
- [Docker Engine](https://www.docker.com/) 27.1.1
- [Docker Compose](https://www.docker.com/) 2.29.1
- [Python](https://www.python.org/) 3.10
- [PyTorch](https://pytorch.org) 2.4.0
- [Ollama](https://ollama.com/) 2.4.0

#### Setup Environment
AU Dub uses RabbitMQ for internal module communication, as long as MongoDB to store the data from the videos. 

```sh
docker compose -f docker/docker-compose.services.yaml up -d
```
By default, RabbitMQ instance will run on `172.20.0.3` and MongoDB on `172.20.0.2`

#### Run Modules


#### Usage
**Preprocessing Module**
```json
{
    "task_type": "PREPROCESSING",
    "task_uuid": "123e4567-e89b-12d3-a456-426614174000",
    "video_id": "video_spanish",
    "video_source":"YOUTUBE",
    "video_uri":"https://www.youtube.com/shorts/Ile_ueJGON8"
}
```
**Transcription Module**
```json
{
    "task_type": "SPEECH_TO_TEXT",
    "task_uuid": "123e4567-e89b-12d3-a456-426614174000",
    "video_id": "video_spanish",
    "video_language": "spanish"
}
```
**Translation Module**
```json
{
    "task_type": "TRANSLATION",
    "task_uuid": "123e4567-e89b-12d3-a456-426614174000",
    "video_id": "video_spanish",
    "target_language": "spanish",
    "additional_info": "It's a video about health recommendations"
}
```

## Credits

- [OpenAI - Whisper]() - Used for video transcription
- [Meta - Llama]() - Used for video translation

## Authors
- [David Sarrat Gonzalez]()
- [Paula Gallucci Zurita]()
