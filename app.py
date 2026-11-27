# -*- coding: utf-8 -*-
"""
Olho na Cota — Painel CEAP 2025 (Streamlit)
Execução:
    pip install -r requirements.txt
    streamlit run app.py
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ------------------------------------------------------------------ config
st.set_page_config(page_title="Olho na Cota — CEAP 2025", page_icon="👁️", layout="wide")

BASE = Path(__file__).parent
ARQ_DADOS = BASE / "data" / "silver" / "CEAP_2025_tratada.csv.gz"
CORES = ["#2563eb", "#f59e0b", "#10b981", "#ef4444", "#8b5cf6", "#94a3b8",
         "#06b6d4", "#ec4899", "#84cc16", "#f97316"]
MESES = ["", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

st.markdown("""
<style>
[data-testid="stSidebar"]{background:#0b1f44}
[data-testid="stSidebar"] *{color:#e2e8f0 !important}
.block-container{padding-top:1.6rem;max-width:1300px}
.hero{background:linear-gradient(120deg,#0b1f44,#2563eb);color:#fff;border-radius:18px;padding:30px 34px;margin-bottom:20px}
.hero h1{color:#fff;font-size:32px;margin:0 0 10px}.hero p{color:#e8eefc;line-height:1.6;font-size:15.5px;margin:6px 0}
.kpi{background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:14px 16px;display:flex;gap:12px;align-items:center;margin-bottom:10px}
.kpi .ic{width:44px;height:44px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:22px;flex-shrink:0}
.kpi span{color:#64748b;font-size:12.5px}.kpi b{display:block;font-size:20px;color:#14213d}
.ins{background:#eef4ff;border-left:4px solid #2563eb;padding:10px 14px;border-radius:7px;font-size:14px;margin:6px 0 18px;line-height:1.5;color:#14213d}
.ins.w{background:#fef2f2;border-color:#dc2626}
.q{color:#64748b;font-size:13.5px;margin-top:-8px}
.map{display:grid;grid-template-columns:repeat(8,1fr);gap:5px;max-width:520px}
.map div{aspect-ratio:1;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700}
.pipe{display:flex;gap:10px;flex-wrap:wrap}.st{flex:1;min-width:170px;padding:16px;border-radius:12px;font-size:13.5px;line-height:1.5;color:#14213d}
.st .e{font-size:28px}
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------ dados
@st.cache_data(show_spinner="Carregando dados da CEAP 2025...")
def carregar():
    df = pd.read_csv(ARQ_DADOS, sep=";", encoding="utf-8-sig", low_memory=False)
    df["categoria"] = df["txtDescricao"].fillna("").str.rstrip(".").str.capitalize()
    return df


df = carregar()
V = "vlrLiquido"
# Registros de lideranças (ex.: LID.GOV-CD) não têm deputado/partido: ficam fora dos rankings.
dep = df[df["nuDeputadoId"].notna() & df["sgPartido"].notna()]

TOTAL = df[V].sum()
N = len(df)
NDEP = dep["nuDeputadoId"].nunique()
NFORN = df["txtCNPJCPF"].nunique()
NOUT = int(df["indicador_outlier_vlrLiquido"].sum())
GLOSA = df["vlrGlosa"].sum()
MEDIA = dep[V].sum() / NDEP


def brl(v):
    return "R$ " + f"{v:,.0f}".replace(",", ".")


def mi(v):
    return "R$ " + f"{v / 1e6:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".") + " mi"


def nf(v):
    return f"{v:,}".replace(",", ".")


def kpis(itens, colunas=3):
    cols = st.columns(colunas)
    for i, (ic, cor, rot, val) in enumerate(itens):
        cols[i % colunas].markdown(
            f'<div class="kpi"><div class="ic" style="background:{cor}22">{ic}</div>'
            f'<div><span>{rot}</span><b>{val}</b></div></div>', unsafe_allow_html=True)


def insight(txt, alerta=False):
    st.markdown(f'<div class="ins{" w" if alerta else ""}">{txt}</div>', unsafe_allow_html=True)


def barras_h(serie, fmt=mi, cor=None, altura=None):
    s = serie.sort_values()
    fig = go.Figure(go.Bar(
        x=s.values, y=s.index, orientation="h",
        marker_color=cor or [CORES[i % 10] for i in range(len(s))][::-1],
        text=[fmt(v) for v in s.values], textposition="outside",
        hovertemplate="%{y}<br><b>R$ %{x:,.2f}</b><extra></extra>"))
    fig.update_layout(height=altura or max(300, 34 * len(s)), margin=dict(l=10, r=40, t=10, b=10),
                      xaxis=dict(visible=False), plot_bgcolor="white", separators=",.")
    return fig


# ------------------------------------------------------------------ menu
with st.sidebar:
    st.markdown("## 👁️ Olho na Cota")
    pagina = st.radio("Navegação", [
        "🏠 Início", "📈 Visão geral", "🧾 Categorias", "👤 Deputados",
        "🗺️ Estados e partidos", "🏢 Fornecedores", "🚨 Alertas", "⚙️ Sobre o projeto"],
        label_visibility="collapsed")
    st.markdown("---")
    st.caption("Fonte: Câmara dos Deputados — Dados Abertos, CEAP 2025.\n\nProjeto ETL & Engenharia de Dados.")

# ================================================================== INÍCIO
if pagina == "🏠 Início":
    st.markdown("""
    <div class="hero"><h1>Para onde vai o dinheiro da Cota Parlamentar?</h1>
    <p>Todo mês, cada deputado federal pode usar a <b>CEAP</b> (Cota para o Exercício da Atividade
    Parlamentar) para pagar passagens, divulgação, aluguel de carros, escritório e mais. Esses dados são
    públicos, mas estão em um arquivo com <b>171 mil linhas</b> que o cidadão comum não consegue ler.</p>
    <p><b>O problema que resolvemos:</b> transformar esses dados em informação clara para apoiar a
    <b>transparência e a fiscalização</b>: quanto foi gasto, em quê, por quem, e onde há gastos fora do padrão.</p>
    <p><b>Como isso ajuda as pessoas:</b> o eleitor pode consultar o deputado em quem votou, comparar estados
    e partidos e votar e cobrar com base em fatos.</p></div>""", unsafe_allow_html=True)
    kpis([("💰", "#2563eb", "Total gasto em 2025", mi(TOTAL)),
          ("🧾", "#f59e0b", "Lançamentos (notas)", nf(N)),
          ("👤", "#10b981", "Deputados com gastos", nf(NDEP)),
          ("📊", "#8b5cf6", "Média por deputado", brl(MEDIA)),
          ("🏢", "#06b6d4", "Fornecedores", nf(NFORN)),
          ("🚨", "#ef4444", "Gastos fora do padrão", nf(NOUT))])
    st.markdown("#### Explore o painel pelo menu ao lado")
    c = st.columns(3)
    for i, (ic, t, s) in enumerate([
            ("📈", "Visão geral", "Evolução mês a mês"), ("🧾", "Categorias", "Em que se gasta mais"),
            ("👤", "Deputados", "Ranking e busca por nome"), ("🗺️", "Estados e partidos", "Mapa de calor do Brasil"),
            ("🚨", "Alertas", "Gastos fora do padrão"), ("⚙️", "Sobre o projeto", "Pipeline e modelo de dados")]):
        c[i % 3].info(f"{ic} **{t}** — {s}")

# ================================================================== VISÃO GERAL
elif pagina == "📈 Visão geral":
    st.title("📈 Visão geral")
    st.markdown('<p class="q">Pergunta 1: como os gastos evoluíram ao longo de 2025?</p>', unsafe_allow_html=True)

    mes = df[df["numAno"] == 2025].groupby("numMes")[V].sum().sort_index()
    st.subheader("Gasto total por mês")
    fig = go.Figure(go.Scatter(
        x=[MESES[int(m)] for m in mes.index], y=mes.values / 1e6, mode="lines+markers+text",
        fill="tozeroy", fillcolor="rgba(37,99,235,.15)", line=dict(color="#2563eb", width=3),
        marker=dict(size=10, color="white", line=dict(color="#2563eb", width=3)),
        text=[f"{v / 1e6:.1f}" for v in mes.values], textposition="top center",
        hovertemplate="%{x}: <b>R$ %{y:.2f} mi</b><extra></extra>"))
    fig.update_layout(height=340, yaxis_title="R$ milhões", plot_bgcolor="white",
                      margin=dict(t=20, b=10), yaxis=dict(rangemode="tozero", gridcolor="#e2e8f0"))
    st.plotly_chart(fig, use_container_width=True)
    mx, mn = mes.idxmax(), mes.idxmin()
    insight(f"💡 Mês de <b>maior</b> gasto: <b>{MESES[int(mx)]}</b> ({brl(mes[mx])}). Mês de <b>menor</b> gasto: "
            f"<b>{MESES[int(mn)]}</b> ({brl(mes[mn])}). Os meses finais podem subir depois, porque as notas chegam com atraso.")

    st.subheader("Composição mensal por categoria")
    top5 = df.groupby("categoria")[V].sum().nlargest(5).index
    base = df[df["numAno"] == 2025].copy()
    base["grupo"] = base["categoria"].where(base["categoria"].isin(top5), "Outras")
    comp = base.groupby(["numMes", "grupo"])[V].sum().reset_index()
    comp["Mês"] = comp["numMes"].astype(int).map(lambda m: MESES[m])
    fig = px.bar(comp, x="Mês", y=V, color="grupo", color_discrete_sequence=CORES,
                 category_orders={"Mês": MESES[1:], "grupo": list(top5) + ["Outras"]},
                 labels={V: "Valor (R$)", "grupo": "Categoria"})
    fig.update_layout(height=420, plot_bgcolor="white", legend=dict(orientation="h", y=-0.2), margin=dict(t=10))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Distribuição dos valores das notas")
    faixas = ["≤ 0", "até 100", "100–500", "500–1 mil", "1–5 mil", "5–20 mil", "> 20 mil"]
    dist = pd.cut(df[V], [-1e12, 0, 100, 500, 1000, 5000, 20000, 1e12], labels=faixas).value_counts(sort=False)
    fig = go.Figure(go.Bar(x=["R$ " + f for f in faixas], y=dist.values, text=[nf(int(v)) for v in dist.values],
                           textposition="outside", marker_color=["#2563eb"] * 5 + ["#ef4444"] * 2))
    fig.update_layout(height=340, plot_bgcolor="white", yaxis_title="Quantidade de notas", margin=dict(t=20))
    st.plotly_chart(fig, use_container_width=True)
    insight("A maioria das despesas é pequena, entre R$ 100 e R$ 500. Por isso, os valores muito altos "
            "chamam atenção e são tratados como <b>alertas</b>.")

# ================================================================== CATEGORIAS
elif pagina == "🧾 Categorias":
    st.title("🧾 Categorias de despesa")
    st.markdown('<p class="q">Pergunta 2: em que tipo de despesa a cota é mais usada?</p>', unsafe_allow_html=True)
    cat = df.groupby("categoria")[V].sum().sort_values(ascending=False)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Participação no total")
        don = pd.concat([cat.head(7), pd.Series({"Outras": cat.iloc[7:].sum()})])
        fig = go.Figure(go.Pie(labels=don.index, values=don.values, hole=.55, marker_colors=CORES,
                               hovertemplate="%{label}<br><b>%{percent}</b> — R$ %{value:,.0f}<extra></extra>"))
        fig.update_layout(height=460, legend=dict(orientation="h", y=-0.15), margin=dict(t=10),
                          annotations=[dict(text=f"Total<br><b>{mi(TOTAL)}</b>", showarrow=False, font_size=16)])
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("Ranking de categorias")
        st.plotly_chart(barras_h(cat.head(12)), use_container_width=True)
    insight(f"💡 <b>{cat.index[0]}</b> sozinha representa <b>{cat.iloc[0] / TOTAL * 100:.0f}%</b> de todo o gasto da cota.")

# ================================================================== DEPUTADOS
elif pagina == "👤 Deputados":
    st.title("👤 Deputados")
    st.markdown('<p class="q">Pergunta 3: quais deputados mais usaram a cota?</p>', unsafe_allow_html=True)
    tab = (dep.groupby(["nuDeputadoId", "txNomeParlamentar", "sgPartido", "sgUF"])
           .agg(total=(V, "sum"), lancamentos=(V, "size")).reset_index())
    maior = (dep.groupby(["nuDeputadoId", "categoria"])[V].sum().reset_index()
             .sort_values(V).groupby("nuDeputadoId").tail(1).set_index("nuDeputadoId")["categoria"])
    tab["maior_categoria"] = tab["nuDeputadoId"].map(maior)
    tab = tab.sort_values("total", ascending=False).reset_index(drop=True)
    tab.insert(0, "posição", [f"{i}º" for i in range(1, len(tab) + 1)])

    st.subheader("Top 10 deputados")
    top = tab.head(10)
    s = pd.Series(top["total"].values,
                  index=top["txNomeParlamentar"] + " (" + top["sgPartido"] + "-" + top["sgUF"] + ")")
    st.plotly_chart(barras_h(s, fmt=brl, cor="#2563eb"), use_container_width=True)
    insight("Gasto alto <b>não significa irregularidade</b>. O ranking mostra por onde começar a fiscalizar.")

    st.subheader("🔎 Consulte qualquer deputado")
    c1, c2 = st.columns([3, 1])
    busca = c1.text_input("Digite um nome, partido ou UF", placeholder="Ex.: Silva, PT, MG...")
    uf = c2.selectbox("UF", ["Todas"] + sorted(tab["sgUF"].unique()))
    f = tab.copy()
    if busca:
        chave = (f["txNomeParlamentar"] + " " + f["sgPartido"] + " " + f["sgUF"]).str.lower()
        f = f[chave.str.contains(busca.lower(), regex=False)]
    if uf != "Todas":
        f = f[f["sgUF"] == uf]
    f = f.drop(columns="nuDeputadoId").rename(columns={
        "txNomeParlamentar": "Deputado", "sgPartido": "Partido", "sgUF": "UF", "total": "Total gasto (R$)",
        "lancamentos": "Lançamentos", "maior_categoria": "Maior categoria", "posição": "#"})
    st.dataframe(f, use_container_width=True, hide_index=True, height=460,
                 column_config={"Total gasto (R$)": st.column_config.NumberColumn(format="R$ %.2f")})

# ================================================================== ESTADOS
elif pagina == "🗺️ Estados e partidos":
    st.title("🗺️ Estados e partidos")
    st.markdown('<p class="q">Perguntas 4 e 5: como os gastos se distribuem pelo país e entre os partidos?</p>',
                unsafe_allow_html=True)
    ufd = dep.groupby("sgUF").agg(total=(V, "sum"), n=("nuDeputadoId", "nunique"))
    ufd["media"] = ufd["total"] / ufd["n"]
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Mapa de calor por estado")
        st.markdown('<p class="q">Média gasta por deputado em cada UF. Quanto mais escuro, maior. '
                    'Passe o mouse para ver os valores.</p>', unsafe_allow_html=True)
        grade = [["", "", "", "RR", "AP", "", "", ""], ["", "AM", "", "PA", "", "MA", "CE", "RN"],
                 ["AC", "", "RO", "TO", "", "PI", "PE", "PB"], ["", "", "MT", "GO", "DF", "BA", "AL", "SE"],
                 ["", "", "", "MS", "MG", "ES", "", ""], ["", "", "", "SP", "RJ", "", "", ""],
                 ["", "", "", "PR", "", "", "", ""], ["", "", "SC", "", "", "", "", ""],
                 ["", "RS", "", "", "", "", "", ""]]
        mn, mx = ufd["media"].min(), ufd["media"].max()
        html = '<div class="map">'
        for u in sum(grade, []):
            if u not in ufd.index:
                html += "<span></span>"
                continue
            r = ufd.loc[u]
            luz = 82 - (r["media"] - mn) / (mx - mn) * 52
            cor_txt = "#14213d" if luz > 60 else "#fff"
            dica = f'{u} | Média/deputado: {brl(r["media"])} | Total: {brl(r["total"])} | {int(r["n"])} deputados'
            html += (f'<div title="{dica}" style="background:hsl(221,80%,{luz:.0f}%);color:{cor_txt}">{u}</div>')
        st.markdown(html + "</div>", unsafe_allow_html=True)
        o = ufd["media"].sort_values(ascending=False)
        insight(f"💡 Maior média por deputado: <b>{o.index[0]}</b> ({brl(o.iloc[0])}). Menor: <b>{o.index[-1]}</b> "
                f"({brl(o.iloc[-1])}). Estados longe de Brasília tendem a gastar mais com deslocamento.")
    with c2:
        st.subheader("Gasto por partido")
        modo = st.selectbox("Comparar por", ["Média por deputado (partidos com 5+)", "Total gasto"])
        pdt = dep.groupby("sgPartido").agg(total=(V, "sum"), n=("nuDeputadoId", "nunique"))
        if modo.startswith("Média"):
            pdt = pdt[pdt["n"] >= 5]
            st.plotly_chart(barras_h((pdt["total"] / pdt["n"]).nlargest(10), fmt=brl), use_container_width=True)
        else:
            st.plotly_chart(barras_h(pdt["total"].nlargest(10)), use_container_width=True)
        insight("O total favorece partidos com mais deputados. A <b>média por deputado</b> é a comparação mais "
                "justa. Só entram partidos com 5 ou mais deputados, para que um único deputado não distorça o resultado.")
    st.subheader("Total por estado")
    st.plotly_chart(barras_h(ufd["total"], cor="#10b981"), use_container_width=True)

# ================================================================== FORNECEDORES
elif pagina == "🏢 Fornecedores":
    st.title("🏢 Fornecedores")
    st.markdown('<p class="q">Quem mais recebeu dinheiro da cota?</p>', unsafe_allow_html=True)
    forn = df.groupby("txtFornecedor")[V].sum().nlargest(10)
    st.subheader("Top 10 fornecedores")
    st.plotly_chart(barras_h(forn, cor="#06b6d4"), use_container_width=True)
    insight(f"💡 Os 10 maiores fornecedores receberam juntos <b>{mi(forn.sum())}</b>, ou "
            f"{forn.sum() / TOTAL * 100:.1f}% do total. Jornalistas e órgãos de controle podem verificar se há concentração.")

# ================================================================== ALERTAS
elif pagina == "🚨 Alertas":
    st.title("🚨 Alertas: gastos fora do padrão")
    st.markdown('<p class="q">Valores identificados como <i>outliers</i> pela regra do intervalo interquartil (IQR)</p>',
                unsafe_allow_html=True)
    kpis([("🚨", "#ef4444", "Gastos sinalizados", nf(NOUT)),
          ("📉", "#f59e0b", "% dos lançamentos", f"{NOUT / N * 100:.1f}%".replace(".", ",")),
          ("✂️", "#8b5cf6", "Total glosado pela Câmara", mi(GLOSA))])
    out = df[df["indicador_outlier_vlrLiquido"] == 1]
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Alertas por categoria")
        s = out.groupby("categoria").size().nlargest(6)
        st.plotly_chart(barras_h(s, fmt=lambda v: f"{nf(int(v))} alertas", cor="#ef4444"), use_container_width=True)
    with c2:
        st.subheader("Como funciona o alerta")
        q1, q3 = df[V].quantile(.25), df[V].quantile(.75)
        lim = q3 + 1.5 * (q3 - q1)
        st.markdown(f"""
- **Q1** (25% das notas abaixo): {brl(q1)}
- **Q3** (75% das notas abaixo): {brl(q3)}
- **IQR** = Q3 − Q1 = {brl(q3 - q1)}
- **Limite de alerta** = Q3 + 1,5 × IQR = **{brl(lim)}**

Toda nota acima desse limite recebe um alerta.""")
        insight("Os outliers <b>não foram apagados</b>: podem ser despesas reais. São marcados para que um cidadão "
                "ou auditor revise a nota fiscal.", alerta=True)
    st.subheader("15 maiores despesas individuais sinalizadas")
    t = out.nlargest(15, V)[["txNomeParlamentar", "categoria", "txtFornecedor", V, "datEmissao"]].copy()
    t["datEmissao"] = t["datEmissao"].astype(str).str[:10].replace("nan", "—")
    t.columns = ["Deputado", "Categoria", "Fornecedor", "Valor (R$)", "Data"]
    st.dataframe(t, use_container_width=True, hide_index=True,
                 column_config={"Valor (R$)": st.column_config.NumberColumn(format="R$ %.2f")})

# ================================================================== SOBRE
elif pagina == "⚙️ Sobre o projeto":
    st.title("⚙️ Sobre o projeto")
    st.markdown('<p class="q">Pipeline de Engenharia de Dados com Arquitetura Medalhão</p>', unsafe_allow_html=True)
    st.subheader("Pipeline ETL")
    st.markdown("""<div class="pipe">
<div class="st" style="background:#f6e7d3"><div class="e">🥉</div><b>Bronze (raw)</b><br>Ano-2025.csv baixado do portal de Dados Abertos da Câmara, guardado sem alterações.</div>
<div class="st" style="background:#e5e9f0"><div class="e">🥈</div><b>Prata (silver)</b><br><code>tratamento_ceap.py</code> (pandas): limpeza, tipos, datas ISO, duplicatas e outliers marcados.</div>
<div class="st" style="background:#fdf0b5"><div class="e">🥇</div><b>Ouro (gold)</b><br>Modelo estrela no MySQL com carga automatizada por <code>carregar_mysql.py</code>.</div>
<div class="st" style="background:#d7f5e1"><div class="e">📊</div><b>Visualização</b><br>Este painel em Streamlit + planejamento do Power BI com medidas DAX.</div>
</div>""", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Modelo estrela (DER)")
        st.graphviz_chart("""
digraph { rankdir=LR; node [shape=record, style=filled, fontname="Arial", fontsize=11];
  fato [label="{fato_despesa|PK despesa_key\\lFK parlamentar_key\\lFK categoria_key\\lFK fornecedor_key\\lvalor_liquido, data...\\l}", fillcolor="#dbeafe"];
  p [label="{dim_parlamentar|PK parlamentar_key\\lnome, uf, partido\\l}", fillcolor="#d1fae5"];
  c [label="{dim_categoria|PK categoria_key\\ldescrição\\l}", fillcolor="#fef3c7"];
  f [label="{dim_fornecedor|PK fornecedor_key\\lcnpj_cpf, nome\\l}", fillcolor="#ede9fe"];
  p -> fato; c -> fato; f -> fato; }""")
    with c2:
        st.subheader("Decisões de tratamento")
        st.table(pd.DataFrame({
            "Decisão": ["Textos com trim e padronização", "Datas convertidas (ISO-8601)", "Nulos mantidos vazios",
                        "Duplicatas só por linha idêntica", "Outliers sinalizados (IQR)", "Lideranças fora dos rankings"],
            "Por quê": ["Evita duplicar o mesmo fornecedor por causa de espaços.", "Permite análise por mês.",
                        "Trocar por zero distorce somas e médias.", "ideDocumento não é único (há notas em parcelas).",
                        "Podem ser reais e são o foco da fiscalização.", "Registros como LID.GOV-CD não são deputados."]}))
    st.subheader("Perguntas de negócio respondidas")
    st.table(pd.DataFrame({
        "Pergunta": ["Como os gastos evoluíram mês a mês em 2025?", "Em que categorias a cota é mais usada?",
                     "Quais deputados mais gastaram?", "Quais estados têm maior gasto médio por deputado?",
                     "Quais gastos fogem do padrão e merecem revisão?"],
        "Tela": ["Visão geral", "Categorias", "Deputados", "Estados e partidos", "Alertas"]},
        index=[1, 2, 3, 4, 5]))
    st.subheader("Impacto na sociedade")
    insight("O painel ajuda o cidadão a <b>votar e cobrar com base em fatos</b>: consultar o próprio deputado, comparar "
            "estados e partidos de forma justa e saber onde há gastos que merecem revisão. O site <b>não diz em quem "
            "votar</b>: mostra os dados para que cada pessoa decida com mais informação.")
