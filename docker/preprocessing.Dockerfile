FROM python:3.10.14-slim-bullseye
RUN apt update && apt install -y ffmpeg
WORKDIR /microservice
COPY ./requirements-preprocessing.txt .

RUN python3 -m pip install -r ./requirements-preprocessing.txt

COPY ../src/ ./src

CMD ["python3", "src/preprocessing.py"]