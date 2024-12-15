import random
import threading
import time

from fastapi import requests
from backend.files_manager import copy_large_vcf_file, select_vcf_file
import streamlit as st  # type: ignore
import pandas as pd # type: ignore
import os
from backend.db import add_user, validate_user
from backend.security import init_sessions, register_user, sign_in
from concurrent.futures import ThreadPoolExecutor
#from backend .file_manager import upload_file, search_files  # Funciones para manejo de archivos
import streamlit as st
import os
def user_dashboard():
    st.set_page_config(page_title="Portal de Archivos de Investigadores", page_icon="📂")
    
    # Inicializar estados de sesión si no existen
    if 'conection' not in st.session_state:
        st.session_state['conection'] = False
    if 'conection_up' not in st.session_state:
        st.session_state['conection_up'] = False
    if 'selected_files' not in st.session_state:
        st.session_state['selected_file'] = []

    # Menú lateral
    menu = st.sidebar.selectbox("Menú", ["Subir Archivos", "Buscar Archivos"])
    aux = None
    
    if menu == "Subir Archivos":
        st.title("Cargar Archivos VCF 📤")
        
        # Tarjeta de carga de archivos
        st.markdown("### Selección y Carga de Archivos")
        with st.form("load_file"):
            if st.form_submit_button("✅ Seleccionar y Subir Archivo"):
                st.session_state['selected_file']= selected_file = select_vcf_file()
                if selected_file:
                    st.session_state['conection'] = True
                    st.success("✅ Archivo seleccionado correctamente")
                    time.sleep(1)
        
                with st.expander("Archivo Seleccionado"): 
                    st.write(f"📄 {os.path.basename(st.session_state['selected_file'])}")
                time.sleep(1)
                        
                with st.spinner("Subiendo archivo..."):
                    copy_large_vcf_file(selected_file)
                st.success("📦 Archivo cargado con éxito")
                time.sleep(1)
                # Resetear estados
                st.session_state['conection'] = False
                st.session_state['selected_file'] = []
            
        # Información adicional
        st.info("💡 Selecciona el archivo VCF que deseas subir. 5 GB Máximo")

    elif menu == "Buscar Archivos":
        st.title("Buscar Archivos VCF 🔍")
        
        
        # Formulario de búsqueda con tarjeta de diseño
        st.markdown("### Parámetros de Búsqueda")
        
        format_filter = st.text_input("Filtro de Búsqueda:")
        
        # Opciones de resultados
        results_per_page = st.selectbox("Resultados por página:", [10, 25, 50, 100], index=1)
        
        # Botón de búsqueda
        if st.button("🔎 Buscar"):
            with st.spinner("Buscando..."):
                try:
                    search_params = {
                        "Format": format_filter,
                    }
                    results = perform_parallel_search(search_params)
                    
                    if results.empty:
                        st.warning("🚫 No se encontraron resultados.")
                    else:
                        display_results(results, results_per_page)
                except Exception as e:
                    st.error(f"❌ Error al buscar archivos: {e}")
        
        # Información de ayuda
        st.info("💡 Ingresa los parámetros de búsqueda.")
        
def perform_parallel_search(search_params):
    """Estrategia de paralelización para realizar búsquedas en los archivos."""
    files = os.listdir("data")  # Directorio donde se almacenan los archivos
    executor = ThreadPoolExecutor(max_workers=4)
    futures = []
    
    # Enviar búsquedas a múltiples hilos
    for file in files:
        futures.append(executor.submit(search_files, file, search_params))

    # Combinar resultados
    results = pd.concat([future.result() for future in futures if future.result() is not None], ignore_index=True)
    return results

def display_results(dataframe, results_per_page):
    """Mostrar resultados en formato paginado con opciones de ordenación."""
    st.dataframe(dataframe)
    
    # Dividir en páginas
    total_pages = (len(dataframe) // results_per_page) + 1
    page = st.selectbox("Página:", list(range(1, total_pages + 1)), index=0)

    # Mostrar solo la página seleccionada
    start_idx = (page - 1) * results_per_page
    end_idx = start_idx + results_per_page
    paginated_data = dataframe.iloc[start_idx:end_idx]
    
    # Tabla con opciones de ordenación
    st.table(paginated_data.sort_values(by=st.selectbox("Ordenar por:", dataframe.columns)))

# Ruta para almacenar los archivos de los investigadores
FILE_STORAGE_PATH = 'backend/data/'

# Inicia sesiones
def init(e):
    # Configuración de la página
    st.set_page_config(page_title="Portal de Vinos", page_icon="🍇", layout="centered")

    # Título y descripción inicial
    st.title("Bienvenido al Portal de Vinos 🍇")
    st.write("Por favor, elige una opción para continuar.")
    
    init_sessions()

    # Formulario de registro
    email = st.text_input("Correo Electrónico:")
    security = st.empty()  # Campo vacío para mostrar el input de la clave después

    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("Iniciar Sesión"):
            e = sign_in(email)

    with col2:
        if st.button("Registrarse"):
            e = register_user(email)

    # Mostrar el campo de texto para la clave de seguridad después del primer clic
    if st.session_state["login_step"] == 1:
        st.session_state["key"] = security.text_input("Llave de Seguridad:", type="password")

    # Mensajes de error o éxito
    handle_error_messages(e)
    

# Función para manejar mensajes de error
def handle_error_messages(e):
    if e == 1:
        st.error("Por favor, ingrese un correo electrónico.")
    elif e == 2:
        st.error("El correo ya está registrado. Intenta con otro.")
    elif e == 3:
        st.error(f"Error al registrar usuario: {e}")
    elif e == 4:
        st.success(f"Usuario registrado con éxito.")
        st.info("Revisa tu correo para obtener más información.")
    elif e == 5:
        st.error("Por favor, ingresa tu llave de seguridad.")
    elif e == 6:
        st.error("Credenciales incorrectas. Verifica tu correo y llave de seguridad.")
    elif e == 7:
        st.success("Inicio de sesión exitoso. ¡Bienvenido!")
        time.sleep(1)
        st.session_state["page"] = "dashboard"
        st.rerun()

# Función para mostrar y realizar la búsqueda de archivos
def display_file_search():
    search_query = st.text_input("Buscar archivos por:")

    # Definir la variable 'page' correctamente, que controlará la paginación
    page = st.number_input("Página", min_value=1, value=1, step=1)

    page_size = 10  # Número de resultados por página

    # Filtrar los archivos
    if search_query:
        # Utilizar búsqueda paginada en el backend (por ejemplo, en una base de datos o sistema de archivos)
        results = search_files(search_query, page, page_size)
        display_search_results(results, page)

# Mostrar los resultados de búsqueda con paginación y ordenación
def display_search_results(results, page):
    if results:
        df = pd.DataFrame(results)  # Convertir los resultados a un DataFrame

        # Ordenación por columnas
        sort_column = st.selectbox("Ordenar por", df.columns)
        df = df.sort_values(by=[sort_column])

        # Mostrar los resultados de la búsqueda
        st.write(f"Mostrando resultados para la página {page}:")
        st.write(df)

        # Paginación
        total_pages = (len(results) // 10) + 1
        st.write(f"Página {page} de {total_pages}")

# Endpoint para cargar archivos mediante curl
def upload_file(file):
    # Guardar el archivo recibido
    file_path = os.path.join(FILE_STORAGE_PATH, file.name)
    with open(file_path, "wb") as f:
        f.write(file.getbuffer())

    # Agregar el archivo al backend (por ejemplo, base de datos)
    add_user(file_path)

    return f"Archivo {file.name} cargado exitosamente."

# Definir un backend que realice búsqueda de archivos
def search_files(query, page, page_size):
    # Aquí deberías consultar la base de datos o el almacenamiento de archivos
    # Suponiendo que tenemos una lista de archivos simulada
    files = [
        {'Chrom': '1', 'Pos': 100, 'Id': 'abc', 'Ref': 'ref1', 'Alt': 'alt1', 'Qual': 'high', 'Filter': 'filter1', 'Info': 'info1', 'Format': 'format1', 'Outputs': 'output1'},
        {'Chrom': '2', 'Pos': 200, 'Id': 'def', 'Ref': 'ref2', 'Alt': 'alt2', 'Qual': 'low', 'Filter': 'filter2', 'Info': 'info2', 'Format': 'format2', 'Outputs': 'output2'},
        # Más archivos de ejemplo
    ]
    
    # Filtrar los archivos que coincidan con la consulta (esto sería más complejo en un caso real)
    results = [f for f in files if query.lower() in f['Chrom'].lower() or query.lower() in f['Filter'].lower() or query.lower() in f['Info'].lower()]
    
    # Paginación
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    return results[start_idx:end_idx]
