from Abastible.filters import filterEv as abastibleEv, filterRanking as abastibleRanking
from Abastible.json import parseTitle as abastibleParseTitle
from Albemarle.filters import albemarleEv, albemarleRanking

def getTitleParser(cliente):
    if cliente.lower() == "abastible_consolidado":
        return abastibleParseTitle
    raise ValueError(f"No se encontró un parser de titulos para el cliente {cliente}.")

def getFilters(cliente, tipo):
    if cliente.lower() == "abastible_consolidado":
        if tipo.lower() == "evolucion":
            return abastibleEv
        elif tipo.lower() == "ranking":
            return abastibleRanking
    elif cliente.lower() == "albemarle":
        if tipo.lower() == "evolucion":
            return albemarleEv
        elif tipo.lower() == "ranking":
            return albemarleRanking
    raise ValueError(f"No se encontró filtrado para cliente {cliente} o el tipo {tipo} de gráfico.")