import pandas as pd
import pymupdf
import os
import json
from jsonUtils import getMetadata
from buildCSV import buildCSVfromTitles
from folders import buildFolder

class CSVExporter:
    def __init__(self, company: str, week: str):
        self.company = company
        self.week = week
        self.basePath = buildFolder(company, week)
        self.jsonPath = os.path.join(self.basePath, 'config.json')
        self.outputDir = os.path.join(self.basePath, 'table')
        self.outputPNG = os.path.join(self.basePath, 'png')
        self.csvPath = os.path.abspath(os.path.join(self.basePath, '..', f'{company}.csv'))

    def export(self, pdfPath):
        print(f"Reading CSV from: {self.csvPath}")
        data = pd.read_csv(self.csvPath)
        
        data['Date'] = pd.to_datetime(data['Date'])
        
        with open(self.jsonPath, 'r', encoding='utf-8') as f:
            config = json.load(f)
        replaces = config.get("Replaces", {})
        
        metadata = getMetadata(self.company, data)
        
        excludes = buildCSVfromTitles(
            data,
            pdfPath,
            self.outputDir,
            self.company,
            replaces,
            metadata,
            self.week
        )
        self.excludes = excludes
        print("Exportación de CSV completada.")
    
    def exportPNG(self, pdfPath):
        print(f'Exportando páginas a PNG desde: {pdfPath}')
        doc = pymupdf.open(pdfPath)
    
        for numPage in range(len(doc)):
            page = doc.load_page(numPage)
            render = page.get_pixmap()
            render.save(os.path.join(self.outputPNG, f"{self.company}_Page_{numPage + 1}.png"))
            print(f'Página {numPage + 1} exportada a PNG.')
        print(f'Exportación de PNG completada. Ruta: {self.outputPNG}')
        
        doc.close()