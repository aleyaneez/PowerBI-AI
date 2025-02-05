import os
import shutil
from folders import buildFolder
from jsonUtils import loadJSON
from runObservations import insertObsPDF
import globals

class ReportGenerator:
    def __init__(self, company: str, week: str, pdfName: str, excludePages: list, riesgo: dict, outputPDF: str):
        self.company = company
        self.week = week
        self.pdfName = pdfName
        self.excludePages = excludePages
        self.riesgo = riesgo
        
        globals.RIESGO.clear()
        globals.RIESGO.update(riesgo)
        
        self.basePath = buildFolder(company, week)
        self.outputPDF = os.path.join(self.basePath, outputPDF)
        
        self.metadataPath = os.path.join(self.basePath, '..', 'metadata.json')
        self.contextJSON = loadJSON(self.metadataPath)
        
        self.pdfPath = os.path.join(self.basePath, f'{pdfName}_{week}.pdf')
        self.csvFolder = os.path.join(self.basePath, 'table')
        
        self.movePDF()
    
    def movePDF(self):
        if not os.path.exists(self.pdfPath):
            currentDir = os.path.dirname(os.path.abspath(__file__))
            pdfSource = os.path.join(currentDir, "PDFs", f"{self.company}_{self.week}.pdf")
            
            if not os.path.exists(pdfSource):
                raise FileNotFoundError(f"El PDF no se encontró en la ruta de origen: {pdfSource}")
            
            shutil.copy2(pdfSource, self.pdfPath)
            print(f"PDF movido de {pdfSource} a {self.pdfPath}")
        else:
            print(f"El PDF ya se encuentra en la ruta destino: {self.pdfPath}")
    
    def generateReport(self):
        insertObsPDF(
            self.pdfPath,
            self.outputPDF,
            self.csvFolder,
            self.excludePages,
            self.company,
            self.contextJSON,
            self.week
        )
