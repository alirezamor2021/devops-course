from fastapi import FastAPI
import uvicorn

app = FastAPI()

# In-memory counter (resets on pod restart)
counter = 0

@app.get("/pingpong")
def ping_pong():
    global counter
    response_text = f"pong {counter}"
    counter += 1
    return response_text

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)