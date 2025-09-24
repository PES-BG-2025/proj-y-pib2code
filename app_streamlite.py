# Dashboard de resultados del encadenamiento (lee columnas: year, quarter, current_value, encadenado, tasa_crecimiento_interanual)

import pandas as pd
import plotly.express as px
import streamlit as st

#Definición de los parámetros de la aplicación
st.set_page_config(page_title="Dashboard PIB de Guatemala", layout="wide")
st.title("📊 Dashboard PIB de Guatemala por actividad económica")

#Carga del archivo desde excel y configuración de la barra de opciones
st.sidebar.header("1) Cargar Excel")
uploaded = st.sidebar.file_uploader("Archivo (.xlsx)", type=["xlsx"])
sheet = st.sidebar.text_input("Hoja", value="resultado")