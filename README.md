# AU-DUB

AU-DUB is an advanced platform designed for the automatic dubbing of videos, utilizing various AI tools and algorithms to transcribe, translate, dub, and clone voices from provided videos. This platform aims to streamline and automate the entire dubbing process, ensuring high-quality results with minimal human intervention.

## Features

## Installation and Running
### Local Development
#### Prerequisites
- [Docker Engine](https://www.docker.com/) 27.1.1
- [Docker Compose](https://www.docker.com/) 2.29.1
- [Python](https://www.python.org/) 3.10

#### Setup Environment
AU Dub uses RabbitMQ for internal module communication, as long as MongoDB to store the data from the videos. 

```sh
docker compose -f docker/docker-compose.services.yaml up -d
```
By default, RabbitMQ instance will run on `172.20.0.3` and MongoDB on `172.20.0.2`

#### Run Modules



## Credits

- [OpenAI - Whisper]() - Used for video transcription
- [Meta - Llama]() - Used for video translation

## Authors
- [David Sarrat Gonzalez]()
- [Paula Gallucci Zurita]()
