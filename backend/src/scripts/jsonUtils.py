import json
import os
from Abastible.json import abastibleJSON
from Albemarle.json import albemarleJSON
from Enex.json import enexJSON

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

def getMetas(path: str) -> dict:
    config = loadJSON(path)
    return config.get("Informacion", {}).get("Metas RAEV/100", {})

def getMetadata(cliente, data):
    if cliente.lower() == "abastible_consolidado":
        return abastibleJSON(data, cliente)
    elif cliente.lower() == "albemarle":
        return albemarleJSON(data, cliente)
    elif cliente.lower() == "enex":
        return enexJSON(data, cliente)
    raise ValueError(f"No se encontró metadata para cliente {cliente}.")