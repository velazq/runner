FROM docker:latest

RUN apk update
RUN apk add python3 git
RUN pip3 install -U celery[redis] docker
RUN git -C / clone https://github.com/velazq/runner.git

WORKDIR /runner/app
CMD ["celery", "worker", "-A", "runner", "--quiet", "--concurrency", "1", "--prefetch-multiplier", "1", "--without-gossip", "--without-mingle", "--without-heartbeat"]
