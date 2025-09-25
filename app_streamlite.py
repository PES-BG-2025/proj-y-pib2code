# Dashboard de resultados del encadenamiento (lee columnas: year, quarter, current_value, encadenado, tasa_crecimiento_interanual)

import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px 

# Inicialización de estado
if "df" not in st.session_state:
    st.session_state["df"] = pd.DataFrame()
if "rename_map" not in st.session_state:
    st.session_state["rename_map"] = {}

#Titulos del Dashboard
st.set_page_config(page_title="PIB de Guatemala", page_icon="📈", layout="wide")
st.title("📈 Valor agregado por sectores económicos agregados, en Guatemala")
st.caption("Sube el archivo, elige años y trimestres y compara hasta 3 series.")

st.session_state.df = pd.read_excel("PIB_encadenado.xlsx", engine="openpyxl")

# #CARGA DE ARCHIVO EN LA SIDEBAR:
# with st.sidebar:
#     st.header("Cargar archivo de datos")
#     uploaded = st.file_uploader("Sube tu archivo (.xlsx)", type=["xlsx"]) 
#     # Botón para cargar
#     boton_carga = st.button("Cargar")

# # Lectura del archivo cuando se presiona el botón
# sheet_name = None
# if boton_carga:
#     try:
#         # Excel
#         if sheet_name is None:
#             # Si por alguna razón no detectamos la hoja, leemos la primera
#             st.session_state.df = pd.read_excel('xlsx')
#         else:
#             st.session_state.df = pd.read_excel(uploaded, sheet_name=sheet_name)
#         st.success(f"Archivo cargado correctamente")
#         # Reiniciar mapa de renombres cada vez que se carga un archivo nuevo
#         st.session_state.rename_map = {c: c for c in st.session_state.df.columns}
#     except Exception as e:
#         st.error(f"Error al leer el archivo: {e}")

# Si no hay datos aún, mostramos una guía rápida en el mensaje
df = st.session_state.get("df", pd.DataFrame())
if st.session_state.df.empty:
    st.info("Sube tu archivo y presiona **Cargar** en la barra lateral para comenzar.")
    st.stop()

#Guarda el dataframe 
df = st.session_state.df
# Vista rápida
with st.expander("👀 Ver datos"):
    st.dataframe(df.head(48), use_container_width=True)

# Convertimos a tipos adecuados (sin romper si ya son numéricos)
work = df.copy()

# #EJE Y:
st.header("📊 Variables a graficar")

# Lista de variables permitidas en Y
VARIABLES= [
    "PIB_nominal", "Prim_nominal", "Sec_nominal", "Ter_nominal",
    "PIB_constante", "Prim_constante", "Sec_constante", "Ter_constante",
    "PIB_encadenado", "Prim_encadenado", "Sec_encadenado", "Ter_encadenado",
    "Var_PIB", "Var_Prim", "Var_Sec", "Var_Ter",
]

# Sugerimos solo las posibles de Y que existen en el Dataframe
columnas = work.select_dtypes(include=[np.number]).columns.tolist()
candidatos = [c for c in VARIABLES if c in work.columns]
if not candidatos:
    candidates = columnas

vars_y = st.multiselect(
    "Elige hasta 3 variables (Y)",
    options=candidatos,
    default=candidatos[:1]
)

# Máximo se pueden elegir 3 variables
if len(vars_y) > 3:
    st.warning("Solo se permiten hasta 3 variables. Se tomarán las 3 primeras seleccionadas.")
    vars_y = vars_y[:3]

#Año y trimestre
# Asegurar tipos (por si vienen como str en algún caso), corce= devuelve NaN
df["year"] = pd.to_numeric(df["year"], errors="coerce")
df["quarter"] = pd.to_numeric(df["quarter"], errors="coerce")

# Opciones en SIDEBAR
all_years = sorted([int(y) for y in df["year"].unique()])
all_quarters = [1, 2, 3, 4]

st.sidebar.markdown("### Filtros de tiempo")
years = st.sidebar.multiselect(
    "Años", options=all_years, default=all_years
)
quarters = st.sidebar.multiselect(
    "Trimestres", options=all_quarters, default=all_quarters, format_func=lambda q: f"T{q}"
)

# Filtrado de los años y trimestres que se eligen
mask = df["year"].isin(years) & df["quarter"].isin(quarters)
df_f = df.loc[mask].copy()

# Ordenar por tiempo y crear etiqueta eje X (Año-Tn)
df_f = df_f.sort_values(["year", "quarter"])
df_f["x_label"] = df_f.apply(lambda r: f"{int(r['year'])}-T{int(r['quarter'])}", axis=1)

#GRÁFICAS:
# Valida series
validas = [c for c in vars_y if c in df_f.columns]
if not validas:
    st.warning("Selecciona al menos una serie válida para graficar.")
else:
    y_cols = validas[0] if len(validas) == 1 else validas  

    fig = px.line(
        df_f,
        x="x_label",
        y=y_cols,
        markers=True,
        title="Serie por Año y Trimestre",
        labels={"x_label": "Año - Trimestre", "value": "Valor", "variable": "Serie"}
    )
st.plotly_chart(fig)



