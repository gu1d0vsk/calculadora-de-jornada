import streamlit as st
import datetime

# --- Configuração da Página e Estilos ---
st.set_page_config(page_title="Calculadora de Horários")

st.markdown("""
    <style>
    .reportview-container .main {
        background-color: #262730;
        color: white;
        max-width: 800px;
        margin: auto;
    }
    .stApp {
        background-color: #262730;
    }
    .st-bu, .st-b5 {
        border-radius: 15px;
        padding: 20px;
    }
    .st-bx, .st-b_ {
        border-radius: 15px;
    }
    .st-dp, .st-dq {
        border-radius: 15px;
    }
    .st-dg, .st-dh {
        color: #f77f00;
        font-weight: bold;
    }
    .st-c4 {
        border: 2px solid #5a5a66;
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 20px;
        width: 100%;
    }
    .st-c5 {
        background-color: #2f2f3f;
    }
    .st-c6 {
        border: 2px solid #5a5a66;
        border-radius: 15px;
    }
    /* Estilo para aumentar a fonte dos campos de texto e labels */
    .stTextInput>div>div>input {
