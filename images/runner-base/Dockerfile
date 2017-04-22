FROM docker:latest

RUN apk update
RUN apk add python3 git
RUN pip3 install -U celery[redis] docker
