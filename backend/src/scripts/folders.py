import os

def buildFolder(company, week, basePath=None):    
    """Crear carpeta para guardar los archivos
    de cada Cliente y semana.
    """
    if basePath is None:
        scriptDir = os.path.dirname(os.path.abspath(__file__))
        projectRoot = os.path.dirname(scriptDir)
        basePath = os.path.join(projectRoot, 'Clientes')
    
    path = os.path.join(basePath, company, week)
    subfolders = ['table', 'png']
    
    for subfolder in subfolders:
        os.makedirs(os.path.join(path, subfolder), exist_ok=True)
    
    return path