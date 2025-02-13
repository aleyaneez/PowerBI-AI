import os
import shutil
import json
import time
from fastapi import APIRouter, Form, HTTPException
from exportCSV import CSVExporter
from reportGenerator import ReportGenerator
from folders import buildFolder
from jsonUtils import getExcludes, getRiesgo, getMetas, getMetadata

router = APIRouter()

@router.post("/finalize")
async def finalize_pdf(
    company: str = Form(...),
    week: str = Form(...),
    pdfName: str = Form(...)
):
    """
    Recibe el PDF subido, procesa el archivo, genera reportes y retorna el PDF final.
    """
    UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "uploads")
    startTime = time.time()
    tempPath = os.path.join(UPLOAD_DIR, f"{company}_{week}.pdf")
    if not os.path.exists(tempPath):
        raise HTTPException(status_code=404, detail="El PDF subido no se encontró en la carpeta temporal.")

    basePath = buildFolder(company, week)
    destPdfPath = os.path.join(basePath, f"{company}_{week}.pdf")
    shutil.copy2(tempPath, destPdfPath)
    print(f"PDF copiado a {destPdfPath}")
    
    configPath = os.path.join(basePath, "config.json")
    excludes = getExcludes(configPath)

    exporter = CSVExporter(company, week)
    try:
        exporter.export()
        exporter.exportPNG(destPdfPath)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exportando CSV: {e}")
    
    metadataPathParent = os.path.join(basePath, '..', 'metadata.json')
    if not os.path.exists(metadataPathParent):
        metadata = getMetadata(company)
        with open(metadataPathParent, 'w', encoding='utf-8') as file:
            json.dump(metadata, file, indent=4, ensure_ascii=False)
    metadataPath = metadataPathParent
    
    riesgo = getMetas(metadataPath) if company == 'enex' else getRiesgo(metadataPath)
    
    outputPDFName = f"{pdfName}_output.pdf"
    try:
        reportStart = time.time()
        reportGen = ReportGenerator(company, week, company, excludes, riesgo, outputPDFName)
        obsList = reportGen.generateReport()
        reportEnd = time.time()
        print(f"Reporte generado en {reportEnd - reportStart:.2f} segundos.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando el reporte: {e}")

    publicPDFPath = os.path.join(UPLOAD_DIR, outputPDFName)
    shutil.copy2(os.path.join(basePath, outputPDFName), publicPDFPath)
    finalPDFUrl = f"http://localhost:8000/uploads/{outputPDFName}"
    
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
    
    pngFiles = sorted(
        [f for f in os.listdir(pngDir) if f.lower().endswith('.png')],
        key=lambda filename: int(filename.split('_')[-1].split('.')[0]) if filename.split('_')[-1].split('.')[0].isdigit() else 0
    )
    
    pngUrls = []
    for file in pngFiles:
        relPath = os.path.relpath(os.path.join(pngDir, file), UPLOAD_DIR)
        url = f"http://localhost:8000/uploads/{relPath.replace(os.path.sep, '/')}"
        pngUrls.append(url)
    
    end_time = time.time()
    print(f"Reporte completo generado en {end_time - startTime:.2f} segundos.")
    
    return {
        "final_pdf_url": finalPDFUrl,
        "observations": obsList,
        "excludes": excludes,
        "png_urls": pngUrls
    }