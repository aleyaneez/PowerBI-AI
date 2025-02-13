import pandas as pd
import numpy as np
import locale
from datetime import datetime, timedelta
from globals import RIESGO, capitalizePalabras, applyGroupEv, applyGroup, getRAEV100Level, joinCols

locale.setlocale(locale.LC_TIME, 'es_CL.UTF-8')

def filterEv(df, startDate, endDate, flotas=None):
    """ 
    1) Sin flotas => columnas [Date, raev100].
    2) Lista de flotas con >1 => [Date, flota1, flota2, ...].
    3) Lista de flotas con 1 => [Date, raev100] (solo esa flota).
    Filtra también distance en (0,10000).
    """
    endDate = pd.to_datetime(endDate)
    endDate = endDate + pd.Timedelta(days=6)
    
    # Filtrado inicial
    df = df[(df['distance'] > 0) & (df['distance'] < 10000)]
    df = df[(df['Date'] >= startDate) & (df['Date'] <= endDate)]

    # Si hay flotas, filtrar
    if flotas:
        df = df[df['Flota'].isin(flotas)]

    # Caso A: Varias flotas => pivot
    if flotas and len(flotas) > 1:
        grouped = applyGroupEv(df, ['Flota'])
        grouped = getRAEV100Level(grouped, RIESGO['bajo'], RIESGO['medio'], RIESGO['alto'])

        pivoted = grouped.pivot_table(
            index='Date', 
            columns='Flota', 
            values=['raev100', 'Riesgo'],
            aggfunc='first'
        ).reset_index()

        newCols = []
        for colTuple in pivoted.columns:
            if colTuple[0] == 'Date':
                newCols.append('Date')
            else:
                metric, flota = colTuple
                if metric == 'raev100':
                    newCols.append(f'{flota.capitalize()}-Raev100')
                else:
                    newCols.append(f'{flota.capitalize()}-Riesgo')
        pivoted.columns = newCols
        
        finalCols = ['Date']
        for flota in flotas:
            finalCols.append(f'{flota.capitalize()}-Raev100')
            finalCols.append(f'{flota.capitalize()}-Riesgo')

        return pivoted[finalCols].sort_values('Date')
    else:
        # Caso B: Cero flotas o 1 flota
        grouped = applyGroupEv(df, [])
        grouped = getRAEV100Level(grouped, RIESGO['bajo'], RIESGO['medio'], RIESGO['alto'])
        dfRet = grouped[['Date', 'raev100', 'Riesgo']].sort_values('Date')
        
        if not flotas:
            dfRet.rename(columns={'raev100': 'Total-Raev100', 'Riesgo': 'Total-Riesgo'}, inplace=True)
        else:
            flotaName = flotas[0]
            dfRet.rename(columns={
                'raev100': f'{flotaName.capitalize()}-Raev100', 
                'Riesgo': f'{flotaName.capitalize()}-Riesgo'
                }, inplace=True)
        return dfRet

def pivotOficina(df):
    """
    Para el caso en que NO hay flotas (o flotas=None) y se desea
    la variación semanal por oficinas (ultimas != None).
    Hace un pivot con la columna 'raev100' a lo largo de las fechas,
    y agrega una columna 'dev' con la suma total de dev por oficina.
    """
    dfPivot = df.pivot(
        index='Oficina',
        columns='Date',
        values='raev100'
    ).reset_index()

    dfPivot.columns = (
        ['Oficina'] + [
            col.strftime('%d %b') if isinstance(col, pd.Timestamp) else col
            for col in dfPivot.columns[1:]
        ]
    )

    dfDev = (
        df.groupby('Oficina', as_index=False)['dev']
        .sum()
        .rename(columns={'dev': 'dev'})
    )

    return dfPivot.merge(dfDev, on='Oficina', how='left')

def joinCols(df, first, second):
    """
    Concatenar dos columnas de un DataFrame
    """
    df[f'{first}-{second}'] = df[first].fillna('NaN') + '-' + df[second].fillna('NaN')
    return df


def filterRanking(df, startDate=None, endDate=None, flotas=None, oficina=None, codigo=None, ultimas=None, top=None, dev=None):
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
    # 2) Filtros adicionales (flotas, oficina, codigo)
    # --------------------------------------------------------------------------------
    if flotas:  # Si se pasa lista de flotas, filtramos
        df = df[df['Flota'].isin(flotas)]

    if oficina:  # Filtrar por oficina si aplica
        df = df[df['Oficina'] == oficina]

    if codigo:   # Filtrar por código si aplica
        df = df[df['Codigo'] == codigo]

    # --------------------------------------------------------------------------------
    # 3) Lógica de salida según parámetros recibidos
    # --------------------------------------------------------------------------------
    # Si top está definido => devolver los N códigos más riesgosos
    if top is not None and dev is not None:
        df = df[df['dev'] >= dev]
        df['Oficina'] = df['Oficina'].apply(capitalizePalabras)
        df = joinCols(df, 'Oficina', 'Codigo')
        grouped = applyGroup(df, ['Codigo', 'Oficina-Codigo'])
        grouped = getRAEV100Level(grouped, RIESGO['bajo'], RIESGO['medio'], RIESGO['alto'])
        grouped = grouped[['Oficina-Codigo', 'raev100', 'dev', 'Riesgo']].sort_values('raev100', ascending=False)
        return grouped.head(top)
    # Si HAY flotas
    if flotas:
        # Múltiples flotas
        if len(flotas) > 1:
            weekly = applyGroup(df, ['Flota'])
            final = (
                weekly.groupby('Flota', as_index=False)
                    .agg(
                        raevSum=('raevSum','sum'),
                        distanceSum=('distanceSum','sum'),
                        dev=('dev','sum')
                    )
            )
            final['raev100'] = ((final['raevSum'] / final['distanceSum']) * 100).round(1)
            final = getRAEV100Level(final, RIESGO['bajo'], RIESGO['medio'], RIESGO['alto'])
            final['Flota'] = final['Flota'].apply(capitalizePalabras)
            return final[['Flota', 'raev100', 'dev', 'Riesgo']].sort_values('raev100')
        
        # Una sola flota
        else:
            # Si oficina y código => agrupar por semana únicamente
            if oficina and codigo:
                grouped = applyGroup(df, [])
                grouped = getRAEV100Level(grouped, RIESGO['bajo'], RIESGO['medio'], RIESGO['alto'])
                return grouped[['Date', 'raev100', 'dev', 'Riesgo']].sort_values('Date')
            
            # Si oficina y sin código => agrupar por semana, 'Codigo'
            elif oficina and not codigo:
                grouped = applyGroup(df, ['Codigo'])
                return grouped[['Codigo', 'raev100', 'dev']].sort_values('raev100')
            
            # Solo flota (sin oficina) => agrupar por 'Oficina'
            else:
                grouped = applyGroup(df, ['Oficina'])
                grouped['Oficina'] = grouped['Oficina'].apply(capitalizePalabras)
                grouped = getRAEV100Level(grouped, RIESGO['bajo'], RIESGO['medio'], RIESGO['alto'])
                return grouped[['Oficina', 'raev100', 'dev', 'Riesgo']].sort_values('raev100', ascending=False)

    # Si NO hay flotas
    else:
        # Si ultimas está definido => variación semanal (pivot oficinas)
        if ultimas is not None:
            grouped = applyGroup(df, ['Oficina'])
            grouped['Oficina'] = grouped['Oficina'].apply(capitalizePalabras)
            grouped = pivotOficina(grouped)
            
            return grouped
        
        # Caso final => sumado total por semana y oficina, se muestran (Oficina, raev100, dev)
        grouped = applyGroup(df, ['Oficina'])
        grouped['Oficina'] = grouped['Oficina'].apply(capitalizePalabras)
        grouped = getRAEV100Level(grouped, RIESGO['bajo'], RIESGO['medio'], RIESGO['alto'])
        return grouped[['Oficina','raev100','dev', 'Riesgo']].sort_values('raev100', ascending=False)