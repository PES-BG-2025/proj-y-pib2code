# Dashboard PIB Guatemala

import pandas as pd # Manejo de datos en tablas (DataFrames)
import streamlit as st
import numpy as np  # Framework para apps web de datos
import plotly.express as px    # Gráficos interactivos


#1. Configuración de la página de Streamlit
st.set_page_config(page_title="PIB de Guatemala", page_icon="📈", layout="wide") # Título de la pestaña del navegador
st.title("📈 Valor agregado por sectores económicos, en Guatemala") # Título principal visible en la app

#2. Carga de archivo de Excel y lo guardo en sesión 
#para almacenar un DataFrame de Pandas (u otros objetos similares) en el estado de sesión de Streamlit, 
# permitiendo que ese DataFrame persista y esté disponible entre diferentes interacciones y 
# ejecuciones de scripts dentro de una misma sesión de usuario. 
df=st.session_state.df = pd.read_excel("PIB_encadenado.xlsx", engine="openpyxl")

# 3. Vista rápida del dataframe
with st.expander("👀 Expandir para ver datos"):
    st.dataframe(df.head(48), use_container_width=True)

#4. Funcionamiento del Dashboard
# Creamos una copia independiente del DataFrame df. 
# si se cambian cosas en work (filtras, renombras, calculas columnas, borras filas…), no no afecta al df original.
work = df.copy()

#Titulo para las variables del eje Y
st.header("📊 Variables a graficar")

# Lista de variables permitidas en Y
VARIABLES= [
    "PIB_nominal", "Prim_nominal", "Sec_nominal", "Ter_nominal",
    "PIB_constante", "Prim_constante", "Sec_constante", "Ter_constante",
    "PIB_encadenado", "Prim_encadenado", "Sec_encadenado", "Ter_encadenado",
    "PIB_tasa_var", "Prim_tasa_var", "Sec_tasa_var", "Ter_tasa_var",
]

# Se sugieren solo las posibles de Y que existen en el Dataframe
columnas = work.select_dtypes(include=[np.number]).columns.tolist() #mira el DataFrame work y selecciona solo las columnas numéricas
candidatos = [c for c in VARIABLES if c in work.columns] #crea una lista con los nombres de VARIABLES que sí existen en el DataFrame work: toma cada c en VARIABLES y se quédqueda ate con ella si c está en las columnas de work

#Desplegable para elegir la variable a graficar
vars_y = st.multiselect(
    "Elige hasta 3 variables (Y)",
    options=candidatos,
    default=candidatos[:1]
)
# Validación: debe elegir al menos 1 variable cuando aún no elige Y
if len(vars_y) == 0:
    st.info("Selecciona al menos una variable para graficar.")
    st.stop()

# Limitación: máximo se pueden elegir 3 variables
if len(vars_y) > 3:
    st.warning("Solo se permiten hasta 3 variables")
    vars_y = vars_y[:3]

#Año y trimestre
#Normalizo tipos de año y trimestre: convierto a numérico; si hay strings, corce= devuelve NaN
df["year"] = pd.to_numeric(df["year"], errors="coerce")
df["quarter"] = pd.to_numeric(df["quarter"], errors="coerce")

# Sidebar de filtros de tiempo: Permite elegir años y trimestres a mostrar
all_years = sorted([int(y) for y in df["year"].unique()])
all_quarters = [1, 2, 3, 4]

st.sidebar.markdown("### Elegir filtros de tiempo")
years = st.sidebar.multiselect(
    "Años", options=all_years, default=all_years
)
quarters = st.sidebar.multiselect(
    "Trimestres", options=all_quarters, default=all_quarters, format_func=lambda q: f"T{q}"
)

# Filtrado de los años y trimestres cuando se eligen
mask = df["year"].isin(years) & df["quarter"].isin(quarters)
df_f = df.loc[mask].copy()
if df_f.empty:
    st.warning("No hay datos para esa combinación de año(s) y trimestre(s).")
    st.stop()

# Ordenar por tiempo y crear etiqueta eje X (Año-Tn)
df_f = df_f.sort_values(["year", "quarter"])
df_f["x_label"] = df_f.apply(lambda r: f"{int(r['year'])}-T{int(r['quarter'])}", axis=1)


#5. Gráfica con Plotly
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
        labels={"x_label": "Año y Trimestre", "value": "Valor", "variable": "Serie"}
    )
st.plotly_chart(fig)



