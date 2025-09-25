# Dashboard de resultados del encadenamiento (lee columnas: year, quarter, current_value, encadenado, tasa_crecimiento_interanual)

import pandas as pd
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# Barside:
#Definición de los parámetros de la aplicación
st.set_page_config(page_title="PIB de Guatemala", page_icon="📈", layout="wide")
st.title("📈 Valor agregado por sector en Guatemala")
st.caption("Carga tu Excel, elige año/trimestres y grafica hasta 3 variables.")

# Lista de variables permitidas en Y
TARGET_Y_VARS = [
    "PIB_nominal", "Prim_nominal", "Sec_nominal", "Ter_nominal",
    "PIB_constante", "Prim_constante", "Sec_constante", "Ter_constante",
    "PIB_encadenado", "Prim_encadenado", "Sec_encadenado", "Ter_encadenado",
    "Var_PIB", "Var_Prim", "Var_Sec", "Var_Ter",
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

# Convertimos a tipos adecuados (sin romper si ya son numéricos)
work = df.copy()

# #EJE Y:

st.header("📊 Variables a graficar")

# Sugerimos solo las variables objetivo si existen en el DataFrame; si no, mostramos todas las numéricas
numeric_cols = work.select_dtypes(include=[np.number]).columns.tolist()
candidates = [c for c in TARGET_Y_VARS if c in work.columns]
if not candidates:
    candidates = numeric_cols  

vars_y = st.multiselect(
    "Elige hasta 3 variables (Y)",
    options=candidates,
    default=candidates[:1]
)

# Máximo se pueden elegir 3 variables
if len(vars_y) > 3:
    st.warning("Solo se permiten hasta 3 variables. Se tomarán las 3 primeras seleccionadas.")
    vars_y = vars_y[:3]

#Año y trimestre
# Asegurar tipos (por si vienen como objeto/str en algún caso)
df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
df["quarter"] = pd.to_numeric(df["quarter"], errors="coerce").astype("Int64")

# Opciones en sidebar
all_years = sorted([int(y) for y in df["year"].dropna().unique()])
all_quarters = [1, 2, 3, 4]

st.sidebar.markdown("### Filtros de tiempo")
sel_years = st.sidebar.multiselect(
    "Años", options=all_years, default=all_years
)
sel_quarters = st.sidebar.multiselect(
    "Trimestres", options=all_quarters, default=all_quarters, format_func=lambda q: f"T{q}"
)

# Filtrado de los años y trimestres que se eligen
mask = df["year"].isin(sel_years) & df["quarter"].isin(sel_quarters)
df_f = df.loc[mask].copy()

# Ordenar por tiempo y crear etiqueta eje X (Año-Tn)
df_f = df_f.sort_values(["year", "quarter"])
df_f["x_label"] = df_f.apply(lambda r: f"{int(r['year'])}-T{int(r['quarter'])}", axis=1)

#GRÁFICAS:
# Valida series
validas = [c for c in vars_y if c in df_f.columns]
if not validas:
    st.warning("Selecciona al menos una serie válida para graficar.")
elif df_f.empty:
    st.info("No hay datos para ese filtro.")
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
    fig.update_xaxes(tickangle=-45)
    fig.update_layout(hovermode="x unified", margin=dict(l=10, r=10, t=50, b=10))

    st.plotly_chart(fig, use_container_width=True)



