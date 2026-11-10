import os
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

PING_PONG_URL = os.environ.get("PING_PONG_URL", "http://pingpong-svc:2345/pings")

def get_ping_count() -> str:
    try:
        with urllib.request.urlopen(PING_PONG_URL, timeout=3) as resp:
            return resp.read().decode("utf-8").strip()
    except Exception as e:
        print(f"Failed to fetch pings: {e}", flush=True)
        return "unavailable"

class StatusHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        status_file = "/shared/status.txt"

        status_content = "Waiting for status..."
        if os.path.exists(status_file):
            try:
                with open(status_file, "r") as f:
                    status_content = f.read().strip()
            except Exception:
                pass

        response_text = f"{status_content}\nPing / Pongs: {get_ping_count()}"

        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(response_text.encode("utf-8"))

    def log_message(self, format, *args):
        return

def run() -> None:
    port = int(os.environ.get("PORT", 5000))
    httpd = HTTPServer(("", port), StatusHandler)
    print(f"Server started in port {port}", flush=True)
    httpd.serve_forever()

if __name__ == "__main__":
    run()