# Build
To build and push this image:
docker build -t <tag>:<ver> -t <tag>:latest .
docker push <tag>:<ver>
docker push <tag>:latest

# Run
To run docker into this image you need to share the socket file:
docker run --name some-runner -v /var/run/docker.sock:/var/run/docker.sock -d <tag>
