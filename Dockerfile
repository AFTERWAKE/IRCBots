FROM ubuntu:latest
RUN apt update -y && apt upgrade -y
RUN apt install -y \
        libffi-dev \
        libssl-dev \
        python \
        python-dev \
        python-pip
WORKDIR /bot
COPY ./requirements.txt /bot
RUN pip install -r requirements.txt
