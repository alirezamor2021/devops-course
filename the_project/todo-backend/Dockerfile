FROM python:3.14-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
# Precompile .pyc files at build time; otherwise every container start
# compiles SQLAlchemy/Pydantic first, which is slow under the 250m CPU limit.
ENV UV_COMPILE_BYTECODE=1
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-cache
COPY main.py .
# Run the venv's Python directly: `uv run` would re-check the environment on every start.
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1
CMD ["python", "main.py"]
