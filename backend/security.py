import random
import threading
import streamlit as st # type: ignore

from app.messaging import consume_messages, publish_message
from backend.db import add_user, validate_user

def init_sessions():
    # Inicializar el estado en la primera ejecución
    if "login_step" not in st.session_state:
        st.session_state["login_step"] = 0  # 0: no iniciado, 1: esperando clave

    if "key" not in st.session_state:
        st.session_state["key"] = ""  # Clave de seguridad ingresada por el usuario
        
    if "conection" not in st.session_state:
        st.session_state["conection"] = False
    
    if "conection_up" not in st.session_state:
        st.session_state["conection_up"] = False
        
    if "files" not in st.session_state:
        st.session_state["files"] = None
        
def sign_in(email):
    e = 0
    if email:
        if st.session_state["login_step"] == 0:  # Primer clic
            st.session_state["login_step"] = 1
        elif st.session_state["login_step"] == 1:  # Segundo clic
            if st.session_state["key"]:
                if validate_user(email, st.session_state["key"]):
                    st.session_state["email"] = email
                    e = 7
                else:
                    e = 6
            else:
                e = 5
    else:
        e = 1
    
    return e

def register_user(email):
    e = 0
    if email:
        # Generar una llave de seguridad única
        first3= random.randint(100,999)
        second3= random.randint(100,999)
        security_key = f"{first3}-{second3}"
        if add_user(email, f"{first3*1000+second3}", security_key):
            # Publicar mensaje en RabbitMQ
            try:
                # Usar threading para no bloquear la interfaz de Streamlit
                threading.Thread(target=publish_message, args=(email, security_key)).start()
                threading.Thread(target=consume_messages, daemon=True).start()
                e = 4
            except Exception as e:
                e = 3
        else:
            e = 2
    else:
        e = 1
        
    return e