import os
from http.server import HTTPServer, BaseHTTPRequestHandler

class StatusHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        log_file_path = "/shared/status.txt"
        content = "Waiting for status..."
        
        if os.path.exists(log_file_path):
            try:
                with open(log_file_path, "r") as f:
                    content = f.read()
            except Exception as e:
                content = f"Error reading status file: {e}"

        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))

    def log_message(self, format, *args):
        return

def run() -> None:
    port = int(os.environ.get("PORT", 5000))
    server_address = ('', port)
    httpd = HTTPServer(server_address, StatusHandler)
    print(f"Server started in port {port}", flush=True)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    run()