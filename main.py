import streamlit as st # type: ignore

from backend.db import init_db
from frontend.init_page import init, user_dashboard

if "page" not in st.session_state:
    st.session_state["page"] = "init"
    #Inicializar base de datos
    init_db()
    
if st.session_state["page"] == "init":
    init(0)
    
    
elif st.session_state["page"] == "dashboard":
    user_dashboard()