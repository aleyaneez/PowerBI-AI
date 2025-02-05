import pandas as pd
from datetime import datetime, timedelta

RIESGO = {
    "bajo": 6.1,
    "medio": 8.2,
    "alto": 9.8
}

def capitalizePalabras(s: str) -> str:
    """Capitalizar las palabras de un string
    """
    return ' '.join([word.capitalize() for word in s.split()])

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

def applyGroupEv(df, groupCols, freq='W'):
    """
    Agrupa el DataFrame df por las columnas en groupCols
    + la frecuencia semanal (freq) sobre 'Date'.
    Calcula:
    - raevSum = suma de raev
    - distanceSum = suma de distance
    - raev100 = (raevSum / distanceSum)*100
    
    Retorna columnas: [Date, *groupCols, raevSum, distanceSum, raev100]
    """
    grouped = (
        df.groupby([pd.Grouper(key='Date', freq=freq)] + groupCols)
            .agg(
                raevSum=('raev', 'sum'),
                distanceSum=('distance', 'sum')
        )
        .reset_index()
    )
    grouped = getRAEV100(grouped)
    grouped['Date'] = grouped['Date'] - timedelta(days=6)
    return grouped

def applyGroup(df, groupCols, freq='W'):
    """
    Agrupa el DataFrame df por semana (según freq)
    y por las columnas en groupCols, calculando:
    - raevSum, distanceSum, dev
    - raev100 = (raevSum / distanceSum) * 100

    Devuelve un nuevo DataFrame con columnas:
    [Date, *groupCols, raevSum, distanceSum, dev, raev100].
    """
    grouped = (
        df.groupby([pd.Grouper(key='Date', freq=freq)] + groupCols)
        .agg(
            raevSum=('raev', 'sum'),
            distanceSum=('distance', 'sum'),
            dev=('dev', 'sum')
        ).reset_index()
    )
    grouped = getRAEV100(grouped)
    grouped['dev'] = grouped['dev'].round(0).astype(int)
    grouped['Date'] = grouped['Date'] - timedelta(days=6)
    return grouped

def joinCols(df, first, second):
    """
    Concatenar dos columnas de un DataFrame
    """
    df[f'{first}-{second}'] = df[first].fillna('NaN') + '-' + df[second].fillna('NaN')
    return df

def pivotIndex(df, index):
    """
    Para el caso en que NO hay flotas (o flotas=None) y se desea
    la variación semanal por oficinas (ultimas != None).
    Hace un pivot con la columna 'raev100' a lo largo de las fechas,
    y agrega una columna 'dev' con la suma total de dev por oficina.
    """
    dfPivot = df.pivot(
        index=index,
        columns='Date',
        values='raev100'
    ).reset_index()

    dfPivot.columns = (
        [index] + [
            col.strftime('%d %b') if isinstance(col, pd.Timestamp) else col
            for col in dfPivot.columns[1:]
        ]
    )

    dfDev = (
        df.groupby(index, as_index=False)['dev']
        .sum()
        .rename(columns={'dev': 'dev'})
    )

    return dfPivot.merge(dfDev, on=index, how='left')