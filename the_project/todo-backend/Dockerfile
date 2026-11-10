FROM python:3.14-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache || uv sync --no-cache
COPY main.py .
CMD ["uv", "run", "--no-dev", "main.py"]
