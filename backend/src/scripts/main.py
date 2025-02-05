import uvicorn

import os
import shutil
import json
import io

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from exportCSV import CSVExporter
from reportGenerator import ReportGenerator
from folders import buildFolder
from companyWeek import getCompanyWeek
from jsonUtils import getExcludes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directorio para guardar los archivos subidos
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Recibe el PDF y lo guarda en UPLOAD_DIR.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF.")
    
    filePath = os.path.join(UPLOAD_DIR, file.filename)
    with open(filePath, "wb") as f:
        f.write(await file.read())
    
    return {"filename": file.filename, "filePath": filePath}

@app.post("/process")
async def processPDF(
    file: UploadFile = File(...)
):
    """
    Copia el PDF subido a la carpeta correspondiente (usando buildFolder)
    y ejecuta la exportación de CSV (llamando a CSVExporter.export()).
    Se espera que el archivo de configuración (config.json) y el CSV principal ya estén en su lugar.
    """
    print(f"Procesando archivo: {file.filename}")
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF.")
    
    # Guarda el archivo temporalmente
    tempPath = os.path.join(UPLOAD_DIR, file.filename)
    with open(tempPath, "wb") as f:
        f.write(await file.read())
    
    try:
        company, week = getCompanyWeek(file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Error al obtener el cliente y semana: {e}')
    
    # Copia el PDF al directorio generado por buildFolder
    basePath = buildFolder(company, week)
    copyPDFPath = os.path.join(basePath, f"{company}_{week}.pdf")
    shutil.copy2(tempPath, copyPDFPath)
    print(f"PDF copiado a {copyPDFPath}")

    # Llama a la exportación de CSV
    exporter = CSVExporter(company, week)
    try:
        exporter.export()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exportando CSV: {e}")
    
    configPath = os.path.join(basePath, 'config.json')
    excludes = getExcludes(configPath)

    return {"detail": "CSV exportado exitosamente", "company": company, "week": week, "excludes": excludes}

@app.post("/finalize")
async def finalizePDF(
    file: UploadFile = File(...),
    company: str = Form(...),
    week: str = Form(...),
    pdfName: str = Form(...),
    excludePages: str = Form(...),
    riesgo: str = Form(...)
):
    """
    Recibe el PDF (o utiliza el que ya se encuentre en la carpeta) y los parámetros para generar el reporte final.
    Se utiliza ReportGenerator para insertar las observaciones y se devuelve el PDF final.
    """
    # Validar que el archivo sea PDF
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF.")

    # Guarda el archivo temporalmente
    tempPath = os.path.join(UPLOAD_DIR, file.filename)
    with open(tempPath, "wb") as f:
        f.write(await file.read())
    
    # Parsear los parámetros JSON
    try:
        excludePagesList = json.loads(excludePages)
        riesgoDict = json.loads(riesgo)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Formato incorrecto en excludePages o riesgo")

    # Copiar el PDF al directorio de destino (la carpeta se crea con buildFolder)
    basePath = buildFolder(company, week)
    copyPDFPath = os.path.join(basePath, f"{pdfName}_{week}.pdf")
    shutil.copy2(tempPath, copyPDFPath)

    # Crear la instancia de ReportGenerator y generar el reporte
    outputPDFName = f"{pdfName}_output.pdf"
    try:
        reportGen = ReportGenerator(company, week, pdfName, excludePagesList, riesgoDict, outputPDFName)
        reportGen.generateReport()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando el reporte: {e}")

    # Leer el PDF final generado y enviarlo como respuesta
    finalPDFPath = os.path.join(basePath, outputPDFName)
    if not os.path.exists(finalPDFPath):
        raise HTTPException(status_code=500, detail="El PDF final no se generó correctamente.")

    with open(finalPDFPath, "rb") as pdfFile:
        pdfBytes = pdfFile.read()

    return StreamingResponse(io.BytesIO(pdfBytes),
                            media_type="application/pdf",
                            headers={"Content-Disposition": "attachment; filename=final.pdf"})

if __name__ == '__main__':
    app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)