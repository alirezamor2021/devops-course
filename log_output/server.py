import os
from http.server import HTTPServer, BaseHTTPRequestHandler

class StatusHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        status_file = "/shared/status.txt"
        counter_file = "/shared/counter.txt"
        
        status_content = "Waiting for status..."
        if os.path.exists(status_file):
            try:
                with open(status_file, "r") as f:
                    status_content = f.read().strip()
            except Exception:
                pass
                
        ping_count = "0"
        if os.path.exists(counter_file):
            try:
                with open(counter_file, "r") as f:
                    ping_count = f.read().strip()
            except Exception:
                pass

        response_text = f"{status_content}\nPing / Pongs: {ping_count}"

        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(response_text.encode("utf-8"))

    def log_message(self, format, *args):
        return

def run() -> None:
    port = int(os.environ.get("PORT", 5000))
    server_address = ('', port)
    httpd = HTTPServer(server_address, StatusHandler)
    print(f"Server started in port {port}", flush=True)
    httpd.serve_forever()

if __name__ == "__main__":
    run()