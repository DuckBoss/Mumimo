FROM docker.io/python:3.10-slim

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update --no-install-recommends \
&& apt-get install -y -qq apt-utils --no-install-recommends 2>&1 | grep -v "debconf: delaying package configuration, since apt-utils is not installed" \
&& apt-get install -y -qq ffmpeg vlc --no-install-recommends \
&& apt-get install -y -qq libopus-dev gcc openssl git \
&& apt-get clean && rm -rf /var/lib/apt/lists/*

# Enable VLC to be executed as root
RUN sed -i 's/geteuid/getppid/' /usr/bin/vlc

# Expose primary web interface port
EXPOSE 7000

WORKDIR /app

# Add all the requirements.txt files from the requirements folder and install them.
ADD ./dev_requirements.txt /app
ADD ./git_requirements.txt /app
ADD ./requirements.txt /app

RUN pip install -r dev_requirements.txt --no-warn-script-location
COPY . /app
