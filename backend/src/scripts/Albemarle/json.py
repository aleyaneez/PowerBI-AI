import pandas as pd
from globals import RIESGO, capitalizePalabras

def albemarleJSON(df: pd.DataFrame, company: str) -> dict:
    """Buildear un JSON con la información de la data extraída
    """
    company = capitalizePalabras(company)
    transportista = sorted(df['Transportista'].apply(capitalizePalabras).dropna().unique().tolist())
    patente = sorted(df['Patente'].dropna().unique().tolist())

    configDict = {
        "Cliente": company,
        "Informacion": {
            "Niveles de Riesgo RAEV/100": RIESGO,
            "Transportista": transportista,
            "Patente": patente,
        },
    }

    return configDict