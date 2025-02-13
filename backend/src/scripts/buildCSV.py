from getFilters import getFilters, getTitleParser
import json
import os
import pandas as pd
import pymupdf

def applyReplaces(data: pd.DataFrame, replaces: dict):
    for col, mapping in replaces.items():
        if col in data.columns:
            for old, new in mapping.items():
                data[col] = data[col].astype(str).str.replace(old, new)
    return data

def functionTitle(title: str) -> str:
    titleLower = title.lower()
    if "ranking" in titleLower:
        return "ranking"
    if "variacion" in titleLower or "variación" in titleLower:
        return "ranking"
    if "evolucion" in titleLower or "evolución" in titleLower:
        return "evolucion"
    return None

def extractTitles(pdfPath: str, titleArea: list = [200, 0, 1900, 68]):
    titlesDict = {}
    excludes = []
    doc = pymupdf.open(pdfPath)
    for numPage in range(len(doc)):
        page = doc.load_page(numPage)
        rectTitle = pymupdf.Rect(titleArea)
        title = page.get_text(clip=rectTitle)
        
        tipo = functionTitle(title)
        if tipo:
            titlesDict[numPage] = title
        else:
            excludes.append(numPage)
    doc.close()
    
    return titlesDict, excludes

def buildCSVfromTitles(data: pd.DataFrame, pdfPath: str, outputDir: str, clientName: str, replaces: dict, metadata: dict, week: str, titleArea: list = [200, 0, 1900, 68]):
    """
    Genera los CSVs a partir de los títulos del PDF en lugar de un config.json.
    Se adapta a distintos clientes sin necesidad de cambiar la implementación.
    """
    os.makedirs(outputDir, exist_ok=True)
    
    titlesDict, excludes = extractTitles(pdfPath, titleArea=titleArea)
    # Imprimir titulos encontrados de una forma fácil de leer
    for pageIndex, title in titlesDict.items():
        print(f"Página {pageIndex+1}:\n{title}")
    print("Páginas excluidas:", excludes)

    if replaces:
        data = applyReplaces(data, replaces)

    parseTitle = getTitleParser(clientName)

    for pageIndex, title in titlesDict.items():
        if pageIndex in excludes:
            continue
        
        print(f'\nParseTitle página {pageIndex+1}')
        parsedParams = parseTitle(title, metadata, week)
        tipo = parsedParams.get("Tipo")
        
        if not tipo:
            print(f"Página {pageIndex+1}: No se pudo determinar el tipo del gráfico, saltando.")
            continue
        
        filterFunc = getFilters(clientName, tipo)
        
        tipo_lower = tipo.lower()
        if tipo_lower == "evolucion":
            allowed_keys = ["flotas"]
        else:
            allowed_keys = ["flotas", "oficina", "codigo", "ultimas", "top", "dev"]
        
        extraArgs = {k.lower(): v for k, v in parsedParams.items() if k.lower() in allowed_keys}
        
        dfResult = filterFunc(
            data,
            startDate=parsedParams.get("startDate"),
            endDate=parsedParams.get("endDate"),
            **extraArgs
        )

        csvName = f"{clientName}_Page_{pageIndex + 1}.csv"
        csvPath = os.path.join(outputDir, csvName)
        dfResult.to_csv(csvPath, index=False, encoding="utf-8")
        print(f"Generado CSV: {csvPath}")
    
    return excludes