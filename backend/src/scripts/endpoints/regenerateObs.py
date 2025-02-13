import os
import json
from fastapi import APIRouter, Form, HTTPException
from runObservations import generateObservation, csvToText
from folders import buildFolder

router = APIRouter()

@router.post("/regenerate-observation")
async def regenerate_observation(
    company: str = Form(...),
    week: str = Form(...),
    pdfName: str = Form(...),
    pageNumber: int = Form(...),
):
    """
    Regenera la observación de la página especificada para la empresa y semana indicadas.
    """
    basePath = buildFolder(company, week)
    destPDFPath = os.path.join(basePath, f"{company}_{week}.pdf")
    if not os.path.exists(destPDFPath):
        raise HTTPException(status_code=404, detail="No se encontró el PDF en la carpeta destino.")

    csvFolder = os.path.join(basePath, 'table')
    csvFile = os.path.join(csvFolder, f"{company}_Page_{pageNumber}.csv")
    if not os.path.exists(csvFile):
        raise HTTPException(status_code=404, detail=f"No existe CSV para la página {pageNumber}.")

    metadataPath = os.path.join(basePath, '..', 'metadata.json')
    if not os.path.exists(metadataPath):
        raise HTTPException(status_code=500, detail="No se encontró el archivo de metadata.")

    with open(metadataPath, 'r', encoding='utf-8') as f:
        contextJSON = json.load(f)

    csvText = csvToText(csvFile)
    prompt = f"""Genera una observación sobre este reporte semanal de riesgo RAEV/100 de la empresa {company.capitalize()} correspondiente a la semana iniciada el {week} utilizando la tabla CSV en texto plano. En caso de existir información sobre semanas anteriores, compara la semana iniciada el {week} con las anteriores. Si no existe información, omite ese paso.
    - Tabla:
    {csvText}

    - Contexto de la empresa:
    {json.dumps(contextJSON, indent=2, ensure_ascii=False)}
    """

    print("Regenerando observación...")
    run, messages, msg_inicial = generateObservation(prompt)
    if run is None or run.status != "completed":
        raise HTTPException(status_code=500, detail="No se logró completar la respuesta de IA.")

    newObservation = "Error: no se completó la respuesta"
    for msg in reversed(messages.data):
        if msg.role == "assistant":
            newObservation = msg.content[0].text.value.replace("Santiago", "Disponibles")
            break
    print("Observación generada:", newObservation)

    return {
        "pageNumber": pageNumber,
        "newObservation": newObservation
    }