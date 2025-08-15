import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# --- Configuración de la página de Streamlit ---
st.set_page_config(
    page_title="Análisis Agrícola en Colombia 🇨🇴",
    page_icon="👨‍🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Título y descripción de la aplicación ---
st.title("👨‍🌾 Análisis Exploratorio de Datos Agrícolas en Colombia")
st.markdown("""
Bienvenido a esta plataforma interactiva para explorar datos simulados del sector agrícola en Colombia.
Utiliza los filtros en la barra lateral izquierda para ajustar los datos y las visualizaciones.
""")

# --- Generación de datos aleatorios para la agricultura en Colombia ---
@st.cache_data # Cacha los datos para que no se regeneren en cada recarga
def generate_agricultural_data(num_samples=500):
    np.random.seed(42) # Para reproducibilidad

    departamentos = [
        "Antioquia", "Boyacá", "Cundinamarca", "Valle del Cauca", "Meta",
        "Córdoba", "Santander", "Nariño", "Tolima", "Huila"
    ]
    productos = [
        "Café", "Plátano", "Papa", "Arroz", "Maíz",
        "Caña de Azúcar", "Palma de Aceite", "Aguacate", "Cacao", "Flores"
    ]
    tipos_suelo = ["Franco", "Arcilloso", "Arenoso", "Limioso"]

    data = {
        'Fecha': pd.to_datetime(pd.date_range(start='2020-01-01', periods=num_samples, freq='D').to_list() * (num_samples // len(pd.date_range(start='2020-01-01', periods=num_samples, freq='D')) + 1))[:num_samples],
        'Departamento': np.random.choice(departamentos, num_samples),
        'Producto': np.random.choice(productos, num_samples),
        'HectareasCultivadas': np.random.randint(50, 5000, num_samples), # Hectáreas cultivadas
        'RendimientoTon_Ha': np.random.uniform(0.5, 30.0, num_samples).round(2), # Toneladas por hectárea
        'Precipitacion_mm': np.random.uniform(50, 400, num_samples).round(1), # Precipitación en mm
        'Temperatura_C': np.random.uniform(18.0, 32.0, num_samples).round(1), # Temperatura en grados Celsius
        'CostoSemilla_USD': np.random.uniform(500, 5000, num_samples).round(2), # Costo de semilla por cultivo
        'CostoFertilizante_USD': np.random.uniform(300, 3000, num_samples).round(2), # Costo de fertilizante por cultivo
        'IngresoVenta_USD': np.random.uniform(2000, 25000, num_samples).round(2), # Ingreso por venta del cultivo
        'TipoSuelo': np.random.choice(tipos_suelo, num_samples),
        'Productividad_USD_Ha': 0 # Inicializar
    }
    df = pd.DataFrame(data)

    # Calcular la productividad
    df['Productividad_USD_Ha'] = (df['IngresoVenta_USD'] - df['CostoSemilla_USD'] - df['CostoFertilizante_USD']) / df['HectareasCultivadas']
    df['Productividad_USD_Ha'] = df['Productividad_USD_Ha'].apply(lambda x: max(0, x)).round(2) # Asegurar que no sea negativo

    return df

df_original = generate_agricultural_data(num_samples=500)
df = df_original.copy() # Usar una copia para las operaciones de filtrado

# --- Barra Lateral para Controles ---
st.sidebar.header("⚙️ Controles de la Aplicación")

# Filtro por fecha
min_date = df['Fecha'].min().date()
max_date = df['Fecha'].max().date()

date_range = st.sidebar.slider(
    "Selecciona Rango de Fechas",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM-DD"
)
df = df[(df['Fecha'].dt.date >= date_range[0]) & (df['Fecha'].dt.date <= date_range[1])]

# Filtros Categóricos
st.sidebar.subheader("Filtros Categóricos")
selected_departamentos = st.sidebar.multiselect(
    "Selecciona Departamento(s)",
    options=df_original['Departamento'].unique().tolist(),
    default=df_original['Departamento'].unique().tolist()
)
df = df[df['Departamento'].isin(selected_departamentos)]

selected_productos = st.sidebar.multiselect(
    "Selecciona Producto(s)",
    options=df_original['Producto'].unique().tolist(),
    default=df_original['Producto'].unique().tolist()
)
df = df[df['Producto'].isin(selected_productos)]

selected_suelos = st.sidebar.multiselect(
    "Selecciona Tipo de Suelo(s)",
    options=df_original['TipoSuelo'].unique().tolist(),
    default=df_original['TipoSuelo'].unique().tolist()
)
df = df[df['TipoSuelo'].isin(selected_suelos)]


# Filtros Numéricos (Sliders)
st.sidebar.subheader("Filtros Numéricos")

numerical_cols = [
    'HectareasCultivadas', 'RendimientoTon_Ha', 'Precipitacion_mm',
    'Temperatura_C', 'CostoSemilla_USD', 'CostoFertilizante_USD',
    'IngresoVenta_USD', 'Productividad_USD_Ha'
]

filters = {}
for col in numerical_cols:
    if not df[col].empty: # Asegurarse de que la columna no esté vacía después de filtros categóricos
        min_val, max_val = float(df_original[col].min()), float(df_original[col].max())
        step = 0.1 if col in ['RendimientoTon_Ha', 'Precipitacion_mm', 'Temperatura_C', 'Productividad_USD_Ha'] else 1.0

        if min_val == max_val: # Manejar caso donde todos los valores son iguales
            st.sidebar.write(f"**{col}:** {min_val:.2f}")
            filters[col] = (min_val, max_val)
        else:
            current_range = st.sidebar.slider(
                f"Rango de {col}",
                min_value=min_val,
                max_value=max_val,
                value=(min_val, max_val),
                step=step,
                format="%.2f" if col in ['RendimientoTon_Ha', 'Precipitacion_mm', 'Temperatura_C', 'Productividad_USD_Ha'] else "%.0f"
            )
            filters[col] = current_range

for col, (min_val, max_val) in filters.items():
    df = df[(df[col] >= min_val) & (df[col] <= max_val)]


# --- Opciones de Visualización ---
st.sidebar.subheader("🎨 Opciones de Visualización")
chart_type = st.sidebar.selectbox(
    "Selecciona Tipo de Gráfico",
    ("Barras", "Líneas", "Dispersión")
)

# Columnas disponibles para los ejes Y
y_options = [col for col in numerical_cols if col in df.columns]

# Seleccionar eje Y
y_axis = st.sidebar.selectbox(
    "Métrica para el Eje Y",
    options=y_options,
    index=y_options.index('IngresoVenta_USD') if 'IngresoVenta_USD' in y_options else 0
)

# Seleccionar columna para el color
color_options = ['Ninguno'] + [col for col in df.columns if df[col].dtype == 'object' or col in ['Departamento', 'Producto', 'TipoSuelo']]
color_by = st.sidebar.selectbox(
    "Colorear por",
    options=color_options
)
color_arg = color_by if color_by != 'Ninguno' else None

# Opciones adicionales para gráfico de dispersión
size_by_options = ['Ninguno'] + numerical_cols
size_by_arg = None
if chart_type == "Dispersión":
    size_by = st.sidebar.selectbox(
        "Tamaño de los puntos por (solo Dispersión)",
        options=size_by_options
    )
    size_by_arg = size_by if size_by != 'Ninguno' else None

# --- Contenido Principal de la Aplicación ---

# Mostrar/Ocultar datos crudos
show_data = st.checkbox("Mostrar Datos Crudos", value=False)
if show_data:
    st.header("📋 Datos Crudos Filtrados")
    st.write(f"Mostrando las primeras 10 filas de {len(df)} registros después de los filtros.")
    st.dataframe(df.head(10))
    if df.empty:
        st.warning("No hay datos que coincidan con los filtros seleccionados.")

# Mostrar/Ocultar estadísticas descriptivas
show_stats = st.checkbox("Mostrar Estadísticas Descriptivas", value=False)
if show_stats:
    st.header("📈 Estadísticas Descriptivas Filtradas")
    if not df.empty:
        st.write(df.describe().T)
    else:
        st.warning("No hay datos para mostrar estadísticas.")

# --- Visualización Dinámica ---
st.header(f"📊 Gráfico Dinámico: {chart_type}")

if df.empty:
    st.warning("No se pueden generar gráficos. Por favor, ajusta los filtros para obtener datos.")
else:
    if chart_type == "Barras":
        # Para barras, agrupamos por una categoría y sumamos el valor Y
        if color_arg: # Si hay una columna para colorear, usamos la que elija el usuario, si no, 'Departamento'
            x_axis_bar = color_arg
        else:
            x_axis_bar = 'Departamento' # Por defecto agrupamos por Departamento

        # Asegurarse de que el eje x para barras sea una columna categórica
        if df[x_axis_bar].dtype not in ['object', 'category']:
            st.warning(f"La columna '{x_axis_bar}' no es adecuada para el eje X de un gráfico de barras. Usando 'Departamento'.")
            x_axis_bar = 'Departamento'


        df_agg = df.groupby(x_axis_bar)[y_axis].sum().reset_index()
        fig = px.bar(
            df_agg,
            x=x_axis_bar,
            y=y_axis,
            title=f'{y_axis} por {x_axis_bar}',
            labels={x_axis_bar: x_axis_bar, y_axis: y_axis},
            color=x_axis_bar, # Colorear por la misma categoría del eje X
            template='plotly_white',
            hover_data=df_agg.columns
        )

    elif chart_type == "Líneas":
        # Para líneas, agrupamos por fecha y calculamos el promedio
        df_line = df.groupby('Fecha')[y_axis].mean().reset_index()
        fig = px.line(
            df_line,
            x='Fecha',
            y=y_axis,
            title=f'Tendencia de {y_axis} en el Tiempo',
            labels={'Fecha': 'Fecha', y_axis: y_axis},
            color_discrete_sequence=px.colors.qualitative.Plotly if color_arg is None else None, # Usa colores por defecto si no hay color_arg
            color=color_arg if color_arg else None, # Solo usa color_arg si no es None
            template='plotly_white',
            hover_data=df_line.columns
        )

    elif chart_type == "Dispersión":
        # Eje X por defecto para dispersión
        x_axis_scatter = st.selectbox(
            "Métrica para el Eje X (Dispersión)",
            options=[col for col in numerical_cols if col != y_axis and col in df.columns],
            index=numerical_cols.index('HectareasCultivadas') if 'HectareasCultivadas' in numerical_cols else 0
        )
        fig = px.scatter(
            df,
            x=x_axis_scatter,
            y=y_axis,
            title=f'{y_axis} vs {x_axis_scatter}',
            labels={x_axis_scatter: x_axis_scatter, y_axis: y_axis},
            color=color_arg,
            size=size_by_arg, # Aplica el tamaño si se seleccionó
            hover_data=df.columns,
            template='plotly_white'
        )

    st.plotly_chart(fig, use_container_width=True)

# --- Pie de página ---
st.markdown("---")
st.markdown("Desarrollado con 💚 y Streamlit para el análisis agrícola en Colombia.")
