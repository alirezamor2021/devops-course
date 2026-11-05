import os
from http.server import HTTPServer, BaseHTTPRequestHandler

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
        }
        h1 { 
            margin-top: 0; 
            color: #2c3e50; 
            font-size: 24px; 
            text-align: center; 
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
    </style>
</head>
<body>
    <div class="container">
        <h1>My Todo Application</h1>
        <div class="input-group">
            <input type="text" id="todoInput" placeholder="Add a new task...">
            <button onclick="addTodo()">Add</button>
        </div>
        <ul id="todoList">
            <li><span>Deploy app to Kubernetes</span></li>
        </ul>
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
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def log_message(self, format, *args):
        # Silence default web server log messages for cleaner stdout
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