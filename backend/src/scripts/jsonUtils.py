import json
import os

def loadJSON(path: str) -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(f"El archivo JSON no se encontró en la ruta: {path}")
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def getExcludes(path: str) -> list:
    config = loadJSON(path)
    return config.get("Excludes", [])

def getRiesgo(path: str) -> dict:
    config = loadJSON(path)
    return config.get("Informacion", {}).get("Niveles de Riesgo", {})