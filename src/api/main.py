
from fastapi import FastAPI, UploadFile, File
import shutil
import os

from src.upload.upload import upload_file

app = FastAPI()

TEMP_DIR = "temp_uploads"

if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(TEMP_DIR,file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        upload_file(file_path)

        return {"message": "File uploaded successfully"}
    
    except Exception as e:
        return {"error": str(e)}