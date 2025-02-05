import pandas as pd
import os
from .csvs import buildCSVfromJSON

def main():
    company = 'abastible_consolidado'
    week = '2025-01-20'
    
    currentDir = os.path.dirname(os.path.realpath(__file__))
    basePath = os.path.abspath(os.path.join(currentDir, '../../Clientes', company, week))
    
    jsonPath = os.path.join(basePath, 'config.json')
    outputDir = os.path.join(basePath, 'table')
    
    csvPath = os.path.join(basePath, '..' , f'{company}.csv')
    print(f"Reading {csvPath}")
    
    data = pd.read_csv(csvPath)
    
    data['Date'] = pd.to_datetime(data['Date'])
    data['Oficina'] = data['Oficina'].str.replace('DISPONIBLES', 'SANTIAGO').replace('Disponibles', 'Santiago')
    
    buildCSVfromJSON(data, jsonPath, outputDir)

if __name__ == '__main__':
    main()