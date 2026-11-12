import os
import threading
from fastapi import FastAPI
from pydantic import BaseModel, Field
import uvicorn


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


PORT = int(require_env("PORT"))
MAX_TODO_LENGTH = int(require_env("MAX_TODO_LENGTH"))

app = FastAPI()

todos: list[dict] = [
    {"id": 1, "text": "Learn Kubernetes basics"},
    {"id": 2, "text": "Deploy application to cluster"},
    {"id": 3, "text": "Configure persistent volumes"},
]
next_id = 4
lock = threading.Lock()


class TodoIn(BaseModel):
    text: str = Field(min_length=1, max_length=MAX_TODO_LENGTH)


@app.get("/todos")
def get_todos():
    with lock:
        return list(todos)


@app.post("/todos", status_code=201)
def create_todo(body: TodoIn):
    global next_id
    with lock:
        todo = {"id": next_id, "text": body.text.strip()}
        next_id += 1
        todos.append(todo)
    return todo


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)