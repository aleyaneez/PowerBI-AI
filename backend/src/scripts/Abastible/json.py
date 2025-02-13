import pandas as pd
import re
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

def parseTitle(title: str, metadata: dict, week: str) -> dict:
    titleLower = title.lower()
    result = {
        "Tipo": None,
        "Flotas": None,
        "Oficina": None,
        "Codigo": None,
        "startDate": None,
        "endDate": None,
        "ultimas": None,
        "top": None,
        "dev": None
    }
    
    if "evolución semanal" in titleLower:
        result["Tipo"] = "Evolucion"
    elif "ranking" in titleLower or "variacion" in titleLower or "variación" in titleLower or "evolución" in titleLower:
        result["Tipo"] = "Ranking"
    
    matchFlota = re.search(r"flota\s+([^\s,]+)", title, re.IGNORECASE)
    if matchFlota:
        flotaName = matchFlota.group(1).strip()
        for f in metadata["Informacion"]["Flotas"]:
            if f.lower() == flotaName.lower():
                result["Flotas"] = [f.upper()]
                break
        print(f"Match flota: {result['Flotas']}")
    
    if "total flotas" in titleLower:
        result["Flotas"] = [flota.upper() for flota in metadata["Informacion"]["Flotas"]]
        print(f"Match total flotas: {result['Flotas']}")
    
    matchOficina = re.search(r"oficina\s+([^\s,]+)", title, re.IGNORECASE)
    if matchOficina:
        oficinaName = matchOficina.group(1).strip()
        for o in metadata["Informacion"]["Oficinas"]:
            if o.lower() == oficinaName.lower():
                result["Oficina"] = o.upper()
                break
        print(f"Match oficina: {result['Oficina']}")
    
    matchCodigo = re.search(r"c[oó]digo\s+(\S+)", title, re.IGNORECASE)
    if matchCodigo:
        codigo = matchCodigo.group(1).strip()
        for c in metadata["Informacion"]["Codigos"]:
            if c.lower() == codigo.lower():
                result["Codigo"] = c
                break
        if not result["Codigo"]:
            print(f"El código {codigo} no se encontró en la metadata.")
        print(f"Match código: {result['Codigo']}")
    
    if matchCodigo:
        result["ultimas"] = 4

    if "variacion" in titleLower or "variación" in titleLower:
        result["ultimas"] = 2

    if "mas riesgosos" in titleLower or "más riesgosos" in titleLower:
        result["top"] = 60
        result["dev"] = 50
    
    week = pd.to_datetime(week)
    if result["Tipo"] == "Evolucion":
        result["endDate"] = week
        result["startDate"] = week - pd.DateOffset(years=1)
    if result["Tipo"] == "Ranking" and result["ultimas"] in [2, 4]:
        result["endDate"] = week + pd.DateOffset(days=6)
        result["startDate"] = None
    elif result["Tipo"] == "Ranking" and result["ultimas"] is None and result["top"] is not None and result["dev"] is not None:
        result["endDate"] = week + pd.DateOffset(days=6)
        result["startDate"] = week - pd.DateOffset(weeks=4)
    else:
        result["endDate"] = week + pd.DateOffset(days=6)
        result["startDate"] = week
    
    print(f"""
Título: {title}
Parámetros extraídos:
    Tipo: {result["Tipo"]}
    startDate: {result["startDate"]}
    endDate: {result["endDate"]}
    Flotas: {result["Flotas"]}
    Oficina: {result["Oficina"]}
    Codigo: {result["Codigo"]}
    ultimas: {result["ultimas"]}
    top: {result["top"]}
    dev: {result["dev"]}
    """)
    
    return result