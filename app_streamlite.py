# Dashboard de resultados del encadenamiento (lee columnas: year, quarter, current_value, encadenado, tasa_crecimiento_interanual)

import pandas as pd
import plotly.express as px
import streamlit as st

# --------- Barra lateral: carga y opciones ---------
#Definición de los parámetros de la aplicación
file = st.sidebar.file_uploader("Sube tu Excel (.xlsx)", type=["xlsx"])
sheet = st.sidebar.text_input("Nombre de la hoja", value="resultado")

st.sidebar.markdown("### Columna de tiempo")
time_mode = st.sidebar.radio("¿Cómo viene la fecha/tiempo?",
                             ["date (timestamp)", "year + quarter"], index=1)

date_col = None
year_col = None
quarter_col = None

if time_mode == "date (timestamp)":
    date_col = st.sidebar.text_input("Nombre de la columna de fecha", value="date")
else:
    year_col = st.sidebar.text_input("Columna de año", value="year")
    quarter_col = st.sidebar.text_input("Columna de trimestre", value="quarter")

btn = st.sidebar.button("Cargar y listar variables")