import pandas as pd
import streamlit as st

# Cargar el archivo CSV
ruta_csv = "catusita_consolidated.csv"  # Ajusta esta ruta según la ubicación de tu archivo CSV
df = pd.read_csv(ruta_csv)

# Convertir columna 'fecha' a datetime
df['fecha'] = pd.to_datetime(df['fecha'])

# Extraer año y mes
df['año'] = df['fecha'].dt.year
df['mes'] = df['fecha'].dt.strftime('%B')

# Orden correcto de meses
orden_meses = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']

# Dashboard Streamlit
st.title("Dashboard de Ventas - Catusita")

# Articulos unicos incluidos Todos
lista_articulos = df['nombre_vendedor'].unique().tolist()
lista_articulos.append("Todos")

# Filtros interactivos
vendedor_especifico = st.selectbox('Selecciona un vendedor:', sorted(df['nombre_vendedor'].unique()))
articulo_especifico = st.selectbox('Selecciona un artículo:', sorted(lista_articulos))
año_especifico = st.selectbox('Selecciona un año:', sorted(df['año'].unique()))

# Filtrar el DataFrame
if articulo_especifico == "Todos":
    df_filtrado = df[(df['nombre_vendedor'] == vendedor_especifico) &
                    (df['año'] == año_especifico)]
else:
        df_filtrado = df[(df['nombre_vendedor'] == vendedor_especifico) &
                    (df['articulo'] == articulo_especifico) &
                    (df['año'] == año_especifico)]

# Tabla por fuente_suministro
tabla_fuente = df_filtrado.pivot_table(index='fuente_suministro',
                                       columns='mes',
                                       values='venta_usd',
                                       aggfunc='sum',
                                       fill_value=0).reindex(columns=orden_meses, fill_value=0)

# Tabla por cliente
tabla_cliente = df_filtrado.pivot_table(index='nombre_cliente',
                                        columns='mes',
                                        values='venta_usd',
                                        aggfunc='sum',
                                        fill_value=0).reindex(columns=orden_meses, fill_value=0)

# Mostrar resultados en Streamlit
st.subheader("Tabla por Fuente de Suministro")
st.dataframe(tabla_fuente)

st.subheader("Tabla por Cliente")
st.dataframe(tabla_cliente)
