import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# Configuração inicial da página - DEVE SER O PRIMEIRO COMANDO STREAMLIT
st.set_page_config(
    page_title="Dashboard Operacional | Shipping",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Na versão final, substituiremos essas funções pela conexão real com o GSheets.
@st.cache_data
def load_mock_raw_activity():
    """Simula os dados da aba raw_activity (Produtividade)"""
    dates = pd.date_range(end=datetime.now(), periods=5).strftime('%Y-%m-%d').tolist() * 4
    data = {
        'data': dates,
        'operator_id': [f'ops{np.random.randint(100000, 999999)}' for _ in range(20)],
        'operator_email': [f'user{i}@email.com' for i in range(20)],
        'station_name': ['FBS_MG_Contagem_1'] * 20,
        'workstation_name': np.random.choice(['INDIRETOS', 'P1_AU01', 'P1_AU09', 'PS_SHIPP'], 20),
        'total_manhr': np.random.uniform(1.0, 8.5, 20).round(1),
        'total_shipments': np.random.randint(0, 1500, 20),
        'total_received': np.random.randint(0, 10, 20),
        'total_packing': np.random.randint(0, 1500, 20),
        'operator_name': [f'Operador {i}' for i in range(20)]
    }
    return pd.DataFrame(data)

@st.cache_data
def load_mock_packed():
    """Simula os dados da aba packed (Perfil de Produtos)"""
    dates = pd.date_range(end=datetime.now(), periods=10).strftime('%Y-%m-%d').tolist() * 5
    data = {
        'data': sorted(dates, reverse=True),
        'galpao': ['FBS_MG_Contagem_1'] * 50,
        'size_type': np.random.choice(['Bulky', 'G', 'M', 'P', 'PP', 'Ultra Bulky'], 50),
        'thp': np.random.randint(5, 15000, 50)
    }
    return pd.DataFrame(data)

@st.cache_data
def load_mock_raw_idle():
    """Simula os dados da aba raw_idle (Ociosidade)"""
    data = {
        'data': ['2026-07-18'] * 20,
        'ops_id': [f'Ops{np.random.randint(100000, 999999)}' for _ in range(20)],
        'idle_horas_decimal': np.random.uniform(0.05, 6.0, 20).round(2),
        'ops_name': [f'Operador {i}' for i in range(20)]
    }
    return pd.DataFrame(data)

@st.cache_data
def load_mock_sla_cot():
    """Simula os dados da aba SLA_COT (Status e Tempos)"""
    data = {
        'shipment_id': [f'BR{np.random.randint(1000000000, 9999999999)}' for _ in range(50)],
        'last_status': np.random.choice(['SOC_Packing', 'SOC_Packed', 'SOC_LHPacking'], 50, p=[0.4, 0.5, 0.1]),
        'created_time_last': pd.date_range(end=datetime.now(), periods=50).strftime('%Y-%m-%d %H:%M:%S')
    }
    return pd.DataFrame(data)

# Carregando dados
df_activity = load_mock_raw_activity()
df_packed = load_mock_packed()
df_idle = load_mock_raw_idle()
df_sla = load_mock_sla_cot()

# Configuração da Barra Lateral (Sidebar)
st.sidebar.image("https://placehold.co/400x150/1e1e1e/FFF?text=Logistics+Hub", use_column_width=True)
st.sidebar.markdown("---")
st.sidebar.header("⚙️ Configurações & Filtros")

# Controle de Navegação Multipáginas na Sidebar
menu_options = ["🏠 Visão Geral", "📊 Produtividade", "📦 Perfil de Carga (Packed)", "⏳ SLA e Ociosidade"]
choice = st.sidebar.radio("Navegação:", menu_options)

st.sidebar.markdown("---")

# Filtro Global de Data
datas_disponiveis = sorted(df_activity['data'].unique(), reverse=True)
data_selecionada = st.sidebar.selectbox("Selecione a Data de Referência:", datas_disponiveis)

# Filtrando os DataFrames principais pela data selecionada (quando aplicável)
df_activity_filtered = df_activity[df_activity['data'] == data_selecionada]
df_packed_filtered = df_packed[df_packed['data'] == data_selecionada]

if choice == "🏠 Visão Geral":
    st.title("🏠 Dashboard Master Operacional")
    st.markdown(f"**Data de Referência:** {data_selecionada}")
    
    # Linha 1: KPIs Principais
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_shipments = df_activity_filtered['total_shipments'].sum()
        st.metric(label="Total Shipments (Dia)", value=f"{total_shipments:,.0f}")
    with col2:
        total_horas = df_activity_filtered['total_manhr'].sum()
        st.metric(label="Total Horas Trabalhadas", value=f"{total_horas:.1f}h")
    with col3:
        # Simulando pacotes pendentes (Packing)
        pendentes = len(df_sla[df_sla['last_status'] == 'SOC_Packing'])
        st.metric(label="Pendentes (SOC_Packing)", value=pendentes, delta="-5%", delta_color="inverse")
    with col4:
        # Calculando ociosidade média do dia
        ociosidade_media = df_idle['idle_horas_decimal'].mean()
        st.metric(label="Ociosidade Média (h)", value=f"{ociosidade_media:.2f}h")
        
    st.markdown("---")
    
    # Linha 2: Gráficos de Resumo
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
            size_counts = df_packed_filtered.groupby('size_type')['thp'].sum().reset_index()
            fig_sizes = px.bar(size_counts, x='size_type', y='thp', 
                               color='size_type', text='thp',
                               title=f"Volume (THP) em {data_selecionada}")
            st.plotly_chart(fig_sizes, use_container_width=True)
        else:
            st.info("Sem dados de pacotes para a data selecionada.")

elif choice == "📊 Produtividade":
    st.title("📊 Análise de Produtividade (Activity)")
    
    st.markdown("### Top 10 Operadores por Volume (Shipments)")
    
    # Agrupando dados por operador e somando
    df_ops = df_activity_filtered.groupby('operator_name').agg({
        'total_shipments': 'sum',
        'total_manhr': 'sum'
    }).reset_index()
    
    # Calculando produtividade (Shipments por Hora)
    df_ops['produtividade_h'] = (df_ops['total_shipments'] / df_ops['total_manhr']).fillna(0)
    
    # Ordenando pelos que mais produziram
    df_top10 = df_ops.sort_values(by='total_shipments', ascending=False).head(10)
    
    fig_top10 = px.bar(df_top10, x='total_shipments', y='operator_name', orientation='h',
                       color='produtividade_h', color_continuous_scale='Viridis',
                       labels={'total_shipments': 'Total Shipments', 'operator_name': 'Operador', 'produtividade_h': 'Prod./Hora'},
                       title="Volume Total vs Produtividade por Hora")
    fig_top10.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_top10, use_container_width=True)
    
    st.markdown("### Detalhamento por Workstation")
    # Agrupando por workstation
    df_ws = df_activity_filtered.groupby('workstation_name').agg({'total_shipments': 'sum', 'total_manhr': 'sum'}).reset_index()
    st.dataframe(df_ws.style.highlight_max(subset=['total_shipments'], color='lightgreen'), use_container_width=True)

elif choice == "📦 Perfil de Carga (Packed)":
    st.title("📦 Análise do Perfil de Carga")
    
    st.markdown("Esta visão permite entender a proporção de tamanhos processados ao longo do tempo.")
    
    # Gráfico de evolução temporal do perfil de carga
    df_packed_trend = df_packed.groupby(['data', 'size_type'])['thp'].sum().reset_index()
    
    fig_trend = px.area(df_packed_trend, x='data', y='thp', color='size_type',
                        title="Evolução do Volume (THP) por Tamanho",
                        labels={'thp': 'Volume Processado', 'data': 'Data', 'size_type': 'Tamanho'})
    st.plotly_chart(fig_trend, use_container_width=True)
    
    st.markdown("### Base de Dados Bruta - Packed")
    st.dataframe(df_packed_filtered, use_container_width=True)

elif choice == "⏳ SLA e Ociosidade":
    st.title("⏳ Controle de Qualidade e Perdas")
    
    col_idle, col_sla = st.columns([1, 1])
    
    with col_idle:
        st.subheader("⚠️ Top Ociosidade (Raw Idle)")
        # Mostrando os operadores com maior tempo de ociosidade
        df_idle_sorted = df_idle.sort_values(by='idle_horas_decimal', ascending=False).head(10)
        
        fig_idle = px.bar(df_idle_sorted, x='idle_horas_decimal', y='ops_name', orientation='h',
                          title="Horas de Ociosidade por Operador (Top 10)",
                          color='idle_horas_decimal', color_continuous_scale='Reds')
        fig_idle.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_idle, use_container_width=True)
        
    with col_sla:
        st.subheader("📋 Últimos Status (SLA COT)")
        st.markdown("Acompanhamento em tempo real dos pacotes.")
        
        # Filtro rápido na própria tela para procurar um shipment
        search_shipment = st.text_input("🔍 Buscar Shipment ID (ex: BR...):")
        
        if search_shipment:
            result = df_sla[df_sla['shipment_id'].str.contains(search_shipment, case=False, na=False)]
            st.dataframe(result, use_container_width=True)
        else:
            # Mostra os 15 mais recentes
            st.dataframe(df_sla.head(15), use_container_width=True)
            
# Footer simples
st.sidebar.markdown("---")
st.sidebar.caption("Desenvolvido com ❤️ no Streamlit")