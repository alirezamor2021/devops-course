# the_project/todo-backend/main.py
import logging
import os
import sys
import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
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
DB_CONNECT_RETRIES = int(require_env("DB_CONNECT_RETRIES"))
DB_RETRY_DELAY_SECONDS = float(require_env("DB_RETRY_DELAY_SECONDS"))
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
    kwargs={"row_factory": dict_row},
)


def init_db() -> None:
    """Create the table, retrying until the database accepts connections."""
    for attempt in range(1, DB_CONNECT_RETRIES + 1):
        try:
            with pool.connection() as conn:
                conn.execute(
                    "CREATE TABLE IF NOT EXISTS todos ("
                    "id SERIAL PRIMARY KEY, "
                    "text TEXT NOT NULL)"
                )
            log.info("Database ready")
            return
        except Exception as e:
            log.warning("DB not ready (attempt %d/%d): %s", attempt, DB_CONNECT_RETRIES, e)
            time.sleep(DB_RETRY_DELAY_SECONDS)
    raise RuntimeError("Could not connect to the database")


@asynccontextmanager
async def lifespan(app: FastAPI):
    pool.open(wait=False)
    init_db()
    log.info("Backend started on port %d, todo limit %d characters", PORT, MAX_TODO_LENGTH)
    yield
    pool.close()


app = FastAPI(lifespan=lifespan)


class TodoIn(BaseModel):
    text: str


def preview(text: str) -> str:
    """repr() escapes newlines, so a todo can't forge extra log lines."""
    shown = text[:LOG_TEXT_PREVIEW_CHARS]
    suffix = "..." if len(text) > LOG_TEXT_PREVIEW_CHARS else ""
    return repr(shown) + suffix


@app.get("/todos")
def get_todos():
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

    with pool.connection() as conn:
        todo = conn.execute(
            "INSERT INTO todos (text) VALUES (%s) RETURNING id, text",
            (text,),
        ).fetchone()

    log.info("Todo created: id=%d length=%d text=%s", todo["id"], len(text), preview(text))
    return todo


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)