import streamlit as st
import pandas as pd
# Ya no es necesaria la importación de 'math' o 'pathlib' si no se usan más.

# -----------------------------------------------------------------------------
# Funciones útiles
@st.cache_data
def get_gdp_data():
    """Obtiene datos de carreras directamente de un archivo Parquet (más rápido)."""

    # 🚨 NOTA: Se recomienda poner FD_data.parquet en la misma carpeta que el script.
    DATA_FILENAME = 'FD_data.parquet' 
    
    # 1. Usamos pd.read_parquet
    gdp_df = pd.read_parquet(DATA_FILENAME) 

    # 2. Las conversiones a numérico pueden seguir siendo útiles
    # (aunque Parquet generalmente preserva los tipos de datos)
    gdp_df['id_mundial'] = pd.to_numeric(gdp_df['id_mundial'], errors='coerce')
    gdp_df['Punto_acumulado_mundial'] = pd.to_numeric(gdp_df['Punto_acumulado_mundial'], errors='coerce')
    gdp_df['Posicion_acumulada_mundial'] = pd.to_numeric(gdp_df['Posicion_acumulada_mundial'], errors='coerce')

    return gdp_df

gdp_df = get_gdp_data()

# -----------------------------------------------------------------------------
# Dibujar la página

'''
# :checkered_flag: Dashboard de Pilotos

Explora el rendimiento de los pilotos a lo largo del mundial (ID Mundial) y por carrera.
'''

''
''

# -----------------------------------------------------------------------------
# FILTROS Y SLIDERS

# 1. Selector del Mundial (Análogo a 'Year')
min_value = gdp_df['id_mundial'].min()
max_value = gdp_df['id_mundial'].max()

from_mundial, to_mundial = st.slider(
    '¿Qué Mundiales (ID Mundial) te interesan?',
    min_value=min_value,
    max_value=max_value,
    value=[min_value, max_value])

# 2. Multiselect de Pilotos (Análogo a 'Countries')
pilots = gdp_df['Piloto'].unique()

if not len(pilots):
    st.warning("Selecciona al menos un piloto")

selected_pilots = st.multiselect(
    '¿Qué pilotos quieres ver?',
    pilots,
    ['Daniel Flipiardo', 'Michael Schufaker', 'Whisky Raikkonen']) # Ajusta los pilotos por defecto

''
''
''

# -----------------------------------------------------------------------------
# FILTRADO DE DATOS

# Filtramos por Piloto y por el rango de Mundiales (id_mundial)
filtered_gdp_df = gdp_df[
    (gdp_df['Piloto'].isin(selected_pilots))
    & (gdp_df['id_mundial'] <= to_mundial)
    & (from_mundial <= gdp_df['id_mundial'])
]

st.header('Puntos Acumulados a lo largo de las Carreras', divider='gray')

''
# -----------------------------------------------------------------------------
# GRÁFICO DE LÍNEAS

st.line_chart(
    filtered_gdp_df,
    x='Carrera_mundial', # Eje X: La carrera dentro del mundial
    y='Punto_acumulado_mundial', # Eje Y: Puntos
    color='Piloto', # Separación por piloto
)

''
''

# -----------------------------------------------------------------------------
# MÉTRICAS (Rendimiento final)

st.header(f'Clasificación Final del Mundial {to_mundial}', divider='gray')

''

cols = st.columns(4)

# Filtramos solo por el Mundial final seleccionado (to_mundial)
# y la última carrera dentro de ese mundial para obtener el valor final.
final_mundial = gdp_df[gdp_df['id_mundial'] == to_mundial]
last_race_in_final_mundial = final_mundial[final_mundial['Carrera_mundial'] == final_mundial['Carrera_mundial'].max()]

for i, pilot in enumerate(selected_pilots):
    col = cols[i % len(cols)]
    
    with col:
        # Datos del piloto en el mundial final
        pilot_data_end = last_race_in_final_mundial[last_race_in_final_mundial['Piloto'] == pilot]
        
        # Datos del piloto en el mundial inicial (para calcular el delta)
        first_mundial = gdp_df[gdp_df['id_mundial'] == from_mundial]
        # Obtenemos la última carrera del mundial inicial
        last_race_in_first_mundial = first_mundial[first_mundial['Carrera_mundial'] == first_mundial['Carrera_mundial'].max()]
        pilot_data_start = last_race_in_first_mundial[last_race_in_first_mundial['Piloto'] == pilot]

        if not pilot_data_end.empty:
            # Puntos y Posición Acumulada Final
            final_points = pilot_data_end['Punto_acumulado_mundial'].iat[0]
            final_position = pilot_data_end['Posicion_acumulada_mundial'].iat[0]

            delta_value = 'n/a'
            delta_color = 'off'
            
            if not pilot_data_start.empty:
                # Posición Acumulada Inicial
                initial_position = pilot_data_start['Posicion_acumulada_mundial'].iat[0]
                
                # Cálculo de la mejora/empeoramiento de posición entre mundiales (una posición menor es mejor)
                position_change = initial_position - final_position 
                
                if position_change > 0:
                    delta_value = f'+{position_change} pos.'
                    delta_color = 'inverse' # El delta se pinta "verde" porque subir posiciones es positivo
                elif position_change < 0:
                    delta_value = f'{position_change} pos.'
                    delta_color = 'normal' # El delta se pinta "rojo" porque bajar posiciones es negativo
                else:
                    delta_value = '0 pos.'
                    delta_color = 'off'

            st.metric(
                label=f'{pilot} (Puntos Finales)',
                value=f'{final_points:,.0f}',
                delta=delta_value,
                delta_color=delta_color,
                help=f'Cambio en la Posición Acumulada Mundial entre el Mundial {from_mundial} y {to_mundial}'
            )
        else:
            st.metric(label=f'{pilot} (Puntos Finales)', value='n/a', delta='n/a', delta_color='off')
