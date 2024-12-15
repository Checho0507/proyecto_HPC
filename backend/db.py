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
