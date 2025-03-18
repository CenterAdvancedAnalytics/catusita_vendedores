import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

# Cargar el archivo CSV
ruta_csv = "catusita_consolidated.csv"  # Ajusta esta ruta según la ubicación de tu archivo CSV
df = pd.read_csv(ruta_csv)

# Convertir columna 'fecha' a datetime
df['fecha'] = pd.to_datetime(df['fecha'])

# Crear columna 'year-month' para agrupar datos por mes y año
df['year-month'] = df['fecha'].dt.strftime('%Y-%m')

# Crear columna de mes en español
df['mes'] = df['fecha'].dt.strftime('%B')
meses_es = {
    "January": "Enero", "February": "Febrero", "March": "Marzo", "April": "Abril",
    "May": "Mayo", "June": "Junio", "July": "Julio", "August": "Agosto",
    "September": "Septiembre", "October": "Octubre", "November": "Noviembre", "December": "Diciembre"
}
df['mes'] = df['mes'].map(meses_es)

# Crear columna de año
df['año'] = df['fecha'].dt.year

# Calcular las fechas límite para los filtros de 3, 6 y 12 meses
hoy = datetime.today()
ayer = hoy - timedelta(days=1)
fecha_3_meses = ayer - pd.DateOffset(months=3)
fecha_6_meses = ayer - pd.DateOffset(months=6)
fecha_12_meses = ayer - pd.DateOffset(months=12)

# Dashboard Streamlit
st.title("Dashboard de Ventas - Catusita")

# Filtros interactivos
lista_vendedores = ["Todos"] + df['nombre_vendedor'].unique().tolist()
vendedor_especifico = st.selectbox('Selecciona un vendedor:', sorted(lista_vendedores))

lista_articulos = ["Todos"] + sorted(df['articulo'].unique().tolist())
articulo_especifico = st.selectbox('Selecciona un artículo:', lista_articulos, index=0)
año_especifico = st.selectbox('Selecciona un año:', sorted(df['año'].unique(), reverse=True))

# Opciones de filtro por meses (solo un toggle activo a la vez)
st.subheader("Filtrar por últimos meses")
col1, col2, col3 = st.columns(3)

filtro_meses = None

with col1:
    if st.button("Últimos 3 meses"):
        filtro_meses = fecha_3_meses

with col2:
    if st.button("Últimos 6 meses"):
        filtro_meses = fecha_6_meses

with col3:
    if st.button("Últimos 12 meses"):
        filtro_meses = fecha_12_meses

# Filtrar el DataFrame según los filtros seleccionados
if vendedor_especifico == "Todos":
    df_filtrado = df.copy()
else:
    df_filtrado = df[df['nombre_vendedor'] == vendedor_especifico]

if articulo_especifico != "Todos":
    df_filtrado = df_filtrado[df_filtrado['articulo'] == articulo_especifico]

# Aplicar filtro de meses si está definido, sino usar el año seleccionado
if filtro_meses:
    df_filtrado = df_filtrado[df_filtrado['fecha'] >= filtro_meses]
    agrupar_por = 'year-month'
else:
    df_filtrado = df_filtrado[df_filtrado['año'] == año_especifico]
    agrupar_por = 'mes'

# Ordenar los datos
if agrupar_por == 'year-month':
    df_filtrado = df_filtrado.sort_values(by='year-month', ascending=True)
else:
    orden_meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                   "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    df_filtrado["mes"] = pd.Categorical(df_filtrado["mes"], categories=orden_meses, ordered=True)
    df_filtrado = df_filtrado.sort_values(by="mes")

# Verificar si hay datos después del filtrado
if df_filtrado.empty:
    st.warning("No hay datos disponibles para el período seleccionado.")
else:
    # Tabla por fuente de suministro
    tabla_fuente = df_filtrado.pivot_table(index='fuente_suministro',
                                           columns=agrupar_por,
                                           values='venta_usd',
                                           aggfunc='sum',
                                           fill_value=0,
                                           observed=False)
    
    # Convertir valores a numéricos antes de sumar
    tabla_fuente = tabla_fuente.apply(pd.to_numeric, errors='coerce')
    tabla_fuente['Total'] = tabla_fuente.sum(axis=1)
    tabla_fuente.loc['Total'] = tabla_fuente.sum()
    
    # Tabla por cliente
    tabla_cliente = df_filtrado.pivot_table(index='nombre_cliente',
                                            columns=agrupar_por,
                                            values='venta_usd',
                                            aggfunc='sum',
                                            fill_value=0,
                                            observed=False)
    
    # Convertir valores a numéricos antes de sumar
    tabla_cliente = tabla_cliente.apply(pd.to_numeric, errors='coerce')
    tabla_cliente['Total'] = tabla_cliente.sum(axis=1)
    tabla_cliente.loc['Total'] = tabla_cliente.sum()
    
    # Formatear solo después de sumar
    tabla_fuente = tabla_fuente.map(lambda x: "{:,}".format(int(x)))
    tabla_cliente = tabla_cliente.map(lambda x: "{:,}".format(int(x)))
    
    # Mostrar resultados en Streamlit
    st.subheader("Tabla por Fuente de Suministro")
    st.dataframe(tabla_fuente)

    st.subheader("Tabla por Cliente")
    st.dataframe(tabla_cliente)