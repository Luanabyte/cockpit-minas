import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

try:
    from streamlit_gsheets import GSheetsConnection
    HAS_GSHEETS = True
except ImportError:
    HAS_GSHEETS = False

st.set_page_config(
    page_title="Shipping Central | Operações",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed" # Esconde a barra lateral automaticamente
)

def check_secrets():
    try:
        if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
            return True
        return False
    except Exception:
        return False

USAR_DADOS_REAIS = check_secrets() and HAS_GSHEETS

@st.cache_data(ttl=60) 
def load_real_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    df_act = conn.read(worksheet="raw_activity", usecols=list(range(17)), ttl="1m")
    df_pck = conn.read(worksheet="packed", usecols=list(range(5)), ttl="1m")
    df_idl = conn.read(worksheet="raw_IDLE", usecols=list(range(10)), ttl="1m") 
    df_sla = conn.read(worksheet="SLA_COT", usecols=list(range(7)), ttl="1m")
    
    # Lendo a nova aba (Tentando 'prod' ou 'productivy' baseado nos seus prints)
    try:
        df_prod = conn.read(worksheet="prod", usecols=list(range(6)), ttl="1m")
    except Exception:
        try:
            df_prod = conn.read(worksheet="productivy", usecols=list(range(6)), ttl="1m")
        except:
            df_prod = pd.DataFrame(columns=['data', 'operador', 'total_packing', 'total_stage_out', 'total_geral', 'name'])
            
    return df_act, df_pck, df_idl, df_sla, df_prod

@st.cache_data
def load_mock_data():
    # Gerando dados falsos caso a internet caia ou a permissão falhe
    dates = ['2026-07-21'] * 20
    df_act = pd.DataFrame({'data': dates, 'total_manhr': [8]*20, 'total_shipments': [100]*20})
    df_pck = pd.DataFrame({'data': dates, 'size_type': ['M']*20, 'thp': [100]*20})
    df_idl = pd.DataFrame({'data': dates, 'idle_horas_decimal': [1]*20})
    df_sla = pd.DataFrame({'last_status': ['SOC_Packing']*16 + ['SOC_Packed']*4})
    
    # Mock da aba PROD
    df_prod = pd.DataFrame({
        'data': dates,
        'operador': [f'user{i}@email.com' for i in range(20)],
        'total_packing': np.random.randint(100, 2000, 20),
        'total_stage_out': np.random.randint(0, 500, 20),
        'total_geral': np.random.randint(100, 2500, 20),
        'name': [f'Operador Shopee {i}' for i in range(20)]
    })
    return df_act, df_pck, df_idl, df_sla, df_prod

st.markdown("""
<style>
    /* Esconde barra padrão do Streamlit para parecer um sistema nativo */
    header {visibility: hidden;}
    .block-container {padding-top: 1rem; padding-bottom: 0rem; max-width: 95%;}
    
    /* Título SHIPPING no Topo */
    .shopee-title {
        text-align: center;
        color: #EE4D2D;
        font-family: 'Arial Black', sans-serif;
        font-size: 5rem;
        margin-top: -60px;
        margin-bottom: -10px;
        text-transform: uppercase;
        letter-spacing: 4px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Customização Extrema dos Cards de Métricas */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #f0f0f0;
        border-top: 10px solid #EE4D2D;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0px 8px 16px rgba(0,0,0,0.08);
        text-align: center;
        transition: transform 0.3s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: scale(1.03);
        box-shadow: 0px 12px 20px rgba(238,77,45,0.2);
    }
    
    /* Título do Card (Ex: THP TOTAL) */
    div[data-testid="metric-container"] label {
        font-size: 1.5rem !important;
        color: #777 !important;
        font-weight: bold;
        justify-content: center;
        margin-bottom: 10px;
    }
    
    /* Valor numérico gigante no Card */
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        font-size: 5.5rem !important;
        color: #EE4D2D !important;
        font-weight: 900 !important;
        justify-content: center;
        line-height: 1.1;
    }
    
    /* Centralizar a caixa de Data no meio da tela */
    .stSelectbox > div {
        max-width: 300px;
        margin: 0 auto;
        border: 2px solid #EE4D2D;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

if USAR_DADOS_REAIS:
    try:
        df_activity, df_packed, df_idle, df_sla, df_prod = load_real_data()
    except Exception as e:
        st.error("Falha na conexão com a planilha real. Mostrando dados simulados.")
        df_activity, df_packed, df_idle, df_sla, df_prod = load_mock_data()
else:
    df_activity, df_packed, df_idle, df_sla, df_prod = load_mock_data()

# Renderização do Título Master
st.markdown('<h1 class="shopee-title">SHIPPING</h1>', unsafe_allow_html=True)

# Tratamento da Data (pegando da aba prod)
df_prod['data'] = df_prod['data'].fillna('Sem Data').astype(str)
datas_disponiveis = sorted([d for d in df_prod['data'].unique() if d != 'Sem Data' and d.strip() != ''], reverse=True)

col_vazia1, col_filtro, col_vazia2 = st.columns([1, 1, 1])
with col_filtro:
    if len(datas_disponiveis) > 0:
        data_selecionada = st.selectbox("Selecione a Data:", datas_disponiveis, label_visibility="collapsed")
    else:
        st.warning("Nenhuma data encontrada na aba prod.")
        data_selecionada = "Nenhuma"

st.markdown("<br><br>", unsafe_allow_html=True)

df_prod_filtered = df_prod[df_prod['data'] == data_selecionada]

# SOMA DO THP: Pegando a coluna 'total_packing' da sua aba 'prod'
thp_total = pd.to_numeric(df_prod_filtered['total_packing'], errors='coerce').sum()

# Outras métricas
pendentes = len(df_sla[df_sla['last_status'] == 'SOC_Packing'])
headcount = df_prod_filtered['operador'].nunique() if not df_prod_filtered.empty else 0

col_met1, col_met_principal, col_met3 = st.columns([1, 1.8, 1])

with col_met1:
    st.metric("Operadores (HC)", f"{headcount}")
with col_met_principal:
    # Este é o card gigante no centro da tela
    st.metric("THP TOTAL", f"{thp_total:,.0f}")
with col_met3:
    st.metric("Pendente (Packing)", f"{pendentes}")

st.markdown("<br><br>", unsafe_allow_html=True)

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("🔥 Top 5 Produtividade (Packing)")
    if not df_prod_filtered.empty:
        df_prod_filtered['total_packing'] = pd.to_numeric(df_prod_filtered['total_packing'], errors='coerce')
        top5 = df_prod_filtered.nlargest(5, 'total_packing')
        fig1 = px.bar(top5, x='total_packing', y='name', orientation='h', 
                     text='total_packing', color_discrete_sequence=['#EE4D2D'])
        fig1.update_layout(yaxis={'categoryorder':'total ascending'}, xaxis_title="THP", yaxis_title="")
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("Sem dados para listar o ranking.")

with col_graf2:
    st.subheader("📋 Gargalo Atual (SLA)")
    status_counts = df_sla['last_status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Quantidade']
    fig2 = px.pie(status_counts, values='Quantidade', names='Status', hole=0.6,
                  color_discrete_sequence=['#EE4D2D', '#FF8C00', '#FFDAB9'])
    st.plotly_chart(fig2, use_container_width=True)
