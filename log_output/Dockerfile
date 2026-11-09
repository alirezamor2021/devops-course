FROM ghcr.io/astral-sh/uv:latest AS uv_bin
FROM python:3.14-slim

COPY --from=uv_bin /uv /uvx /bin/
WORKDIR /app

COPY pyproject.toml ./
RUN uv sync --frozen --no-cache || uv sync --no-cache

# Copy both scripts into the container image
COPY writer.py server.py ./

ENV PYTHONUNBUFFERED=1