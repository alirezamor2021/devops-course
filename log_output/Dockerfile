# Use the official uv image as build helper
FROM ghcr.io/astral-sh/uv:latest AS uv_bin

# Base stage with Python 3.14
FROM python:3.14-slim

# Copy uv binary into the image
COPY --from=uv_bin /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency definition files first for optimal caching
COPY pyproject.toml ./

# Sync project dependencies using uv
RUN uv sync --frozen --no-cache || uv sync --no-cache

# Copy application source code
COPY main.py ./

# Set environment variable to ensure unbuffered logs
ENV PYTHONUNBUFFERED=1

# Run the app using uv
CMD ["uv", "run", "python", "main.py"]