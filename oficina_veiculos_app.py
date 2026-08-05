"""Oficina Veículos SV — Lançamento de OS (Leve, Pesado, Moto)."""
from __future__ import annotations

import re
from datetime import date, datetime
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st
from supabase import Client

from sigcf_auth import BG_URL, LOGO_URL, conectar_supabase, exigir_acesso, link_instagram, logo_html

TZ_BR = ZoneInfo("America/Sao_Paulo")
SCHEMA = "oficina_veiculos"
MECANICO_PADRAO = "ANDRE LUIS BRITO GOMES"
PRESTADOR_INTERNO = "OFICINA INTERNA — SV"

ITENS_FINANCEIRO = ["PECAS", "TROCA DE OLEO", "M.O. MECANICO", "OUTROS"]

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
.stApp{
 background:linear-gradient(rgba(10,20,9,0.68),rgba(10,20,9,0.82)),
 url('__BG__') center center/cover no-repeat fixed!important;}
[data-testid="stAppViewContainer"]{background:transparent!important;}
[data-testid="stSidebar"]{display:none;}
[data-testid="stHeader"]{background:rgba(10,20,9,0.45)!important;}
[data-testid="stDecoration"]{display:none!important;}
.block-container{background:transparent!important;max-width:1240px!important;
 padding-top:2.75rem!important;padding-bottom:2rem!important;}
header[data-testid="stHeader"]{background:rgba(10,20,9,0.55)!important;}
.sv-header-row{margin-top:0.25rem;margin-bottom:0.5rem;}
[data-testid="stImage"] img{border-radius:8px;}
h1,h2,h3,h4,p,span,label{color:#e8edd0;}
h1{font-family:'Barlow Condensed',sans-serif;letter-spacing:1px;}
.stCaption,[data-testid="stCaptionContainer"] p{color:#9ab892!important;}
.logo-frame{background:linear-gradient(145deg,#0a1628,#0d2040);border:2px solid #c9a227;
 border-radius:12px;padding:5px;display:inline-block;box-shadow:0 4px 18px rgba(0,0,0,.45);}
.logo-frame img{display:block;border-radius:8px;}
.insta-link{display:inline-flex;align-items:center;gap:6px;color:#8ec486!important;
 text-decoration:none;font-weight:600;}
.insta-link:hover{color:#a8d8a0!important;text-decoration:none;}
.insta-ico{width:17px;height:17px;flex-shrink:0;}
div[data-testid="stForm"]{
 background:rgba(13,24,12,0.88)!important;border:1px solid #2a3d28!important;
 border-radius:14px;padding:20px 22px;}
.os-badge{display:inline-flex;flex-direction:column;align-items:flex-start;
 background:rgba(13,24,12,0.92);border:2px solid #5a9452;border-radius:12px;
 padding:8px 20px;margin-bottom:4px;}
.os-badge-lbl{font-family:'Barlow Condensed',sans-serif;font-size:10px;color:#9ab892;
 letter-spacing:2px;text-transform:uppercase;font-weight:700;}
.os-badge-num{font-family:'Barlow Condensed',sans-serif;font-size:26px;font-weight:700;
 color:#8ec486;line-height:1.15;letter-spacing:1px;}
.ctx-bar{background:rgba(13,24,12,0.72);border:1px solid #2a3d28;border-radius:10px;
 padding:8px 14px;margin:0 0 14px;}
.form-spacer{height:4px;}
div[data-testid="stSelectbox"] label,div[data-testid="stNumberInput"] label,
div[data-testid="stTextArea"] label,div[data-testid="stTextInput"] label,
div[data-testid="stRadio"] label,div[data-testid="stRadio"] p{
 color:#9ab892!important;font-family:'Barlow Condensed',sans-serif;
 text-transform:uppercase;letter-spacing:1px;font-size:12px!important;}
div[data-testid="stRadio"] div[role="radiogroup"] p{
 color:#e8edd0!important;font-size:14px!important;text-transform:none;}
.stTextInput input,.stNumberInput input,.stTextArea textarea,
[data-testid="stDateInput"] input{
 background:#dce6d2!important;color:#1a2818!important;
 border:1px solid #4a6644!important;border-radius:8px!important;}
.stTextInput input:focus,.stNumberInput input:focus,.stTextArea textarea:focus{
 border-color:#6fcf60!important;box-shadow:0 0 0 1px #6fcf6044!important;}
div[data-baseweb="select"] > div{
 background:#dce6d2!important;border:1px solid #4a6644!important;
 color:#1a2818!important;border-radius:8px!important;}
div[data-baseweb="select"] div{color:#1a2818!important;}
div[data-baseweb="select"] svg{fill:#4a6644!important;}
ul[data-testid="stSelectboxVirtualDropdown"],div[data-baseweb="popover"] ul{background:#e8edd0!important;}
div[data-baseweb="popover"] li{color:#1a2818!important;}
.stNumberInput button{background:#cdd9c4!important;color:#1a2818!important;border:1px solid #4a6644!important;}
div[data-testid="stMetric"],div[data-testid="metric-container"]{
 background:rgba(13,24,12,0.88);border:1px solid #2a3d28;border-radius:10px;padding:12px 18px;}
div[data-testid="stMetric"] label{color:#9ab892!important;}
div[data-testid="stMetricValue"]{color:#8ec486!important;font-family:'Barlow Condensed',sans-serif;}
.stButton button,[data-testid="stFormSubmitButton"] button{
 background:#4a9e3f!important;color:#ffffff!important;border:1px solid #6fa864!important;
 font-family:'Barlow Condensed',sans-serif;font-weight:700;letter-spacing:1.5px;
 text-transform:uppercase;border-radius:8px;min-height:44px;padding:10px 28px;}
.stButton button:hover,[data-testid="stFormSubmitButton"] button:hover{background:#3d8534!important;}
.stButton button p,[data-testid="stFormSubmitButton"] button p{color:#ffffff!important;font-weight:700;}
.sec{font-family:'Barlow Condensed',sans-serif;font-size:12px;font-weight:700;
 letter-spacing:2px;text-transform:uppercase;color:#9ab892;
 border-left:4px solid #5a9452;padding-left:10px;margin:8px 0 12px;}
.os-table{width:100%;border-collapse:collapse;font-size:12px;background:rgba(13,24,12,0.88);}
.os-table th{color:#9ab892;text-transform:uppercase;font-size:10px;letter-spacing:1px;
 text-align:left;padding:6px 8px;border-bottom:1px solid #1e2e1c;font-family:'Barlow Condensed',sans-serif;}
.os-table td{color:#e8edd0;padding:6px 8px;border-bottom:1px solid #16241480;}
.st-fin{color:#8ec486;font-weight:700;}
.st-pend{color:#d4a017;font-weight:700;}
.stTabs [data-baseweb="tab-list"]{background:rgba(13,24,12,0.88);border-bottom:1px solid #2a3d28;gap:8px;}
.stTabs [data-baseweb="tab"]{
 color:#9ab892!important;font-family:'Barlow Condensed',sans-serif;
 font-size:15px;font-weight:600;background:transparent!important;}
.stTabs [aria-selected="true"]{color:#e8edd0!important;border-bottom-color:#5a9452!important;}
.stTabs [data-baseweb="tab-highlight"]{background-color:#5a9452!important;}
@media (max-width:768px){
 .block-container{padding-left:0.75rem!important;padding-right:0.75rem!important;}
 div[data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;}
}
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
    return conectar_supabase()


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
def carregar_veiculos(categoria: str):
    sb = get_supabase()
    return (
        tbl(sb, "veiculos")
        .select("id, placa, modelo, categoria")
        .eq("ativo", True)
        .eq("categoria", categoria)
        .order("placa")
        .execute()
        .data
        or []
    )


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


def opcao_veiculo(v: dict, categoria: str) -> str:
    """Leve: só placa. Pesado/Moto: frota - modelo para identificação."""
    if categoria == "LEVE":
        return str(v["placa"])
    return f"{v['placa']} - {v['modelo']}"


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
            f"<td>{CATEGORIAS.get(o.get('categoria', ''), o.get('categoria', '—'))}</td>"
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
    categoria: str,
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
    numero_os = defaults.get("numero_os") or proximo_numero_os(sb)

    veiculos = carregar_veiculos(categoria)
    if not veiculos:
        st.warning(
            f"Nenhum veículo cadastrado em {CATEGORIAS[categoria]}. "
            "Use a aba Cadastros para incluir."
        )

    opcoes_veic = [opcao_veiculo(v, categoria) for v in veiculos] or ["—"]
    veic_map = {opcao_veiculo(v, categoria): v for v in veiculos}
    placa_default = defaults.get("placa", "")
    idx_veic = next(
        (i for i, v in enumerate(veiculos) if v["placa"] == placa_default),
        0,
    )

    with st.form("form_os_veiculos", clear_on_submit=not modo_edicao):
        st.markdown(
            f'<div class="os-badge"><span class="os-badge-lbl">O.S. ATUAL</span>'
            f'<span class="os-badge-num">{numero_os}</span></div>',
            unsafe_allow_html=True,
        )

        r1a, r1b, r1c = st.columns([2.2, 1.4, 1.4])
        with r1a:
            veic_sel = st.selectbox("Selecione o Veículo", options=opcoes_veic, index=idx_veic)
        with r1b:
            mec_idx = nomes_mecanicos.index(defaults["mecanico"]) if defaults.get("mecanico") in nomes_mecanicos else (
                nomes_mecanicos.index(MECANICO_PADRAO) if MECANICO_PADRAO in nomes_mecanicos else 0
            )
            mecanico = st.selectbox("Mecânico", options=nomes_mecanicos, index=mec_idx)
        with r1c:
            tipo_idx = TIPOS_SERVICO.index(defaults["tipo_servico"]) if defaults.get("tipo_servico") in TIPOS_SERVICO else 0
            tipo_servico = st.selectbox("Tipo de Serviço", options=TIPOS_SERVICO, index=tipo_idx)

        r2a, r2b, r2c = st.columns([2, 1, 1.2])
        with r2a:
            prest_default = defaults.get("prestador_nome") or PRESTADOR_INTERNO
            prest_idx = opcoes_prestador.index(prest_default) if prest_default in opcoes_prestador else 0
            prestador_sel = st.selectbox("Prestador de Serviço", options=opcoes_prestador, index=prest_idx)
        with r2b:
            horimetro = st.number_input(
                "Horímetro ou KM Atual",
                min_value=0.0,
                step=0.1,
                format="%.1f",
                value=float(defaults.get("horimetro_km") or 0.0),
            )
        with r2c:
            operador = st.text_input(
                "Operador (apontado no equipamento)",
                value=defaults.get("operador") or "",
                placeholder="Nome do operador",
            )

        r3a, r3b, r3c = st.columns([1, 1, 1.2])
        with r3a:
            hora_entrada_txt = st.text_input(
                "Hora Entrada",
                value=defaults.get("hora_entrada") or "",
                placeholder="Ex: 08:30",
            )
        with r3b:
            hora_saida_txt = st.text_input(
                "Hora Saída",
                value=defaults.get("hora_saida") or "",
                placeholder="Ex: 14:30",
            )
        with r3c:
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

        r4a, r4b = st.columns(2)
        with r4a:
            descricao = st.text_area(
                "Descrição do Serviço e Peças Aplicadas",
                value=defaults.get("descricao") or "",
                max_chars=500,
                height=120,
            )
        with r4b:
            observacao = st.text_area(
                "Observação",
                value=defaults.get("observacao") or "",
                max_chars=300,
                height=120,
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
        "categoria": categoria,
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
        "tempo_minutos": tempo_min,
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


def fmt_moeda(v) -> str:
    try:
        return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (TypeError, ValueError):
        return "R$ 0,00"


def dark_table_fin(df: pd.DataFrame, height: int = 280):
    if df.empty:
        st.info("Nenhum registro.")
        return
    rows = "".join(
        "<tr>"
        + "".join(
            f'<td style="padding:6px 10px;border-bottom:1px solid #1e2e1c;'
            f'color:#e8edd0;font-size:12px;white-space:nowrap;">{v}</td>'
            for v in row
        )
        + "</tr>"
        for _, row in df.iterrows()
    )
    headers = "".join(
        f'<th style="padding:7px 10px;background:#111c10;color:#9ab892;font-size:10px;'
        f'font-weight:700;text-transform:uppercase;letter-spacing:1px;'
        f'border-bottom:2px solid #1e2e1c;">{c}</th>'
        for c in df.columns
    )
    st.markdown(
        f'<div style="overflow-x:auto;border:1px solid #1e2e1c;border-radius:10px;">'
        f'<div style="max-height:{height}px;overflow-y:auto;">'
        f'<table style="width:100%;border-collapse:collapse;background:rgba(13,24,12,0.88);'
        f'font-family:Barlow Condensed,sans-serif;"><thead><tr>{headers}</tr></thead>'
        f'<tbody>{rows}</tbody></table></div></div>',
        unsafe_allow_html=True,
    )


@st.cache_data(ttl=10)
def carregar_financeiro_custos(limit: int = 500):
    sb = get_supabase()
    cols = (
        "id, os_id, numero_os, data, categoria, placa, mecanico, item, "
        "tipo_manutencao, descricao_peca, nfe, id_fornecedor_sap, quantidade, "
        "valor_unitario, valor, tempo_minutos_mecanico, custo_hora_mecanico, "
        "custo_mo_mecanico, observacao, created_at"
    )
    queries = [
        lambda: (
            tbl(sb, "financeiro_custos")
            .select(cols)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        ),
        lambda: (
            tbl(sb, "financeiro_custos")
            .select(cols)
            .order("data", desc=True)
            .limit(limit)
            .execute()
        ),
        lambda: (
            tbl(sb, "financeiro_custos")
            .select("*")
            .limit(limit)
            .execute()
        ),
    ]
    last_exc = None
    for run in queries:
        try:
            return run().data or []
        except Exception as exc:
            last_exc = exc
    raise last_exc or RuntimeError("financeiro_custos indisponivel")


@st.cache_data(ttl=15)
def carregar_os_para_financeiro():
    sb = get_supabase()
    res = (
        tbl(sb, "ordens_servico")
        .select(
            "id, numero_os, placa, modelo, categoria, mecanico, "
            "tipo_servico, tempo_minutos, status, hora_entrada, hora_saida"
        )
        .order("created_at", desc=True)
        .limit(200)
        .execute()
    )
    return res.data or []


def lancamentos_do_dia(rows: list, data_ref: date) -> list:
    data_str = str(data_ref)
    return [r for r in rows if str(r.get("data", ""))[:10] == data_str]


def custo_map_mecanicos() -> dict[str, float]:
    return {
        m["nome"]: float(m.get("custo_hora") or 0)
        for m in carregar_mecanicos()
    }


def calcular_mo_mecanico(os_row: dict) -> tuple[int, float, float]:
    tempo = int(os_row.get("tempo_minutos") or 0)
    if tempo <= 0:
        he, hs = os_row.get("hora_entrada"), os_row.get("hora_saida")
        if he and hs:
            tempo = calc_tempo_min(str(he), str(hs)) or 0
    custo_h = custo_map_mecanicos().get(os_row.get("mecanico", ""), 0.0)
    custo_mo = round((tempo / 60) * custo_h, 2) if tempo and custo_h else 0.0
    return tempo, custo_h, custo_mo


def label_os_fin(o: dict) -> str:
    cat = o.get("categoria", "")
    placa = o.get("placa", "")
    if cat in ("PESADO", "MOTO") and o.get("modelo"):
        veic = f"{placa} - {o['modelo']}"
    else:
        veic = placa
    return f"{o['numero_os']} | {veic} | {o.get('tipo_servico', '')} | {o.get('status', '')}"


def render_financeiro(sb: Client):
    st.markdown(
        '<div class="sec">💰 Lançamentos financeiros — custo veículos</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Peças, troca de óleo e M.O. do mecânico (hora parada). "
        "Sem hora de operador — leves e motos permanecem na adm."
    )

    lancamentos = []
    try:
        lancamentos = carregar_financeiro_custos()
    except Exception as exc:
        st.error(
            "Não foi possível carregar lançamentos financeiros. "
            "Verifique se a migração 006/007 foi aplicada no Supabase "
            f"(tabela `oficina_veiculos.financeiro_custos`). Detalhe: {exc}"
        )
    os_list = carregar_os_para_financeiro()

    st.markdown('<div class="sec">Resumo do dia</div>', unsafe_allow_html=True)
    fc1, fc2, fc3 = st.columns([2, 1, 1])
    with fc1:
        filtro_data = st.date_input(
            "Filtrar por data",
            value=date.today(),
            format="DD/MM/YYYY",
            key="fin_data_filtro",
        )
    lanc_dia = lancamentos_do_dia(lancamentos, filtro_data)
    total_dia = sum(float(l.get("valor") or 0) for l in lanc_dia)
    with fc2:
        st.metric("Total do dia", fmt_moeda(total_dia))
    with fc3:
        st.metric("Lançamentos", len(lanc_dia))

    if not os_list:
        st.warning("Cadastre e finalize OS antes de lançar custos.")
        return

    st.markdown('<div class="sec">Novo lançamento vinculado à OS</div>', unsafe_allow_html=True)

    opcoes_os = [label_os_fin(o) for o in os_list]
    os_map = {label_os_fin(o): o for o in os_list}
    os_sel_label = st.selectbox("Selecione a OS", options=opcoes_os, key="fin_os_sel")
    os_sel = os_map[os_sel_label]

    tempo_min, custo_h, custo_mo = calcular_mo_mecanico(os_sel)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("OS", os_sel.get("numero_os", "—"))
    k2.metric("Placa / Frota", os_sel.get("placa", "—"))
    k3.metric("Tempo mecânico", f"{tempo_min} min")
    k4.metric("M.O. mecânico (calc.)", fmt_moeda(custo_mo))

    if custo_h <= 0:
        st.info(
            "Cadastre o **custo/hora** do mecânico na aba Cadastros para calcular a M.O. automaticamente."
        )

    with st.form("form_fin_veiculos", clear_on_submit=True):
        r1a, r1b, r1c = st.columns(3)
        with r1a:
            data_lanc = st.date_input("📅 Data *", value=date.today(), format="DD/MM/YYYY")
        with r1b:
            nfe = st.text_input("🧾 NFE")
        with r1c:
            id_fornecedor = st.text_input("🏭 ID Fornecedor SAP")

        r2a, r2b, r2c = st.columns(3)
        with r2a:
            item = st.selectbox("📦 Item *", options=ITENS_FINANCEIRO)
        with r2b:
            tipo_manut = st.selectbox(
                "🔧 Tipo de manutenção *",
                options=TIPOS_SERVICO,
                index=TIPOS_SERVICO.index(os_sel["tipo_servico"])
                if os_sel.get("tipo_servico") in TIPOS_SERVICO
                else 0,
            )
        with r2c:
            if item == "M.O. MECANICO":
                valor = st.number_input(
                    "💰 Valor M.O. mecânico (R$) *",
                    min_value=0.0,
                    step=0.01,
                    format="%.2f",
                    value=float(custo_mo),
                    help="Calculado: tempo da OS × custo/hora do mecânico.",
                )
            else:
                valor = st.number_input("💰 Valor (R$) *", min_value=0.0, step=0.01, format="%.2f")

        r3a, r3b = st.columns(2)
        with r3a:
            descricao_peca = st.text_input(
                "Descrição (peça / serviço)",
                placeholder="Ex: Filtro de óleo, pastilha de freio…",
            )
        with r3b:
            observacao = st.text_area("💬 Observação", height=68)

        if item == "PECAS":
            rq1, rq2 = st.columns(2)
            with rq1:
                quantidade = st.number_input("Quantidade", min_value=0.01, step=1.0, format="%.2f", value=1.0)
            with rq2:
                valor_unit = st.number_input(
                    "Valor unitário (R$)",
                    min_value=0.0,
                    step=0.01,
                    format="%.2f",
                    value=float(valor),
                )
        else:
            quantidade = 1.0
            valor_unit = float(valor)

        enviar = st.form_submit_button("✅ Salvar lançamento", use_container_width=True)

    if enviar:
        if item == "M.O. MECANICO" and tempo_min <= 0:
            st.warning("A OS não possui tempo de mecânico (hora entrada/saída). Informe na OS ou use outro item.")
        elif item != "M.O. MECANICO" and valor <= 0:
            st.warning("Informe um valor maior que zero.")
        elif item == "M.O. MECANICO" and valor <= 0:
            st.warning("Valor M.O. zerado — cadastre custo/hora do mecânico.")
        else:
            val_final = round(float(valor), 2)
            qtd_final = float(quantidade)
            if item == "PECAS" and valor_unit > 0:
                val_final = round(valor_unit * qtd_final, 2)

            payload = {
                "os_id": os_sel.get("id"),
                "numero_os": os_sel["numero_os"],
                "data": str(data_lanc),
                "categoria": os_sel["categoria"],
                "placa": os_sel["placa"],
                "mecanico": os_sel.get("mecanico"),
                "item": item,
                "tipo_manutencao": tipo_manut,
                "descricao_peca": descricao_peca.strip() or None,
                "nfe": nfe.strip() or None,
                "id_fornecedor_sap": id_fornecedor.strip() or None,
                "quantidade": qtd_final,
                "valor_unitario": round(float(valor_unit), 2) if item == "PECAS" else None,
                "valor": val_final,
                "tempo_minutos_mecanico": tempo_min if item == "M.O. MECANICO" else None,
                "custo_hora_mecanico": custo_h if item == "M.O. MECANICO" else None,
                "custo_mo_mecanico": val_final if item == "M.O. MECANICO" else None,
                "observacao": observacao.strip() or None,
            }
            try:
                tbl(sb, "financeiro_custos").insert(payload).execute()
                st.success(f"Lançamento salvo — {item} | {fmt_moeda(val_final)}")
                st.cache_data.clear()
                st.rerun()
            except Exception as exc:
                st.error(f"Erro ao salvar: {exc}")

    st.markdown(
        f'<div class="sec">Lançamentos em {filtro_data.strftime("%d/%m/%Y")}</div>',
        unsafe_allow_html=True,
    )
    lanc_dia = lancamentos_do_dia(lancamentos, filtro_data)
    if lanc_dia:
        df = pd.DataFrame(lanc_dia)
        show = df[
            [
                c
                for c in [
                    "numero_os",
                    "placa",
                    "item",
                    "tipo_manutencao",
                    "descricao_peca",
                    "valor",
                    "nfe",
                ]
                if c in df.columns
            ]
        ].copy()
        if "valor" in show.columns:
            show["valor"] = show["valor"].apply(fmt_moeda)
        show = show.rename(
            columns={
                "numero_os": "OS",
                "placa": "Placa",
                "item": "Item",
                "tipo_manutencao": "Tipo",
                "descricao_peca": "Descrição",
                "valor": "Valor",
                "nfe": "NFE",
            }
        )
        dark_table_fin(show, height=260)

        st.markdown('<div class="sec">Custo acumulado por OS (com M.O. mecânico)</div>', unsafe_allow_html=True)
        try:
            resumo = tbl(sb, "v_custo_os_resumo").select("*").order("custo_total", desc=True).limit(20).execute()
            if resumo.data:
                df_r = pd.DataFrame(resumo.data)
                for col in ("custo_pecas", "custo_oleo", "custo_mo_mecanico", "custo_outros", "custo_total"):
                    if col in df_r.columns:
                        df_r[col] = df_r[col].apply(fmt_moeda)
                dark_table_fin(
                    df_r.rename(
                        columns={
                            "numero_os": "OS",
                            "categoria": "Cat.",
                            "placa": "Placa",
                            "custo_pecas": "Peças",
                            "custo_oleo": "Óleo",
                            "custo_mo_mecanico": "M.O. Mec.",
                            "custo_outros": "Outros",
                            "custo_total": "Total",
                        }
                    ),
                    height=220,
                )
        except Exception:
            pass
    else:
        st.info("Nenhum lançamento nesta data.")


# ── App principal ───────────────────────────────────────────────────────────
exigir_acesso("Ordem de Serviço — Oficina Veículos", "SIGCF | Controladoria — Gestão e Análise de Dados")
st.markdown(CSS.replace("__BG__", BG_URL), unsafe_allow_html=True)

col_logo, col_titulo, col_btn = st.columns([1, 5, 1], vertical_alignment="center")
with col_logo:
    st.image(LOGO_URL, width=92)
with col_titulo:
    st.title("🔧 ORDEM DE SERVIÇO — OFICINA VEÍCULOS")
    st.caption("SIGCF | CONTROLADORIA — GESTÃO E ANÁLISE DE DADOS · LEVE · PESADO · MOTO")
    st.markdown(
        f'<p style="margin:4px 0 0;font-size:13px;">{link_instagram()}</p>',
        unsafe_allow_html=True,
    )
with col_btn:
    if st.button("🔄 Atualizar", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.divider()

try:
    sb = get_supabase()
except Exception as exc:
    st.error(f"Configure SUPABASE_URL e SUPABASE_KEY nos Secrets. Erro: {exc}")
    st.stop()

aba_lanc, aba_edit, aba_fin, aba_painel, aba_cad = st.tabs([
    "📝 Nova OS",
    "✏️ Editar OS Pendente",
    "💰 Financeiro",
    "📊 Painel",
    "⚙️ Cadastros",
])

with aba_lanc:
    st.markdown('<div class="sec">Nova ordem de serviço</div>', unsafe_allow_html=True)
    cat_col, info_col = st.columns([1.6, 2.4])
    with cat_col:
        categoria_nova = st.selectbox(
            "Categoria do Veículo",
            options=list(CATEGORIAS.keys()),
            format_func=lambda x: CATEGORIAS[x],
            key="os_categoria_nova",
        )
    with info_col:
        qtd = len(carregar_veiculos(categoria_nova))
        st.markdown(
            f'<div class="ctx-bar" style="margin-top:28px;">'
            f'<span style="color:#9ab892;font-size:12px;">{qtd} veículo(s) em '
            f'{CATEGORIAS[categoria_nova]}</span></div>',
            unsafe_allow_html=True,
        )
    render_formulario_os(sb, categoria_nova, modo_edicao=False)

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
        cat_os = os_sel.get("categoria", "LEVE")
        st.caption(
            f"Criada em {fmt_dt_br(os_sel.get('created_at'))} · "
            f"{CATEGORIAS.get(cat_os, cat_os)}"
        )
        render_formulario_os(sb, cat_os, modo_edicao=True, os_existente=os_sel)

with aba_fin:
    render_financeiro(sb)

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
