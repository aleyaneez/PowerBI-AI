import pandas as pd
import numpy as np
import locale
from datetime import datetime, timedelta
from globals import RIESGO, capitalizePalabras, applyGroupEv, applyGroup, joinCols, getRAEV100Level, pivotIndex

locale.setlocale(locale.LC_TIME, 'es_CL.UTF-8')

def getRAEV100(df):
    df['raev100'] = ((df['raevSum'] / df['distanceSum']) * 100).round(1)
    return df

def getRAEV100Level(df: pd.DataFrame, bajo: float, medio: float, alto: float) -> pd.DataFrame:
    """Obtener el nivel de RAEV 100 de acuerdo a los umbrales
    establecidos.
    """
    df['Riesgo'] = df['raev100'].apply(
        lambda x: 'N/A' if pd.isna(x) 
        else 'bajo' if x <= bajo 
        else 'medio' if x <= medio 
        else 'alto' if x <= alto 
        else 'muy alto'
        )
    return df

def albemarleEv(df, startDate, endDate, transportista=None):
    """
    1) Sin transportista => columnas [Date, raev100].
    2) Lista de transportista con >1 => [Date, transportista1, transportista2, ...].
    3) Lista de transportista con 1 => [Date, raev100] (solo ese transportista).
    Filtra también distance en (0,10000).
    """
    endDate = pd.to_datetime(endDate)
    endDate = endDate + pd.Timedelta(days=6)
    
    # Filtrado inicial
    df = df[(df['distance'] > 0) & (df['distance'] < 10000)]
    df = df[(df['Date'] >= startDate) & (df['Date'] <= endDate)]

    # Si hay transportista, filtrar
    if transportista:
        df = df[df['Transportista'].isin(transportista)]

    # Caso A: Varios transportistas => pivot
    if transportista and len(transportista) > 1:
        grouped = applyGroupEv(df, ['Transportista'])
        grouped = getRAEV100Level(grouped, RIESGO['bajo'], RIESGO['medio'], RIESGO['alto'])

        pivoted = grouped.pivot_table(
            index='Date', 
            columns='Transportista', 
            values=['raev100', 'Riesgo'],
            aggfunc='first'
        ).reset_index()

        newCols = []
        for colTuple in pivoted.columns:
            if colTuple[0] == 'Date':
                newCols.append('Date')
            else:
                metric, t = colTuple
                if metric == 'raev100':
                    newCols.append(f'{t.capitalize()}-Raev100')
                else:
                    newCols.append(f'{t.capitalize()}-Riesgo')
        pivoted.columns = newCols
        
        finalCols = ['Date']
        for t in transportista:
            finalCols.append(f'{t.capitalize()}-Raev100')
            finalCols.append(f'{t.capitalize()}-Riesgo')

        return pivoted[finalCols].sort_values('Date')
    else:
        # Caso B: Cero transportistas o 1 transportista
        grouped = applyGroupEv(df, [])
        grouped = getRAEV100Level(grouped, RIESGO['bajo'], RIESGO['medio'], RIESGO['alto'])
        dfRet = grouped[['Date', 'raev100', 'Riesgo']].sort_values('Date')
        
        if not transportista:
            dfRet.rename(columns={'raev100': 'Total-Raev100', 'Riesgo': 'Total-Riesgo'}, inplace=True)
        else:
            tName = transportista[0]
            dfRet.rename(columns={
                'raev100': f'{tName.capitalize()}-Raev100', 
                'Riesgo': f'{tName.capitalize()}-Riesgo'
                }, inplace=True)
        return dfRet

def albemarleRanking(df, startDate=None, endDate=None, transportista=None, patente=None, codigo=None, ultimas=None, top=None, dev=None):
    """
    Casos:
    1) Si hay endDate y ultimas => variación semanal (pivot):
        - Oficinas en filas, semanas en columnas, dev total.
    2) Si hay flotas:
        2.1) Varias flotas => [Flota, raev100, dev] (todas sumadas por semana).
        2.2) Una sola flota + oficina
            - Si también hay código => agrupa por semana => [Date, raev100, dev]
            - Sin código => agrupa por semana y 'Codigo' => [Codigo, raev100, dev]
        2.3) Una sola flota SIN oficina (nuevo subcaso)
            => agrupar por 'Oficina' => [Oficina, raev100, dev]
    3) Si no hay flotas pero no hay ultimas => ranking de oficinas (Oficina, raev100, dev).
    
    Si top está definido (int) => 
    Se ignora la lógica anterior y se devuelven
    los top 'N' códigos más riesgosos (por raev100) en ese período.
    """
    # --------------------------------------------------------------------------------
    # 1) Filtrado por fechas (startDate, endDate o ultimas)
    # --------------------------------------------------------------------------------
    if endDate:
        endDate = pd.to_datetime(endDate)
        df = df[df['Date'] <= endDate]

    if startDate:
        startDate = pd.to_datetime(startDate)
        df = df[df['Date'] >= startDate]
    else:
        # Si no hay startDate pero hay ultimas => 
        # se calcula el rango (endDate - ultimas semanas)
        if ultimas is not None:
            startDate = endDate - pd.DateOffset(weeks=ultimas) + pd.Timedelta(days=1)
            df = df[df['Date'] >= startDate]

    # --------------------------------------------------------------------------------
    # 2) Filtros adicionales (transportista, patente)
    # --------------------------------------------------------------------------------
    if transportista:  # Si se pasa lista de transportista, filtramos
        df = df[df['Transportista'].isin(transportista)]

    if patente:  # Filtrar por patente si aplica
        df = df[df['Patente'] == patente]

    # --------------------------------------------------------------------------------
    # 3) Lógica de salida según parámetros recibidos
    # --------------------------------------------------------------------------------
    # Si top está definido => devolver los N códigos más riesgosos
    if top is not None and dev is not None:
        df = joinCols(df, 'Transportista', 'Patente')
        grouped = applyGroup(df, ['Patente', 'Transportista-Patente'])
        grouped = getRAEV100Level(grouped, RIESGO['bajo'], RIESGO['medio'], RIESGO['alto'])
        grouped = grouped[['Transportista-Patente', 'raev100', 'dev', 'Riesgo']].sort_values('raev100', ascending=False)
        final = grouped[grouped['dev'] >= dev]
        return final.head(top)
    # Si HAY transportitstas
    if transportista:
        # Múltiples transportistas
        if len(transportista) > 1:
            weekly = applyGroup(df, ['Transportista'])
            final = (
                weekly.groupby('Transportista', as_index=False)
                    .agg(
                        raevSum=('raevSum','sum'),
                        distanceSum=('distanceSum','sum'),
                        dev=('dev','sum')
                    )
            )
            final['raev100'] = ((final['raevSum'] / final['distanceSum']) * 100).round(1)
            final['Transportista'] = final['Transportista'].apply(capitalizePalabras)
            return final[['Transportista', 'raev100', 'dev']].sort_values('raev100')
        
        # Un solo transportista
        else:
            grouped = applyGroup(df, ['Patente'])
            grouped = getRAEV100Level(grouped, RIESGO['bajo'], RIESGO['medio'], RIESGO['alto'])
            return grouped[['Patente', 'raev100', 'dev', 'Riesgo']].sort_values('raev100', ascending=False)

    # Si NO hay transportistas
    else:
        # Si ultimas está definido => variación semanal (pivot Transportista)
        if ultimas is not None:
            grouped = applyGroup(df, ['Transportista'])
            grouped['Transportista'] = grouped['Transportista'].apply(capitalizePalabras)
            grouped = pivotIndex(grouped, 'Transportista')
            
            return grouped
        # Caso final => sumado total por semana y patente, se muestran (Patente, raev100, dev)
        grouped = applyGroup(df, ['Patente'])
        grouped = getRAEV100Level(grouped, RIESGO['bajo'], RIESGO['medio'], RIESGO['alto'])
        return grouped[['Patente', 'raev100', 'dev', 'Riesgo']].sort_values('raev100', ascending=False)