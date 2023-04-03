FROM python:3.8-slim-buster
WORKDIR /app

RUN apt-get update -y && \
    apt-get install -y curl && \
    curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-410.0.0-linux-x86_64.tar.gz && \
    tar -xvzf google-cloud-cli-410.0.0-linux-x86_64.tar.gz && \
    ./google-cloud-sdk/install.sh --quiet && \
    pip install --upgrade pip
ENV LOG_LEVEL=INFO
LABEL maintainer="<your name>"
LABEL description="A Docker image for running vertex AI jobs"

COPY requirements.txt /app/
RUN  pip install --no-cache-dir -r requirements.txt
COPY . /app