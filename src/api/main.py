
from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import os
import uuid

from src.upload.upload import upload_file

app = FastAPI()

TEMP_DIR = "temp_uploads"
MAX_FILE_SIZE = 5 * 1024 * 1024

if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        ## VALIDATE FILE TYPE
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detial="Only PDF files are allowed")
        
        ## GENERATE SAFE UNIQUE NAME
        unique_id = str(uuid.uuid4())
        filename = f"{unique_id}_{file.filename}"

        file_path = os.path.join(TEMP_DIR,file.filename)

        ## SAVE FILE TEMPORARILY
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        ## VALIDATE FILE SIZE
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail="File exceeds 5MD limit")

        upload_file(file_path)

        return {
            "message": "File uploaded successfully",
            "filename": filename,
            "size" : file_size,
        }
    
    except HTTPException as e:
        raise e
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))