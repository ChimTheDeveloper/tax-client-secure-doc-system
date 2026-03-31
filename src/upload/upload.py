import boto3
from src.audit.logger import log_upload

# Initialize S3 client
s3 = boto3.client("s3", region_name="us-east-1")

BUCKET_NAME = "tax-doc-system-chim-dev"

def upload_file(file_bytes, bucket_name, filename):

    try:
        # Use put_object for bytes instead of upload_file for paths
        s3.put_object(
            Bucket=bucket_name,
            Key=filename,
            Body=file_bytes,
            ContentType="application/pdf" # Good for tax docs
        )
        
        # Log the upload (Note: pass the filename now instead of a path)
        log_upload(filename, bucket_name)
        
        print(f"[SUCCESS] Uploaded {filename} to S3 bucket: {bucket_name}")
        return True

    except Exception as e:
        print(f"[ERROR] Upload failed: {str(e)}")
        return False