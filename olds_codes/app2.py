import streamlit as st
import pathlib
import os
from Results import ResultsTable
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# Configurar el diseño de la página
st.set_page_config(page_title="EMTP Results Reporter", layout="wide")

# Instancia de la clase Gui
class Gui:
    def __init__(self):
        self.html_full_file_name = None

    def write_file(self, uploaded_file):
        if uploaded_file:
            self.html_full_file_name = uploaded_file
            st.session_state.html_full_file_name = uploaded_file
            st.success(f"Archivo HTML cargado: {uploaded_file.name}")
        else:
            st.warning("No se seleccionó ningún archivo.")
        return uploaded_file

    def show_html_results(self):
        if self.html_full_file_name:
            results = ResultsTable(self.html_full_file_name, None)
            return results.get_report()
        else:
            st.error("El archivo HTML no ha sido cargado.")
            return None
    
    def show_BusData_results(self):
        if self.html_full_file_name:
            results = ResultsTable(self.html_full_file_name, None)
            return results.get_BusData()
        else:
            st.error("El archivo HTML no ha sido cargado.")
            return None
        
    def show_GenData_results(self):
        if self.html_full_file_name:
            results = ResultsTable(self.html_full_file_name, None)
            return results.get_GenData()
        else:
            st.error("El archivo HTML no ha sido cargado.")
            return None

    def show_LoadData_results(self):
        if self.html_full_file_name:
            results = ResultsTable(self.html_full_file_name, None)
            return results.get_LoadData()
        else:
            st.error("El archivo HTML no ha sido cargado.")
            return None


# Crear la instancia de GUI
gui_instance = Gui()

# Sección de título con fondo
st.markdown("""
    <div class="title-section">
        <h1 class="main-title">EMTP Results Reporter</h1>
        <h2 class="subtitle">CEN - DSLTR (LAB)</h2>
    </div>
""", unsafe_allow_html=True)

st.divider()

# Diseño en dos columnas
col1, col2 = st.columns([2, 1])

# Sección izquierda (Descripción)
with col1:
    st.markdown("""
        ## About this app:
        - **HTML output file analysis**
        - **ECF file exploration**
        - **TBD** (busbars, tlines, switches, synch. gens, etc.)
    """)

# Sección derecha (Cargar archivo HTML)
with col2:
    st.write("### Cargar archivo HTML")
    uploaded_file = st.file_uploader("Arrastra y suelta tu archivo HTML", type=["html"])
    if uploaded_file:
        gui_instance.write_file(uploaded_file)

# Línea divisoria
st.divider()

# Mostrar resultados
st.write("### Opciones:")

# Estilo Tabla 



st.markdown(
    """
    <style>
    .stDataFrame div[data-testid="stVerticalBlock"] div {
        padding-top: 1px !important;
        padding-bottom: 1px !important;
    </style>
    """,
    unsafe_allow_html=True
)


if st.button("Show Report"):
    df = gui_instance.show_html_results()
    if df is not None:
        st.dataframe(df, height=1050, use_container_width=False)
        

# Línea divisoria
st.divider()

# Sección de datos organizados en tres columnas
col3, col4, col5 = st.columns(3)

with col3:
    if st.button("Get Bus Voltages"):
        df = gui_instance.show_BusData_results()
        if df is not None:
            st.dataframe(df, width=1200, height=800)

with col4:
    if st.button("Get Generation Data"):
        df = gui_instance.show_GenData_results()
        if df is not None:
            st.dataframe(df, width=1200, height=800)

with col5:
    if st.button("Get Load Data"):
        df = gui_instance.show_LoadData_results()
        if df is not None:
            st.dataframe(df, width=1200, height=800)

# Línea divisoria
st.divider()

# Otras opciones
if st.button("Más opciones"):
    st.info("Funciones en desarrollo... 🚀")
# Estilos personalizados en CSS
st.markdown("""
    <style>
        /* Fondo de la sección del título */
        .title-section {
            background-color:  #4a4a4a;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            color: white;
        }
        .main-title {
            font-size: 36px;
            font-weight: bold;
        }
        .subtitle {
            font-size: 24px;
        }
        /* Estilo de los botones */
        .stButton>button {
            background-color: #1f4e79;
            color: white;
            border-radius: 8px;
            font-size: 16px;
            padding: 10px 20px;
            width: 100%;
        }
        .stButton>button:hover {
            background-color: #4c709d;
        }
        /* Ajustar el ancho máximo de la página */
        .main {
            max-width: 50px;  /* Establece el ancho máximo de la página */
            margin: auto;  /* Centra la página */
        }
        .appview-container {
            max-width: 60% !important;
            margin: auto !important;   /* Centra el contenido horizontalmente */
        }    
    </style>
""", unsafe_allow_html=True)

