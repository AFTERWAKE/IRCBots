FROM ubuntu:latest
RUN apt update -y && apt upgrade -y
RUN apt install -y \
        libffi-dev \
        libssl-dev \
        python \
        python-dev \
        python-pip
WORKDIR /magic_conch
COPY . /magic_conch
RUN pip install -r requirements.txt
CMD ["python", "magic_conch.py"]
