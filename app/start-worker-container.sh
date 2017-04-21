#!/bin/sh

docker run \
  -d \
  --name runner-ctrl \
  --restart unless-stopped \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e MASTER_IP="${MASTER_IP}",BROKER="${BROKER}",BACKEND="${BACKEND}" \
  -w /runner/app \
  alvelazq/runner \
    celery worker -A runner
