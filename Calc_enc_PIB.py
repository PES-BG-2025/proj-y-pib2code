import pandas as pd
import numpy as np

#_______________
#lectura de data
#__________________
df = pd.read_excel("PIB_original.xlsx", sheet_name="series", engine="openpyxl")
print("Lectura OK")
print("Nulos por columna:\n", df.isnull().sum())
 # Ordenar los datos por año y trimestre
df = df.sort_values(by=["year", "quarter"]).reset_index(drop=True)

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
cols_corr = ["PIB_nominal","Prim_nominal","Sec_nominal","Ter_nominal"]
cols_cons = ["PIB_constante","Prim_constante","Sec_constante","Ter_constante"]

#promedios del año t
prom_anual_corr = df.groupby("year")[cols_corr].mean()
prom_anual_const = df.groupby("year")[cols_cons].mean()

# Promedio del año anterior
prom_anual_corr_prev = prom_anual_corr.shift(-1) #desplaza al anterior en el dataframee
prom_anual_const_prev = prom_anual_const.shift(-1) #desplaza al anterior en el dataframee

def calcular_encadenado(df):
    """
    Calcula el encadenado trimestral (Ke).
    Requiere que df tenga columnas: year, quarter, current_value, constant_prev_year_prices
    """
     
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
        # -Corrientes
            c_prom_PIB = promedio_C_PIB[year - 1]
            c_prom_Prim = promedio_C_PIB[year - 1]
            c_prom_Sec = promedio_C_PIB[year - 1]
            c_prom_Ter = promedio_C_PIB[year - 1]

        #-encadenado        
            
            ke_prom_PIB = promedio_encadenado_PIB[year - 1]
            ke_prom_Prim = promedio_encadenado_PIB[year - 1]
            ke_prom_Sec = promedio_encadenado_PIB[year - 1]
            ke_prom_Ter = promedio_encadenado_PIB[year - 1]

    return calcular_encadenado(df)

        


       
          
