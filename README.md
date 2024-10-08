# AU-DUB - Microservices

AU-DUB is an advanced platform designed for the automatic dubbing of videos, utilizing various AI tools and algorithms to transcribe, translate, dub, and clone voices from provided videos. This platform aims to streamline and automate the entire dubbing process, ensuring high-quality results with minimal human intervention.

## Features

## Installation and Running
### Platform Testing
- [Docker Engine](https://www.docker.com/) 27.1.1
- [Docker Compose](https://www.docker.com/) 2.29.1

#### Setup Environment

```sh
docker compose -f docker/docker-compose.yaml up -d
```

####

### Local Development
#### Prerequisites
- [Docker Engine](https://www.docker.com/) 27.1.1
- [Docker Compose](https://www.docker.com/) 2.29.1
- [Python](https://www.python.org/) 3.10
- [PyTorch](https://pytorch.org) 2.4.0
- [Ollama](https://ollama.com/) 2.4.0

**RECOMENDATION:** To avoid package incompatibilities, virtual environments are highly recommended
> **Virtual Environment** on Windows
> ```sh
> python3 -m venv .environmnet
> ./.environment/Scripts/activate
> ``` 

> **Virtual Environment** on Linux & MacOS
> ```sh
> python3 -m venv .environmnet
> source .environment/bin/activate
> ```


#### Setup Environment

Install the different Python package requirements by pip
```sh
python3 -m pip install -r requirements.txt
```

AU Dub uses RabbitMQ for internal module communication, as long as MongoDB to store the data from the videos. 

```sh
docker compose -f docker/docker-compose.services.yaml up -d
```
By default, RabbitMQ instance will run on `172.20.0.3` and MongoDB on `172.20.0.2`

#### Run Modules
Different modules can be executed direclty by using Python:
```sh
python3 src/preprocessing.py
```
```sh
python3 src/texttospeech.py
```
```sh
python3 src/transcription.py
```
```sh
python3 src/translation.py
```
```sh
python3 src/texttospeech.py
```
```sh
python3 src/mounter.py
```
## Usage
Different modules can be used by directly ending a message through the queue specified in `config/config.yaml`

**Preprocessing Module**
```json
{
    "task_type": "PREPROCESSING",
    "task_uuid": "123e4567-e89b-12d3-a456-426614174000",
    "video_id": "video_example",
    "video_source":"YOUTUBE",
    "video_uri":"https://www.youtube.com/shorts/Ile_ueJGON8"
}
```
**Transcription Module**
```json
{
    "task_type": "SPEECH_TO_TEXT",
    "task_uuid": "123e4567-e89b-12d3-a456-426614174000",
    "video_id": "ter",
    "video_language": "spanish"
}
```
**Translation Module**
```json
{
    "task_type": "TRANSLATION",
    "task_uuid": "123e4567-e89b-12d3-a456-426614174000",
    "video_id": "video_example",
    "target_language": "spanish",
}
```
**TTS Module**
```json
{
    "task_type": "TEXT_TO_SPEECH",
    "task_uuid": "123e4567-e89b-12d3-a456-426614174000",
    "media_id": "short",
    "target_language": "spanish",
    "max_target_time":50,
    "text":"Esta semana podría ser ojo de tritón o quizás un mapa del tesoro. Nunca se sabe hasta que no miras. ¿Qué será lo que tiene Antonio?",
    "voice_target_id": "tauren"
}
```
**Mount module**
```json
{
    "task_type": "MOUNT_AUDIO",
    "task_uuid": "123e4567-e89b-12d3-a456-426614174000",
    "video_id": "video_example",
    "target_language": "english"
}
```
## Credits

- [OpenAI - Whisper](https://openai.com/research/whisper) - Used for video transcription
- [Meta - Llama](https://ai.facebook.com/blog/large-language-model-llama-meta-ai/) - Used for video translation
- [Coqui - Coqui XTTS](https://coqui.ai/) - Used for TTS and Voice Cloning

## Authors
- [Paula "Latra" Gallucci Zurita](https://github.com/latra)
- [David Sarrat González](https://github.com/davidsarratgonzalez)
