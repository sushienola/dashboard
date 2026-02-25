import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta
import requests

st.set_page_config(
    page_title="Dashboard Vendas - Sushi Leblon",
    page_icon="🍣",
    layout="wide"
)

st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e2130, #2a2d3e);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #3a3d4e;
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-value { font-size: 2rem; font-weight: bold; color: #e94560; }
    .metric-label { font-size: 0.85rem; color: #9a9db0; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

# ── CREDENCIAIS via Streamlit Secrets ──────────────────────
USUARIO       = st.secrets["USUARIO"]
SENHA         = st.secrets["SENHA"]
NUMERO_SERIAL = st.secrets["NUMERO_SERIAL"]
LOJAS         = ["1", "2"]
BASE_URL      = "https://chefweb.chef.totvs.com.br/chefwebapi/api"

# ── FUNÇÕES API ─────────────────────────────────────────────
def gerar_token():
    r = requests.post(
        f"{BASE_URL}/Token/GerarToken",
        json={"Usuario": USUARIO, "Senha": SENHA,
              "NumeroSerialLoja": NUMERO_SERIAL, "Chave": "SerialNumber"},
        timeout=30
    )
    r.raise_for_status()
    dados = r.json()
    if not dados.get("Sucesso"):
        raise Exception("Erro ao gerar token")
    return dados["Token"]

def buscar_vendas_dia(token, loja, data):
    r = requests.post(
        f"{BASE_URL}/CapaVenda/ListPorDataMovimento",
        json={
            "Token": token, "CodigoLoja": loja, "Composicoes": False,
            "DataMovimentoInicial": data.strftime("%Y-%m-%dT00:00:00"),
            "DataMovimentoFinal":   data.strftime("%Y-%m-%dT23:59:59"),
            "Online": False, "ValidaSaltoNota": False, "NotasInutilizadas": False
        },
        timeout=60
    )
    r.raise_for_status()
    return r.json().get("Vendas", [])

def processar_vendas(vendas):
    linhas = []
    for venda in vendas:
        loja_d  = venda.get("Loja", {})
        caixa   = venda.get("Caixa", {})
        total   = venda.get("TotalizadorVenda", {})
        pgtos   = venda.get("Pagamentos", [])
        formas  = ", ".join([p.get("Descricao", "") for p in (pgtos or [])])
        for item in (venda.get("Itens") or []):
            prod = item.get("Produto", {})
            linhas.append({
                "ChaveVenda":    venda.get("ChaveVenda"),
                "DataMovimento": venda.get("DataMovimento"),
                "NumeroCupom":   venda.get("NumeroCupom"),
                "StatusVenda":   venda.get("StatusVenda"),
                "Loja.Nome":     loja_d.get("Nome"),
                "Produto.Nome":  prod.get("Nome"),
                "Produto.Grupo": prod.get("Grupo"),
                "Item.Quantidade":   item.get("Quantidade"),
                "Item.ValorUnitario":item.get("ValorUnitario"),
                "Item.ValorTotal":   item.get("ValorTotal"),
                "Total.ValorTotal":  total.get("ValorTotal"),
                "FormasPagamento":   formas,
            })
    return linhas

@st.cache_data(show_spinner=False)
def carregar_dados(data_ini_str, data_fim_str):
    data_ini = datetime.strptime(data_ini_str, "%Y-%m-%d")
    data_fim = datetime.strptime(data_fim_str, "%Y-%m-%d")
    dias = []
    d = data_ini
    while d <= data_fim:
        dias.append(d)
        d += timedelta(days=1)

    todas = []
    for dia in dias:
        for loja in LOJAS:
            try:
                token  = gerar_token()
                vendas = buscar_vendas_dia(token, loja, dia)
                todas.extend(processar_vendas(vendas))
            except:
                pass

    if not todas:
        return pd.DataFrame()

    df = pd.DataFrame(todas)
    df["DataMovimento"] = pd.to_datetime(df["DataMovimento"], errors="coerce")
    df["Data"] = df["DataMovimento"].dt.date
    return df

# ── SIDEBAR ─────────────────────────────────────────────────
st.sidebar.title("🍣 Sushi Leblon")
st.sidebar.markdown("---")

hoje       = date.today()
inicio_mes = hoje.replace(day=1)

data_ini = st.sidebar.date_input("Data inicial", value=inicio_mes)
data_fim = st.sidebar.date_input("Data final",   value=hoje)

if st.sidebar.button("🔍 Buscar dados"):
    st.cache_data.clear()

st.sidebar.markdown("---")
st.sidebar.caption("Dados puxados ao vivo da TOTVS Chef")

# ── CARREGAMENTO ────────────────────────────────────────────
st.title("📊 Dashboard de Vendas")

if data_ini > data_fim:
    st.error("Data inicial não pode ser maior que a data final.")
    st.stop()

dias_selecionados = (data_fim - data_ini).days + 1
if dias_selecionados > 31:
    st.warning(f"⚠️ Período de {dias_selecionados} dias pode demorar alguns minutos para carregar.")

with st.spinner(f"Buscando dados de {data_ini.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}..."):
    df = carregar_dados(str(data_ini), str(data_fim))

if df.empty:
    st.warning("Nenhum dado encontrado para o período.")
    st.stop()

# Só vendas finalizadas
dff = df[df["StatusVenda"] == 2].copy()

# Filtro de loja
lojas_disp = sorted(dff["Loja.Nome"].dropna().unique().tolist())
lojas_sel  = st.sidebar.multiselect("Lojas", lojas_disp, default=lojas_disp)
dff = dff[dff["Loja.Nome"].isin(lojas_sel)]

if dff.empty:
    st.warning("Nenhum dado para as lojas selecionadas.")
    st.stop()

# ── MÉTRICAS ────────────────────────────────────────────────
vendas_unicas = dff.drop_duplicates(subset="ChaveVenda")
faturamento   = vendas_unicas["Total.ValorTotal"].sum()
total_vendas  = vendas_unicas["ChaveVenda"].nunique()
ticket_medio  = faturamento / total_vendas if total_vendas > 0 else 0
total_itens   = dff["Item.Quantidade"].sum()

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="metric-card"><div class="metric-value">R$ {faturamento:,.2f}</div><div class="metric-label">💰 Faturamento Total</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{total_vendas:,}</div><div class="metric-label">🧾 Total de Vendas</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-card"><div class="metric-value">R$ {ticket_medio:,.2f}</div><div class="metric-label">🎯 Ticket Médio</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{total_itens:,.0f}</div><div class="metric-label">📦 Itens Vendidos</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── FATURAMENTO POR DIA ─────────────────────────────────────
st.subheader("📅 Faturamento por Dia")
fat_dia = vendas_unicas.groupby(["Data","Loja.Nome"])["Total.ValorTotal"].sum().reset_index()
fat_dia["Data"] = pd.to_datetime(fat_dia["Data"])
fig = px.bar(fat_dia, x="Data", y="Total.ValorTotal", color="Loja.Nome",
             barmode="group", template="plotly_dark",
             color_discrete_sequence=["#e94560","#0f3460"],
             labels={"Total.ValorTotal":"Faturamento (R$)","Data":"","Loja.Nome":"Loja"})
fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                  yaxis_tickprefix="R$ ", yaxis_tickformat=",.0f", height=380)
st.plotly_chart(fig, use_container_width=True)

# ── PRODUTOS MAIS VENDIDOS ──────────────────────────────────
st.subheader("🏆 Produtos Mais Vendidos")
ca, cb = st.columns(2)

with ca:
    st.caption("Por quantidade")
    top_q = dff.groupby("Produto.Nome")["Item.Quantidade"].sum().sort_values(ascending=False).head(10).reset_index()
    fig_q = px.bar(top_q, x="Item.Quantidade", y="Produto.Nome", orientation="h",
                   template="plotly_dark", color="Item.Quantidade",
                   color_continuous_scale=["#0f3460","#e94560"],
                   labels={"Item.Quantidade":"Quantidade","Produto.Nome":""})
    fig_q.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                        coloraxis_showscale=False, yaxis=dict(autorange="reversed"), height=380)
    st.plotly_chart(fig_q, use_container_width=True)

with cb:
    st.caption("Por faturamento")
    top_f = dff.groupby("Produto.Nome")["Item.ValorTotal"].sum().sort_values(ascending=False).head(10).reset_index()
    fig_f = px.bar(top_f, x="Item.ValorTotal", y="Produto.Nome", orientation="h",
                   template="plotly_dark", color="Item.ValorTotal",
                   color_continuous_scale=["#0f3460","#e94560"],
                   labels={"Item.ValorTotal":"Faturamento (R$)","Produto.Nome":""})
    fig_f.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                        coloraxis_showscale=False, yaxis=dict(autorange="reversed"),
                        xaxis_tickprefix="R$ ", xaxis_tickformat=",.0f", height=380)
    st.plotly_chart(fig_f, use_container_width=True)

# ── COMPARATIVO LOJAS ───────────────────────────────────────
if len(lojas_sel) > 1:
    st.subheader("🏪 Comparativo entre Lojas")
    comp = vendas_unicas.groupby("Loja.Nome").agg(
        Faturamento=("Total.ValorTotal","sum"),
        Vendas=("ChaveVenda","nunique")
    ).reset_index()
    comp["Ticket"] = comp["Faturamento"] / comp["Vendas"]
    cols = st.columns(len(comp))
    for i, row in comp.iterrows():
        with cols[i]:
            st.markdown(f'<div class="metric-card"><div class="metric-label">{row["Loja.Nome"]}</div><div class="metric-value">R$ {row["Faturamento"]:,.2f}</div><div class="metric-label">{row["Vendas"]} vendas · Ticket R$ {row["Ticket"]:,.2f}</div></div>', unsafe_allow_html=True)

# ── TABELA ──────────────────────────────────────────────────
with st.expander("📋 Ver dados detalhados"):
    cols_show = ["Data","Loja.Nome","NumeroCupom","Produto.Nome","Produto.Grupo",
                 "Item.Quantidade","Item.ValorUnitario","Item.ValorTotal","Total.ValorTotal"]
    cols_ok = [c for c in cols_show if c in dff.columns]
    st.dataframe(dff[cols_ok].sort_values("Data", ascending=False).reset_index(drop=True),
                 use_container_width=True, height=400)
