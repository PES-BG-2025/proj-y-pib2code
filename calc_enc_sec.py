import pandas as pd
import numpy as np

# --------------------------------------------
# 1) Lectura y orden de Data
# --------------------------------------------
df = pd.read_excel("PIB_original.xlsx", sheet_name="series", engine="openpyxl")
print("Lectura OK")
df = df.sort_values(by=["year", "quarter"]).reset_index(drop=True)

#Fase de revisión de la data contenido en el archivo de entrada
print("Nulos por columna:\n", df.isnull().sum())
conteo_trimestres = df.groupby("year")["quarter"].nunique()
print("Trimestres por año:\n", conteo_trimestres)

# --------------------------------------------
# 2) Función: encadenado por UNA serie (sector o el PIB)
# --------------------------------------------
def calcular_encadenado_sector(df, col_nominal, col_constante):
    """
    Retorna una Serie con el encadenado trimestral (Ke) para la serie dada.
    - col_nominal: columna con la serie a precios corrientes
    - col_constante: columna con la serie a precios del año anterior o constantes (CN) (K)
    Fórmula:
        Año base: Ke = K
        Años siguientes: Ke_t = (K_t / c̅_{t-1}) * Ke̅_{t-1}
    donde:
        c̅_{t-1} = promedio corriente del año anterior (4T)
        Ke̅_{t-1} = promedio encadenado del año anterior (4T)
    """
    # Promedios corrientes por año
    prom_corr = df.groupby("year")[col_nominal].mean().to_dict()
    prom_enc = {}  # diccionario para el encadenado

    enc = np.full(len(df), np.nan, dtype=float) #se crea arreglo de Numpy para meter todo el encadenado, se intento hacer con 0, pero segun la libreria es mehjor hacerlo con nan, ya que lo señalas como marcador faltante o indefinido
    years = sorted(df["year"].unique())
    
    #asignación de año de referencia (deberia ser 2013, REVISAR)
    base_Year = years[0] 
    #print(base_Year)
    for y in years:
        ref = (df["year"] == y)
        if y == base_Year:
            # Año base: igual a las cifras constantes (a precios del año anterior)
            enc[ref] = df.loc[ref, col_constante].to_numpy(dtype=float)
        else:
            c_prev = prom_corr[y - 1]      # promedio corriente del año anterior
            ke_prev = prom_enc[y - 1]      # promedio encadenado del año anterior
            enc[ref] = (
                df.loc[ref, col_constante].to_numpy(dtype=float) / float(c_prev)
            ) * float(ke_prev)

        # promedio encadenado del año actual (los 4T)
        prom_enc[y] = np.nanmean(enc[ref]) #podriamos usar el nan.mean para setear años incompletos (2025 1 y 2T, REVISAR)

    return pd.Series(enc, index=df.index)
