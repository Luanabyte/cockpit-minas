import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

try:
    from streamlit_gsheets import GSheetsConnection
    HAS_GSHEETS = True
except ImportError:
    HAS_GSHEETS = False

st.set_page_config(
    page_title="Shipping Central | Operações",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed" 
)

def check_secrets():
    try:
        if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
            return True
        return False
    except Exception:
        return False

USAR_DADOS_REAIS = check_secrets() and HAS_GSHEETS

@st.cache_data(ttl="1m") 
def load_real_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    df_act = conn.read(worksheet="raw_activity", usecols=list(range(17)), ttl="1m")
    df_pck = conn.read(worksheet="packed", usecols=list(range(5)), ttl="1m")
    df_idl = conn.read(worksheet="raw_IDLE", usecols=list(range(10)), ttl="1m") 
    df_sla = conn.read(worksheet="SLA_COT", usecols=list(range(7)), ttl="1m")
    
    try:
        df_prod = conn.read(worksheet="prod", usecols=list(range(6)), ttl="1m")
    except Exception:
        try:
            df_prod = conn.read(worksheet="productivy", usecols=list(range(6)), ttl="1m")
        except:
            df_prod = pd.DataFrame(columns=['data', 'operador', 'total_packing', 'total_stage_out', 'total_geral', 'name'])

    try:
        df_dmo = conn.read(worksheet="DMO", usecols=list(range(10)), ttl="1m")
    except Exception:
        df_dmo = pd.DataFrame(columns=['A', 'B', 'C', 'D'])
            
    return df_act, df_pck, df_idl, df_sla, df_prod, df_dmo

@st.cache_data
def load_mock_data():
    dates = ['2026-07-21'] * 20
    df_act = pd.DataFrame({
        'data': dates, 
        'operator_id': [f'ops{i}' for i in range(20)],
        'workstation_name': ['P1_AU01', 'SORT_GER', 'BREAK_MEAL', 'PS_SHIPP', 'AU_02'] * 4,
        'total_manhr': [8]*20, 
        'last_checkout': ['Em aberto', 'Em aberto', 'Em aberto', '2026-07-21 10:00:00', 'Em aberto'] * 4
    })
    df_pck = pd.DataFrame({'data': dates, 'size_type': ['M']*20, 'thp': [100]*20})
    df_idl = pd.DataFrame({'data': dates, 'idle_horas_decimal': [1]*20})
    df_sla = pd.DataFrame({'last_status': ['SOC_Packing']*16 + ['SOC_Packed']*4})
    
    df_prod = pd.DataFrame({
        'data': dates,
        'operador': [f'user{i}@email.com' for i in range(20)],
        'total_packing': np.random.randint(100, 2000, 20),
        'total_stage_out': np.random.randint(0, 500, 20),
        'total_geral': np.random.randint(100, 2500, 20),
        'name': [f'Operador Shopee {i}' for i in range(20)]
    })
    
    df_dmo = pd.DataFrame({
        'A': [''] * 30,
        'B': [''] * 30,
        'C': [''] * 30,
        'D': [1000] * 30 
    })
    
    return df_act, df_pck, df_idl, df_sla, df_prod, df_dmo

# ==========================================
# CSS CUSTOMIZADO (AZUL ESCURO, LARANJA E CARDS)
# ==========================================
st.markdown("""
<style>
    /* Ocultar header padrão */
    header {visibility: hidden;}
    .block-container {padding-top: 1rem; padding-bottom: 0rem; max-width: 98%;}
    
    /* Barra Lateral Azul Escuro */
    [data-testid="stSidebar"] {
        background-color: #0d1b2a !important;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    /* Títulos Principais */
    .shopee-title {
        text-align: center;
        color: #0d1b2a;
        font-family: 'Arial Black', sans-serif;
        font-size: 3.5rem;
        margin-top: -30px;
        margin-bottom: 0px;
        text-transform: uppercase;
        letter-spacing: 4px;
    }
    .cockpit-title {
        text-align: right; 
        color: #EE4D2D;
