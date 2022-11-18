FROM python:3.9-slim-buster

ENV PYTHONUNBUFFERED = 1
COPY requirements.txt /
COPY start.sh /start.sh
COPY firebase_key.json /firebase_key.json
COPY nginx.conf /etc/nginx/conf.d/virtual.conf

RUN apt-get -y update && \
	apt-get -y install \
    git \
	python3-dev \
    libjpeg-dev \
    zlib1g-dev \
    ffmpeg

RUN apt-get -y install \
    gcc\
    build-essential
WORKDIR /app

RUN python3 -m pip install -r /app/requirements.txt
RUN python3 -m pip install -r /app/yolov7/requirements.txt


EXPOSE 80
ENTRYPOINT ["sh", "/start.sh"]
