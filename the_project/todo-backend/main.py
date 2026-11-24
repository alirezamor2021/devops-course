# the_project/todo-backend/main.py
import logging
import os
import sys
import threading
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from psycopg.conninfo import make_conninfo
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from pydantic import BaseModel


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


PORT = int(require_env("PORT"))
MAX_TODO_LENGTH = int(require_env("MAX_TODO_LENGTH"))
DB_HOST = require_env("DB_HOST")
DB_PORT = require_env("DB_PORT")
DB_NAME = require_env("POSTGRES_DB")
DB_USER = require_env("POSTGRES_USER")
DB_PASSWORD = require_env("POSTGRES_PASSWORD")
DB_TIMEOUT_SECONDS = float(require_env("DB_TIMEOUT_SECONDS"))
LOG_LEVEL = require_env("LOG_LEVEL")
LOG_TEXT_PREVIEW_CHARS = int(require_env("LOG_TEXT_PREVIEW_CHARS"))

logging.basicConfig(
    stream=sys.stdout,
    level=LOG_LEVEL.upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("todo-backend")

conninfo = make_conninfo(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
)

pool = ConnectionPool(
    conninfo,
    min_size=1,
    max_size=5,
    open=False,
    timeout=DB_TIMEOUT_SECONDS,
    kwargs={"row_factory": dict_row, "connect_timeout": max(1, int(DB_TIMEOUT_SECONDS))},
)

# Set to False by POST /break. The liveness probe then fails and Kubernetes
# restarts the container, which starts healthy again.
is_healthy = True

_schema_ready = False
_schema_lock = threading.Lock()


def ensure_schema() -> None:
    """Create the table once the database is reachable. Raises if it is not."""
    global _schema_ready
    if _schema_ready:
        return
    with _schema_lock:
        if _schema_ready:
            return
        with pool.connection() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS todos ("
                "id SERIAL PRIMARY KEY, "
                "text TEXT NOT NULL)"
            )
        _schema_ready = True
        log.info("Database ready")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Don't block startup on the database: the readiness probe keeps the pod
    # out of the Service until /healthz can reach it.
    pool.open(wait=False)
    log.info("Backend started on port %d, todo limit %d characters", PORT, MAX_TODO_LENGTH)
    yield
    pool.close()


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def broken_guard(request: Request, call_next):
    """Once broken, every endpoint (probes included) fails."""
    if not is_healthy:
        return JSONResponse(status_code=500, content={"status": "unhealthy"})
    return await call_next(request)


@app.get("/livez")
def livez():
    """Liveness: the process is serving and has not been broken."""
    return {"status": "ok"}


@app.get("/healthz")
def healthz():
    """Readiness: the database is reachable and the table exists."""
    try:
        ensure_schema()
        with pool.connection() as conn:
            conn.execute("SELECT 1")
    except Exception as e:
        log.warning("Readiness check failed: %s", e)
        return JSONResponse(status_code=503, content={"status": "database unavailable"})
    return {"status": "ok"}


@app.post("/break")
def break_app():
    global is_healthy
    is_healthy = False
    log.warning("App broken on request; liveness probe will now fail")
    return {"status": "broken"}


class TodoIn(BaseModel):
    text: str


def preview(text: str) -> str:
    """repr() escapes newlines, so a todo can't forge extra log lines."""
    shown = text[:LOG_TEXT_PREVIEW_CHARS]
    suffix = "..." if len(text) > LOG_TEXT_PREVIEW_CHARS else ""
    return repr(shown) + suffix


@app.get("/todos")
def get_todos():
    ensure_schema()
    with pool.connection() as conn:
        rows = conn.execute("SELECT id, text FROM todos ORDER BY id").fetchall()
    log.info("Listed %d todos", len(rows))
    return rows


@app.post("/todos", status_code=201)
def create_todo(body: TodoIn):
    text = body.text.strip()

    if not text:
        log.warning("Todo REJECTED: empty text")
        raise HTTPException(status_code=422, detail="Todo text must not be empty")

    if len(text) > MAX_TODO_LENGTH:
        log.warning(
            "Todo REJECTED: too long, length=%d limit=%d text=%s",
            len(text), MAX_TODO_LENGTH, preview(text),
        )
        raise HTTPException(
            status_code=422,
            detail=f"Todo must be at most {MAX_TODO_LENGTH} characters",
        )

    ensure_schema()
    with pool.connection() as conn:
        todo = conn.execute(
            "INSERT INTO todos (text) VALUES (%s) RETURNING id, text",
            (text,),
        ).fetchone()

    log.info("Todo created: id=%d length=%d text=%s", todo["id"], len(text), preview(text))
    return todo


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)