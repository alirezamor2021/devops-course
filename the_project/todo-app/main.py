import os
import time
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

# Use shared volume if available, fallback to local directory for testing
SHARED_DIR = "/shared" if os.path.exists("/shared") else "./shared"
IMAGE_PATH = os.path.join(SHARED_DIR, "image.jpg")
IMAGE_URL = "https://picsum.photos/1200"
CACHE_DURATION = 10 * 60  # 10 minutes in seconds

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
            max-width: 500px; 
            text-align: center;
        }
        h1 { 
            margin-top: 0; 
            color: #2c3e50; 
            font-size: 28px; 
            margin-bottom: 20px; 
        }
        .image-container {
            margin-bottom: 20px;
        }
        .image-container img {
            width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .input-group { 
            display: flex; 
            gap: 10px; 
            margin-bottom: 20px; 
        }
        input[type="text"] { 
            flex: 1; 
            padding: 10px; 
            border: 1px solid #ddd; 
            border-radius: 4px; 
            font-size: 14px; 
        }
        button { 
            padding: 10px 15px; 
            background: #3498db; 
            color: white; 
            border: none; 
            border-radius: 4px; 
            cursor: pointer; 
            font-weight: bold; 
        }
        button:hover { 
            background: #2980b9; 
        }
        ul { 
            list-style: none; 
            padding: 0; 
            text-align: left;
        }
        li { 
            background: #f8f9fa; 
            padding: 10px 15px; 
            margin-bottom: 8px; 
            border-radius: 4px; 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            border-left: 4px solid #3498db; 
        }
        .footer {
            margin-top: 25px;
            font-size: 14px;
            color: #7f8c8d;
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
            <input type="text" id="todoInput" placeholder="Add a new task...">
            <button onclick="addTodo()">Add</button>
        </div>
        <ul id="todoList">
            <li><span>Deploy app to Kubernetes</span></li>
        </ul>
        <div class="footer">
            DevOps with Kubernetes 2026
        </div>
    </div>
    <script>
        function addTodo() {
            const input = document.getElementById('todoInput');
            const text = input.value.trim();
            if (text) {
                const ul = document.getElementById('todoList');
                const li = document.createElement('li');
                li.innerHTML = `<span>${text}</span>`;
                ul.appendChild(li);
                input.value = '';
            }
        }
    </script>
</body>
</html>
"""

class TodoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode("utf-8"))
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
    port = int(os.environ.get("PORT", 5000))
    server_address = ('', port)
    httpd = HTTPServer(server_address, TodoHandler)
    
    print(f"Server started in port {port}", flush=True)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    run()