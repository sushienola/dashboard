import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import requests

st.set_page_config(
    page_title="BI Hub — Sushi Leblon & Nola",
    page_icon="🍱",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;600&family=DM+Mono:wght@300;400&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Mono', monospace;
    background-color: #0a0a0a;
    color: #d4c5a9;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0f0f0f;
    border-right: 1px solid #1e1e1e;
}
section[data-testid="stSidebar"] * { color: #d4c5a9 !important; }

/* Header brand */
.brand {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.1rem;
    font-weight: 300;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: #c9a96e !important;
    padding: 0 0 6px 0;
}
.brand span { color: #d4c5a9 !important; font-weight: 600; }
.brand-sub {
    font-size: 0.6rem;
    letter-spacing: 0.4em;
    color: #555 !important;
    text-transform: uppercase;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid #1e1e1e;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #555 !important;
    padding: 12px 24px;
    border-bottom: 2px solid transparent;
    background: transparent;
}
.stTabs [aria-selected="true"] {
    color: #c9a96e !important;
    border-bottom: 2px solid #c9a96e !important;
    background: transparent;
}

/* Metric cards */
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; background: #1a1a1a; margin-bottom: 2px; }
.kpi-card {
    background: #0f0f0f;
    padding: 28px 24px;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 2px; height: 100%;
    background: #c9a96e;
    opacity: 0.4;
}
.kpi-label {
    font-size: 0.6rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #555;
    margin-bottom: 12px;
}
.kpi-value {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2.4rem;
    font-weight: 300;
    color: #c9a96e;
    line-height: 1;
    margin-bottom: 6px;
}
.kpi-sub { font-size: 0.65rem; color: #444; }

/* Section headers */
.section-header {
    font-size: 0.6rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: #555;
    border-bottom: 1px solid #1a1a1a;
    padding-bottom: 10px;
    margin: 32px 0 20px 0;
    display: flex;
    align-items: center;
    gap: 12px;
}
.section-header::before {
    content: '';
    width: 20px;
    height: 1px;
    background: #c9a96e;
}

/* Top produtos */
.produto-row {
    display: flex;
    align-items: center;
    padding: 10px 0;
    border-bottom: 1px solid #141414;
    gap: 16px;
}
.produto-rank {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.1rem;
    color: #333;
    width: 24px;
    text-align: right;
    flex-shrink: 0;
}
.produto-rank.gold { color: #c9a96e; }
.produto-rank.silver { color: #8a9ba8; }
.produto-rank.bronze { color: #a0784a; }
.produto-info { flex: 1; }
.produto-nome { font-size: 0.75rem; color: #d4c5a9; letter-spacing: 0.05em; }
.produto-grupo { font-size: 0.6rem; color: #444; letter-spacing: 0.1em; text-transform: uppercase; margin-top: 2px; }
.produto-valor {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.2rem;
    color: #c9a96e;
    text-align: right;
    flex-shrink: 0;
}
.produto-unidade { font-size: 0.6rem; color: #444; }

/* Period bar */
.period-bar {
    background: #0f0f0f;
    border: 1px solid #1a1a1a;
    padding: 14px 20px;
    margin-bottom: 2px;
    display: flex;
    align-items: center;
    gap: 20px;
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    color: #555;
}
.period-bar strong { color: #d4c5a9; }

/* Plotly dark override */
.js-plotly-plot .plotly { background: transparent !important; }

/* Streamlit overrides */
div[data-testid="stMetric"] { background: transparent; }
.stButton button {
    background: transparent;
    border: 1px solid #2a2a2a;
    color: #d4c5a9;
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    padding: 8px 20px;
    transition: all 0.2s;
}
.stButton button:hover {
    border-color: #c9a96e;
    color: #c9a96e;
}
label, .stDateInput label { 
    font-size: 0.6rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    color: #444 !important;
}
div[data-testid="stDateInput"] input {
    background: #0f0f0f !important;
    border: 1px solid #1e1e1e !important;
    color: #d4c5a9 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
}
</style>
""", unsafe_allow_html=True)

# ── CREDENCIAIS ─────────────────────────────────────────────
USUARIO       = st.secrets["USUARIO"]
SENHA         = st.secrets["SENHA"]
NUMERO_SERIAL = st.secrets["NUMERO_SERIAL"]
BASE_URL      = "https://chefweb.chef.totvs.com.br/chefwebapi/api"

RESTAURANTES = {
    "1": "SUSHI LEBLON",
    "2": "NOLA"
}

# ── API ──────────────────────────────────────────────────────
def gerar_token():
    r = requests.post(f"{BASE_URL}/Token/GerarToken", json={
        "Usuario": USUARIO, "Senha": SENHA,
        "NumeroSerialLoja": NUMERO_SERIAL, "Chave": "SerialNumber"
    }, timeout=30)
    r.raise_for_status()
    d = r.json()
    if not d.get("Sucesso"):
        raise Exception("Token inválido")
    return d["Token"]

def buscar_dia(token, loja, data):
    r = requests.post(f"{BASE_URL}/CapaVenda/ListPorDataMovimento", json={
        "Token": token, "CodigoLoja": loja, "Composicoes": False,
        "DataMovimentoInicial": data.strftime("%Y-%m-%dT00:00:00"),
        "DataMovimentoFinal":   data.strftime("%Y-%m-%dT23:59:59"),
        "Online": False, "ValidaSaltoNota": False, "NotasInutilizadas": False
    }, timeout=60)
    r.raise_for_status()
    return r.json().get("Vendas", [])

def processar(vendas, loja_id):
    linhas = []
    for v in vendas:
        tot  = v.get("TotalizadorVenda", {})
        pgts = v.get("Pagamentos", [])
        formas = ", ".join([p.get("Descricao","") for p in (pgts or [])])
        for item in (v.get("Itens") or []):
            prod = item.get("Produto", {})
            linhas.append({
                "ChaveVenda":        v.get("ChaveVenda"),
                "DataMovimento":     v.get("DataMovimento"),
                "NumeroCupom":       v.get("NumeroCupom"),
                "StatusVenda":       v.get("StatusVenda"),
                "Restaurante":       RESTAURANTES.get(loja_id, loja_id),
                "Loja.ID":           loja_id,
                "Produto.Nome":      prod.get("Nome",""),
                "Produto.Grupo":     prod.get("Grupo",""),
                "Produto.SubGrupo":  prod.get("SubGrupo",""),
                "Item.Quantidade":   item.get("Quantidade", 0),
                "Item.ValorUnitario":item.get("ValorUnitario", 0),
                "Item.ValorTotal":   item.get("ValorTotal", 0),
                "Total.ValorTotal":  tot.get("ValorTotal", 0),
                "Total.Desconto":    tot.get("ValorTotalDescontoFiscal", 0),
                "Total.Servico":     tot.get("ValorTotalServico", 0),
                "FormasPagamento":   formas,
            })
    return linhas

@st.cache_data(show_spinner=False, ttl=1800)
def carregar(ini_str, fim_str):
    ini = datetime.strptime(ini_str, "%Y-%m-%d")
    fim = datetime.strptime(fim_str, "%Y-%m-%d")
    dias = [(ini + timedelta(days=i)) for i in range((fim - ini).days + 1)]
    todas = []
    prog = st.progress(0, text="Carregando dados...")
    total = len(dias) * len(RESTAURANTES)
    n = 0
    for dia in dias:
        for loja_id in RESTAURANTES:
            try:
                token  = gerar_token()
                vendas = buscar_dia(token, loja_id, dia)
                todas.extend(processar(vendas, loja_id))
            except:
                pass
            n += 1
            prog.progress(n / total, text=f"Carregando {dia.strftime('%d/%m')} — {RESTAURANTES[loja_id]}...")
    prog.empty()
    if not todas:
        return pd.DataFrame()
    df = pd.DataFrame(todas)
    df["DataMovimento"] = pd.to_datetime(df["DataMovimento"], errors="coerce")
    df["Data"] = df["DataMovimento"].dt.date
    return df

# ── SIDEBAR ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="brand">SUSHI <span>LEBLON</span><br><small>& NOLA</small></div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">BI HUB</div>', unsafe_allow_html=True)
    st.markdown("---")

    hoje       = date.today()
    inicio_mes = hoje.replace(day=1)
    data_ini   = st.date_input("Início de dados", value=inicio_mes)
    data_fim   = st.date_input("Dados finais",    value=hoje)

    buscar = st.button("↳ Buscar dados")
    if buscar:
        st.cache_data.clear()

    st.markdown("---")
    st.markdown('<div style="font-size:0.6rem;letter-spacing:0.15em;color:#333">DADOS AO VIVO · TOTVS CHEF</div>', unsafe_allow_html=True)

# ── CARREGAMENTO ─────────────────────────────────────────────
if data_ini > data_fim:
    st.error("Data inicial maior que final.")
    st.stop()

with st.spinner(""):
    df = carregar(str(data_ini), str(data_fim))

if df.empty:
    st.warning("Nenhum dado encontrado.")
    st.stop()

dff = df[df["StatusVenda"] == 2].copy()

# ── TABS ─────────────────────────────────────────────────────
tab_geral, tab_sushi, tab_nola = st.tabs([
    "⬡  VISÃO GERAL",
    "⬡  SUSHI LEBLON",
    "⬡  NOLA"
])

PLOT_LAYOUT = dict(
    plot_bgcolor="#0a0a0a",
    paper_bgcolor="#0a0a0a",
    font=dict(family="DM Mono, monospace", color="#555", size=10),
    margin=dict(l=0, r=0, t=20, b=0),
    xaxis=dict(gridcolor="#141414", linecolor="#1a1a1a", tickcolor="#333"),
    yaxis=dict(gridcolor="#141414", linecolor="#1a1a1a", tickcolor="#333"),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#555", size=10)),
    height=320
)

def kpis(data, label_prefix=""):
    vu   = data.drop_duplicates("ChaveVenda")
    fat  = vu["Total.ValorTotal"].sum()
    nv   = vu["ChaveVenda"].nunique()
    tick = fat / nv if nv > 0 else 0
    qtd  = data["Item.Quantidade"].sum()
    desc = vu["Total.Desconto"].sum()

    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-label">Faturamento</div>
            <div class="kpi-value">R$ {fat:,.0f}</div>
            <div class="kpi-sub">{fat:,.2f} faturados</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Unidades Vendidas</div>
            <div class="kpi-value">{qtd:,.0f}</div>
            <div class="kpi-sub">{nv:,} cupons</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Ticket Médio</div>
            <div class="kpi-value">R$ {tick:,.2f}</div>
            <div class="kpi-sub">por cupom</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Descontos</div>
            <div class="kpi-value">R$ {desc:,.0f}</div>
            <div class="kpi-sub">{(desc/fat*100) if fat>0 else 0:.1f}% do faturamento</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def graf_fat_dia(data, cores):
    vu = data.drop_duplicates("ChaveVenda")
    g  = vu.groupby(["Data","Restaurante"])["Total.ValorTotal"].sum().reset_index()
    g["Data"] = pd.to_datetime(g["Data"])
    fig = px.bar(g, x="Data", y="Total.ValorTotal", color="Restaurante",
                 barmode="group", color_discrete_sequence=cores,
                 labels={"Total.ValorTotal":"","Data":""})
    fig.update_layout(**PLOT_LAYOUT)
    fig.update_traces(marker_line_width=0)
    fig.update_yaxes(tickprefix="R$", tickformat=",.0f")
    return fig

def top_produtos_html(data, por="qtd", n=8):
    if por == "qtd":
        top = data.groupby(["Produto.Nome","Produto.Grupo"])["Item.Quantidade"].sum().sort_values(ascending=False).head(n).reset_index()
        col_val, col_unit = "Item.Quantidade", "un"
    else:
        top = data.groupby(["Produto.Nome","Produto.Grupo"])["Item.ValorTotal"].sum().sort_values(ascending=False).head(n).reset_index()
        col_val, col_unit = "Item.ValorTotal", ""

    ranks = {1:"gold", 2:"silver", 3:"bronze"}
    html = ""
    for i, row in top.iterrows():
        r    = i + 1
        cls  = ranks.get(r, "")
        val  = f"R$ {row[col_val]:,.2f}" if col_unit == "" else f"{row[col_val]:,.0f}"
        unit = f'<div class="produto-unidade">{col_unit}</div>' if col_unit else ""
        html += f"""
        <div class="produto-row">
            <div class="produto-rank {cls}">{r}</div>
            <div class="produto-info">
                <div class="produto-nome">{row['Produto.Nome']}</div>
                <div class="produto-grupo">{row['Produto.Grupo']}</div>
            </div>
            <div class="produto-valor">{val}{unit}</div>
        </div>"""
    return html

def graf_categorias(data):
    g = data.groupby("Produto.Grupo")["Item.Quantidade"].sum().sort_values(ascending=False).head(10).reset_index()
    fig = px.bar(g, x="Produto.Grupo", y="Item.Quantidade",
                 color="Item.Quantidade", color_continuous_scale=["#1a1a1a","#c9a96e"],
                 labels={"Item.Quantidade":"","Produto.Grupo":""})
    fig.update_layout(**PLOT_LAYOUT, coloraxis_showscale=False)
    fig.update_traces(marker_line_width=0)
    return fig

def render_tab(data, titulo, cores):
    st.markdown(f"""
    <div class="period-bar">
        <span>PERÍODO DO RELATÓRIO</span>
        <strong>{data_ini.strftime('%d/%m/%Y')} — {data_fim.strftime('%d/%m/%Y')}</strong>
        <span style="margin-left:auto">DADOS CONSOLIDADOS</span>
    </div>
    """, unsafe_allow_html=True)

    kpis(data)

    # Faturamento por dia
    st.markdown('<div class="section-header">Faturamento Diário</div>', unsafe_allow_html=True)
    vu = data.drop_duplicates("ChaveVenda")
    g  = vu.groupby("Data")["Total.ValorTotal"].sum().reset_index()
    g["Data"] = pd.to_datetime(g["Data"])
    fig = px.bar(g, x="Data", y="Total.ValorTotal",
                 color_discrete_sequence=[cores[0]],
                 labels={"Total.ValorTotal":"","Data":""})
    fig.update_layout(**PLOT_LAYOUT)
    fig.update_traces(marker_line_width=0)
    fig.update_yaxes(tickprefix="R$", tickformat=",.0f")
    st.plotly_chart(fig, use_container_width=True)

    # Categorias + Top produtos
    st.markdown('<div class="section-header">Vendas por Categoria & Top Produtos</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns([6, 4])

    with col_a:
        st.plotly_chart(graf_categorias(data), use_container_width=True)

    with col_b:
        modo = st.radio("", ["QUANTIDADE", "FATURAMENTO"], horizontal=True, key=f"modo_{titulo}")
        por  = "qtd" if modo == "QUANTIDADE" else "fat"
        st.markdown(f'<div style="font-size:0.65rem;color:#555;letter-spacing:0.15em;margin-bottom:8px">TOP 8 PRODUTOS — {modo}</div>', unsafe_allow_html=True)
        st.markdown(top_produtos_html(data, por=por), unsafe_allow_html=True)

# ── TAB GERAL ────────────────────────────────────────────────
with tab_geral:
    st.markdown(f"""
    <div class="period-bar">
        <span>PERÍODO DO RELATÓRIO</span>
        <strong>{data_ini.strftime('%d/%m/%Y')} — {data_fim.strftime('%d/%m/%Y')}</strong>
        <span style="margin-left:auto">DADOS CONSOLIDADOS · 2 RESTAURANTES</span>
    </div>
    """, unsafe_allow_html=True)

    kpis(dff)

    st.markdown('<div class="section-header">Faturamento Diário por Restaurante</div>', unsafe_allow_html=True)
    st.plotly_chart(graf_fat_dia(dff, ["#c9a96e","#6e9ac9"]), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">Top Produtos — SUSHI LEBLON</div>', unsafe_allow_html=True)
        d_s = dff[dff["Loja.ID"] == "1"]
        st.markdown(top_produtos_html(d_s, por="qtd"), unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="section-header">Top Produtos — NOLA</div>', unsafe_allow_html=True)
        d_n = dff[dff["Loja.ID"] == "2"]
        st.markdown(top_produtos_html(d_n, por="qtd"), unsafe_allow_html=True)

# ── TAB SUSHI LEBLON ─────────────────────────────────────────
with tab_sushi:
    render_tab(dff[dff["Loja.ID"] == "1"], "sushi", ["#c9a96e","#a07840"])

# ── TAB NOLA ─────────────────────────────────────────────────
with tab_nola:
    render_tab(dff[dff["Loja.ID"] == "2"], "nola", ["#6e9ac9","#3a6a9a"])
