import os
from datetime import datetime

# 1. Use an absolute-style path for the log file 
# This ensures the log stays in the root project folder regardless of where you start the server
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_FILE = os.path.join(BASE_DIR, "audit_log.txt")

def log_upload(filename, bucket_name, file_size=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 2. Handle the 'None' case for file_size gracefully
    # This prevents 'None bytes' from appearing in your professional logs
    display_size = f"{file_size:,}" if file_size is not None else "Unknown"

    log_entry = (
        f"Timestamp: {timestamp}\n"
        f"File:      {filename}\n"
        f"Size:      {display_size} bytes\n"
        f"Bucket:    {bucket_name}\n"
        f"{'-' * 40}\n"
    )

    try:
        with open(LOG_FILE, "a") as log:
            log.write(log_entry)
        print(f"[AUDIT] Logged upload for: {filename}")
    except Exception as e:
        # Use f-strings for clearer error reporting
        print(f"[ERROR] Could not write to audit log: {e}")