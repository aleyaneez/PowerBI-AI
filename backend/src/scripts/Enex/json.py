import pandas as pd
from globals import META, capitalizePalabras

def enexJSON(df: pd.DataFrame, company: str) -> dict:
    """Buildear un JSON con la información de la data extraída
    """
    company = capitalizePalabras(company)
    mercado = sorted(df['Mercado'].apply(capitalizePalabras).dropna().unique().tolist())
    planta = sorted(df['Planta'].apply(capitalizePalabras).dropna().unique().tolist())
    especialista = sorted(df['Especialista'].dropna().unique().tolist())
    transportista = sorted(df['Transportista'].apply(capitalizePalabras).dropna().unique().tolist())
    patente = sorted(df['Patente'].dropna().unique().tolist())

    configDict = {
        "Cliente": company,
        "Informacion": {
            "Metas RAEV/100": META,
            "Mercados": mercado,
            "Plantas": planta,
            "Especialistas": especialista,
            "Transportistas": transportista,
            "Patentes": patente
        },
    }

    return configDict