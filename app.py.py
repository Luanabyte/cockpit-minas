# ... existing code ...
    df_dmo = pd.DataFrame({
        'A': [''] * 30,
        'B': [''] * 30,
        'C': [''] * 30,
        'D': [1000] * 30 
    })
    
    return df_act, df_pck, df_idl, df_sla, df_prod, df_dmo

# STREAMING_CHUNK:Configuring custom CSS styles...
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

# STREAMING_CHUNK:Initializing real data connection...
if USAR_DADOS_REAIS:
# ... existing code ...
```eof

Please apply this diff to your `app.py` file. I have ensured the triple quotes (`"""`) are perfectly formed. Let me know if this resolves the syntax error and you can see the new layout!
