import os
import time
import uuid
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timezone

# Store the random string and startup timestamp in memory
STORED_STRING = str(uuid.uuid4())
STARTUP_TIME = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def background_logger():
    """Outputs the timestamp and random string to stdout every 5 seconds."""
    while True:
        current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        print(f"{current_time}: {STORED_STRING}", flush=True)
        time.sleep(5)

class StatusHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        
        # Response body containing the requested status info
        response_text = f"Startup time: {STARTUP_TIME}\nCurrent time: {current_time}\nStored string: {STORED_STRING}"
        self.wfile.write(response_text.encode("utf-8"))

    def log_message(self, format, *args):
        # Suppress default HTTP server access logs to keep terminal clean
        return

def run() -> None:
    port = int(os.environ.get("PORT", 5000))
    
    # Start the background logging loop in a separate thread
    logger_thread = threading.Thread(target=background_logger, daemon=True)
    logger_thread.start()

    # Start the HTTP server
    server_address = ('', port)
    httpd = HTTPServer(server_address, StatusHandler)
    print(f"Server started in port {port}", flush=True)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    run()