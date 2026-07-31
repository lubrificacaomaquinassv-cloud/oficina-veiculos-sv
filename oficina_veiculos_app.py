"""Oficina Veículos SV — Lançamento de OS (Leve, Pesado, Moto)."""
from __future__ import annotations

import re
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st
from supabase import Client, create_client

from sigcf_auth import exigir_acesso, logo_html

TZ_BR = ZoneInfo("America/Sao_Paulo")
SCHEMA = "oficina_veiculos"
MECANICO_PADRAO = "Andre Luis Brito Gomes"
PRESTADOR_INTERNO = "OFICINA INTERNA — SV"

TIPOS_SERVICO = [
    "ELETRICO",
    "HIDRAULICO",
    "SUSPENSAO",
    "FREIO",
    "CARDAN",
    "REVISAO GERAL",
    "TROCA DE OLEO",
]

CATEGORIAS = {
    "LEVE": "Veículo Leve",
    "PESADO": "Veículo Pesado (Linha Pesada)",
    "MOTO": "Motocicleta",
}

st.set_page_config(
    page_title="Oficina Veículos — SV",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700&display=swap');
[data-testid="stAppViewContainer"]{background:#0a1409;}
[data-testid="stSidebar"]{display:none;}
[data-testid="stHeader"]{background:#0a1409;}
h1,h2,h3,h4,p,span,label{color:#e8edd0;}
h1{font-family:'Barlow Condensed',sans-serif;letter-spacing:1px;}
.stCaption,[data-testid="stCaptionContainer"] p{color:#8aab80!important;}
.logo-frame{background:linear-gradient(145deg,#0a1628,#0d2040);border:2px solid #c9a227;
 border-radius:12px;padding:5px;display:inline-block;box-shadow:0 4px 18px rgba(0,0,0,.45);}
.logo-frame img{display:block;border-radius:8px;}
div[data-testid="stForm"]{background:#0d180c;border:1px solid #1e2e1c;border-radius:12px;padding:24px;}
div[data-testid="stSelectbox"] label,div[data-testid="stNumberInput"] label,
div[data-testid="stTextArea"] label,div[data-testid="stTextInput"] label,
div[data-testid="stRadio"] label,div[data-testid="stRadio"] p{
 color:#8aab80!important;font-family:'Barlow Condensed',sans-serif;
 text-transform:uppercase;letter-spacing:1px;font-size:12px!important;}
div[data-testid="stRadio"] div[role="radiogroup"] p{
 color:#e8edd0!important;font-size:14px!important;text-transform:none;}
.stTextInput input,.stNumberInput input,.stTextArea textarea{
 background:#dce6d2!important;color:#1a2818!important;
 border:1px solid #4a6644!important;border-radius:8px!important;}
div[data-baseweb="select"] > div{
 background:#dce6d2!important;border:1px solid #4a6644!important;
 color:#1a2818!important;border-radius:8px!important;}
.stNumberInput button{background:#cdd9c4!important;color:#1a2818!important;border:1px solid #4a6644!important;}
div[data-testid="stMetric"],div[data-testid="metric-container"]{
 background:#0d180c;border:1px solid #4a9e3f;border-radius:10px;padding:12px 18px;}
div[data-testid="stMetric"] label{color:#8aab80!important;}
div[data-testid="stMetricValue"]{color:#6fcf60!important;font-family:'Barlow Condensed',sans-serif;}
.stButton button,[data-testid="stFormSubmitButton"] button{
 background:#4a9e3f!important;color:#ffffff!important;border:1px solid #6fcf60!important;
 font-family:'Barlow Condensed',sans-serif;font-weight:700;letter-spacing:1.5px;
 text-transform:uppercase;border-radius:8px;padding:10px 28px;}
.stButton button:hover,[data-testid="stFormSubmitButton"] button:hover{background:#3d8534!important;}
.sec{font-family:'Barlow Condensed',sans-serif;font-size:12px;font-weight:700;
 letter-spacing:2px;text-transform:uppercase;color:#8aab80;
 border-left:4px solid #4a9e3f;padding-left:10px;margin:4px 0 10px;}
.os-table{width:100%;border-collapse:collapse;font-size:12px;}
.os-table th{color:#8aab80;text-transform:uppercase;font-size:10px;letter-spacing:1px;
 text-align:left;padding:6px 8px;border-bottom:1px solid #1e2e1c;font-family:'Barlow Condensed',sans-serif;}
.os-table td{color:#e8edd0;padding:6px 8px;border-bottom:1px solid #16241480;}
.st-fin{color:#6fcf60;font-weight:700;}
.st-pend{color:#d4a017;font-weight:700;}
.stTabs [data-baseweb="tab-list"]{gap:0;border-bottom:1px solid #1e2e1c;}
.stTabs [data-baseweb="tab"]{
 color:#8aab80!important;font-family:'Barlow Condensed',sans-serif;
 font-size:15px;font-weight:600;background:transparent!important;}
.stTabs [aria-selected="true"]{color:#e8edd0!important;border-bottom:3px solid #4a9e3f!important;}
</style>
"""


def parse_hora(txt: str | None):
    if not txt or not str(txt).strip():
        return None
    txt = str(txt).strip().replace("h", ":")
    m = re.match(r"^(\d{1,2}):(\d{2})(?::(\d{2}))?$", txt)
    if not m:
        return None
    h, mi = int(m.group(1)), int(m.group(2))
    if h > 23 or mi > 59:
        return None
    return datetime.strptime(f"{h:02d}:{mi:02d}", "%H:%M").time()


def fmt_dt_br(value) -> str:
    if not value:
        return "—"
    try:
        raw = str(value).strip().replace("Z", "+00:00")
        dt = datetime.fromisoformat(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo("UTC"))
        return dt.astimezone(TZ_BR).strftime("%d/%m/%Y %H:%M")
    except Exception:
        return str(value)[:16]


def calc_tempo_min(hora_entrada_txt: str, hora_saida_txt: str) -> int | None:
    he = parse_hora(hora_entrada_txt)
    hs = parse_hora(hora_saida_txt)
    if not he or not hs:
        return None
    dt_entrada = datetime.combine(datetime.today(), he)
    dt_saida = datetime.combine(datetime.today(), hs)
    if dt_saida <= dt_entrada:
        return None
    return int((dt_saida - dt_entrada).total_seconds() / 60)


@st.cache_resource
def get_supabase() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


def tbl(sb: Client, nome: str):
    return sb.schema(SCHEMA).from_(nome)


def proximo_numero_os(sb: Client) -> str:
    res = tbl(sb, "ordens_servico").select("numero_os").order("created_at", desc=True).limit(200).execute()
    nums = []
    for row in res.data or []:
        n = row.get("numero_os", "")
        if n.startswith("OS-V-"):
            try:
                nums.append(int(n.replace("OS-V-", "")))
            except ValueError:
                pass
    seq = max(nums) + 1 if nums else 1
    return f"OS-V-{seq:04d}"


@st.cache_data(ttl=30)
def carregar_veiculos(categoria: str | None = None):
    sb = get_supabase()
    q = tbl(sb, "veiculos").select("id, placa, modelo, categoria").eq("ativo", True).order("modelo")
    if categoria:
        q = q.eq("categoria", categoria)
    return q.execute().data or []


@st.cache_data(ttl=30)
def carregar_prestadores():
    sb = get_supabase()
    res = tbl(sb, "prestadores").select("id, nome").eq("ativo", True).order("nome").execute()
    return res.data or []


@st.cache_data(ttl=30)
def carregar_mecanicos():
    sb = get_supabase()
    res = tbl(sb, "mecanicos").select("nome, custo_hora, responsavel").eq("ativo", True).order("nome").execute()
    return res.data or []


@st.cache_data(ttl=10)
def carregar_os(limit: int = 100):
    sb = get_supabase()
    res = (
        tbl(sb, "ordens_servico")
        .select("*")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return res.data or []


@st.cache_data(ttl=10)
def carregar_os_pendentes():
    sb = get_supabase()
    res = (
        tbl(sb, "ordens_servico")
        .select("*")
        .eq("status", "PENDENTE")
        .order("created_at", desc=True)
        .execute()
    )
    return res.data or []


@st.cache_data(ttl=15)
def carregar_painel():
    sb = get_supabase()
    resumo = tbl(sb, "v_painel_resumo").select("*").limit(1).execute().data or [{}]
    prest = tbl(sb, "v_prestadores_ranking").select("*").execute().data or []
    tipos = tbl(sb, "v_tipos_servico_ranking").select("*").execute().data or []
    return resumo[0], prest, tipos


def label_veiculo(v: dict) -> str:
    return f"{v['placa']} — {v['modelo']}"


def render_tabela_os(rows: list[dict], limite: int = 15):
    if not rows:
        st.info("Nenhuma OS registrada.")
        return
    linhas = ""
    for o in rows[:limite]:
        status = str(o.get("status", "—")).upper()
        cls = "st-fin" if "FINAL" in status else "st-pend"
        linhas += (
            f"<tr><td>{o.get('numero_os', '—')}</td>"
            f"<td>{CATEGORIAS.get(o.get('categoria_veiculo', ''), o.get('categoria_veiculo', '—'))}</td>"
            f"<td>{o.get('placa', '—')}</td>"
            f"<td>{o.get('tipo_servico', '—')}</td>"
            f"<td>{o.get('prestador_nome') or PRESTADOR_INTERNO}</td>"
            f"<td>{o.get('mecanico', '—')}</td>"
            f"<td class='{cls}'>{status}</td>"
            f"<td>{fmt_dt_br(o.get('created_at'))}</td></tr>"
        )
    st.markdown(
        "<table class='os-table'>"
        "<tr><th>OS</th><th>Categoria</th><th>Placa</th><th>Serviço</th>"
        "<th>Prestador</th><th>Mecânico</th><th>Status</th><th>Data/Hora</th></tr>"
        f"{linhas}</table>",
        unsafe_allow_html=True,
    )


def render_formulario_os(
    sb: Client,
    *,
    modo_edicao: bool = False,
    os_existente: dict | None = None,
):
    prestadores = carregar_prestadores()
    mecanicos = carregar_mecanicos()
    nomes_mecanicos = [m["nome"] for m in mecanicos] or [MECANICO_PADRAO]
    if MECANICO_PADRAO not in nomes_mecanicos:
        nomes_mecanicos.insert(0, MECANICO_PADRAO)

    opcoes_prestador = [PRESTADOR_INTERNO] + [p["nome"] for p in prestadores]
    prest_map = {p["nome"]: p["id"] for p in prestadores}

    defaults = os_existente or {}
    cat_default = defaults.get("categoria_veiculo", "LEVE")
    idx_cat = list(CATEGORIAS.keys()).index(cat_default) if cat_default in CATEGORIAS else 0

    numero_os = defaults.get("numero_os") or proximo_numero_os(sb)

    with st.form("form_os_veiculos", clear_on_submit=not modo_edicao):
        col_os, _ = st.columns([1, 3])
        with col_os:
            st.metric("O.S. ATUAL", numero_os)

        categoria = st.selectbox(
            "Categoria do Veículo",
            options=list(CATEGORIAS.keys()),
            format_func=lambda x: CATEGORIAS[x],
            index=idx_cat,
            disabled=modo_edicao,
        )

        veiculos = carregar_veiculos(categoria)
        if not veiculos:
            st.warning(
                f"Nenhum veículo cadastrado em {CATEGORIAS[categoria]}. "
                "Use a aba Cadastros para incluir."
            )
            labels_veic = ["—"]
            veic_map = {}
        else:
            labels_veic = [label_veiculo(v) for v in veiculos]
            veic_map = {label_veiculo(v): v for v in veiculos}

        placa_default = defaults.get("placa", "")
        idx_veic = 0
        for i, lbl in enumerate(labels_veic):
            if placa_default and lbl.startswith(placa_default):
                idx_veic = i
                break

        c1, c2 = st.columns(2)

        with c1:
            veic_sel = st.selectbox("Selecione o Veículo", options=labels_veic, index=idx_veic)
            mec_idx = nomes_mecanicos.index(defaults["mecanico"]) if defaults.get("mecanico") in nomes_mecanicos else (
                nomes_mecanicos.index(MECANICO_PADRAO) if MECANICO_PADRAO in nomes_mecanicos else 0
            )
            mecanico = st.selectbox("Mecânico", options=nomes_mecanicos, index=mec_idx)
            tipo_idx = TIPOS_SERVICO.index(defaults["tipo_servico"]) if defaults.get("tipo_servico") in TIPOS_SERVICO else 0
            tipo_servico = st.selectbox("Tipo de Serviço", options=TIPOS_SERVICO, index=tipo_idx)
            prest_default = defaults.get("prestador_nome") or PRESTADOR_INTERNO
            prest_idx = opcoes_prestador.index(prest_default) if prest_default in opcoes_prestador else 0
            prestador_sel = st.selectbox("Prestador de Serviço", options=opcoes_prestador, index=prest_idx)
            operador = st.text_input(
                "Operador (apontado no equipamento)",
                value=defaults.get("operador") or "",
                placeholder="Digite o nome do operador",
            )

        with c2:
            horimetro = st.number_input(
                "Horímetro ou KM Atual",
                min_value=0.0,
                step=0.1,
                format="%.1f",
                value=float(defaults.get("horimetro_km") or 0.0),
            )
            hora_entrada_txt = st.text_input(
                "Hora Entrada",
                value=defaults.get("hora_entrada") or "",
                placeholder="Ex: 08:30",
            )
            hora_saida_txt = st.text_input(
                "Hora Saída",
                value=defaults.get("hora_saida") or "",
                placeholder="Ex: 14:30",
            )
            status_default = defaults.get("status", "PENDENTE")
            status_idx = 0 if status_default == "FINALIZADO" else 1
            status_os = st.radio("Status", ["FINALIZADO", "PENDENTE"], horizontal=True, index=status_idx)

            odometro_ultima = st.number_input(
                "Odômetro da Última Troca de Óleo",
                min_value=0.0,
                step=0.1,
                format="%.1f",
                value=float(defaults.get("odometro_ultima_troca") or 0.0),
                help="Obrigatório quando o tipo de serviço for TROCA DE OLEO.",
            )

        descricao = st.text_area(
            "Descrição do Serviço e Peças Aplicadas",
            value=defaults.get("descricao") or "",
            max_chars=500,
        )
        observacao = st.text_area(
            "Observação",
            value=defaults.get("observacao") or "",
            max_chars=300,
        )

        label_btn = "✅ ATUALIZAR OS" if modo_edicao else "✅ SALVAR NO SISTEMA"
        enviar = st.form_submit_button(label_btn)

    if not enviar:
        return

    if not veiculos or veic_sel == "—":
        st.warning("Selecione ou cadastre um veículo.")
        return

    if hora_entrada_txt.strip() and not parse_hora(hora_entrada_txt):
        st.warning("Hora de entrada inválida. Use HH:MM (ex: 08:30).")
        return
    if hora_saida_txt.strip() and not parse_hora(hora_saida_txt):
        st.warning("Hora de saída inválida. Use HH:MM (ex: 14:30).")
        return
    if not descricao.strip():
        st.warning("Descrição é obrigatória.")
        return
    if tipo_servico == "TROCA DE OLEO" and (odometro_ultima is None or odometro_ultima <= 0):
        st.warning("Informe o odômetro da última troca de óleo.")
        return

    veic = veic_map[veic_sel]
    he = parse_hora(hora_entrada_txt)
    hs = parse_hora(hora_saida_txt)
    tempo_min = calc_tempo_min(hora_entrada_txt, hora_saida_txt)

    prestador_id = prest_map.get(prestador_sel) if prestador_sel != PRESTADOR_INTERNO else None
    prestador_nome = None if prestador_sel == PRESTADOR_INTERNO else prestador_sel

    payload = {
        "categoria_veiculo": categoria,
        "veiculo_id": veic["id"],
        "placa": veic["placa"],
        "modelo": veic["modelo"],
        "horimetro_km": horimetro,
        "mecanico": mecanico,
        "prestador_id": prestador_id,
        "prestador_nome": prestador_nome,
        "tipo_servico": tipo_servico,
        "hora_entrada": str(he) if he else None,
        "hora_saida": str(hs) if hs else None,
        "tempo_min": tempo_min,
        "operador": (operador.strip().upper() or None),
        "status": status_os,
        "descricao": descricao.strip(),
        "observacao": observacao.strip() or None,
        "odometro_ultima_troca": odometro_ultima if tipo_servico == "TROCA DE OLEO" else None,
        "updated_at": datetime.now(TZ_BR).isoformat(),
    }

    try:
        if modo_edicao and os_existente:
            tbl(sb, "ordens_servico").update(payload).eq("id", os_existente["id"]).execute()
            st.success(f"✅ {numero_os} atualizada! Status: {status_os}")
        else:
            payload["numero_os"] = numero_os
            tbl(sb, "ordens_servico").insert(payload).execute()
            msg = f"✅ {numero_os} registrada!"
            if tempo_min:
                msg += f" Tempo: {tempo_min} min"
            st.success(msg)
        st.cache_data.clear()
        st.rerun()
    except Exception as exc:
        st.error(f"Erro ao salvar: {exc}")


def render_painel():
    try:
        resumo, prest_rank, tipos_rank = carregar_painel()
    except Exception as exc:
        st.error(
            f"Não foi possível carregar o painel. Verifique se o schema "
            f"'{SCHEMA}' foi aplicado e exposto no Supabase. Detalhe: {exc}"
        )
        return

    st.markdown('<div class="sec">📊 Resumo acumulado</div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total OS", resumo.get("total_os", 0))
    c2.metric("Veículos Leves", resumo.get("os_leve", 0))
    c3.metric("Veículos Pesados", resumo.get("os_pesado", 0))
    c4.metric("Motos", resumo.get("os_moto", 0))
    c5.metric("Pendentes", resumo.get("pendentes", 0))

    st.markdown('<div class="sec">🏆 Prestadores com mais chamados</div>', unsafe_allow_html=True)
    if prest_rank:
        df_p = pd.DataFrame(prest_rank)
        st.bar_chart(df_p.set_index("prestador")["qtd_os"], color="#4a9e3f")
        st.dataframe(
            df_p.rename(columns={"prestador": "Prestador", "qtd_os": "Qtd OS"}),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Sem dados de prestadores ainda.")

    st.markdown('<div class="sec">🔧 Tipos de serviço</div>', unsafe_allow_html=True)
    if tipos_rank:
        df_t = pd.DataFrame(tipos_rank)
        st.bar_chart(df_t.set_index("tipo_servico")["qtd_os"], color="#6fcf60")
        st.dataframe(
            df_t.rename(columns={"tipo_servico": "Tipo", "qtd_os": "Qtd OS"}),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Sem dados de serviços ainda.")


def render_cadastros(sb: Client):
    st.markdown('<div class="sec">🚗 Cadastrar veículo</div>', unsafe_allow_html=True)
    with st.form("form_veiculo"):
        cv1, cv2, cv3 = st.columns(3)
        with cv1:
            cat_nova = st.selectbox(
                "Categoria",
                options=list(CATEGORIAS.keys()),
                format_func=lambda x: CATEGORIAS[x],
                key="cad_cat",
            )
        with cv2:
            placa_nova = st.text_input("Placa", placeholder="Ex: ABC1D23").upper()
        with cv3:
            modelo_novo = st.text_input("Modelo", placeholder="Ex: KWID / SCANIA / CG 160")
        salvar_v = st.form_submit_button("Cadastrar Veículo")

    if salvar_v:
        if not placa_nova.strip() or not modelo_novo.strip():
            st.warning("Informe placa e modelo.")
        else:
            try:
                tbl(sb, "veiculos").insert({
                    "placa": placa_nova.strip().upper(),
                    "modelo": modelo_novo.strip().upper(),
                    "categoria": cat_nova,
                }).execute()
                st.success(f"Veículo {placa_nova} cadastrado.")
                st.cache_data.clear()
                st.rerun()
            except Exception as exc:
                st.error(f"Erro: {exc}")

    st.markdown('<div class="sec">👷 Mecânicos — custo/hora</div>', unsafe_allow_html=True)
    mecanicos = carregar_mecanicos()
    if mecanicos:
        df_m = pd.DataFrame(mecanicos)
        st.dataframe(
            df_m.rename(columns={
                "nome": "Mecânico",
                "custo_hora": "Custo/h (R$)",
                "responsavel": "Responsável",
            }),
            use_container_width=True,
            hide_index=True,
        )
    with st.form("form_mec_custo"):
        mc1, mc2 = st.columns(2)
        with mc1:
            mec_nome = st.selectbox(
                "Mecânico",
                options=[m["nome"] for m in mecanicos] or [MECANICO_PADRAO],
            )
        with mc2:
            custo_h = st.number_input("Custo hora (R$)", min_value=0.0, step=0.01, format="%.2f")
        salvar_c = st.form_submit_button("Atualizar Custo/Hora")
    if salvar_c:
        try:
            tbl(sb, "mecanicos").update({"custo_hora": custo_h}).eq("nome", mec_nome).execute()
            st.success(f"Custo/hora de {mec_nome} atualizado.")
            st.cache_data.clear()
            st.rerun()
        except Exception as exc:
            st.error(f"Erro: {exc}")

    st.markdown('<div class="sec">🏢 Prestadores cadastrados</div>', unsafe_allow_html=True)
    prestadores = carregar_prestadores()
    if prestadores:
        st.dataframe(
            pd.DataFrame(prestadores)[["nome"]].rename(columns={"nome": "Prestador"}),
            use_container_width=True,
            hide_index=True,
        )


# ── App principal ───────────────────────────────────────────────────────────
exigir_acesso("Ordem de Serviço — Oficina Veículos", "SIGCF | Controladoria — Gestão e Análise de Dados")
st.markdown(CSS, unsafe_allow_html=True)

col_logo, col_titulo = st.columns([1.1, 5.9])
with col_logo:
    st.markdown(logo_html(118), unsafe_allow_html=True)
with col_titulo:
    st.title("🔧 ORDEM DE SERVIÇO — OFICINA VEÍCULOS")
    st.caption("SIGCF | CONTROLADORIA — GESTÃO E ANÁLISE DE DADOS · Leve · Pesado · Moto")

st.divider()

try:
    sb = get_supabase()
except Exception as exc:
    st.error(f"Configure SUPABASE_URL e SUPABASE_KEY nos Secrets. Erro: {exc}")
    st.stop()

aba_lanc, aba_edit, aba_painel, aba_cad = st.tabs([
    "📝 Nova OS",
    "✏️ Editar OS Pendente",
    "📊 Painel",
    "⚙️ Cadastros",
])

with aba_lanc:
    render_formulario_os(sb, modo_edicao=False)

with aba_edit:
    pendentes = carregar_os_pendentes()
    if not pendentes:
        st.info("Nenhuma OS pendente. Abra uma nova OS e deixe o status como PENDENTE.")
    else:
        opcoes = [
            f"{o['numero_os']} | {o['placa']} | {o['tipo_servico']} | {o['mecanico']}"
            for o in pendentes
        ]
        sel = st.selectbox("Selecione a OS para editar/concluir", options=opcoes)
        idx = opcoes.index(sel)
        os_sel = pendentes[idx]
        st.caption(f"Criada em {fmt_dt_br(os_sel.get('created_at'))} · {CATEGORIAS.get(os_sel.get('categoria_veiculo'), '')}")
        render_formulario_os(sb, modo_edicao=True, os_existente=os_sel)

with aba_painel:
    render_painel()

with aba_cad:
    render_cadastros(sb)

st.divider()
st.markdown('<div class="sec">🕒 Últimas OS lançadas</div>', unsafe_allow_html=True)
render_tabela_os(carregar_os(), limite=12)
st.caption("Horário de Brasília · Mecânico responsável: Andre Luis Brito Gomes")
st.divider()
st.caption("SIGCF | Oficina Veículos SV | Controladoria Bataguassu-MS")
