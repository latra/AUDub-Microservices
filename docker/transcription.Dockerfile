FROM python:3.10.14-slim-bullseye
RUN apt update && apt install -y ffmpeg
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

WORKDIR /microservice
COPY ./requirements-transcription.txt .

RUN python3 -m pip install -r ./requirements-transcription.txt

COPY ../src/ ./src

CMD ["python3", "src/transcription.py"]