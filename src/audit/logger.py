import os
from datetime import datetime

LOG_FILE = "audit_log.txt"

def log_upload(filename, bucket_name, file_size):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_entry = f"""
    Timestamp: {timestamp}
    File: {filename}
    Size: {file_size} bytes 
    Destination: {bucket_name}
    ------------------------------------
    """

    # Ensure we append to the log file safely
    try:
        with open(LOG_FILE, "a") as log:
            log.write(log_entry + "\n")
        print(f"[AUDIT] Logged upload for: {filename}")
    except Exception as e:
        print(f"[ERROR] Could not write to audit log: {e}")