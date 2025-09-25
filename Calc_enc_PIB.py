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

______