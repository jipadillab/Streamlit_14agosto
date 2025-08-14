import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- Configuración de la página ---
st.set_page_config(
    page_title="EDA con Datos Aleatorios",
    page_icon="📊",
    layout="wide"
)

# --- Título y descripción de la aplicación ---
st.title("📊 Análisis Exploratorio de Datos con Streamlit")
st.markdown("""
Esta aplicación demuestra un análisis exploratorio básico de datos aleatorios utilizando Streamlit.
Podrás ver los datos, estadísticas descriptivas y dos tipos de visualizaciones interactivas:
un **gráfico de barras** y un **gráfico de líneas**.
""")

# --- Generación de datos aleatorios ---
@st.cache_data # Cacha los datos para que no se regeneren en cada recarga
def generate_random_data():
    np.random.seed(42) # Para reproducibilidad

    data_size = 500
    categories = ['A', 'B', 'C', 'D', 'E']
    start_date = pd.to_datetime('2023-01-01')

    data = {
        'Fecha': pd.date_range(start=start_date, periods=data_size, freq='D'),
        'Categoria': np.random.choice(categories, data_size),
        'Valor1': np.random.rand(data_size) * 100,
        'Valor2': np.random.randint(1, 1000, data_size),
        'Valor3': np.random.normal(loc=50, scale=15, size=data_size) # Datos con distribución normal
    }
    df = pd.DataFrame(data)

    # Añadir una columna de "Mes" para el gráfico de barras
    df['Mes'] = df['Fecha'].dt.month_name()
    return df

df = generate_random_data()

# --- Sección de Visualización de Datos Crudos ---
st.header("Datos Crudos")
st.write("Aquí puedes ver las primeras filas de los datos generados aleatoriamente:")
st.dataframe(df.head())

# --- Sección de Estadísticas Descriptivas ---
st.header("Estadísticas Descriptivas")
st.write("Un resumen estadístico de las columnas numéricas:")
st.write(df.describe())

# --- Sección de Gráfico de Barras ---
st.header("Gráfico de Barras: Suma de Valor1 por Categoría")
st.write("Este gráfico muestra la suma de 'Valor1' para cada 'Categoría'.")

# Calcular la suma de Valor1 por Categoría
df_bar = df.groupby('Categoria')['Valor1'].sum().reset_index()

# Crear el gráfico de barras interactivo con Plotly Express
fig_bar = px.bar(
    df_bar,
    x='Categoria',
    y='Valor1',
    title='Suma de Valor1 por Categoría',
    labels={'Categoria': 'Categoría de Producto/Servicio', 'Valor1': 'Suma del Valor Principal'},
    color='Categoria', # Colorear las barras por categoría
    template='plotly_white' # Estilo del gráfico
)
st.plotly_chart(fig_bar, use_container_width=True)


# --- Sección de Gráfico de Líneas ---
st.header("Gráfico de Líneas: Tendencia de Valor2 y Valor3 a lo largo del Tiempo")
st.write("Este gráfico muestra la evolución de 'Valor2' y 'Valor3' a lo largo del tiempo.")

# Para el gráfico de líneas, podemos re-muestrear los datos por día o agruparlos
# Aquí agruparemos por fecha para mostrar una tendencia diaria de promedios
df_line = df.groupby('Fecha')[['Valor2', 'Valor3']].mean().reset_index()

# Crear el gráfico de líneas interactivo con Plotly Express
fig_line = px.line(
    df_line,
    x='Fecha',
    y=['Valor2', 'Valor3'],
    title='Tendencia de Valor2 y Valor3 en el Tiempo',
    labels={'Fecha': 'Fecha', 'value': 'Valor Promedio', 'variable': 'Métrica'},
    template='plotly_white'
)
st.plotly_chart(fig_line, use_container_width=True)

# --- Pie de página ---
st.markdown("---")
st.markdown("Desarrollado con ❤️ y Streamlit.")

