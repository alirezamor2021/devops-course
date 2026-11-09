import os
from fastapi import FastAPI
import uvicorn

app = FastAPI()

COUNTER_FILE = "/shared/counter.txt"

def get_and_increment_counter() -> int:
    os.makedirs(os.path.dirname(COUNTER_FILE), exist_ok=True)
    count = 0
    if os.path.exists(COUNTER_FILE):
        try:
            with open(COUNTER_FILE, "r") as f:
                content = f.read().strip()
                if content.isdigit():
                    count = int(content)
        except Exception:
            pass
    
    count += 1
    
    try:
        with open(COUNTER_FILE, "w") as f:
            f.write(str(count))
    except Exception as e:
        print(f"Error writing counter: {e}", flush=True)
        
    return count

@app.get("/pingpong")
def ping_pong():
    current_count = get_and_increment_counter()
    return f"pong {current_count - 1}"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)