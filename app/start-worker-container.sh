#!/bin/bash

if [[ ! "$BROKER" ]] || [[ ! "$BACKEND" ]]; then
  echo Error: you must set both \$BROKER and \$BACKEND
  echo Example:
  echo export BROKER=pyamqp://10.0.0.1:5672
  echo export BACKEND=redis://redis.example.com:6379
  exit 1
fi

docker run \
  --name runner-ctrl \
  -d \
  --restart unless-stopped \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /data \
  -e BROKER="$BROKER" \
  -e BACKEND="$BACKEND" \
  -e CONTAINERIZE=1 \
  -w /runner/app \
  alvelazq/runner \
    celery worker -A runner
