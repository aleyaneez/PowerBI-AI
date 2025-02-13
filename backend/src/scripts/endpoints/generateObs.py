import os
import json
import shutil
import time
import pandas as pd
from fastapi import APIRouter, Form, HTTPException
from exportCSV import CSVExporter
from reportGenerator import ReportGenerator
from folders import buildFolder
from jsonUtils import getRiesgo, getMetas, getMetadata
from config import UPLOAD_DIR

router = APIRouter()

@router.post("/generate-observations")
async def generate_observations(
    company: str = Form(...),
    week: str = Form(...),
    pdfName: str = Form(...)
):
    """
    Prepara CSVs, PNGs y genera observaciones (sin insertarlas en el PDF).
    """
    startTime = time.time()

    tempPDF = os.path.join(UPLOAD_DIR, f"{company}_{week}.pdf")
    if not os.path.exists(tempPDF):
        raise HTTPException(status_code=404, detail="El PDF subido no se encontró en la carpeta temporal.")

    # Crear carpeta destino y copiar PDF
    basePath = buildFolder(company, week)
    destPDFPath = os.path.join(basePath, f"{company}_{week}.pdf")
    shutil.copy2(tempPDF, destPDFPath)
    print(f"PDF copiado a {destPDFPath}")

    print("Exportando CSV y PNG...")
    # Generar CSV y PNG
    exporter = CSVExporter(company, week)
    try:
        exporter.export(destPDFPath)
        exporter.exportPNG(destPDFPath)
    except Exception as e:
        print(f"Error al exportar CSV: {e}")
        raise HTTPException(status_code=500, detail=f"Error al exportar CSV: {e}")
    print("CSV y PNG generados.")

    excludes = exporter.excludes

    metadataPathParent = os.path.join(basePath, '..', 'metadata.json')
    if not os.path.exists(metadataPathParent):
        data_csv = pd.read_csv(exporter.csvPath)
        metadata = getMetadata(company, data_csv)
        with open(metadataPathParent, 'w', encoding='utf-8') as file:
            json.dump(metadata, file, indent=4, ensure_ascii=False)
    metadataPath = metadataPathParent

    riesgo = getMetas(metadataPath) if company == 'enex' else getRiesgo(metadataPath)

    outputPDFName = f"{pdfName}_output.pdf"
    reportGen = ReportGenerator(company, week, company, excludes, riesgo, outputPDFName)
    obsList = reportGen.generateObservations()

    pngDir = os.path.join(UPLOAD_DIR, "png", company, week)
    os.makedirs(pngDir, exist_ok=True)
    if os.path.exists(exporter.outputPNG):
        for file in os.listdir(exporter.outputPNG):
            if file.lower().endswith('.png'):
                src = os.path.join(exporter.outputPNG, file)
                dst = os.path.join(pngDir, file)
                shutil.copy2(src, dst)
    else:
        raise HTTPException(status_code=500, detail="No se encontraron imágenes PNG generadas.")

    pngFiles = [f for f in os.listdir(pngDir) if f.lower().endswith('.png')]
    def extract_page(filename):
        try:
            parts = filename.split('_')
            num_str = parts[-1].split('.')[0]
            return int(num_str)
        except Exception:
            return 0

    pngFiles_sorted = sorted(pngFiles, key=extract_page)
    pngUrls = []
    for file in pngFiles_sorted:
        relPath = os.path.relpath(os.path.join(pngDir, file), UPLOAD_DIR)
        url = f"http://localhost:8000/uploads/{relPath.replace(os.path.sep, '/')}"
        pngUrls.append(url)
    
    end_time = time.time()
    print(f"Observaciones generadas en {end_time - startTime:.2f} segundos.")
    return {
        "observations": obsList,
        "excludes": excludes,
        "png_urls": pngUrls
    }