import os
import json
import shutil
from fastapi import APIRouter, Form, HTTPException
from jsonUtils import getExcludes, getRiesgo, getMetas, getMetadata
from folders import buildFolder
from reportGenerator import ReportGenerator
from config import UPLOAD_DIR

router = APIRouter()

@router.post("/apply-observations")
async def apply_observations(
    company: str = Form(...),
    week: str = Form(...),
    pdfName: str = Form(...),
    obsJSON: str = Form(...)
):
    """
    Recibe observaciones en formato JSON, las inserta en el PDF y retorna la URL del PDF final.
    """
    try:
        obsList = json.loads(obsJSON)
    except Exception:
        raise HTTPException(status_code=400, detail="obsJSON no es un JSON válido")

    basePath = buildFolder(company, week)
    destPDFPath = os.path.join(basePath, f"{company}_{week}.pdf")
    if not os.path.exists(destPDFPath):
        raise HTTPException(status_code=404, detail="No se encontró el PDF base.")

    configPath = os.path.join(basePath, "config.json")
    excludes = getExcludes(configPath)

    metadataPath = os.path.join(basePath, '..', 'metadata.json')
    if not os.path.exists(metadataPath):
        metadata = getMetadata(company)
        with open(metadataPath, 'w', encoding='utf-8') as file:
            json.dump(metadata, file, indent=4, ensure_ascii=False)

    riesgo = getMetas(metadataPath) if company == 'enex' else getRiesgo(metadataPath)

    outputPDFName = f"{pdfName}_output.pdf"
    reportGen = ReportGenerator(company, week, company, excludes, riesgo, outputPDFName)
    reportGen.applyObservations(obsList)

    publicPDFPath = os.path.join(UPLOAD_DIR, outputPDFName)
    finalPDFPath = os.path.join(basePath, outputPDFName)
    if not os.path.exists(finalPDFPath):
        raise HTTPException(status_code=500, detail="No se generó el PDF final.")
    shutil.copy2(finalPDFPath, publicPDFPath)

    final_pdf_url = f"http://localhost:8000/uploads/{outputPDFName}"
    return {"final_pdf_url": final_pdf_url}