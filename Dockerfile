FROM python:3.12-alpine

EXPOSE 80

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV API_PORT=80


WORKDIR /app

RUN --mount=type=bind,source=requirements/prod.txt,target=/tmp/requirements.txt \
    --mount=type=cache,target=/root/.cache/pip \
    apk --no-cache add curl && \
    pip install -r /tmp/requirements.txt


COPY . .


HEALTHCHECK --interval=5s --timeout=10s --retries=3 CMD curl -sS --fail 127.0.0.1:80/ping

ENTRYPOINT ["python3", "/app/api"]
