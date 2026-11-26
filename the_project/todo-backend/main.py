# the_project/todo-backend/main.py
import logging
import os
import sys
import threading
from contextlib import asynccontextmanager
from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Path, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ConfigDict, StrictBool
from sqlalchemy import URL, text
from sqlmodel import Field, Session, SQLModel, create_engine, select


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


PORT = int(require_env("PORT"))
MAX_TODO_LENGTH = int(require_env("MAX_TODO_LENGTH"))
DB_HOST = require_env("DB_HOST")
DB_PORT = int(require_env("DB_PORT"))
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


# --- Models -------------------------------------------------------------------

class Todo(SQLModel, table=True):
    """Database table."""
    __tablename__ = "todos"

    id: int | None = Field(default=None, primary_key=True)
    text: str
    done: bool = Field(default=False, sa_column_kwargs={"server_default": text("false")})


class TodoCreate(SQLModel):
    """Body of POST /todos. Unknown fields are rejected; text is trimmed first."""
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    text: str = Field(min_length=1, max_length=MAX_TODO_LENGTH)


class TodoUpdate(SQLModel):
    """Body of PUT /todos/{id}. Only a real JSON boolean is accepted (not "true" or 1)."""
    model_config = ConfigDict(extra="forbid")

    done: StrictBool


# --- Database -----------------------------------------------------------------

engine = create_engine(
    URL.create(
        "postgresql+psycopg",
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
    ),
    pool_size=5,
    pool_pre_ping=True,          # drop connections the database has closed
    pool_timeout=DB_TIMEOUT_SECONDS,
    connect_args={"connect_timeout": max(1, int(DB_TIMEOUT_SECONDS))},
)

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
        SQLModel.metadata.create_all(engine)
        # Tables created before the "done" field existed get the column added.
        with engine.begin() as conn:
            conn.execute(text(
                "ALTER TABLE todos ADD COLUMN IF NOT EXISTS done BOOLEAN NOT NULL DEFAULT FALSE"
            ))
        _schema_ready = True
        log.info("Database ready")


def get_session():
    ensure_schema()
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


# --- App ----------------------------------------------------------------------

# Set to False by POST /break. The liveness probe then fails and Kubernetes
# restarts the container, which starts healthy again.
is_healthy = True


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Don't block startup on the database: the readiness probe keeps the pod
    # out of the Service until /healthz can reach it.
    log.info("Backend started on port %d, todo limit %d characters", PORT, MAX_TODO_LENGTH)
    yield
    engine.dispose()


app = FastAPI(lifespan=lifespan)


def preview(value: object) -> str:
    """repr() escapes newlines, so a todo can't forge extra log lines."""
    shown = str(value)[:LOG_TEXT_PREVIEW_CHARS]
    suffix = "..." if len(str(value)) > LOG_TEXT_PREVIEW_CHARS else ""
    return repr(shown) + suffix


@app.exception_handler(RequestValidationError)
async def log_rejected_request(request: Request, exc: RequestValidationError):
    """Log every rejected body, then answer like FastAPI's default 422."""
    errors = exc.errors()
    reasons = "; ".join(
        f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in errors
    )
    body = exc.body if isinstance(exc.body, dict) else {}
    if "text" in body:
        log.warning(
            "Todo REJECTED: %s %s reason=%s length=%d text=%s",
            request.method, request.url.path, reasons, len(str(body["text"])), preview(body["text"]),
        )
    else:
        log.warning("Todo REJECTED: %s %s reason=%s", request.method, request.url.path, reasons)
    return JSONResponse(status_code=422, content={"detail": jsonable_encoder(errors)})


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
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
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


@app.get("/todos", response_model=list[Todo])
def get_todos(session: SessionDep):
    todos = session.exec(select(Todo).order_by(Todo.id)).all()
    log.info("Listed %d todos", len(todos))
    return todos


@app.post("/todos", status_code=201, response_model=Todo)
def create_todo(body: TodoCreate, session: SessionDep):
    todo = Todo.model_validate(body)
    session.add(todo)
    session.commit()
    session.refresh(todo)
    log.info("Todo created: id=%d length=%d text=%s", todo.id, len(todo.text), preview(todo.text))
    return todo


@app.put("/todos/{todo_id}", response_model=Todo)
def update_todo(
    todo_id: Annotated[int, Path(gt=0)],
    body: TodoUpdate,
    session: SessionDep,
):
    todo = session.get(Todo, todo_id)
    if todo is None:
        log.warning("Todo update REJECTED: id=%d not found", todo_id)
        raise HTTPException(status_code=404, detail="Todo not found")

    todo.done = body.done
    session.add(todo)
    session.commit()
    session.refresh(todo)
    log.info("Todo updated: id=%d done=%s", todo.id, todo.done)
    return todo


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
