FROM python:3.10.14-slim-bullseye

WORKDIR /microservice
COPY ./requirements-translation.txt .

RUN python3 -m pip install -r ./requirements-translation.txt

COPY ../src/ ./src



CMD ["python3", "src/translation.py"]