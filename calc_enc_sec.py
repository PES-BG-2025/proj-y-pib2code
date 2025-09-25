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
    Devuelve una Serie con el encadenado trimestral (Ke) para la serie elegida (PIB, o sectores).
    - col_nominal: columna con la serie a precios corrientes.
    - col_constante: columna con la serie a precios del año anterior o constantes ( en CN -> K)
    Fórmula (como se hace en SCN GT):
        Año base: Ke = K (en el primer año, son iguales pues es el año base)
        Años siguientes: Ke_t = (K_t / c̅_{t-1}) * Ke̅_{t-1} (constante dividido promedio corriente año anterior * promedio encadenado año anterior)
    donde:
        c̅_{t-1} = promedio corriente del año anterior (los 4T) (pendiente si se le añade años en coyuntura)
        Ke̅_{t-1} = promedio encadenado del año anterior (los 4T)
    """
    # Promedios corrientes por año
    prom_corr = df.groupby("year")[col_nominal].mean().to_dict()
    prom_enc = {}  # diccionario para el encadenado

    enc = np.full(len(df), np.nan, dtype=float) #se crea arreglo de Numpy para meter todo el encadenado, se intento hacer con 0, pero segun la libreria es mehjor hacerlo con nan, ya que lo señalas como marcador faltante o indefinido
    years = sorted(df["year"].unique()) #se penso en ordenar una lista ordenada de los años que hay disponibles en el DF.
    
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

# step 3 ) Mapeo de series (para ubicarlas tanto en sus versiones corrientes como constantes ) y cálculo por sector


#se genera un map, (segun documentaciones -> aplica otra función a cada elemento de un iterable (como una lista) y devuelve un objeto map, que es un iterador)
series_map = {
    "PIB":  ("PIB_nominal",  "PIB_constante"),
    "Prim": ("Prim_nominal", "Prim_constante"),
    "Sec":  ("Sec_nominal",  "Sec_constante"),
    "Ter":  ("Ter_nominal",  "Ter_constante"),
}

#agregando columnas con sus respectivas etiquetas (iterando el mapa)

for etiqueta, (col_nom, col_cons) in series_map.items():
    # Columna del encadenado a crear
    enc_col = f"{etiqueta}_encadenado"
    # Columna de tasa interanual (YoY) a crear
    tasa_col = f"{etiqueta}_tasa_interanual"

# Encadenado por serie (sector)
    df[enc_col] = calcular_encadenado_sector(df, col_nom, col_cons)

    # Tasa de crecimiento interanual (respecto al mismo trimestre del año anterior)
    df[tasa_col] = (df[enc_col] / df[enc_col].shift(4) * 100) - 100.0
    df[tasa_col] = df[tasa_col].round(2)  # redondeo a 2 decimales para que se vea mejor en el dashboard

#Step 4 ) #exportación a excel (agregando las columnas del encadenado y de las tasas de var.)

cols_originales = [
    "year", "quarter",
    "PIB_nominal","Prim_nominal","Sec_nominal","Ter_nominal",
    "PIB_constante","Prim_constante","Sec_constante","Ter_constante"]

#a las originales añadiles las nuevas ¿cuales son las nuevas?       

#constantes y tasas de variación

enc_cols  = [f"{s}_encadenado" for s in ["PIB","Prim","Sec","Ter"]]
#print(enc_cols)
tasas_cols = [f"{j}_Tasa_var" for j in ["PIB","Prim","Sec","Ter"]]

orden_final = cols_originales + enc_cols + tasas_cols
df_final = df[orden_final]

#¿cual es el orden final? cols_original + nuevas columnas

#orden_final = cols_originales + enc_cols + tasas_cols
#df_final = df[orden_final]

#df_final = df[cuadricula_final]
#out_file = "PIB_encadenado.xlsx"

#exportar a nuevo excel
#with pd.ExcelWriter(out_file, engine="openpyxl", mode="w") as writer:
    #df_final.to_excel(writer, sheet_name="resultado", index=False)

#print(f"Archivo guardado: {out_file}")
