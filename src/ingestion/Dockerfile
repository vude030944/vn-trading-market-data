# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS base

# uv for fast installs and tight version pinning
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /usr/local/bin/uv

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Install dependencies first, separately from source -> code changes skip reinstall
COPY pyproject.toml ./
RUN uv venv /opt/venv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --python /opt/venv --no-cache \
        websockets aiokafka cramjam httpx uvloop python-dotenv \
        opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp-proto-http \
        msgpack

# Source goes under /app/ingestion so `python -m ingestion` works
COPY . /app/ingestion/

# Do not run as root
RUN useradd --create-home --uid 10001 appuser \
    && mkdir -p /tmp/health \
    && chown -R appuser:appuser /app /tmp/health
USER appuser

ENV HEALTH_FILE=/tmp/health/ingestion.json

# --broker is supplied by docker-compose
ENTRYPOINT ["python", "-m", "ingestion"]
