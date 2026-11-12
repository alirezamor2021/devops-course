import os
import time
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


PORT = int(require_env("PORT"))
IMAGE_DIR = require_env("IMAGE_DIR")
IMAGE_URL = require_env("IMAGE_URL")
CACHE_DURATION_SECONDS = int(require_env("CACHE_DURATION_SECONDS"))
TODOS_URL = require_env("TODOS_URL")
MAX_TODO_LENGTH = int(require_env("MAX_TODO_LENGTH"))

IMAGE_PATH = os.path.join(IMAGE_DIR, "image.jpg")

def get_cached_image():
    """Checks if the cached image is older than 10 minutes. If so, fetches a new one."""
    os.makedirs(SHARED_DIR, exist_ok=True)
    
    fetch_new = False
    if not os.path.exists(IMAGE_PATH):
        fetch_new = True
    else:
        file_age = time.time() - os.path.getmtime(IMAGE_PATH)
        if file_age > CACHE_DURATION:
            fetch_new = True

    if fetch_new:
        try:
            print("Fetching new image from Lorem Picsum...", flush=True)
            req = urllib.request.Request(IMAGE_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(IMAGE_PATH, 'wb') as out_file:
                out_file.write(response.read())
        except Exception as e:
            print(f"Failed to fetch image: {e}", flush=True)
            
    return IMAGE_PATH

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Todo Application</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
            background-color: #f4f6f9; 
            color: #333; 
            margin: 0; 
            padding: 40px; 
            display: flex; 
            justify-content: center; 
        }
        .container { 
            background: #fff; 
            padding: 30px; 
            border-radius: 8px; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.05); 
            width: 100%; 
            max-width: 600px; 
            text-align: center;
        }
        h1 { 
            margin-top: 0; 
            color: #2c3e50; 
            font-size: 32px; 
            margin-bottom: 20px; 
        }
        h2 {
            color: #2c3e50;
            font-size: 22px;
            margin-top: 30px;
            margin-bottom: 15px;
        }
        .image-container {
            margin-bottom: 25px;
        }
        .image-container img {
            width: 100%;
            max-width: 400px;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        .input-group { 
            display: flex; 
            gap: 10px; 
            margin-bottom: 30px; 
            justify-content: center;
        }
        input[type="text"] { 
            width: 70%; 
            padding: 12px 15px; 
            border: 1px solid #27ae60; 
            border-radius: 4px; 
            font-size: 15px; 
            outline: none;
        }
        input[type="text"]:focus {
            box-shadow: 0 0 5px rgba(39, 174, 96, 0.4);
        }
        button { 
            padding: 12px 25px; 
            background: #27ae60; 
            color: white; 
            border: none; 
            border-radius: 4px; 
            cursor: pointer; 
            font-size: 15px;
            font-weight: bold; 
        }
        button:hover { 
            background: #219653; 
        }
        ul { 
            list-style: none; 
            padding: 0; 
            text-align: left;
        }
        li { 
            background: #fff; 
            padding: 15px 20px; 
            margin-bottom: 12px; 
            border-radius: 4px; 
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            border-left: 5px solid #27ae60; 
            border-top: 1px solid #eee;
            border-right: 1px solid #eee;
            border-bottom: 1px solid #eee;
            font-size: 16px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Todo App</h1>
        <div class="image-container">
            <img src="/image" alt="Random Daily Image">
        </div>
        <div class="input-group">
            <input type="text" id="todoInput" maxlength="__MAX_TODO_LENGTH__" placeholder="Enter a new todo (max __MAX_TODO_LENGTH__ characters)">
            <button onclick="addTodo()">Send</button>
        </div>
        <h2>Todos</h2>
        <ul id="todoList"></ul>
        <p id="error" style="color:#c0392b;"></p>
    </div>
    </div>
    <script>
        const TODOS_URL = "__TODOS_URL__";
        const MAX_TODO_LENGTH = __MAX_TODO_LENGTH__;
        const list = document.getElementById('todoList');
        const input = document.getElementById('todoInput');
        const errorEl = document.getElementById('error');

        function render(todos) {
            list.innerHTML = '';
            for (const todo of todos) {
                const li = document.createElement('li');
                const span = document.createElement('span');
                span.textContent = todo.text;
                li.appendChild(span);
                list.appendChild(li);
            }
        }

        async function loadTodos() {
            try {
                const res = await fetch(TODOS_URL);
                if (!res.ok) throw new Error('HTTP ' + res.status);
                render(await res.json());
                errorEl.textContent = '';
            } catch (e) {
                errorEl.textContent = 'Could not load todos.';
            }
        }

        async function addTodo() {
            const text = input.value.trim();
            if (!text || text.length > MAX_TODO_LENGTH) return;
            try {
                const res = await fetch(TODOS_URL, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text })
                });
                if (!res.ok) throw new Error('HTTP ' + res.status);
                input.value = '';
                await loadTodos();
            } catch (e) {
                errorEl.textContent = 'Could not add todo.';
            }
        }

        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') addTodo();
        });
        loadTodos();
    </script>
</body>
</html>
"""

HTML_PAGE = (
    HTML_CONTENT
    .replace("__MAX_TODO_LENGTH__", str(MAX_TODO_LENGTH))
    .replace("__TODOS_URL__", TODOS_URL)
)
class TodoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        elif self.path == "/image":
            img_path = get_cached_image()
            if os.path.exists(img_path):
                self.send_response(200)
                self.send_header("Content-type", "image/jpeg")
                self.end_headers()
                with open(img_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Image not found")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def log_message(self, format, *args):
        return


def run() -> None:
    httpd = HTTPServer(("", PORT), TodoHandler)
    print(f"Server started in port {PORT}", flush=True)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    run()