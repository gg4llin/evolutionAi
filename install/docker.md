# Installation Guide — Docker

This guide describes how to containerise the AdaptiveAgent local engine for repeatable environments.

## Prerequisites
- Docker Engine 24+
- Access to the repository source (volume mount or baked image)
- ngrok account (optional)

## Sample Dockerfile
```Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir pyyaml \
    && adduser --disabled-password agent

USER agent
ENV PYTHONUNBUFFERED=1 \
    ADAPTIVE_CAPABILITY_SECRET=changeme \
    HOST=0.0.0.0 \
    PORT=8080

EXPOSE 8080
CMD ["python", "-m", "local_engine.main", "--host", "${HOST}", "--port", "${PORT}"]
```

## Build and Run
```bash
docker build -t adaptive-agent:latest .
docker run -p 8080:8080 \
  -e ADAPTIVE_CAPABILITY_SECRET="<32+ character secret>" \
  adaptive-agent:latest
```

Mount the repository if you expect to edit specs without rebuilding:
```bash
docker run -p 8080:8080 \
  -e ADAPTIVE_CAPABILITY_SECRET="<secret>" \
  -v "$PWD/docs/blueprints:/app/docs/blueprints" \
  adaptive-agent:latest
```

## Optional: ngrok Sidecar
```bash
docker run --network host \
  -e NGROK_AUTHTOKEN="<token>" \
  ngrok/ngrok:latest http 8080
```

Ensure the capability secret is rotated regularly and never bake production secrets into the image.
