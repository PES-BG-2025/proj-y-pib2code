# Dashboard de resultados del encadenamiento (lee columnas: year, quarter, current_value, encadenado, tasa_crecimiento_interanual)

import pandas as pd
import plotly.express as px
import streamlit as st
import numpy as np


# --------- Barra lateral: carga y opciones ---------
#Definición de los parámetros de la aplicación
st.set_page_config(page_title="PIB de Guatemala", page_icon="📈", layout="wide")
st.title("📈 PIB en Guatemala")
st.caption("Carga tu Excel, elige Año/Quarter y grafica hasta 3 variables.")

# Obtiene los colores de fondo y texto del tema actual de streamlit
backgroundColor = st.get_option('theme.secondaryBackgroundColor')
textColor = st.get_option('theme.textColor')


# Lista objetivo de variables permitidas en Y
TARGET_Y_VARS = [
    "PIB_nominal", "Prim_nominal", "Sec_nominal", "Ter_nominal",
    "PIB_constante", "Prim_constante", "Sec_constante", "Ter_constante",
    "PIB_encadenado", "Prim_encadenado", "Sec_encadenado", "Ter_encadenado",
    "Var_PIB", "Var_prim", "Var_Sec", "Var_Ter",
]
#CARGA DE ARCHIVO
with st.sidebar:
    st.header("Cargar archivo de datos")
    uploaded = st.file_uploader("Sube tu archivo (.xlsx, .xls o .csv)", type=["xlsx", "xls", "csv"]) 

    sheet_name = None
    if uploaded is not None and uploaded.name.lower().endswith((".xlsx", ".xls")):
        # Si es Excel, intentamos listar hojas
        try:
            xls = pd.ExcelFile(uploaded)
            sheet_name = st.selectbox("Hoja de Excel", xls.sheet_names, index=0)
        except Exception as e:
            st.error("No se pudo leer el Excel") #Asegurar de tener 'openpyxl' instalado si es .xlsx.

    # Botón para cargar/leer definitivamente
    load_btn = st.button("Cargar")

# Lectura del archivo cuando se presiona el botón
if load_btn:
    try:
        if uploaded is None:
            st.warning("Sube un archivo.")
        else:
            fname = uploaded.name.lower()
            if fname.endswith(".csv"):
                st.session_state.df = pd.read_csv(uploaded)
            else:
                # Excel
                if sheet_name is None:
                    # Si por alguna razón no detectamos la hoja, leemos la primera
                    st.session_state.df = pd.read_excel(uploaded)
                else:
                    st.session_state.df = pd.read_excel(uploaded, sheet_name=sheet_name)
            st.success(f"Archivo cargado correctamente: {uploaded.name} — {st.session_state.df.shape[0]} filas × {st.session_state.df.shape[1]} columnas")
            # Reiniciar mapa de renombres cada vez que se carga un archivo nuevo
            st.session_state.rename_map = {c: c for c in st.session_state.df.columns}
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")

# Si no hay datos aún, mostramos una guía rápida y sale
if st.session_state.df.empty:
    st.info("Sube tu archivo y presiona **Cargar** en la barra lateral para comenzar.")
    st.stop()

#Guarda el dataframe 
df = st.session_state.df
# Vista rápida
with st.expander("👀 Ver datos"):
    st.dataframe(df.head(48), use_container_width=True)


#EJE X



#EJE Y:
# Convertimos a tipos adecuados (sin romper si ya son numéricos)
work = df.copy()

st.header("📊 Variables a graficar")

# Sugerimos solo las variables objetivo si existen en el DataFrame; si no, mostramos todas las numéricas
numeric_cols = work.select_dtypes(include=[np.number]).columns.tolist()
candidates = [c for c in TARGET_Y_VARS if c in work.columns]
if not candidates:
    candidates = numeric_cols  

y_vars = st.multiselect(
    "Elige hasta 3 variables (Y)",
    options=candidates,
    default=candidates[:1]
)

# Máximo se pueden elegir 3 variables
if len(y_vars) > 3:
    st.warning("Solo se permiten hasta 3 variables. Se tomarán las 3 primeras seleccionadas.")
    y_vars = y_vars[:3]

chart_type = st.selectbox("Tipo de gráfica", ["Líneas", "Barras", "Área", "Dispersión"], index=0)

#Gráficas