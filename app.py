import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client
import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# Configuração da página
st.set_page_config(
    page_title="Gestão de Ausências Docentes",
    page_icon="🏫",
    layout="wide"
)

# Inicialização da Conexão com Supabase
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets.get("SUPABASE_URL", "SUA_URL_SUPABASE")
    key = st.secrets.get("SUPABASE_KEY", "SUA_KEY_SUPABASE")
    return create_client(url, key)

supabase = init_supabase()

# Funções Auxiliares de Banco de Dados
def get_professores():
    res = supabase.table("professores").select("*").execute()
    return pd.DataFrame(res.data)

def get_disciplinas():
    res = supabase.table("disciplinas").select("*").execute()
    return pd.DataFrame(res.data)

def get_turmas():
    res = supabase.table("turmas").select("*").execute()
    return pd.DataFrame(res.data)

def get_ausencias_completas():
    # Consulta relacionando ausencias com professores, disciplinas e turmas
    query = """
        id, data_ausencia, horario, motivo, status,
        professores!ausencias_professor_id_fkey(nome),
        disciplinas!ausencias_disciplina_id_fkey(nome, codigo),
        turmas!ausencias_turma_id_fkey(codigo, curso)
    """
    res = supabase.table("ausencias").select(query).execute()
    data = []
    for item in res.data:
        data.append({
            "ID": item["id"],
            "Data": item["data_ausencia"],
            "Horário": item["horario"],
            "Professor": item["professores"]["nome"] if item.get("professores") else "N/A",
            "Disciplina": f"{item['disciplinas']['codigo']} - {item['disciplinas']['nome']}" if item.get("disciplinas") else "N/A",
            "Turma": f"{item['turmas']['codigo']} ({item['turmas']['curso']})" if item.get("turmas") else "N/A",
            "Motivo": item["motivo"],
            "Status": item["status"]
        })
    return pd.DataFrame(data)

def gerar_pdf_relatorio(df):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Relatório de Ausências e Reposições Docentes", styles['Title']))
    elements.append(Spacer(1, 12))

    data_tabela = [["Data", "Professor", "Disciplina", "Turma", "Status"]]
    for _, row in df.iterrows():
        data_tabela.append([str(row["Data"]), str(row["Professor"]), str(row["Disciplina"]), str(row["Turma"]), str(row["Status"])])

    t = Table(data_tabela)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(t)
    doc.build(elements)
    buffer.seek(0)
    return buffer

# Interface Principal
st.title("🏫 Módulo de Gestão de Ausências e Substituições")

abas = st.tabs([
    "📌 Lançamento Diário", 
    "🔄 Substituições & Aulas Vagas", 
    "📑 Atestados & Reposições", 
    "📊 Dashboard do Coordenador"
])

# Carrega dados fundamentais
df_prof = get_professores()
df_disc = get_disciplinas()
df_turmas = get_turmas()

# TAB 1: LANÇAMENTO DIÁRIO DE AUSÊNCIAS
with abas[0]:
    st.header("Registrar Ausência Docente")
    with st.form("form_ausencia", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            prof_selected = st.selectbox("Professor", df_prof["nome"].tolist() if not df_prof.empty else [])
            disc_selected = st.selectbox("Disciplina", df_disc["nome"].tolist() if not df_disc.empty else [])
            turma_selected = st.selectbox("Turma", df_turmas["codigo"].tolist() if not df_turmas.empty else [])
        with col2:
            data_aus = st.date_input("Data da Ausência", datetime.date.today())
            horario = st.selectbox("Horário / Período", ["1º Horário (07:30 - 09:10)", "2º Horário (09:30 - 11:10)", "3º Horário (19:00 - 20:40)", "4º Horário (20:50 - 22:30)"])
            motivo = st.text_area("Motivo da Falta")

        submitted = st.form_submit_button("Registrar Ausência")
        if submitted:
            prof_id = df_prof[df_prof["nome"] == prof_selected]["id"].values[0]
            disc_id = df_disc[df_disc["nome"] == disc_selected]["id"].values[0]
            turma_id = df_turmas[df_turmas["codigo"] == turma_selected]["id"].values[0]

            res = supabase.table("ausencias").insert({
                "professor_id": prof_id,
                "disciplina_id": disc_id,
                "turma_id": turma_id,
                "data_ausencia": str(data_aus),
                "horario": horario,
                "motivo": motivo,
                "status": "Pendente"
            }).execute()

            st.success("Ausência registrada com sucesso!")

# TAB 2: GESTÃO DE SUBSTITUIÇÕES
with abas[1]:
    st.header("Atribuição de Substitutos e Aulas Vagas")
    df_ausencias = get_ausencias_completas()
    
    if not df_ausencias.empty:
        pendentes = df_ausencias[df_ausencias["Status"] == "Pendente"]
        if not pendentes.empty:
            ausencia_escolhida = st.selectbox(
                "Selecione a ausência pendente para gerenciar:",
                pendentes["ID"].tolist(),
                format_func=lambda x: f"{pendentes[pendentes['ID']==x]['Data'].values[0]} | {pendentes[pendentes['ID']==x]['Professor'].values[0]} | {pendentes[pendentes['ID']==x]['Turma'].values[0]}"
            )
            
            tipo_acao = st.radio("Ação a ser tomada:", ["Alocar Professor Substituto", "Classificar como Aula Vaga"])
            
            if tipo_acao == "Alocar Professor Substituto":
                substituto = st.selectbox("Selecione o Professor Substituto:", df_prof["nome"].tolist())
                if st.button("Confirmar Substituição"):
                    sub_id = df_prof[df_prof["nome"] == substituto]["id"].values[0]
                    supabase.table("substituicoes").insert({
                        "ausencia_id": ausencia_escolhida,
                        "professor_substituto_id": sub_id,
                        "aula_vaga": False
                    }).execute()
                    supabase.table("ausencias").update({"status": "Substituída"}).eq("id", ausencia_escolhida).execute()
                    st.success("Substituição alocada!")
                    st.rerun()
            else:
                obs = st.text_input("Observação referente à Aula Vaga:")
                if st.button("Confirmar Aula Vaga"):
                    supabase.table("substituicoes").insert({
                        "ausencia_id": ausencia_escolhida,
                        "aula_vaga": True,
                        "observacoes": obs
                    }).execute()
                    supabase.table("ausencias").update({"status": "Aula Vaga"}).eq("id", ausencia_escolhida).execute()
                    st.warning("Registrado como Aula Vaga.")
                    st.rerun()
        else:
            st.info("Não há ausências pendentes no momento.")
    else:
        st.info("Nenhuma ausência cadastrada.")

# TAB 3: ATESTADOS E REPOSIÇÕES
with abas[2]:
    st.header("Anexo de Atestados e Agendamento de Reposições")
    df_ausencias = get_ausencias_completas()
    
    if not df_ausencias.empty:
        ausencia_id = st.selectbox(
            "Selecione a ausência para anexo/agendamento:",
            df_ausencias["ID"].tolist(),
            format_func=lambda x: f"{df_ausencias[df_ausencias['ID']==x]['Data'].values[0]} - {df_ausencias[df_ausencias['ID']==x]['Professor'].values[0]}"
        )
        
        file_upload = st.file_uploader("Anexar Atestado (PDF ou Imagem)", type=["pdf", "png", "jpg"])
        data_rep = st.date_input("Data da Reposição da Aula")
        horario_rep = st.text_input("Horário da Reposição", "14:00 - 15:40")
        
        if st.button("Salvar Comprovante e Reposição"):
            file_url = None
            if file_upload is not None:
                file_path = f"atestados/{ausencia_id}_{file_upload.name}"
                supabase.storage.from_("atestados").upload(file_path, file_upload.getvalue())
                file_url = supabase.storage.from_("atestados").get_public_url(file_path)
            
            supabase.table("reposicoes_atestados").insert({
                "ausencia_id": ausencia_id,
                "atestado_url": file_url,
                "data_reposicao": str(data_rep),
                "horario_reposicao": horario_rep,
                "comprovada": True if file_url else False
            }).execute()
            
            supabase.table("ausencias").update({"status": "Reposta"}).eq("id", ausencia_id).execute()
            st.success("Informações salvas com sucesso!")

# TAB 4: DASHBOARD DO COORDENADOR
with abas[3]:
    st.header("Dashboard do Coordenador")
    df_ausencias = get_ausencias_completas()
    
    if not df_ausencias.empty:
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Total de Ausências", len(df_ausencias))
        substituidas = len(df_ausencias[df_ausencias["Status"] == "Substituída"])
        col_m2.metric("Substituições Realizadas", substituidas)
        aulas_vagas = len(df_ausencias[df_ausencias["Status"] == "Aula Vaga"])
        col_m3.metric("Aulas Vagas", aulas_vagas)
        
        st.markdown("---")
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            fig_status = px.pie(df_ausencias, names="Status", title="Distribuição por Status da Ausência")
            st.plotly_chart(fig_status, use_container_width=True)
            
        with col_g2:
            fig_prof = px.bar(df_ausencias, x="Professor", title="Ausências por Professor", color="Status")
            st.plotly_chart(fig_prof, use_container_width=True)
            
        st.markdown("---")
        st.subheader("Exportar Relatórios PDF")
        pdf_bytes = gerar_pdf_relatorio(df_ausencias)
        st.download_button(
            label="📄 Baixar Relatório em PDF",
            data=pdf_bytes,
            file_name="relatorio_ausencias_docentes.pdf",
            mime="application/pdf"
        )
    else:
        st.info("Nenhum dado disponível no dashboard.")