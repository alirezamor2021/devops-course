# the_project/todo-backend/main.py
import os
import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from psycopg.conninfo import make_conninfo
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from pydantic import BaseModel, Field


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
            print("Database ready", flush=True)
            return
        except Exception as e:
            print(f"DB not ready (attempt {attempt}/{DB_CONNECT_RETRIES}): {e}", flush=True)
            time.sleep(DB_RETRY_DELAY_SECONDS)
    raise RuntimeError("Could not connect to the database")


@asynccontextmanager
async def lifespan(app: FastAPI):
    pool.open(wait=False)
    init_db()
    yield
    pool.close()


app = FastAPI(lifespan=lifespan)


class TodoIn(BaseModel):
    text: str = Field(min_length=1, max_length=MAX_TODO_LENGTH)


@app.get("/todos")
def get_todos():
    with pool.connection() as conn:
        return conn.execute("SELECT id, text FROM todos ORDER BY id").fetchall()


@app.post("/todos", status_code=201)
def create_todo(body: TodoIn):
    with pool.connection() as conn:
        return conn.execute(
            "INSERT INTO todos (text) VALUES (%s) RETURNING id, text",
            (body.text.strip(),),
        ).fetchone()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)