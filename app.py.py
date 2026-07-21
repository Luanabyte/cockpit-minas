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
        font-weight: 900; 
        font-size: 1.5rem; 
        letter-spacing: 2px; 
        margin-top: 10px;
    }
    
    /* Customização dos Cards Superiores (st.metric) */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border-left: 6px solid #EE4D2D;
        border-radius: 8px;
        padding: 15px 20px;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.05);
    }
    div[data-testid="metric-container"] label {
        font-size: 1.1rem !important;
        color: #0d1b2a !important;
        font-weight: 700;
        margin-bottom: 5px;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        font-size: 3rem !important;
        color: #0d1b2a !important;
        font-weight: 900 !important;
    }
    
    /* Mini-Cards de Alocação (Pessoinhas) */
    .alloc-container {
        display: flex;
        justify-content: space-between;
        gap: 15px;
        margin-top: 15px;
        margin-bottom: 25px;
    }
    .alloc-card {
        background-color: #0d1b2a;
        color: #ffffff;
        flex: 1;
        text-align: center;
        padding: 10px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 1.2rem;
        border-bottom: 4px solid #EE4D2D;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.1);
    }
    .alloc-number {
        font-size: 1.5rem;
        color: #EE4D2D;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# CARREGAMENTO DE DADOS
# ==========================================
if USAR_DADOS_REAIS:
    try:
        df_activity, df_packed, df_idle, df_sla, df_prod, df_dmo = load_real_data()
    except Exception as e:
        st.sidebar.error(f"Erro de permissão: Compartilhe a planilha com o e-mail do Service Account. Detalhe: {e}")
        df_activity, df_packed, df_idle, df_sla, df_prod, df_dmo = load_mock_data()
else:
    st.sidebar.warning("⚠️ Usando dados simulados. Preencha as senhas na nuvem.")
    df_activity, df_packed, df_idle, df_sla, df_prod, df_dmo = load_mock_data()

st.sidebar.title("Opções")

df_prod['data'] = df_prod['data'].fillna('Sem Data').astype(str)
datas_disponiveis = sorted([d for d in df_prod['data'].unique() if d != 'Sem Data' and d.strip() != ''], reverse=True)

if len(datas_disponiveis) > 0:
    data_selecionada = st.sidebar.selectbox("Selecione a Data:", datas_disponiveis)
else:
    st.sidebar.warning("Nenhuma data encontrada na aba prod.")
    data_selecionada = "Nenhuma"

# ==========================================
# TOPO DA PÁGINA (TÍTULOS)
# ==========================================
col_topo1, col_topo2, col_topo3 = st.columns([1, 2, 1])
with col_topo2:
    st.markdown('<h1 class="shopee-title">SHIPPING</h1>', unsafe_allow_html=True)
with col_topo3:
    st.markdown('<div class="cockpit-title">COCKPIT</div>', unsafe_allow_html=True)


# ==========================================
# CÁLCULOS DAS MÉTRICAS GERAIS
# ==========================================
df_prod_filtered = df_prod[df_prod['data'] == data_selecionada]
thp_total = pd.to_numeric(df_prod_filtered['total_packing'], errors='coerce').sum()

# Meta DMO
try:
    if not df_dmo.empty and len(df_dmo) >= 25:
        coluna_meta = df_dmo.columns[3] if len(df_dmo.columns) > 3 else df_dmo.columns[-1]
        meta_dia = pd.to_numeric(df_dmo[coluna_meta].iloc[15:25], errors='coerce').sum()
    else:
        meta_dia = 20000 
except:
    meta_dia = 20000
if pd.isna(meta_dia) or meta_dia == 0: meta_dia = 20000

# Pendentes Packing
pendentes = len(df_sla[df_sla['last_status'] == 'SOC_Packing'])

# ==========================================
# CÁLCULOS DE ALOCAÇÃO E HORAS (Aba raw_activity)
# ==========================================
df_activity['data'] = df_activity['data'].astype(str)
df_act_filtered = df_activity[df_activity['data'] == data_selecionada].copy()

# Total de Horas Trabalhadas no dia (Soma da Coluna J = total_manhr)
horas_trabalhadas = pd.to_numeric(df_act_filtered.get('total_manhr', 0), errors='coerce').sum()

# Filtro de colaboradores "Em aberto" (Ativos agora)
if 'last_checkout' in df_act_filtered.columns:
    ativos_mask = df_act_filtered['last_checkout'].astype(str).str.strip().str.upper() == 'EM ABERTO'
    df_ativos = df_act_filtered[ativos_mask]
else:
    df_ativos = pd.DataFrame()

# Remove duplicatas caso o mesmo operador apareça logado duas vezes
if not df_ativos.empty and 'operator_id' in df_ativos.columns:
    df_ativos = df_ativos.drop_duplicates(subset=['operator_id'])

# Contagem por Workstation (Alocação)
direto, indireto, improdutivo, pstl = 0, 0, 0, 0

if 'workstation_name' in df_ativos.columns:
    for ws in df_ativos['workstation_name'].dropna():
        ws_str = str(ws).strip().upper()
        
        if ws_str.startswith('P1_') or ws_str.startswith('AU_'):
            direto += 1
        elif ws_str in ['SORT_GER', 'SORT_ASM']:
            indireto += 1
        elif ws_str in ['BREAK_MEAL', 'OUTHERS', 'FIVE_S', 'BREAK_MEAL ']:
            improdutivo += 1
        elif ws_str == 'PS_SHIPP':
            pstl += 1

# ==========================================
# EXIBIÇÃO: CARDS KPI SUPERIORES
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)
col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

with col_kpi1:
    st.metric("📦 THP TOTAL", f"{thp_total:,.0f}")
with col_kpi2:
    st.metric("🎯 META DO DIA", f"{meta_dia:,.0f}")
with col_kpi3:
    st.metric("⏱️ HORAS TRABALHADAS", f"{horas_trabalhadas:,.1f}h")
with col_kpi4:
    st.metric("⚠️ PENDENTE (PACKING)", f"{pendentes}")

# ==========================================
# EXIBIÇÃO: MINI-CARDS DE ALOCAÇÃO (PESSOINHAS)
# ==========================================
html_alloc = f"""
<div class="alloc-container">
    <div class="alloc-card">
        DIRETO<br>
        👥 <span class="alloc-number">{direto}</span>
    </div>
    <div class="alloc-card">
        INDIRETO<br>
        👥 <span class="alloc-number">{indireto}</span>
    </div>
    <div class="alloc-card">
        IMPRODUTIVO<br>
        👥 <span class="alloc-number">{improdutivo}</span>
    </div>
    <div class="alloc-card">
        PS / TL<br>
        👥 <span class="alloc-number">{pstl}</span>
    </div>
</div>
"""
st.markdown(html_alloc, unsafe_allow_html=True)


# ==========================================
# GRÁFICOS INFERIORES
# ==========================================
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.markdown('<h3 style="color: #0d1b2a;">🔥 Top 5 Produtividade</h3>', unsafe_allow_html=True)
    if not df_prod_filtered.empty:
        # Copiando e limpando os dados com rigor para evitar Crash
        df_chart = df_prod_filtered.copy()
        df_chart['total_packing'] = pd.to_numeric(df_chart['total_packing'], errors='coerce')
        df_chart = df_chart.dropna(subset=['total_packing'])
        df_chart = df_chart[df_chart['total_packing'] > 0]
        
        if 'name' not in df_chart.columns:
            df_chart['name'] = df_chart.get('operador', 'Desconhecido')
        df_chart['name'] = df_chart['name'].astype(str)
        
        if not df_chart.empty:
            top5 = df_chart.nlargest(5, 'total_packing')
            fig1 = px.bar(top5, x='total_packing', y='name', orientation='h', 
                          text_auto='.0f', color_discrete_sequence=['#EE4D2D']) # Laranja Shopee
            fig1.update_layout(
                yaxis={'categoryorder':'total ascending'}, 
                xaxis_title="", yaxis_title="",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=10, b=0)
            )
            # Escurece as letras do eixo Y
            fig1.update_yaxes(tickfont=dict(color="#0d1b2a", size=12))
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("Valores zerados ou inválidos.")
    else:
        st.info("Sem dados para listar o ranking.")

with col_graf2:
    st.markdown('<h3 style="color: #0d1b2a;">🎯 Atingimento da Meta</h3>', unsafe_allow_html=True)
    
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = thp_total,
        domain = {'x': [0, 1], 'y': [0, 1]},
        delta = {'reference': meta_dia, 'increasing': {'color': "#0d1b2a"}, 'decreasing': {'color': "#EE4D2D"}},
        gauge = {
            'axis': {'range': [None, max(thp_total, meta_dia) * 1.2], 'tickwidth': 1, 'tickcolor': "#0d1b2a"},
            'bar': {'color': "#EE4D2D"}, # Laranja Shopee
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#0d1b2a",
            'steps': [
                {'range': [0, meta_dia * 0.5], 'color': '#f8f9fa'},
                {'range': [meta_dia * 0.5, meta_dia * 0.9], 'color': '#e9ecef'},
                {'range': [meta_dia * 0.9, meta_dia * 1.5], 'color': '#dee2e6'}],
            'threshold': {
                'line': {'color': "#0d1b2a", 'width': 6}, # Azul Escuro
                'thickness': 0.8,
                'value': meta_dia}
        }
    ))
    fig_gauge.update_layout(
        height=320, 
        margin=dict(l=20, r=20, t=30, b=20),
        font=dict(color="#0d1b2a")
    )
    st.plotly_chart(fig_gauge, use_container_width=True)
```eof

Eu configurei a caixa preta do `[data-testid="stSidebar"]` para `#0d1b2a`, e os cards de alocação também carregam esse azul escuro premium com as bordas em laranja (`#EE4D2D`).

Faça o teste e me conte se as caixinhas de alocação bateram com as pessoas que estão em operação agora no seu galpão!
