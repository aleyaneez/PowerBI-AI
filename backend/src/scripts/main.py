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
from jsonUtils import getExcludes, getRiesgo, getMetas, getMetadata

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directorio para guardar los archivos subidos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Recibe el PDF y lo guarda en UPLOAD_DIR.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF.")
    
    filePath = os.path.join(UPLOAD_DIR, file.filename)
    print(f'Base dir: {BASE_DIR}')
    print(f'Upload dir: {UPLOAD_DIR}')
    with open(filePath, "wb") as f:
        f.write(await file.read())
    
    return {"filename": file.filename, "filePath": filePath}

@app.post("/finalize")
async def finalize_pdf(
    company: str = Form(...),
    week: str = Form(...),
    pdfName: str = Form(...)
):
    """
    Recibe el PDF subido, extrae company y week, copia el PDF a la carpeta destino,
    ejecuta CSVExporter.export() y ReportGenerator.generateReport(), y devuelve el PDF final.
    """
    temp_path = os.path.join(UPLOAD_DIR, f"{company}_{week}.pdf")
    if not os.path.exists(temp_path):
        raise HTTPException(status_code=404, detail="El PDF subido no se encontró en la carpeta temporal.")

    # Crea la carpeta destino usando buildFolder y copia el PDF allí
    base_path = buildFolder(company, week)
    dest_pdf_path = os.path.join(base_path, f"{company}_{week}.pdf")
    shutil.copy2(temp_path, dest_pdf_path)
    print(f"PDF copiado a {dest_pdf_path}")

    # Llama a CSVExporter para generar los CSV necesarios a partir del PDF y config.json
    exporter = CSVExporter(company, week)
    try:
        exporter.export()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exportando CSV: {e}")

    # Extrae la lista de páginas a excluir y los niveles de riesgo desde el config
    config_path = os.path.join(base_path, "config.json")
    excludes = getExcludes(config_path)
    
    metadataPathParent = os.path.join(base_path, '..', 'metadata.json')
    if not os.path.exists(metadataPathParent):
        metadata = getMetadata(company)
        with open(metadataPathParent, 'w', encoding='utf-8') as file:
            json.dump(metadata, file, indent=4, ensure_ascii=False)
    metadataPath = metadataPathParent
    
    if company == 'enex':
        riesgo = getMetas(metadataPath)
    else:
        riesgo = getRiesgo(metadataPath)

    print(f'Config path: {config_path}')
    print(f'Metadata path: {metadataPath}')
    
    # Instancia ReportGenerator y genera el PDF final con observaciones insertadas
    output_pdf_name = f"{pdfName}_output.pdf"
    try:
        reportGen = ReportGenerator(company, week, company, excludes, riesgo, output_pdf_name)
        obsList = reportGen.generateReport()
    except Exception as e:
        print(f"Error generando el reporte: {e}")
        raise HTTPException(status_code=500, detail=f"Error generando el reporte: {e}")

    # Copiar el PDF final a UPLOAD_DIR para exponerlo vía URL
    public_pdf_path = os.path.join(UPLOAD_DIR, output_pdf_name)
    shutil.copy2(os.path.join(base_path, output_pdf_name), public_pdf_path)
    final_pdf_url = f"http://localhost:8000/uploads/{output_pdf_name}"
    
    # Retornar JSON con la URL del PDF final, el listado de observaciones y el array de exclusiones
    return {
        "final_pdf_url": final_pdf_url,
        "observations": obsList,
        "excludes": excludes
    }

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)