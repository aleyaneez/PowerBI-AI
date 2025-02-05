import re

def getCompanyWeek(filename: str):
    pattern = re.compile(r'^(.*?)[-_](\d{4}-\d{2}-\d{2})\.pdf$', re.IGNORECASE)
    match = pattern.match(filename)
    if not match:
        raise ValueError(f"El nombre del archivo no coincide con el formato esperado: {filename}")
    company = match.group(1)
    week = match.group(2)
    return company, week