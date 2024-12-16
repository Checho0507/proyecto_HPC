import sqlite3
import streamlit as st

# Configuración de la base de datos
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            security_key TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    
    conn2 = sqlite3.connect('files.db')
    cursor2 = conn2.cursor()
    cursor2.execute('''
        CREATE TABLE IF NOT EXISTS files (
            table_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            file_name TEXT NOT NULL,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            chrom TEXT,
            pos INTEGER,
            id TEXT,
            ref TEXT,
            alt TEXT,
            qual TEXT,
            filter TEXT,
            info TEXT,
            format TEXT,
            outputs TEXT
        )
    ''')
    conn2.commit()
    conn2.close()

def add_user(email, password, security_key):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (email, password, security_key) VALUES (?, ?, ?)", 
                       (email, password, security_key))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def validate_user(email, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
    user = cursor.fetchone()
    conn.close()
    return user

def iniciar_sesion():
    st.subheader("Iniciar sesión")

    email = st.text_input("Correo electrónico", placeholder="Ingrese su correo electrónico")
    password = st.text_input("Contraseña", type="password", placeholder="Ingrese su contraseña")

    if st.button("Iniciar sesión"):
        if email and password:
            user = "user"
            if user:
                st.success("Inicio de sesión exitoso. ¡Bienvenido!")
            else:
                st.error("Credenciales incorrectas. Por favor, verifica tu correo y contraseña.")
        else:
            st.error("Por favor, completa todos los campos.")

def save_vcf_data_to_db(file_name, extracted_data):
    conn = sqlite3.connect('files.db')
    cursor = conn.cursor()
    for data in extracted_data:
        cursor.execute('''
            INSERT INTO files (user_email, file_name, chrom, pos, id, ref, alt, qual, filter, info, format, outputs)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            st.session_state["email"],
            file_name,
            data['chrom'], data['pos'], data['id'], data['ref'], data['alt'],
            data['qual'], data['filter'], data['info'], data['format'], data['outputs']
        ))
    conn.commit()
    conn.close()

def search_files_in_db(query, page, page_size, file_query):
    """
    Realiza una consulta a la base de datos para obtener resultados filtrados en columnas específicas.
    Args:
        query (str): El valor a buscar en las columnas específicas (Chrom, Filter, Info, Format).
        page (int): Número de página para la paginación.
        page_size (int): Número de resultados por página.
    Returns:
        results (list): Lista de resultados filtrados.
        total_results (int): Total de resultados encontrados (sin paginación).
    """
    conn = sqlite3.connect('files.db')
    cursor = conn.cursor()
    query = f"%{query}%"  # Patrón de búsqueda parcial

    # Contar el total de resultados sin paginación
    cursor.execute(f'''
        SELECT COUNT(*)
        FROM files
        WHERE file_name LIKE ? AND user_email LIKE ? AND (chrom LIKE ? OR filter LIKE ? OR info LIKE ? OR format LIKE ?)
    ''', (f"%{file_query}%", f"%{st.session_state['email']}%", query, query, query, query))
    total_results = cursor.fetchone()[0]

    # Aplicar filtro con paginación
    offset = (page - 1) * page_size
    cursor.execute(f'''
        SELECT chrom, pos, id, ref, alt, qual, filter, info, format, outputs
        FROM files
        WHERE file_name LIKE ? AND user_email LIKE ? AND (chrom LIKE ? OR filter LIKE ? OR info LIKE ? OR format LIKE ?)
        LIMIT ? OFFSET ?
    ''', (f"%{file_query}%", f"%{st.session_state['email']}%", query, query, query, query, page_size, offset))

    results = cursor.fetchall()
    conn.close()
    return results, total_results


