FROM alvelazq/runner-base:latest

RUN git -C / clone https://github.com/velazq/runner.git

WORKDIR /runner/app
CMD ["celery", "worker", "-A", "runner", "--quiet", "--concurrency", "1", "--prefetch-multiplier", "1", "--without-gossip", "--without-mingle", "--without-heartbeat"]
