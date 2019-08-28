FROM ubuntu:latest
RUN ln -sf /bin/bash /bin/sh
RUN readlink $(which sh)
RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y \
        libffi-dev libssl-dev python python-dev python-pip curl git bison vim less golang
RUN go get github.com/AFTERWAKE/IRCBots/dad/dadbot
WORKDIR /bot
COPY ./requirements.txt /bot
RUN pip install -r requirements.txt
