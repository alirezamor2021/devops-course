import time
import uuid
from datetime import datetime, timezone

def main() -> None:
    # Generate a random string (UUID) on startup and store it in memory
    stored_string = str(uuid.uuid4())
    
    # Optional startup log
    print(f"[{datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')}] App started with string: {stored_string}", flush=True)

    try:
        while True:
            # Generate the ISO timestamp matching the exercise format
            current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            
            # Output matching the requested format: timestamp: string
            print(f"{current_time}: {stored_string}", flush=True)
            
            time.sleep(5)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()