import os
import time
from fastapi import APIRouter, UploadFile, File, HTTPException
from config import UPLOAD_DIR

router = APIRouter()

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Recibe el PDF y lo guarda en UPLOAD_DIR.
    """
    startTime = time.time()
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF.")
    
    filePath = os.path.join(UPLOAD_DIR, file.filename)
    with open(filePath, "wb") as f:
        f.write(await file.read())
    
    end_time = time.time()
    print(f"Archivo subido en {end_time - startTime:.2f} segundos.")
    return {"filename": file.filename, "filePath": filePath}
