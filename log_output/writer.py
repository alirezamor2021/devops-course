import os
import time
import uuid
from datetime import datetime, timezone


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


STATUS_FILE = require_env("STATUS_FILE")
WRITE_INTERVAL_SECONDS = float(require_env("WRITE_INTERVAL_SECONDS"))


def main() -> None:
    stored_string = str(uuid.uuid4())
    print(f"Writer started. Generating string: {stored_string}", flush=True)

    while True:
        current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        log_line = f"{current_time}: {stored_string}\n"
        try:
            with open(STATUS_FILE, "w") as f:
                f.write(log_line)
        except Exception as e:
            print(f"Error writing to shared file: {e}", flush=True)
        time.sleep(WRITE_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()