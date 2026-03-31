import boto3
from datetime import datetime, timezone

# Initialize the resource (make sure region matches your S3/Textract)
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("TaxDocumentAudit")

def log_to_db(filename, file_size, upload_method="FastAPI_Bytes"):

    try:
        table.put_item(
            Item={
                "file_name": filename,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "file_size": file_size,
                "upload_method": upload_method
            }
        )
        print(f"[DB LOG] Successfully logged {filename} to DynamoDB")
    
    except Exception as e:
        # If the table doesn't exist yet, this will catch the error
        print(f"[DB ERROR] Could not log to DynamoDB: {str(e)}")