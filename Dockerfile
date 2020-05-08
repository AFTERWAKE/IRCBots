FROM ubuntu:latest
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update -y && apt upgrade -y
RUN apt install -y \
        libffi-dev libssl-dev python python-dev python-pip curl \
        git bison vim less golang wamerican tzdata
RUN go get github.com/AFTERWAKE/IRCBots/dad/dadbot
WORKDIR /bot
COPY ./requirements.txt /bot
RUN pip install -r requirements.txt
RUN echo "America/Chicago" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata

