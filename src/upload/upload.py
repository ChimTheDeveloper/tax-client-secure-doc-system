## Simulate secure file uploads before integrating with cloud storage
import boto3
import os

## Connecting upload audit & tracking system
from src.audit.logger import log_upload

## Initialize S3 client
s3 = boto3.client("s3")

BUCKET_NAME = "tax-doc-system-chim-dev"

def upload_file(file_path):
    ## Uploads a file to AWS S3
    
    try:
        ## Validation step
        if not os.path.exists(file_path):
            print("[ERROR] File not found")
            return
        ## Extract file name
        filename = os.path.basename(file_path)
        ## Upload to S3
        s3.upload_file(file_path, BUCKET_NAME, filename)
        ## Updating upload to include audit & tracking
        log_upload(file_path, BUCKET_NAME)
        print(f"[SUCCESS] Uploaded {filename} to S3 bucket: {BUCKET_NAME}")

    except Exception as e:
        print(f"[ERROR] Upload failed")
        print(f"Details: {str(e)}")

if __name__ == "__main__":
    test_file = "test_document.pdf"
    upload_file(test_file)