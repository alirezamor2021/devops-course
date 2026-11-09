import time
import uuid
from datetime import datetime, timezone

def main() -> None:
    stored_string = str(uuid.uuid4())
    log_file_path = "/shared/status.txt"
    
    print(f"Writer started. Generating string: {stored_string}", flush=True)

    while True:
        current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        log_line = f"{current_time}: {stored_string}\n"
        
        # Write/append to the shared file
        try:
            with open(log_file_path, "w") as f:
                f.write(log_line)
        except Exception as e:
            print(f"Error writing to shared file: {e}", flush=True)
            
        time.sleep(5)

if __name__ == "__main__":
    main()