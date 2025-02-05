from Abastible.filters import filterEv as abastibleEv, filterRanking as abastibleRanking
from Albemarle.filters import albemarleEv, albemarleRanking

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