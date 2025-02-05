import pandas as pd
import numpy as np
import json
from globals import RIESGO, capitalizePalabras

def abastibleJSON(df: pd.DataFrame, company: str) -> dict:
    """Buildear un JSON con la información de la data extraída
    """
    company = capitalizePalabras(company)
    flotas = sorted(df['Flota'].apply(capitalizePalabras).dropna().unique().tolist())
    oficinas = sorted(df['Oficina'].apply(capitalizePalabras).dropna().unique().tolist())
    codigos = sorted(df['Codigo'].dropna().unique().tolist())

    configDict = {
        "Cliente": company,
        "Informacion": {
            "Niveles de Riesgo RAEV/100": RIESGO,
            "Flotas": flotas,
            "Oficinas": oficinas,
            "Codigos": codigos,
        },
    }

    return configDict

def loadJSON(path):
    """Cargar el JSON con la metadata de las empresas
    devolviendo un diccionario de Python.
    """
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data