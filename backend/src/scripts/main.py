import uvicorn

import os
import shutil
import json
import time

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from exportCSV import CSVExporter
from reportGenerator import ReportGenerator
from runObservations import generateObservation, csvToText
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
    # Cronometrar el tiempo de subida del archivo
    startTime = time.time()
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF.")
    
    filePath = os.path.join(UPLOAD_DIR, file.filename)
    print(f'Base dir: {BASE_DIR}')
    print(f'Upload dir: {UPLOAD_DIR}')
    with open(filePath, "wb") as f:
        f.write(await file.read())
    
    endTime = time.time()
    print(f"Archivo subido en {endTime - startTime:.2f} segundos.")
    
    return {"filename": file.filename, "filePath": filePath}

@app.post("/generate-observations")
async def generate_observations(
    company: str = Form(...),
    week: str = Form(...),
    pdfName: str = Form(...)
):
    """
    Prepara CSVs, imágenes PNG, y genera observaciones (texto) pero NO inserta en el PDF.
    Retorna las observaciones y la lista de PNGs, para que el usuario las edite/avale.
    """
    startTime = time.time()

    # 1) Verificar que el PDF temporal exista
    temp_pdf = os.path.join(UPLOAD_DIR, f"{company}_{week}.pdf")
    if not os.path.exists(temp_pdf):
        raise HTTPException(status_code=404, detail="El PDF subido no se encontró en la carpeta temporal.")

    # 2) Crear carpeta destino y copiar PDF
    base_path = buildFolder(company, week)
    dest_pdf_path = os.path.join(base_path, f"{company}_{week}.pdf")
    shutil.copy2(temp_pdf, dest_pdf_path)
    print(f"PDF copiado a {dest_pdf_path}")

    # 3) Leer config.json y extraer excludes
    config_path = os.path.join(base_path, "config.json")
    excludes = getExcludes(config_path)

    # 4) Generar CSV y PNG
    exporter = CSVExporter(company, week)
    try:
        exporter.export()
        exporter.exportPNG(dest_pdf_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al exportar CSV: {e}")

    # 5) Asegurarse de tener un metadata.json
    metadataPathParent = os.path.join(base_path, '..', 'metadata.json')
    if not os.path.exists(metadataPathParent):
        metadata = getMetadata(company)
        with open(metadataPathParent, 'w', encoding='utf-8') as file:
            json.dump(metadata, file, indent=4, ensure_ascii=False)
    metadataPath = metadataPathParent

    # 6) Obtener riesgo
    if company == 'enex':
        riesgo = getMetas(metadataPath)
    else:
        riesgo = getRiesgo(metadataPath)

    # 7) Instanciar ReportGenerator, pero solo usaremos generateObservations()
    output_pdf_name = f"{pdfName}_output.pdf"  # Se usará más tarde
    reportGen = ReportGenerator(company, week, company, excludes, riesgo, output_pdf_name)

    # Generar solo la lista de observaciones (sin insertar en PDF)
    obsList = reportGen.generateObservations()

    # 8) Copiar PNGs a la carpeta uploads para exponerlas vía URL
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

    # Construir las URLs de las PNG
    pngFiles = [f for f in os.listdir(pngDir) if f.lower().endswith('.png')]
    def extractPage(filename):
        try:
            parts = filename.split('_')
            numStr = parts[-1].split('.')[0]
            return int(numStr)
        except Exception:
            return 0

    pngFilesSorted = sorted(pngFiles, key=extractPage)
    pngUrls = []
    for file in pngFilesSorted:
        relPath = os.path.relpath(os.path.join(pngDir, file), UPLOAD_DIR)
        url = f"http://localhost:8000/uploads/{relPath.replace(os.path.sep, '/')}"
        pngUrls.append(url)

    endTime = time.time()
    print(f"Observaciones generadas en {endTime - startTime:.2f} segundos.")

    # 9) Retornar la lista de observaciones, excludes y pngUrls (aún NO hay PDF final)
    return {
        "observations": obsList,
        "excludes": excludes,
        "png_urls": pngUrls
    }

@app.post("/regenerate-observation")
async def regenerate_observation(
    company: str = Form(...),
    week: str = Form(...),
    pdfName: str = Form(...),
    pageNumber: int = Form(...),
):
    """
    Regenera la observación de la página `pageNumber` (1-based) para la empresa `company`
    en la semana `week`. Retorna la nueva observación.
    """
    # 1) Verificar ruta PDF y CSV
    base_path = buildFolder(company, week)
    dest_pdf_path = os.path.join(base_path, f"{company}_{week}.pdf")
    if not os.path.exists(dest_pdf_path):
        raise HTTPException(status_code=404, detail="No se encontró el PDF en la carpeta destino.")

    csv_folder = os.path.join(base_path, 'table')
    csv_file = os.path.join(csv_folder, f"{company}_Page_{pageNumber}.csv")
    if not os.path.exists(csv_file):
        raise HTTPException(status_code=404, detail=f"No existe CSV para la página {pageNumber}.")

    metadata_path = os.path.join(base_path, '..', 'metadata.json')
    if not os.path.exists(metadata_path):
        raise HTTPException(status_code=500, detail="No se encontró el archivo de metadata.")

    with open(metadata_path, 'r', encoding='utf-8') as f:
        contextJSON = json.load(f)

    csv_text = csvToText(csv_file)
    prompt = f"""Genera una observación sobre este reporte semanal de riesgo RAEV/100 
    de la empresa {company.capitalize()} correspondiente a la semana iniciada el {week} 
    utilizando la tabla CSV en texto plano. En caso de existir información sobre semanas anteriores, 
    compara la semana iniciada el {week} con las anteriores. 
    Si no existe información, omite ese paso.

    - Tabla:
    {csv_text}

    - Contexto de la empresa:
    {json.dumps(contextJSON, indent=2, ensure_ascii=False)}
    """

    run, messages, msg_inicial = generateObservation(prompt)
    if run is None or run.status != "completed":
        raise HTTPException(status_code=500, detail="No se logró completar la respuesta de IA.")
    
    new_observation = "Error: no se completó la respuesta"
    for msg in reversed(messages.data):
        if msg.role == "assistant":
            new_observation = msg.content[0].text.value.replace("Santiago","Disponibles")
            break

    # Retornar la nueva observación
    return {
        "pageNumber": pageNumber,
        "newObservation": new_observation
    }

@app.post("/apply-observations")
async def apply_observations(
    company: str = Form(...),
    week: str = Form(...),
    pdfName: str = Form(...),
    obsJSON: str = Form(...)
):
    """
    Recibe una lista de observaciones (con pageNumber, observation, excluded) en formato JSON (obsJSON)
    y las inserta en el PDF, retornando la URL final del PDF para descargar.
    """
    try:
        obsList = json.loads(obsJSON)  # convertir el string JSON a lista
    except Exception:
        raise HTTPException(status_code=400, detail="obsJSON no es un JSON válido")

    # Localizar la carpeta / PDF
    base_path = buildFolder(company, week)
    dest_pdf_path = os.path.join(base_path, f"{company}_{week}.pdf")
    if not os.path.exists(dest_pdf_path):
        raise HTTPException(status_code=404, detail="No se encontró el PDF base.")

    # Cargar la configuración (puede que la necesites, o no)
    config_path = os.path.join(base_path, "config.json")
    excludes = getExcludes(config_path)

    # Cargar metadata / riesgo
    metadataPath = os.path.join(base_path, '..', 'metadata.json')
    if not os.path.exists(metadataPath):
        metadata = getMetadata(company)
        with open(metadataPath, 'w', encoding='utf-8') as file:
            json.dump(metadata, file, indent=4, ensure_ascii=False)

    if company == 'enex':
        riesgo = getMetas(metadataPath)
    else:
        riesgo = getRiesgo(metadataPath)

    # Instanciamos el ReportGenerator
    output_pdf_name = f"{pdfName}_output.pdf"
    reportGen = ReportGenerator(company, week, company, excludes, riesgo, output_pdf_name)
    # En este caso, ya no generamos observaciones nuevas. Solo aplicamos las que mandó el frontend.
    reportGen.applyObservations(obsList)

    # Copiamos el PDF final a UPLOAD_DIR
    public_pdf_path = os.path.join(UPLOAD_DIR, output_pdf_name)
    finalPDFPath = os.path.join(base_path, output_pdf_name)
    if not os.path.exists(finalPDFPath):
        raise HTTPException(status_code=500, detail="No se generó el PDF final.")
    shutil.copy2(finalPDFPath, public_pdf_path)

    final_pdf_url = f"http://localhost:8000/uploads/{output_pdf_name}"
    return {"final_pdf_url": final_pdf_url}

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)