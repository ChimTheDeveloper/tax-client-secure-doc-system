import os
from datetime   import datetime

LOG_FILE = "audit_log.txt"

def log_upload(file_path, bucket_name):
    ## Logs metadata for uploaded files for audit tracking
    if not os.path.exists(file_path):
        print("[ERROR] File does not exist")
        return
    
    filename = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_entry = f"""
    Timestamp: {timestamp}
    File: {filename}
    Size: {file_size} bytes 
    Destination: {bucket_name}
    ------------------------------------
    """

    with open(LOG_FILE, "a") as log:
        log.write(log_entry + "\n")

    print(f"[AUDIT] {log_entry}")