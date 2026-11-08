FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency specification files
COPY pyproject.toml ./

# Install dependencies using uv without creating a virtual environment
RUN uv pip install --system --no-cache-dir .

# Copy application code
COPY main.py .

EXPOSE 3000

CMD ["python", "main.py"]