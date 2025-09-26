import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px    # Gráficos interactivos


# --------------------------------------------
# 1) Lectura y orden de Data
# --------------------------------------------
df = pd.read_excel("PIB_original.xlsx", sheet_name="series", engine="openpyxl")
print("Lectura OK")
df = df.sort_values(by=["year", "quarter"]).reset_index(drop=True)

#Fase de revisión de la data contenido en el archivo de entrada
print("Nulos por columna:\n", df.isnull().sum())
conteo_trimestres = df.groupby("year")["quarter"].nunique()
print("Trimestres por año:\n", conteo_trimestres)

# --------------------------------------------
# 2) Función: encadenado por UNA serie (sector o el PIB)
# --------------------------------------------
def calcular_encadenado_sector(df, col_nominal, col_constante):
    """
    Devuelve una Serie con el encadenado trimestral (Ke) para la serie elegida (PIB, o sectores).
    - col_nominal: columna con la serie a precios corrientes.
    - col_constante: columna con la serie a precios del año anterior o constantes ( en CN -> K)
    Fórmula (como se hace en SCN GT):
        Año base: Ke = K (en el primer año, son iguales pues es el año base)
        Años siguientes: Ke_t = (K_t / c̅_{t-1}) * Ke̅_{t-1} (constante dividido promedio corriente año anterior * promedio encadenado año anterior)
    donde:
        c̅_{t-1} = promedio corriente del año anterior (los 4T) (pendiente si se le añade años en coyuntura)
        Ke̅_{t-1} = promedio encadenado del año anterior (los 4T)
    """
    # Promedios corrientes por año
    prom_corr = df.groupby("year")[col_nominal].mean().to_dict()
    prom_enc = {}  # diccionario para el encadenado

    enc = np.full(len(df), np.nan, dtype=float) #se crea arreglo de Numpy para adicionar todo el encadenado.
    years = sorted(df["year"].unique()) 
    
    #asignación de año de referencia
    base_Year = years[0]   
    for y in years:
        ref = (df["year"] == y) 
        if y == base_Year:
            # Año base: igual a las cifras constantes (a precios del año anterior)
            enc[ref] = df.loc[ref, col_constante].to_numpy(dtype=float)
        else:
            c_prev = prom_corr[y - 1]      # promedio corriente del año anterior
            ke_prev = prom_enc[y - 1]      # promedio encadenado del año anterior
            enc[ref] = (
                df.loc[ref, col_constante].to_numpy(dtype=float) / float(c_prev)
            ) * float(ke_prev)

        # promedio encadenado del año actual (los 4T)
        prom_enc[y] = np.mean(enc[ref])
    return pd.Series(enc, index=df.index)

# --------------------------------------------
# 3) Función: Mapeo de series (para ubicarlas tanto en sus versiones corrientes como constantes ) y cálculo por sector
# --------------------------------------------
series_map = {
    "PIB":  ("PIB_nominal",  "PIB_constante"),
    "Prim": ("Prim_nominal", "Prim_constante"),
    "Sec":  ("Sec_nominal",  "Sec_constante"),
    "Ter":  ("Ter_nominal",  "Ter_constante"),
}

#agregando columnas con sus respectivas etiquetas (iterando el mapa)

for etiqueta, (col_nom, col_cons) in series_map.items():
    # Columna del encadenado a crear
    enc_col = f"{etiqueta}_encadenado"
    # Columna de tasa interanual  a crear
    tasa_col = f"{etiqueta}_tasa_var"

# Encadenado por serie (sector)
    df[enc_col] = calcular_encadenado_sector(df, col_nom, col_cons)

    # Tasa de crecimiento interanual (respecto al mismo trimestre del año anterior)
    df[tasa_col] = (df[enc_col] / df[enc_col].shift(4) * 100) - 100.0
    df[tasa_col] = df[tasa_col].round(2)  

# --------------------------------------------
# 4) exportación a excel (agregando las columnas del encadenado y de las tasas de var.)
# --------------------------------------------

cols_originales = [
    "year", "quarter",
    "PIB_nominal","Prim_nominal","Sec_nominal","Ter_nominal",
    "PIB_constante","Prim_constante","Sec_constante","Ter_constante"]
    
#constantes y tasas de variación

enc_cols  = [f"{s}_encadenado" for s in ["PIB","Prim","Sec","Ter"]]
tasas_cols = [f"{j}_tasa_var" for j in ["PIB","Prim","Sec","Ter"]]

#¿cual es el orden final? cols_original + nuevas columnas
orden_final = cols_originales + enc_cols + tasas_cols
df_final = df[orden_final]

out_file = "PIB_encadenado.xlsx"

#exportar a nuevo excel
with pd.ExcelWriter(out_file, engine="openpyxl", mode="w") as writer:
    df_final.to_excel(writer, sheet_name="resultado", index=False)

    print(f"Archivo guardado: {out_file}")

#-----------------------------------------------------------------------------------------------------------------------
#   DASHBOARD INTERACTIVO

# --------------------------------------------
#1. Configuración de la página de Streamlit
# --------------------------------------------
st.set_page_config(page_title="PIB de Guatemala", page_icon="📈", layout="wide") # Título de la pestaña del navegador
st.title("📈 Valor agregado por sectores económicos, en Guatemala") # Título principal visible en la app

# --------------------------------------------
#2. Carga de archivo de Excel y lo guardo en sesión 
# --------------------------------------------
#Para almacenar un DataFrame de Pandas (u otros objetos similares) en el estado de sesión de Streamlit, 
# permitiendo que ese DataFrame persista y esté disponible entre diferentes interacciones y 
# ejecuciones de scripts dentro de una misma sesión de usuario. 
df=st.session_state.df = pd.read_excel("PIB_encadenado.xlsx", engine="openpyxl")

# --------------------------------------------
# 3. Vista rápida del dataframe
# --------------------------------------------
with st.expander("👀 Expandir para ver datos"):
    st.dataframe(df.head(48), use_container_width=True)

# --------------------------------------------
#4. Funcionamiento del Dashboard
# --------------------------------------------
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

# --------------------------------------------
#5. Gráfica con Plotly
# --------------------------------------------
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
