from fastapi import FastAPI, UploadFile, File, HTTPException
import os
import uuid
import boto3

from src.upload.upload import upload_file
from src.processing.parser import process_document
from src.processing.storage import save_result
from src.processing.textract_service import analyze_document_bytes
from src.audit.logger import log_upload
from src.processing.field_mapper import map_textract_to_tax_fields
from src.processing.classifier import classify_document
from src.processing.validator import validate_w2_data
from src.processing.normalizer import normalize_w2_data
# from src.audit.db_logger import log_to_db

app = FastAPI()

s3 =boto3.client('s3', region_name='us-east-1')

BUCKET_NAME = "tax-doc-system-chim-dev"
TEMP_DIR = "temp_uploads"
MAX_FILE_SIZE = 5 * 1024 * 1024

if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

from fastapi import Query

@app.get("/generate-upload-url")
def generate_upload_url(filename: str = Query(...)):
    try:
        unique_filename = f"{uuid.uuid4()}_{filename}"

        url = s3.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": BUCKET_NAME,
                "Key": unique_filename,
                "ContentType": "application/pdf"
            },
            ExpiresIn=300
        )

        return {
            "upload_url": url,
            "filename": unique_filename
        }
    except Exception as e:
        return {"error": str(e)}

textract = boto3.client('textract', region_name='us-east-1')

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        ## STEP 1. VALIDATE FILE TYPE
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail= "Only PDF files are allowed")
        
        ## STEP 2. READ FILE INTO BYTES IMMEDIATELY
        file_bytes = await file.read()
        file_size = len(file_bytes)

        if file_size == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        if file_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail= "File exceeds 5MB limit")
        
        # STEP 3. TEXTRACT PROCESSING
        raw_text_data = analyze_document_bytes(file_bytes)
        print("[TEXTRACT RESPONSE RECEIVED]")

        # STEP 4. CLASSIFY DOCUMENT
        doc_type = classify_document(raw_text_data)
        print("[DOCUMENT TYPE]", doc_type)

        if doc_type != "W2":
            raise HTTPException(
                status_code=422,
                detail="Uploaded document is not a W-2. Processing aborted."
            )

        # STEP 5. PROCESS DOCUMENT
        result = process_document(file_bytes, raw_text_data)

        # STEP 6. MAP TO TAX FIELDS
        mapped_data = map_textract_to_tax_fields(raw_text_data)

        validated_data, confidence = validate_w2_data(mapped_data)

        print("[VALIDATED DATA]", validated_data)
        print("[CONFIDENCE]", confidence)

        # STEP 7. NORMALIZE DATA

        normalized_data = normalize_w2_data(validated_data)

        print("[NORMALIZED DATA]", normalized_data)

        # STEP 7. STRICT VALIDATION (REJECT LOW-CONFIDENCE CORE FIELDS)
        if (
            confidence.get("wages_box_1") == "low" or
            confidence.get("employer_ein") == "low"
        ):
            
            raise HTTPException(
                status_code=422,
                detail="Unable to confidently extract required W-2 data (Wages or EIN invalid)"
        )

        # Attach mapped data to result
        result["mapped_data"] = mapped_data

        ## STEP 8. PROCEED WITH ANALYZING AND SAVING

        # GENERATE SAFE UNIQUE NAME & SAVE METADATA
        unique_id = str(uuid.uuid4())
        filename = f"{unique_id}_{file.filename}"
        
        result["file_name"] = filename
        result["size"] = file_size
        save_result(result)

        ## STEP 9. UPLOAD TO S3
        upload_success = upload_file(file_bytes, BUCKET_NAME, filename)
        
        if upload_success:
            # LOG TO TEXT FILE
            log_upload(filename, BUCKET_NAME, file_size)
            
            # LOG TO DYNAMODB (coming soon)
            # log_to_db(filename, file_size, "FastAPI_Memory_Upload")

        return {
            "status": "success",
            "file_name": filename,
            "file_size": file_size,
            "data": normalized_data,
            "confidence": confidence
        }
    
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))