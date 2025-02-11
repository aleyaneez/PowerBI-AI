import pandas as pd
import locale
from globals import METAS, applyGroupEv, getCumplimiento, pivotIndex, joinCols, applyGroup

locale.setlocale(locale.LC_TIME, 'es_CL.UTF-8')

def enexEv(df, startDate, endDate, mercado=None, group: bool = None):
    endDate = pd.to_datetime(endDate)
    endDate = endDate + pd.Timedelta(days=6)
    
    # Filtrado inicial
    df = df[(df['distance'] > 0) & (df['distance'] < 10000)]
    df = df[(df['Date'] >= startDate) & (df['Date'] <= endDate)]
    
    dfTotal = df.copy()

    # Si hay mercado, filtrar
    if mercado:
        df = df[df['Mercado'].isin(mercado)]
    
    totalGrouped = applyGroupEv(dfTotal, [])
    totalGrouped = getCumplimiento(totalGrouped, METAS)
    dfTotal = totalGrouped[['Date', 'raev100', 'Meta']].sort_values('Date')
    dfTotal.rename(columns={'raev100': 'Total-Raev100', 'Meta': 'Total-Meta'}, inplace=True)
    
    if group:
        grouped = applyGroupEv(df, [])
        grouped = getCumplimiento(grouped, METAS)
        dfGrouped = grouped[['Date', 'raev100', 'Meta']].sort_values('Date')
        
        prefix = 'Agrupado' if mercado else 'Total'
        dfGrouped.rename(columns={'raev100': f'{prefix}-Raev100', 'Meta': f'{prefix}-Meta'}, inplace=True)
        
        merged = dfGrouped.merge(dfTotal, on='Date', how='left')
        finalCols = ['Date', f'{prefix}-Raev100', f'{prefix}-Meta', 'Total-Raev100', 'Total-Meta']
        return merged[finalCols].sort_values('Date')

    # Caso A: Varios mercados => pivot
    if mercado and len(mercado) > 1:
        grouped = applyGroupEv(df, ['Mercado'])
        grouped = getCumplimiento(grouped, METAS)

        pivoted = grouped.pivot_table(
            index='Date', 
            columns='Mercado', 
            values=['raev100', 'Meta'],
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
                    newCols.append(f'{t.capitalize()}-Meta')
        pivoted.columns = newCols
        
        merged = pivoted.merge(dfTotal, on='Date', how='left')
        
        finalCols = ['Date']
        for m in mercado:
            finalCols.append(f'{m.capitalize()}-Raev100')
            finalCols.append(f'{m.capitalize()}-Meta')
        finalCols.extend(['Total-Raev100', 'Total-Meta'])

        return merged[finalCols].sort_values('Date')
    else:
        # Caso B: Cero transportistas o 1 transportista
        grouped = applyGroupEv(df, [])
        grouped = getCumplimiento(grouped, METAS)
        dfRet = grouped[['Date', 'raev100', 'Meta']].sort_values('Date')
        
        if not mercado:
            dfRet.rename(columns={'raev100': 'Total-Raev100', 'Meta': 'Total-Meta'}, inplace=True)
            return dfRet
        else:
            mName = mercado[0]
            dfRet.rename(columns={
                'raev100': f'{mName.capitalize()}-Raev100', 
                'Meta': f'{mName.capitalize()}-Meta'
                }, inplace=True)
            dfRet = dfRet.merge(dfTotal, on='Date', how='left')
            finalCols = ['Date', f'{mName.capitalize()}-Raev100', f'{mName.capitalize()}-Meta', 'Total-Raev100', 'Total-Meta']
            return dfRet

def enexRanking(df, startDate=None, endDate=None, especialista=None, ultimas=None, top=None):
    # 1. Procesar endDate: convertir a datetime y extenderlo para incluir la semana completa.
    if endDate:
        endDate = pd.to_datetime(endDate)
        # Se extiende para incluir la semana completa (6 días más)
        endDate_extended = endDate + pd.Timedelta(days=6)
    else:
        endDate_extended = None

    # 2. Calcular startDate si no se proporciona y se define ultimas.
    if not startDate and ultimas is not None and endDate is not None:
        startDate = endDate - pd.DateOffset(weeks=ultimas - 1)
    elif startDate:
        startDate = pd.to_datetime(startDate)

    # 3. Filtrar el DataFrame por fecha entre startDate y endDate_extended.
    if startDate and endDate_extended:
        df = df[(df['Date'] >= startDate) & (df['Date'] <= endDate_extended)]
    elif startDate:
        df = df[df['Date'] >= startDate]
    elif endDate_extended:
        df = df[df['Date'] <= endDate_extended]

    # 4. Filtrar por especialista, si se indica.
    if especialista:
        if isinstance(especialista, str):
            especialista = [especialista]
        df = df[df['Especialista'].isin(especialista)]

    # 5. Crear la columna "Transportista-Patente"
    df = joinCols(df, 'Transportista', 'Patente')

    # 6. Agrupar semanalmente usando la función applyGroup, agrupando por "Transportista-Patente".
    agrupado = applyGroup(df, ['Transportista-Patente'], freq='W')
    # Cada fila de "agrupado" contiene: Date (inicio de la semana), raev100, dev, etc.

    # 7. Pivotar el DataFrame para que cada fila corresponda a un especialista y cada columna (por fecha) tenga el raev100.
    pivot = pivotIndex(agrupado, 'Transportista-Patente')

    # 8. Calcular el agregado global por especialista para obtener raev100 y el total acumulado de dev en todo el período.
    # Se agrupa a partir del df filtrado (sin pivotear), de modo que 'dev' corresponde a la suma total de todos los registros filtrados.
    agg = df.groupby('Transportista-Patente').agg(
        raevSum=('raev', 'sum'),
        distanceSum=('distance', 'sum'),
        dev=('dev', 'sum')
    ).reset_index()
    agg['raev100'] = ((agg['raevSum'] / agg['distanceSum']) * 100).round(1)
    # Para que getCumplimiento funcione, se agrega una columna "Date" (se asigna endDate o el valor máximo de 'Date')
    if endDate:
        agg['Date'] = endDate
    else:
        agg['Date'] = df['Date'].max()
    agg = getCumplimiento(agg, METAS)
    # Se conservan las columnas necesarias para el ranking
    agg = agg[['Transportista-Patente', 'raev100', 'dev']]

    # 9. Combinar la tabla pivot con el agregado global.
    final = pivot.merge(agg, on='Transportista-Patente', how='left')

    # 11. Ordenar de forma descendente por raev100 global y seleccionar los top solicitados.
    if top is not None:
        final = final.sort_values('raev100', ascending=False).head(top)

    # 12. Se muestran las columnas: "Transportista-Patente", las columnas de cada semana y "dev".
    # Se elimina la columna global "raev100" de la vista final.
    if 'raev100' in final.columns:
        final = final.drop(columns='raev100')

    return final