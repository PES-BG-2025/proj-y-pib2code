# Dashboard de resultados del encadenamiento (lee columnas: year, quarter, current_value, encadenado, tasa_crecimiento_interanual)

import pandas as pd
import plotly.express as px
import streamlit as st

# --------- Barra lateral: carga y opciones ---------
#Definición de los parámetros de la aplicación
file = st.sidebar.file_uploader("Sube tu Excel (.xlsx)", type=["xlsx"])
sheet = st.sidebar.text_input("Nombre de la hoja", value="resultado")
