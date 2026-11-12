import os
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


PORT = int(require_env("PORT"))
PING_PONG_URL = require_env("PING_PONG_URL")
PING_TIMEOUT_SECONDS = float(require_env("PING_TIMEOUT_SECONDS"))
CONFIG_FILE = require_env("CONFIG_FILE")
STATUS_FILE = require_env("STATUS_FILE")
MESSAGE = require_env("MESSAGE")


def get_ping_count() -> str:
    try:
        with urllib.request.urlopen(PING_PONG_URL, timeout=PING_TIMEOUT_SECONDS) as resp:
            return resp.read().decode("utf-8").strip()
    except Exception as e:
        print(f"Failed to fetch pings: {e}", flush=True)
        return "unavailable"


def get_file_content() -> str:
    try:
        with open(CONFIG_FILE, "r") as f:
            return f.read().strip()
    except Exception as e:
        print(f"Failed to read {CONFIG_FILE}: {e}", flush=True)
        return "unavailable"


class StatusHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        status_content = "Waiting for status..."
        if os.path.exists(STATUS_FILE):
            try:
                with open(STATUS_FILE, "r") as f:
                    status_content = f.read().strip()
            except Exception:
                pass

        response_text = (
            f"file content: {get_file_content()}\n"
            f"env variable: MESSAGE={MESSAGE}\n"
            f"{status_content}\n"
            f"Ping / Pongs: {get_ping_count()}"
        )

        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(response_text.encode("utf-8"))

    def log_message(self, format, *args):
        return


def run() -> None:
    httpd = HTTPServer(("", PORT), StatusHandler)
    print(f"Server started in port {PORT}", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    run()