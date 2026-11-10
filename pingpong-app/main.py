import threading
from fastapi import FastAPI
import uvicorn

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
    uvicorn.run(app, host="0.0.0.0", port=3000)