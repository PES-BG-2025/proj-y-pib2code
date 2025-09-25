import pandas as pd
import numpy as np

# Leer archivo Excel
df = pd.read_excel("PIB_original.xlsx", sheet_name="series", engine="openpyxl")

print("Lectura OK")
df.info

#___________________________________
#Fase de revisión de la data contenido en el archivo de entrada
#___________________________________

#valores nulos
print(df.isnull().sum())

# Revisar si cada año tiene 4 trimestres
conteo_trimestres = df.groupby("year")["quarter"].nunique()
print(conteo_trimestres)

#______________________________________________________
# Calculo de encadenamiento
#______________________________________________________

# Promedio de cifras corrientes por año
promedio_C_PIB = df.groupby("year")["PIB_nominal"].mean()
promedio_C_Prim = df.groupby("year")["Prim_nominal"].mean()
promedio_C_Sec = df.groupby("year")["Sec_nominal"].mean()
promedio_C_Ter = df.groupby("year")["Ter_nominal"].mean()

# Promedio de cifras encadenadas 
def calcular_encadenado(df):
    """
    Calcula el encadenado trimestral (Ke).
    Requiere que df tenga columnas: year, quarter, current_value, constant_prev_year_prices
    """
    # Ordenar los datos por año y trimestre
    df = df.sort_values(by=["year", "quarter"]).reset_index(drop=True)
    
    # Diccionarios para almacenar promedios anuales
promedio_C_PIB = df.groupby("year")["PIB_nominal"].mean().to_dict()
promedio_C_Prim = df.groupby("year")["PIB_nominal"].mean().to_dict()
promedio_C_Sec = df.groupby("year")["PIB_nominal"].mean().to_dict()
promedio_C_Ter = df.groupby("year")["PIB_nominal"].mean().to_dict()

promedio_encadenado_PIB = {}
promedio_encadenado_Prim = {}
promedio_encadenado_Sec = {}
promedio_encadenado_Ter = {}

# Proceso de iteración año por año
for year in sorted(df["year"].unique()):
    if year == df["year"].min(): #año base.
        # Año base: encadenado = cifras constantes
         df.loc[df["year"] == year, "PIB_encadenado"] = df.loc[df["year"] == year, "PIB_constante"]
         df.loc[df["year"] == year, "Prim_encadenado"] = df.loc[df["year"] == year, "Prim_constante"]
         df.loc[df["year"] == year, "Sec_encadenado"] = df.loc[df["year"] == year, "Sec_constante"]
         df.loc[df["year"] == year, "Ter_encadenado"] = df.loc[df["year"] == year, "Ter_constante"]
    
    else: 
         # Obtener promedios del año anterior
         c_prom_PIB = promedio_C_PIB[year - 1]
         c_prom_Prim = promedio_C_PIB[year - 1]
         c_prom_Sec = promedio_C_PIB[year - 1]
         c_prom_Ter = promedio_C_PIB[year - 1]

         #ke_prom = promedio_encadenado_PIB[year - 1]
     

       
          
