# Dockerfile to run api server
FROM python:3.9.9-bullseye

WORKDIR /src

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
    apt-get install -y \
    libgl1 libglib2.0-0 ffmpeg imagemagick libmagickwand-dev ghostscript

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY .env ./
COPY finished_videos ./finished_videos/
COPY audio ./audio/
COPY workflows ./workflows/
COPY video_clips ./video_clips/
COPY scripts ./scripts/

ENTRYPOINT ["python3", "-u", "./scripts/server.py"]


# docker build -t animated-video-builder:latest .

