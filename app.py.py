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
    page_title="Dashboard Operacional | Shipping",
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

# Reduzi o tempo de cache (ttl) para 1 minuto enquanto estamos testando
@st.cache_data(ttl=60) 
def load_real_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # AJUSTE: Nomes exatos das abas respeitando maiúsculas/minúsculas
    df_act = conn.read(worksheet="raw_activity", usecols=list(range(17)))
    df_pck = conn.read(worksheet="packed", usecols=list(range(5)))
    df_idl = conn.read(worksheet="raw_IDLE", usecols=list(range(10))) # Corrigido para IDLE maiúsculo
    df_sla = conn.read(worksheet="SLA_COT", usecols=list(range(7)))
    
    return df_act, df_pck, df_idl, df_sla

@st.cache_data
def load_mock_data():
    dates_act = pd.date_range(end=datetime.now(), periods=5).strftime('%Y-%m-%d').tolist() * 4
    df_act = pd.DataFrame({'data': dates_act, 'operator_id': [f'ops{np.random.randint(100000, 999999)}' for _ in range(20)], 'operator_email': [f'user{i}@email.com' for i in range(20)], 'station_name': ['FBS_MG_Contagem_1'] * 20, 'workstation_name': np.random.choice(['INDIRETOS', 'P1_AU01', 'P1_AU09', 'PS_SHIPP'], 20), 'total_manhr': np.random.uniform(1.0, 8.5, 20).round(1), 'total_shipments': np.random.randint(0, 1500, 20), 'total_received': np.random.randint(0, 10, 20), 'total_packing': np.random.randint(0, 1500, 20), 'operator_name': [f'Operador Simulado {i}' for i in range(20)]})
    dates_pck = pd.date_range(end=datetime.now(), periods=10).strftime('%Y-%m-%d').tolist() * 5
    df_pck = pd.DataFrame({'data': sorted(dates_pck, reverse=True), 'galpao': ['FBS_MG_Contagem_1'] * 50, 'size_type': np.random.choice(['Bulky', 'G', 'M', 'P', 'PP', 'Ultra Bulky'], 50), 'thp': np.random.randint(5, 15000, 50)})
    df_idl = pd.DataFrame({'data': ['2026-07-18'] * 20, 'ops_id': [f'Ops{np.random.randint(100000, 999999)}' for _ in range(20)], 'idle_horas_decimal': np.random.uniform(0.05, 6.0, 20).round(2), 'ops_name': [f'Operador Simulado {i}' for i in range(20)]})
    df_sla = pd.DataFrame({'shipment_id': [f'BR{np.random.randint(1000000000, 9999999999)}' for _ in range(50)], 'last_status': np.random.choice(['SOC_Packing', 'SOC_Packed', 'SOC_LHPacking'], 50, p=[0.4, 0.5, 0.1]), 'created_time_last': pd.date_range(end=datetime.now(), periods=50).strftime('%Y-%m-%d %H:%M:%S')})
    return df_act, df_pck, df_idl, df_sla


st.sidebar.image("https://placehold.co/400x150/1e1e1e/FFF?text=Logistics+Hub", use_column_width=True)
st.sidebar.markdown("---")
st.sidebar.header("⚙️ Navegação e Filtros")

# Lógica de conexão com aviso de erro melhorado
if USAR_DADOS_REAIS:
    try:
        df_activity, df_packed, df_idle, df_sla = load_real_data()
        st.sidebar.success("✅ Conectado ao Google Sheets Oficial!")
    except Exception as e:
        st.sidebar.error("❌ Falha na conexão com a planilha real.")
        st.error(f"DETALHE DO ERRO (Mande isso para correção):\n{e}")
        df_activity, df_packed, df_idle, df_sla = load_mock_data()
else:
    st.sidebar.warning("⚠️ Usando dados simulados. Você não preencheu as senhas (Secrets) na nuvem.")
    if not HAS_GSHEETS:
        st.sidebar.error("Falta instalar a biblioteca: rode `pip install st-gsheets-connection`.")
    df_activity, df_packed, df_idle, df_sla = load_mock_data()


menu_options = ["🏠 Visão Geral", "📊 Produtividade", "📦 Perfil de Carga (Packed)", "⏳ SLA e Ociosidade"]
choice = st.sidebar.radio("Ir para:", menu_options)

st.sidebar.markdown("---")

df_activity['data'] = df_activity['data'].fillna('Sem Data').astype(str)
df_packed['data'] = df_packed['data'].fillna('Sem Data').astype(str)

datas_disponiveis = sorted([d for d in df_activity['data'].unique() if d != 'Sem Data'], reverse=True)
if len(datas_disponiveis) > 0:
    data_selecionada = st.sidebar.selectbox("Selecione a Data de Referência:", datas_disponiveis)
    df_activity_filtered = df_activity[df_activity['data'] == data_selecionada]
    df_packed_filtered = df_packed[df_packed['data'] == data_selecionada]
else:
    data_selecionada = "Nenhuma data"
    df_activity_filtered = df_activity
    df_packed_filtered = df_packed

if choice == "🏠 Visão Geral":
    st.title("🏠 Dashboard Master Operacional")
    st.markdown(f"**Data de Referência:** {data_selecionada}")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_shipments = pd.to_numeric(df_activity_filtered['total_shipments'], errors='coerce').sum()
        st.metric(label="Total Shipments (Dia)", value=f"{total_shipments:,.0f}")
    with col2:
        total_horas = pd.to_numeric(df_activity_filtered['total_manhr'], errors='coerce').sum()
        st.metric(label="Total Horas Trabalhadas", value=f"{total_horas:.1f}h")
    with col3:
        pendentes = len(df_sla[df_sla['last_status'] == 'SOC_Packing'])
        st.metric(label="Pendentes (SOC_Packing)", value=pendentes)
    with col4:
        ociosidade_media = pd.to_numeric(df_idle['idle_horas_decimal'], errors='coerce').mean()
        st.metric(label="Ociosidade Média (h)", value=f"{ociosidade_media:.2f}h")
        
    st.markdown("---")
    
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.subheader("Distribuição de Status (SLA)")
        status_counts = df_sla['last_status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Quantidade']
        fig_status = px.pie(status_counts, values='Quantidade', names='Status', 
                            hole=0.4, color_discrete_sequence=px.colors.sequential.Teal)
        st.plotly_chart(fig_status, use_container_width=True)
        
    with col_chart2:
        st.subheader("Volume por Tamanho (Packed)")
        if not df_packed_filtered.empty:
            df_packed_filtered['thp'] = pd.to_numeric(df_packed_filtered['thp'], errors='coerce')
            size_counts = df_packed_filtered.groupby('size_type')['thp'].sum().reset_index()
            fig_sizes = px.bar(size_counts, x='size_type', y='thp', 
                               color='size_type', text='thp')
            st.plotly_chart(fig_sizes, use_container_width=True)

elif choice == "📊 Produtividade":
    st.title("📊 Análise de Produtividade (Activity)")
    st.markdown("### Top 10 Operadores por Volume")
    
    df_activity_filtered['total_shipments'] = pd.to_numeric(df_activity_filtered['total_shipments'], errors='coerce')
    df_activity_filtered['total_manhr'] = pd.to_numeric(df_activity_filtered['total_manhr'], errors='coerce')
    
    df_ops = df_activity_filtered.groupby('operator_name').agg({'total_shipments': 'sum', 'total_manhr': 'sum'}).reset_index()
    df_ops['produtividade_h'] = (df_ops['total_shipments'] / df_ops['total_manhr']).fillna(0)
    df_top10 = df_ops.sort_values(by='total_shipments', ascending=False).head(10)
    
    fig_top10 = px.bar(df_top10, x='total_shipments', y='operator_name', orientation='h',
                       color='produtividade_h', color_continuous_scale='Viridis',
                       title="Volume Total vs Produtividade por Hora")
    fig_top10.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_top10, use_container_width=True)
    
    st.markdown("### Base Bruta da Data Selecionada")
    st.dataframe(df_activity_filtered, use_container_width=True)

elif choice == "📦 Perfil de Carga (Packed)":
    st.title("📦 Análise do Perfil de Carga")
    df_packed['thp'] = pd.to_numeric(df_packed['thp'], errors='coerce')
    df_packed_trend = df_packed.groupby(['data', 'size_type'])['thp'].sum().reset_index()
    fig_trend = px.area(df_packed_trend, x='data', y='thp', color='size_type')
    st.plotly_chart(fig_trend, use_container_width=True)
    st.dataframe(df_packed_filtered, use_container_width=True)

elif choice == "⏳ SLA e Ociosidade":
    st.title("⏳ Controle de Qualidade e Perdas")
    
    col_idle, col_sla = st.columns([1, 1])
    with col_idle:
        st.subheader("⚠️ Top Ociosidade (Raw Idle)")
        df_idle['idle_horas_decimal'] = pd.to_numeric(df_idle['idle_horas_decimal'], errors='coerce')
        df_idle_sorted = df_idle.sort_values(by='idle_horas_decimal', ascending=False).head(10)
        fig_idle = px.bar(df_idle_sorted, x='idle_horas_decimal', y='ops_name', orientation='h',
                          color='idle_horas_decimal', color_continuous_scale='Reds')
        fig_idle.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_idle, use_container_width=True)
        
    with col_sla:
        st.subheader("📋 Últimos Status (SLA COT)")
        search_shipment = st.text_input("🔍 Buscar Shipment ID (ex: BR...):")
        if search_shipment:
            df_sla['shipment_id'] = df_sla['shipment_id'].astype(str)
            result = df_sla[df_sla['shipment_id'].str.contains(search_shipment, case=False, na=False)]
            st.dataframe(result, use_container_width=True)
        else:
            st.dataframe(df_sla.head(15), use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.caption("Desenvolvido com ❤️ no Streamlit")
