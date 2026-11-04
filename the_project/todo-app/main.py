import os
from http.server import HTTPServer, BaseHTTPRequestHandler

class TodoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Todo app is running!")

    def log_message(self, format, *args):
        # Optional: Suppress default request logs to keep output clean, or let it log standard requests
        return

def run() -> None:
    # Read PORT from environment variable, default to 5000 if not set
    port = int(os.environ.get("PORT", 5000))
    server_address = ('', port)
    
    httpd = HTTPServer(server_address, TodoHandler)
    
    # Required startup message
    print(f"Server started in port {port}", flush=True)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    run()