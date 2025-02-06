import openai
import os
import pandas as pd
import tiktoken
import pymupdf
import json
import concurrent.futures
from base64 import b64encode
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")

client = openai.OpenAI()

def csvToText(csvPath):
    """Convertir un archivo CSV a texto plano
    """
    df = pd.read_csv(csvPath)
    return df.to_string(index=False)

def pngBase64(pngPath):
    with open(pngPath, "rb") as img:
        return b64encode(img.read()).decode("utf-8")

def GetFileId(filePath, purp = "assistants"):
    """Subir un archivo y obtener su file_id."""
    with open(filePath, "rb") as file:
        response = client.files.create(
            file=file,
            purpose=purp
        )
    return response.id

def countTokens(text, modelName="gpt-4o-mini"):
    """Contar los tokens de un texto según el modelo."""
    encoding = tiktoken.encoding_for_model(modelName)
    return len(encoding.encode(text))

def generateObservation(prompt):
    """Generar una observación a partir de un archivo CSV y una imagen PNG
    """
    try:
        thread = client.beta.threads.create()
        
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=prompt
        )
        run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID
        )

        print("Run completed with status: " + run.status)
        
        messages = None
        if run.status == "completed":
            promptTokens = countTokens(prompt)
            
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            
            outputTokens = 0

            print("messages: ")
            for message in messages:
                #assert message.content[0].type == "text"
                try:
                    print({"role": message.role, "message": message.content[0].text.value[:500].replace("Santiago", "Disponibles").replace("SANTIAGO", "DISPONIBLES")})
                    outputTokens += countTokens(message.content[0].text.value)
                except:
                    break
            print(f'Tokens input: {promptTokens} - Tokens output: {outputTokens}')
        else:
            print(f'Error en la generación de observación: {run.last_error}')
        return run, messages, message
    except Exception as e:
        print(f'Error en la generación de observación: {e}')
    
    return None, None, None

def generateObsAsync(args):
    """Generar observaciones de forma asíncrona
    """
    numPage = args['page']
    csvPath = args['csvPath']
    prompt = args['prompt']
    
    run, messages, message = generateObservation(prompt)
    if run is None:
        return (numPage, "Error: no se realizó la respuesta en el asistente")
    assistantResponse = None
    if run.status == "completed":
        for msg in reversed(messages.data):
            if msg.role == "assistant":
                assistantResponse = msg.content[0].text.value.replace("Santiago", "Disponibles").replace("SANTIAGO", "DISPONIBLES")
                break
    else:
        assistantResponse = "Error: no se completó la respuesta"

    return (numPage, assistantResponse)

def insertObsPDF(
    pdfPath: str,
    outputPDF: str,
    csvFolder: str,
    excludePages: list,
    company: str,
    context: dict,
    week: str,
    marginTop: float = 15,
    marginLeft: float = 60,
    textBoxHeight: float = 140
):
    print(f'Abriendo PDF: {pdfPath}')
    doc = pymupdf.open(pdfPath)
    totalPages = len(doc)

    # Crear lista de prompts
    tasks = []
    for p in range(totalPages):
        if p in excludePages:
            continue
        numPage = p + 1
        csvName = f"{company}_Page_{numPage}.csv"
        csvPath = os.path.join(csvFolder, csvName)
        if not os.path.exists(csvPath):
            continue

        csvText = csvToText(csvPath)

        prompt = f"""Genera una observación sobre este reporte semanal de riesgo RAEV/100 de la empresa {company.capitalize()} correspondiente a la semana iniciada el {week} utilizando la tabla CSV en texto plano. En caso de existir información sobre semanas anteriores, compara la semana iniciada el {week} con las anteriores, si no existe información sobre las anteriores, omite este paso.
        - Tabla:
        {csvText}

        - Contexto de la empresa:
        {json.dumps(context, indent=2, ensure_ascii=False)}
        """

        tasks.append({"page": p, "csvPath": csvPath, "prompt": prompt})

    # Lanzar en paralelo
    responses = {}  # dict: pageIndex -> assistantResponse
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futureToPage = {
            executor.submit(generateObsAsync, t): t["page"] for t in tasks
        }
        for future in concurrent.futures.as_completed(futureToPage):
            pageIndex = futureToPage[future]
            try:
                page_num, assistantResponse = future.result()
                responses[page_num] = assistantResponse
            except Exception as exc:
                responses[pageIndex] = f"Error: {exc}"
    
    print(f'Generación de observaciones listas.')
    print(f'Excluyendo páginas: {excludePages}')

    # Insertar en PDF en orden
    for p in range(totalPages):
        if p in excludePages:
            print(f'Omitiendo página {p + 1}')
            continue
        if p not in responses:
            print(f"No se encontró respuesta del asistente para la página {p + 1}. Saltando la inserción.")
            continue
        try:
            print(f'Intentando asignar respuesta para página {p + 1}\n Respuesta: {responses[p]}')
            assistantResponse = responses[p]
        except Exception as e:
            print(f"Error al intentar asignar la respuesta del asistente para la página {p + 1}: {e}")
            continue
        if not assistantResponse:
            print(f"No se encontró respuesta del asistente para la página {p + 1}. Saltando la inserción.")
            continue

        page = doc.load_page(p)
        width = page.rect.width
        height = page.rect.height

        pos = pymupdf.Rect(
            marginLeft,
            height - marginTop - textBoxHeight,
            width - marginLeft,
            height - marginTop,
        )
        
        fontName = "Montserrat-Regular"
        fontFile = f"fonts/{fontName}.ttf"
        page.insert_font(fontname=fontName, fontfile=fontFile)
        
        print(f"Escribiendo observación en página {p + 1}")
        try:
            page.insert_htmlbox(
                pos,
                '<b>Observación:</b> ' + assistantResponse,
                css=f"* {{font-family: {fontName}; font-size: 24px; color: #000000;}}",
            )
        except Exception as e:
            print(f"Error al insertar observación en página {p + 1}: {e}")
        print(f"Observación insertada en página {p + 1}")

    doc.save(outputPDF)
    doc.close()
    print(f"PDF guardado en: {outputPDF}")
    
    obsList = []
    for p in range(totalPages):
        obsObj = {
            "pageNumber": p + 1,
            "observation": responses.get(p, "No se encontró observación"),
            "excluded": p in excludePages
        }
        obsList.append(obsObj)
    print(f'Lista de observaciones creada:\n {obsList}')
    return obsList