import boto3
from datetime import datetime

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("TaxDocumentAudit")

def log_to_db(filename, file_size, upload_method_):
    try:
        table.put_item(
            Item={
                "file_name": filename,
                "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
                "file_size": file_size,
                "upload_method": upload_method_
            }
        )
        print("[DB LOG] Logged to DynamoDB")
    
    except Exception as e:
        print(f"[DB ERROR] {str(e)}")