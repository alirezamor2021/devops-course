import os
import threading

import psycopg
import uvicorn
from fastapi import FastAPI, HTTPException


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


PORT = int(require_env("PORT"))
DB_CONNINFO = (
    f"host={require_env('POSTGRES_HOST')} "
    f"port={os.environ.get('POSTGRES_PORT', '5432')} "
    f"dbname={require_env('POSTGRES_DB')} "
    f"user={require_env('POSTGRES_USER')} "
    f"password={require_env('POSTGRES_PASSWORD')} "
    f"connect_timeout=2"
)

app = FastAPI()

_conn: psycopg.Connection | None = None
_lock = threading.Lock()


def _get_conn() -> psycopg.Connection:
    """Return a live DB connection, (re)connecting and creating the schema if needed."""
    global _conn
    if _conn is not None and not _conn.closed and not _conn.broken:
        return _conn
    conn = psycopg.connect(DB_CONNINFO, autocommit=True)
    conn.execute("CREATE TABLE IF NOT EXISTS pingpong (id INT PRIMARY KEY, counter BIGINT NOT NULL)")
    conn.execute("INSERT INTO pingpong (id, counter) VALUES (1, 0) ON CONFLICT (id) DO NOTHING")
    _conn = conn
    return conn


def _run(query: str) -> int:
    with _lock:
        try:
            return _get_conn().execute(query).fetchone()[0]
        except psycopg.Error as e:
            print(f"Database error: {e}", flush=True)
            raise HTTPException(status_code=503, detail="database unavailable")


@app.get("/")
def ping_pong():
    current = _run("UPDATE pingpong SET counter = counter + 1 WHERE id = 1 RETURNING counter - 1")
    return f"pong {current}"


@app.get("/pings")
def pings():
    return _run("SELECT counter FROM pingpong WHERE id = 1")


@app.get("/healthz")
def healthz():
    """Readiness: OK only when the database is reachable."""
    _run("SELECT 1")
    return "ok"


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
