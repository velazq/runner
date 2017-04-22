FROM docker:latest

RUN apk update
RUN apk add python3 git
RUN pip3 install -U celery[redis] docker
RUN git clone https://github.com/velazq/runner.git /runner

WORKDIR /runner/app
ENTRYPOINT ["celery", "worker", "--app", "runner", "--quiet", "--concurrency", "1", "--prefetch-multiplier", "1", "--without-gossip", "--without-mingle", "--without-heartbeat"]
