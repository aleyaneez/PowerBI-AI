from getFilters import getFilters
import json
import os
import pandas as pd

def applyReplaces(data: pd.DataFrame, replaces: dict):
    for col, mapping in replaces.items():
        if col in data.columns:
            for old, new in mapping.items():
                data[col] = data[col].astype(str).str.replace(old, new)
    return data

def buildCSVfromJSON(data: pd.DataFrame, jsonPath: str, outputDir: str):
    os.makedirs(outputDir, exist_ok=True)
    with open(jsonPath, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    nombreCliente = config["Cliente"]
    
    replaces = config.get("Replaces", {})
    
    data = applyReplaces(data, replaces)

    for grafico in config["Graficos"]:
        numPage = grafico.get("Pagina", 1)
        tipo = grafico["Tipo"]
        
        filter = getFilters(nombreCliente, tipo)
        
        for filtrosDict in grafico["Filtros"]:
            if "ultimas" in filtrosDict:
                filtrosDict["ultimas"] = int(filtrosDict["ultimas"])
            if "top" in filtrosDict:
                filtrosDict["top"] = int(filtrosDict["top"])
            
            extraArgs = {k.lower(): filtrosDict[k] for k in filtrosDict if k.lower() not in ["startdate", "enddate"]}
            
            dfResult = filter(
                data, 
                startDate=filtrosDict.get("startDate"),
                endDate=filtrosDict.get("endDate"),
                **extraArgs
            )
            
            csvFile = f"{nombreCliente}_Page_{numPage}.csv"
            outputPath = os.path.join(outputDir, csvFile)
            dfResult.to_csv(outputPath, index=False, encoding="utf-8")
            print(f"Generado CSV: {outputPath}")