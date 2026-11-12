import os
import threading
from fastapi import FastAPI
import uvicorn


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


PORT = int(require_env("PORT"))

app = FastAPI()

counter = 0
lock = threading.Lock()


@app.get("/pingpong")
def ping_pong():
    global counter
    with lock:
        current = counter
        counter += 1
    return f"pong {current}"


@app.get("/pings")
def pings():
    with lock:
        return counter


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)