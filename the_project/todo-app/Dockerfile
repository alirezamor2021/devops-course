# Use official uv image as build helper
FROM ghcr.io/astral-sh/uv:latest AS uv_bin

# Base stage with Python 3.14
FROM python:3.14-slim

# Copy uv binary into the image
COPY --from=uv_bin /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency definition files
COPY pyproject.toml ./

# Sync project dependencies using uv
RUN uv sync --frozen --no-cache || uv sync --no-cache

# Copy application code
COPY main.py ./

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

# Expose port
EXPOSE 5000

# Run the app using uv
CMD ["uv", "run", "python", "main.py"]