import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
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
    initial_sidebar_state="expanded" 
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
    df_act = pd.DataFrame({'data': dates, 'total_manhr': [8]*20, 'total_shipments': [100]*20})
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
    
    # Mock for DMO tab to calculate target
    df_dmo = pd.DataFrame({
        'A': [''] * 30,
        'B': [''] * 30,
        'C': [''] * 30,
        'D': [1000] * 30 
    })
    
    return df_act, df_pck, df_idl, df_sla, df_prod, df_dmo

st.markdown("""
<style>
    /* Esconde barra padrão do Streamlit para parecer um sistema nativo */
    header {visibility: hidden;}
    .block-container {padding-top: 1rem; padding-bottom: 0rem; max-width: 95%;}
    
    /* Personalização da Barra Lateral - AZUL ESCURO */
    [data-testid="stSidebar"] {
        background-color: #0d1b2a !important; /* Azul escuro profundo */
    }
    
    /* Cor do texto na barra lateral para contraste */
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
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
    
    /* Título do Card */
    div[data-testid="metric-container"] label {
        font-size: 1.5rem !important;
        color: #777 !important;
        font-weight: bold;
        justify-content: center;
        margin-bottom: 10px;
    }
    
    /* Valor numérico no Card */
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
        df_activity, df_packed, df_idle, df_sla, df_prod, df_dmo = load_real_data()
    except Exception as e:
        st.sidebar.error(f"Erro ao carregar dados reais: {e}")
        df_activity, df_packed, df_idle, df_sla, df_prod, df_dmo = load_mock_data()
else:
    st.sidebar.warning("Usando dados simulados.")
    df_activity, df_packed, df_idle, df_sla, df_prod, df_dmo = load_mock_data()

st.sidebar.title("Opções")
st.sidebar.info("Utilize este espaço para filtros secundários ou navegação futura.")

st.markdown('<h1 class="shopee-title">SHIPPING</h1>', unsafe_allow_html=True)

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

# SOMA DO THP
thp_total = pd.to_numeric(df_prod_filtered['total_packing'], errors='coerce').sum()

# CALCULO DA META (Soma da coluna D da aba DMO, linhas 16 a 25. O Pandas usa índice 0, então 15 a 24)
try:
    if not df_dmo.empty and len(df_dmo) >= 25:
        # Pega a coluna D (índice 3, assumindo A=0, B=1, C=2, D=3)
        # Pode variar dependendo de como usecols leu. Vou assumir a 4ª coluna real disponível.
        coluna_meta = df_dmo.columns[3] if len(df_dmo.columns) > 3 else df_dmo.columns[-1]
        meta_dia = pd.to_numeric(df_dmo[coluna_meta].iloc[15:25], errors='coerce').sum()
    else:
        meta_dia = 20000 # Fallback 
except:
    meta_dia = 20000

if meta_dia == 0 or pd.isna(meta_dia):
    meta_dia = 20000 # Prevent division by zero or weird charts

# Outras métricas
pendentes = len(df_sla[df_sla['last_status'] == 'SOC_Packing'])
headcount = df_prod_filtered['operador'].nunique() if not df_prod_filtered.empty else 0

col_met1, col_met_principal, col_met3 = st.columns([1, 1.8, 1])

with col_met1:
    st.metric("Operadores (HC)", f"{headcount}")
with col_met_principal:
    st.metric("THP TOTAL", f"{thp_total:,.0f}")
with col_met3:
    st.metric("Pendente (Packing)", f"{pendentes}")

st.markdown("<br><br>", unsafe_allow_html=True)

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("🔥 Top 5 Produtividade (Packing)")
    if not df_prod_filtered.empty:
        df_prod_filtered = df_prod_filtered.copy()
        df_prod_filtered['total_packing'] = pd.to_numeric(df_prod_filtered['total_packing'], errors='coerce')
        # Filtra nulos e zeros para evitar erro no gráfico de barras
        df_prod_valid = df_prod_filtered[df_prod_filtered['total_packing'] > 0]
        
        if not df_prod_valid.empty:
            top5 = df_prod_valid.nlargest(5, 'total_packing')
            fig1 = px.bar(top5, x='total_packing', y='name', orientation='h', 
                         text='total_packing', color_discrete_sequence=['#EE4D2D'])
            fig1.update_layout(yaxis={'categoryorder':'total ascending'}, xaxis_title="THP", yaxis_title="")
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("Todos os valores de total_packing são zero ou nulos para esta data.")
    else:
        st.info("Sem dados para listar o ranking.")

with col_graf2:
    st.subheader("🎯 Atingimento da Meta")
    
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = thp_total,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Progresso THP", 'font': {'size': 24}},
        delta = {'reference': meta_dia, 'increasing': {'color': "#008000"}, 'decreasing': {'color': "#FF0000"}},
        gauge = {
            'axis': {'range': [None, max(thp_total, meta_dia) * 1.2], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "#EE4D2D"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, meta_dia * 0.5], 'color': '#ffcccb'},
                {'range': [meta_dia * 0.5, meta_dia * 0.9], 'color': '#fffacd'},
                {'range': [meta_dia * 0.9, meta_dia * 1.5], 'color': '#d4edda'}],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': meta_dia}
        }
    ))
    fig_gauge.update_layout(height=350, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_gauge, use_container_width=True)
