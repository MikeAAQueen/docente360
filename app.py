import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client
import datetime
import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# ==============================================================================
# CONFIGURAÇÃO GERAL DA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Docente360 — Gestão Acadêmica",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização visual moderna e semântica
st.markdown("""
<style>
    .auth-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 24px;
        margin-top: 10px;
    }
    .main-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.1rem;
    }
    .sub-title {
        font-size: 0.95rem;
        color: #64748B;
        margin-bottom: 1rem;
    }
    .user-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .badge-sec { background-color: #DBEAFE; color: #1E40AF; }
    .badge-coord { background-color: #FEF3C7; color: #92400E; }
    .badge-admin { background-color: #D1FAE5; color: #065F46; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# INICIALIZAÇÃO DA CONEXÃO COM O SUPABASE
# ==============================================================================
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
    key = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY", ""))
    if not url or not key:
        st.error("Credenciais do Supabase ausentes em `.streamlit/secrets.toml`.")
        st.stop()
    return create_client(url, key)

supabase = init_supabase()

# ==============================================================================
# GERENCIAMENTO DE SESSÃO / ESTADO DO USUÁRIO
# ==============================================================================
if "auth_user" not in st.session_state:
    st.session_state["auth_user"] = None
if "user_profile" not in st.session_state:
    st.session_state["user_profile"] = None

def get_profile_data(user_id: str, email: str, metadata: dict = None) -> dict:
    """Busca os dados do perfil na tabela 'usuarios', com fallback nos metadados do Supabase Auth."""
    metadata = metadata or {}
    try:
        res = supabase.table("usuarios").select("*").eq("id", user_id).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]
    except Exception:
        pass
    
    # Fallback se a tabela ainda estiver sendo configurada
    return {
        "id": user_id,
        "email": email,
        "nome": metadata.get("nome", email.split("@")[0]),
        "perfil": metadata.get("perfil", "Secretaria"),
        "cargo": metadata.get("cargo", "Equipe Operacional")
    }

def handle_login(email: str, password: str):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if res.user:
            profile = get_profile_data(res.user.id, res.user.email, res.user.user_metadata)
            st.session_state["auth_user"] = res.user
            st.session_state["user_profile"] = profile
            st.success(f"Bem-vindo(a), {profile.get('nome')}!")
            st.rerun()
    except Exception as e:
        msg = str(e)
        if "Invalid login credentials" in msg:
            st.error("E-mail ou senha incorretos.")
        elif "Email not confirmed" in msg:
            st.warning("E-mail ainda não confirmado. Verifique sua caixa de entrada no e-mail ou desative a exigência de confirmação no painel do Supabase.")
        else:
            st.error(f"Erro ao autenticar: {msg}")

def handle_signup(email: str, password: str, nome: str, perfil: str, cargo: str):
    if len(password) < 6:
        st.error("A senha deve conter no mínimo 6 caracteres.")
        return
    try:
        # 1. Cria o usuário no Supabase Auth com metadados
        res = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "nome": nome,
                    "perfil": perfil,
                    "cargo": cargo
                }
            }
        })
        
        if res.user:
            # 2. Tenta registrar explicitamente na tabela 'usuarios'
            try:
                supabase.table("usuarios").upsert({
                    "id": res.user.id,
                    "nome": nome,
                    "email": email,
                    "perfil": perfil,
                    "cargo": cargo
                }).execute()
            except Exception:
                pass  # A trigger do banco ou o RLS podem tratar
            
            # Se a sessão já foi iniciada (sem confirmação obrigatória de email)
            if res.session:
                st.session_state["auth_user"] = res.user
                st.session_state["user_profile"] = {
                    "id": res.user.id,
                    "nome": nome,
                    "email": email,
                    "perfil": perfil,
                    "cargo": cargo
                }
                st.success("Conta criada e login realizado com sucesso!")
                st.rerun()
            else:
                st.success("✅ Usuário cadastrado com sucesso! Se a confirmação de e-mail estiver ativa no seu projeto Supabase, confirme o link enviado ao seu e-mail antes de efetuar o login.")
    except Exception as e:
        st.error(f"Erro ao criar conta: {e}")

def handle_logout():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    st.session_state["auth_user"] = None
    st.session_state["user_profile"] = None
    st.rerun()

# ==============================================================================
# FUNÇÕES DE CONSULTA DO BANCO DE DADOS
# ==============================================================================
def get_professores() -> pd.DataFrame:
    try:
        res = supabase.table("professores").select("*").order("nome").execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame(columns=["id", "nome", "email", "departamento"])
    except Exception:
        return pd.DataFrame()

def get_disciplinas() -> pd.DataFrame:
    try:
        res = supabase.table("disciplinas").select("*").order("nome").execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame(columns=["id", "codigo", "nome"])
    except Exception:
        return pd.DataFrame()

def get_turmas() -> pd.DataFrame:
    try:
        res = supabase.table("turmas").select("*").order("codigo").execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame(columns=["id", "codigo", "curso", "periodo"])
    except Exception:
        return pd.DataFrame()

def get_ausencias_completas() -> pd.DataFrame:
    try:
        query = """
            id, data_ausencia, horario, motivo, status, professor_id, disciplina_id, turma_id,
            professores!ausencias_professor_id_fkey(id, nome, email),
            disciplinas!ausencias_disciplina_id_fkey(codigo, nome),
            turmas!ausencias_turma_id_fkey(codigo, curso)
        """
        res = supabase.table("ausencias").select(query).order("data_ausencia", desc=True).execute()
        data = []
        for item in res.data or []:
            prof = item.get("professores") or {}
            disc = item.get("disciplinas") or {}
            turma = item.get("turmas") or {}
            data.append({
                "ID": item["id"],
                "Data": item["data_ausencia"],
                "Horário": item["horario"],
                "ProfessorID": item.get("professor_id"),
                "Professor": prof.get("nome", "Docente não informado"),
                "EmailProfessor": prof.get("email", ""),
                "Disciplina": f"{disc.get('codigo', '')} - {disc.get('nome', '')}".strip(" -"),
                "Turma": f"{turma.get('codigo', '')} ({turma.get('curso', '')})".strip(" ()"),
                "Motivo": item.get("motivo") or "Não informado",
                "Status": item.get("status", "Pendente")
            })
        return pd.DataFrame(data)
    except Exception:
        return pd.DataFrame()

def get_reposicoes() -> pd.DataFrame:
    try:
        res = supabase.table("reposicoes_atestados").select("*").execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def get_usuarios_cadastrados() -> pd.DataFrame:
    try:
        res = supabase.table("usuarios").select("*").order("nome").execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def gerar_pdf_relatorio(df: pd.DataFrame) -> BytesIO:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    elements = []
    styles = getSampleStyleSheet()

    header_style = ParagraphStyle(
        name="HeaderStyle",
        parent=styles['Heading1'],
        fontName="Helvetica-Bold",
        fontSize=15,
        textColor=colors.HexColor("#1E3A8A"),
        alignment=1
    )
    elements.append(Paragraph("Docente360 — Relatório Oficial de Ausências e Substituições", header_style))
    elements.append(Paragraph(f"Emitido em: {datetime.datetime.now().strftime('%d/%m/%Y às %H:%M')}", ParagraphStyle('Data', parent=styles['Normal'], alignment=1, fontSize=9, textColor=colors.gray)))
    elements.append(Spacer(1, 14))

    col_widths = [65, 110, 130, 110, 85]
    data_tabela = [["Data", "Professor", "Disciplina", "Turma", "Status"]]
    for _, row in df.iterrows():
        data_tabela.append([
            str(row.get("Data", "")),
            str(row.get("Professor", ""))[:20],
            str(row.get("Disciplina", ""))[:22],
            str(row.get("Turma", ""))[:18],
            str(row.get("Status", ""))
        ])

    t = Table(data_tabela, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    elements.append(t)
    doc.build(elements)
    buffer.seek(0)
    return buffer

# ==============================================================================
# TELA 1: PORTAL DE AUTENTICAÇÃO (QUANDO NÃO LOGADO)
# ==============================================================================
if st.session_state["auth_user"] is None:
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.markdown('<div class="main-title" style="text-align: center;">🎓 Docente360</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-title" style="text-align: center;">Portal de Gestão de Ausências — Secretaria & Coordenação Acadêmica</div>', unsafe_allow_html=True)
        
        tab_login, tab_cadastro = st.tabs(["🔑 Entrar no Sistema", "📝 Criar Nova Conta de Usuário"])
        
        # ABA DE LOGIN
        with tab_login:
            st.markdown("##### Identifique-se com sua conta institucional")
            with st.form("form_login"):
                login_email = st.text_input("E-mail Institucional", placeholder="ex: secretaria@escola.edu.br")
                login_senha = st.text_input("Senha", type="password")
                btn_entrar = st.form_submit_button("Acessar Sistema", use_container_width=True, type="primary")
                
                if btn_entrar:
                    if not login_email or not login_senha:
                        st.warning("Preencha todos os campos para entrar.")
                    else:
                        handle_login(login_email, login_senha)
                        
        # ABA DE CADASTRO
        with tab_cadastro:
            st.markdown("##### Cadastro de Operador (Secretaria ou Coordenação)")
            with st.form("form_cadastro"):
                cad_nome = st.text_input("Nome Completo *", placeholder="Ex: Ana Carolina Silva")
                cad_email = st.text_input("E-mail Institucional *", placeholder="Ex: ana.silva@escola.edu.br")
                
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    cad_perfil = st.selectbox("Perfil de Acesso *", ["Secretaria", "Coordenador Acadêmico", "Administrador"])
                with col_c2:
                    cad_cargo = st.text_input("Cargo / Função", placeholder="Ex: Secretária Acadêmica")
                    
                cad_senha = st.text_input("Senha (mínimo 6 dígitos) *", type="password")
                btn_cadastrar = st.form_submit_button("Cadastrar Usuário", use_container_width=True)
                
                if btn_cadastrar:
                    if not cad_nome or not cad_email or not cad_senha:
                        st.warning("Preencha todos os campos obrigatórios (*).")
                    else:
                        handle_signup(cad_email, cad_senha, cad_nome, cad_perfil, cad_cargo)

    st.stop()  # Impede renderizar o restante do app enquanto não autenticado

# ==============================================================================
# TELA 2: SISTEMA PRINCIPAL (USUÁRIO AUTENTICADO)
# ==============================================================================
usuario = st.session_state["user_profile"] or {}
nome_usuario = usuario.get("nome", "Usuário")
perfil_usuario = usuario.get("perfil", "Secretaria")
cargo_usuario = usuario.get("cargo", "Equipe")
email_usuario = usuario.get("email", "")

# BARRA LATERAL COM INFORMAÇÕES DO USUÁRIO LOGADO
with st.sidebar:
    st.markdown("### 🎓 **Docente360**")
    st.caption("Sistema de Gestão de Ausências e Substituições")
    st.markdown("---")
    
    st.markdown("#### 👤 Usuário Conectado")
    st.markdown(f"**{nome_usuario}**")
    st.caption(f"📧 {email_usuario}")
    st.caption(f"💼 Cargo: {cargo_usuario}")
    
    badge_class = "badge-sec" if perfil_usuario == "Secretaria" else ("badge-coord" if perfil_usuario == "Coordenador Acadêmico" else "badge-admin")
    st.markdown(f'<span class="user-badge {badge_class}">{perfil_usuario}</span>', unsafe_allow_html=True)
    
    st.markdown("---")
    if st.button("🚪 Sair do Sistema (Logout)", use_container_width=True):
        handle_logout()
        
    st.markdown("---")
    st.caption("🟢 Supabase Auth: **Autenticado**")

# Carregamento de dados para as telas
df_prof = get_professores()
df_disc = get_disciplinas()
df_turmas = get_turmas()
df_ausencias = get_ausencias_completas()

# CABEÇALHO DO PAINEL
st.markdown(f'<div class="main-title">Docente360 — Painel da {perfil_usuario}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">Sessão ativa de <b>{nome_usuario}</b> ({cargo_usuario})</div>', unsafe_allow_html=True)

# ==============================================================================
# FLUXO ESPECÍFICO POR PERFIL DE ACESSO
# ==============================================================================

# ------------------------------------------------------------------------------
# PERFIL: SECRETARIA (Operação de Ausências, Substituições e Aulas Vagas)
# ------------------------------------------------------------------------------
if perfil_usuario == "Secretaria":
    abas_sec = st.tabs([
        "📌 Lançamento Diário de Ausências", 
        "🔄 Gestão de Substituições & Aulas Vagas",
        "📑 Anexo de Atestados & Reposições",
        "📋 Histórico Geral de Ocorrências"
    ])
    
    # TAB 1: LANÇAMENTO
    with abas_sec[0]:
        st.subheader("Registrar Ocorrência de Falta Docente")
        with st.form("form_sec_ausencia", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                prof_escolhido = st.selectbox("Docente Ausente *", df_prof["nome"].tolist() if not df_prof.empty else [])
                disc_escolhida = st.selectbox("Disciplina *", [f"{r['codigo']} - {r['nome']}" for _, r in df_disc.iterrows()] if not df_disc.empty else [])
                turma_escolhida = st.selectbox("Turma Afetada *", [f"{r['codigo']} - {r['curso']}" for _, r in df_turmas.iterrows()] if not df_turmas.empty else [])
            with col_b:
                data_falta = st.date_input("Data da Ausência *", datetime.date.today())
                horario_bloco = st.selectbox("Horário / Bloco *", ["1º Horário (07:30 - 09:10)", "2º Horário (09:30 - 11:10)", "3º Horário (19:00 - 20:40)", "4º Horário (20:50 - 22:30)"])
                motivo_tipo = st.selectbox("Categoria do Motivo", ["Problemas de Saúde", "Assuntos Pessoais", "Compromisso Institucional", "Trânsito / Deslocamento", "Outros"])
                motivo_obs = st.text_area("Observações Adicionais (opcional)")

            if st.form_submit_button("💾 Salvar Registro de Ausência", use_container_width=True):
                if df_prof.empty or df_disc.empty or df_turmas.empty:
                    st.error("Cadastros de apoio incompletos.")
                else:
                    prof_id = df_prof[df_prof["nome"] == prof_escolhido]["id"].values[0]
                    cod_disc = disc_escolhida.split(" - ")[0]
                    disc_id = df_disc[df_disc["codigo"] == cod_disc]["id"].values[0]
                    cod_turma = turma_escolhida.split(" - ")[0]
                    turma_id = df_turmas[df_turmas["codigo"] == cod_turma]["id"].values[0]
                    
                    supabase.table("ausencias").insert({
                        "professor_id": prof_id,
                        "disciplina_id": disc_id,
                        "turma_id": turma_id,
                        "data_ausencia": str(data_falta),
                        "horario": horario_bloco,
                        "motivo": f"[{motivo_tipo}] {motivo_obs}".strip(),
                        "status": "Pendente"
                    }).execute()
                    st.success("✅ Falta registrada com sucesso!")
                    st.rerun()

    # TAB 2: SUBSTITUIÇÃO E AULA VAGA
    with abas_sec[1]:
        st.subheader("Atribuição de Substituto ou Registro de Aula Vaga")
        pendentes = df_ausencias[df_ausencias["Status"] == "Pendente"] if not df_ausencias.empty else pd.DataFrame()
        if pendentes.empty:
            st.success("🎉 Nenhuma ausência pendente de tratativa no momento.")
        else:
            opcoes_pend = {r["ID"]: f"{r['Data']} | {r['Professor']} | {r['Turma']} ({r['Horário']})" for _, r in pendentes.iterrows()}
            esc_id = st.selectbox("Ausência Pendente:", list(opcoes_pend.keys()), format_func=lambda x: opcoes_pend[x])
            detalhe = pendentes[pendentes["ID"] == esc_id].iloc[0]
            
            acao = st.radio("Ação:", ["Alocar Docente Substituto", "Marcar como Aula Vaga"], horizontal=True)
            if acao == "Alocar Docente Substituto":
                disp = df_prof[df_prof["id"] != detalhe["ProfessorID"]]
                sub_nome = st.selectbox("Selecione o Professor Substituto:", disp["nome"].tolist())
                if st.button("Confirmar Substituição", type="primary"):
                    sub_id = disp[disp["nome"] == sub_nome]["id"].values[0]
                    supabase.table("substituicoes").insert({
                        "ausencia_id": esc_id,
                        "professor_substituto_id": sub_id,
                        "aula_vaga": False
                    }).execute()
                    supabase.table("ausencias").update({"status": "Substituída"}).eq("id", esc_id).execute()
                    st.success("Substituição alocada!")
                    st.rerun()
            else:
                obs_vaga = st.text_input("Justificativa para a Turma:")
                if st.button("Confirmar Aula Vaga"):
                    supabase.table("substituicoes").insert({
                        "ausencia_id": esc_id,
                        "professor_substituto_id": None,
                        "aula_vaga": True,
                        "observacoes": obs_vaga
                    }).execute()
                    supabase.table("ausencias").update({"status": "Aula Vaga"}).eq("id", esc_id).execute()
                    st.warning("Classificada como Aula Vaga.")
                    st.rerun()

    # TAB 3: ATESTADOS & REPOSIÇÕES
    with abas_sec[2]:
        st.subheader("Anexo de Atestados e Registro de Reposição Acordada")
        if not df_ausencias.empty:
            opcoes_todas = {r["ID"]: f"{r['Data']} — {r['Professor']} — {r['Disciplina']} ({r['Status']})" for _, r in df_ausencias.iterrows()}
            aus_id = st.selectbox("Selecione a ausência:", list(opcoes_todas.keys()), format_func=lambda x: opcoes_todas[x])
            
            with st.form("form_sec_anexo"):
                doc_file = st.file_uploader("Anexo do Comprovante (PDF ou Imagem)", type=["pdf", "png", "jpg", "jpeg"])
                data_rep = st.date_input("Data Acordada para Reposição", datetime.date.today() + datetime.timedelta(days=7))
                horario_rep = st.text_input("Horário e Local da Reposição", placeholder="Ex: Sábado, 08:00 - 10:00 (Sala 102)")
                
                if st.form_submit_button("Salvar e Enviar para Homologação"):
                    url_atestado = None
                    if doc_file:
                        try:
                            fpath = f"{aus_id}_{doc_file.name}"
                            supabase.storage.from_("atestados").upload(fpath, doc_file.getvalue())
                            url_atestado = supabase.storage.from_("atestados").get_public_url(fpath)
                        except Exception as e:
                            st.warning(f"Aviso de anexo: Verifique se o bucket 'atestados' foi criado. Erro: {e}")
                    
                    supabase.table("reposicoes_atestados").insert({
                        "ausencia_id": aus_id,
                        "atestado_url": url_atestado,
                        "data_reposicao": str(data_rep),
                        "horario_reposicao": horario_rep,
                        "comprovada": False
                    }).execute()
                    
                    supabase.table("ausencias").update({"status": "Aguardando Homologação"}).eq("id", aus_id).execute()
                    st.success("Enviado para homologação do Coordenador Acadêmico!")
                    st.rerun()

    # TAB 4: HISTÓRICO GERAL
    with abas_sec[3]:
        st.subheader("Histórico Completo de Ausências")
        st.dataframe(df_ausencias, use_container_width=True)

# ------------------------------------------------------------------------------
# PERFIL: COORDENADOR ACADÊMICO (Dashboard, Homologação e Relatórios PDF)
# ------------------------------------------------------------------------------
elif perfil_usuario == "Coordenador Acadêmico":
    abas_coord = st.tabs([
        "📊 Dashboard Analítico de Indicadores", 
        "✅ Homologação de Reposições", 
        "📄 Relatórios Gerenciais em PDF"
    ])
    
    # SUBTAB 1: DASHBOARD
    with abas_coord[0]:
        st.subheader("Painel de Indicadores de Frequência e Aulas Vagas")
        if df_ausencias.empty:
            st.info("Nenhuma ausência registrada no sistema.")
        else:
            total = len(df_ausencias)
            subst = len(df_ausencias[df_ausencias["Status"] == "Substituída"])
            vagas = len(df_ausencias[df_ausencias["Status"] == "Aula Vaga"])
            aguard = len(df_ausencias[df_ausencias["Status"] == "Aguardando Homologação"])
            repostas = len(df_ausencias[df_ausencias["Status"] == "Reposta"])
            taxa = (subst / total * 100) if total > 0 else 0.0
            
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Total de Ausências", total)
            c2.metric("Substituições", subst, f"{taxa:.1f}%")
            c3.metric("Aulas Vagas", vagas, delta_color="inverse")
            c4.metric("Aguardando Homologação", aguard)
            c5.metric("Aulas Repostas", repostas)
            
            st.markdown("---")
            g1, g2 = st.columns(2)
            cores = {"Pendente": "#F59E0B", "Substituída": "#3B82F6", "Aula Vaga": "#EF4444", "Aguardando Homologação": "#F97316", "Reposta": "#10B981"}
            with g1:
                fig_p = px.pie(df_ausencias, names="Status", title="Ausências por Status", color="Status", color_discrete_map=cores, hole=0.35)
                st.plotly_chart(fig_p, use_container_width=True)
            with g2:
                fig_b = px.bar(df_ausencias, x="Professor", color="Status", title="Frequência por Professor", color_discrete_map=cores)
                st.plotly_chart(fig_b, use_container_width=True)

    # SUBTAB 2: HOMOLOGAÇÃO
    with abas_coord[1]:
        st.subheader("Homologação Pedagógica de Reposições de Aula")
        pendentes_homolog = df_ausencias[df_ausencias["Status"] == "Aguardando Homologação"] if not df_ausencias.empty else pd.DataFrame()
        
        if pendentes_homolog.empty:
            st.success("✨ Nenhuma reposição pendente de homologação.")
        else:
            df_rep = get_reposicoes()
            for _, r in pendentes_homolog.iterrows():
                with st.expander(f"📌 {r['Professor']} — {r['Disciplina']} ({r['Turma']})"):
                    rep_det = df_rep[df_rep["ausencia_id"] == r["ID"]] if not df_rep.empty else pd.DataFrame()
                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.write(f"**Data da Falta:** {r['Data']} ({r['Horário']})")
                        st.write(f"**Motivo:** {r['Motivo']}")
                    with col_info2:
                        if not rep_det.empty:
                            st.write(f"**Data Proposta para Reposição:** {rep_det.iloc[0].get('data_reposicao')}")
                            st.write(f"**Horário:** {rep_det.iloc[0].get('horario_reposicao')}")
                            if rep_det.iloc[0].get("atestado_url"):
                                st.markdown(f"📎 [Visualizar Atestado]({rep_det.iloc[0]['atestado_url']})")
                    
                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button("✅ Homologar Reposição", key=f"ap_{r['ID']}", type="primary"):
                            supabase.table("ausencias").update({"status": "Reposta"}).eq("id", r["ID"]).execute()
                            supabase.table("reposicoes_atestados").update({"comprovada": True}).eq("ausencia_id", r["ID"]).execute()
                            st.success("Homologado!")
                            st.rerun()
                    with b2:
                        if st.button("❌ Recusar / Solicitar Ajuste", key=f"rec_{r['ID']}"):
                            supabase.table("ausencias").update({"status": "Pendente"}).eq("id", r["ID"]).execute()
                            st.warning("Retornado para pendente.")
                            st.rerun()

    # SUBTAB 3: RELATÓRIOS
    with abas_coord[2]:
        st.subheader("Exportação de Relatórios Gerenciais")
        if df_ausencias.empty:
            st.info("Nenhuma ausência registrada.")
        else:
            st.dataframe(df_ausencias, use_container_width=True)
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                pdf = gerar_pdf_relatorio(df_ausencias)
                st.download_button("📄 Baixar Relatório em PDF", pdf, file_name=f"relatorio_ausencias_{datetime.date.today()}.pdf", mime="application/pdf", use_container_width=True)
            with col_d2:
                csv = df_ausencias.to_csv(index=False).encode('utf-8')
                st.download_button("📊 Baixar Planilha em CSV", csv, file_name=f"ausencias_{datetime.date.today()}.csv", mime="text/csv", use_container_width=True)

# ------------------------------------------------------------------------------
# PERFIL: ADMINISTRADOR (Visão Global + Gestão de Usuários)
# ------------------------------------------------------------------------------
elif perfil_usuario == "Administrador":
    abas_admin = st.tabs(["👥 Usuários da Secretaria & Coordenação", "📌 Visão Geral da Operação", "📊 Dashboard Global"])
    
    with abas_admin[0]:
        st.subheader("Equipe Cadastrada no Sistema (Tabela `usuarios`)")
        df_users = get_usuarios_cadastrados()
        if not df_users.empty:
            st.dataframe(df_users[["nome", "email", "perfil", "cargo", "criado_em"]], use_container_width=True)
        else:
            st.info("Nenhum usuário listado ou tabela 'usuarios' pendente de execução no SQL Editor do Supabase.")
            
    with abas_admin[1]:
        st.subheader("Ocorrências Registradas")
        st.dataframe(df_ausencias, use_container_width=True)
        
    with abas_admin[2]:
        st.subheader("Métricas Gerais")
        st.metric("Total de Ausências", len(df_ausencias))