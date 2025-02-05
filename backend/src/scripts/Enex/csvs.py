import pandas as pd
import json
import os
from .filters import filterEv, filterRanking

def buildCSVfromJSON(data: pd.DataFrame, jsonPath: str, outputDir: str):
    """Leer el config JSON, y para cada cliente llamar a 
    la función de filter adecuada según los parámetros.
    """
    os.makedirs(outputDir, exist_ok=True)

    with open(jsonPath, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    nombreCliente = config["Cliente"]

    for grafico in config["Graficos"]:
        numPage = grafico.get("Pagina", 1)
        tipo = grafico["Tipo"]
        
        for filtrosDict in grafico["Filtros"]:
            if "ultimas" in filtrosDict:
                filtrosDict["ultimas"] = int(filtrosDict["ultimas"])
            if "top" in filtrosDict:
                filtrosDict["top"] = int(filtrosDict["top"])

            if tipo == "Evolucion":
                dfResult = filterEv(
                    data,
                    startDate=filtrosDict.get("startDate"),
                    endDate=filtrosDict.get("endDate"),
                    flotas=filtrosDict.get("Flotas")
                )
            elif tipo == "Ranking":
                dfResult = filterRanking(
                    data,
                    startDate=filtrosDict.get("startDate"),
                    endDate=filtrosDict.get("endDate"),
                    flotas=filtrosDict.get("Flotas"),
                    oficina=filtrosDict.get("Oficina"),
                    codigo=filtrosDict.get("Codigo"),
                    ultimas=filtrosDict.get("ultimas"),
                    top=filtrosDict.get("top"),
                    dev=filtrosDict.get("dev")
                )
            else:
                print(f"[Advertencia] Tipo de gráfico no reconocido: {tipo}")
                continue

            csvFile = f"{nombreCliente}_Page_{numPage}.csv"
            outputPath = os.path.join(outputDir, csvFile)
            
            dfResult.to_csv(outputPath, index=False, encoding="utf-8")
            
            print(f"Generado CSV: {outputPath}")