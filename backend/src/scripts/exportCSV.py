import pandas as pd
import os
from buildCSV import buildCSVfromJSON
from folders import buildFolder

class CSVExporter:
    def __init__(self, company: str, week: str):
        self.company = company
        self.week = week
        self.basePath = buildFolder(company, week)
        self.jsonPath = os.path.join(self.basePath, 'config.json')
        self.outputDir = os.path.join(self.basePath, 'table')
        self.csvPath = os.path.abspath(os.path.join(self.basePath, '..', f'{company}.csv'))

    def export(self):
        print(f"Reading CSV from: {self.csvPath}")
        data = pd.read_csv(self.csvPath)
        
        data['Date'] = pd.to_datetime(data['Date'])
        
        buildCSVfromJSON(data, self.jsonPath, self.outputDir)
        print("Exportación de CSV completada.")