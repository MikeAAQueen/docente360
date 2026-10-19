import datetime
import streamlit as st
import pandas as pd
from supabase import Client
from services.supabase_service import (
    get_professores,
    get_disciplinas,
    get_turmas,
    get_ausencias_completas
)
from components.cadastros import render_cadastros_base

def render_secretaria_view(supabase: Client, user_profile: dict):
    """Renderiza a visão e as operações diárias da Secretaria."""
    df_prof = get_professores(supabase)
    df_disc = get_disciplinas(supabase)
    df_turmas = get_turmas(supabase)
    df_ausencias = get_ausencias_completas(supabase)

    abas_sec = st.tabs([
        "📌 Lançamento",
        "🔄 Substituições",
        "📑 Atestados",
        "📚 Cadastros",
        "📋 Histórico"
    ])

    # --------------------------------------------------------------------------
    # TAB 1: LANÇAMENTO DIÁRIO
    # --------------------------------------------------------------------------
    with abas_sec[0]:
        st.subheader("Registrar Ocorrência de Falta Docente")
        if df_prof.empty or df_disc.empty or df_turmas.empty:
            st.warning("⚠️ **Atenção:** Há dados básicos não cadastrados (professores, matérias ou turmas). Acesse a aba **'📚 Cadastros'** para adicioná-los.")
        else:
            st.caption("💡 Não encontrou o docente ou a matéria? Cadastre-os rapidamente na aba **'📚 Cadastros'**.")
        with st.form("form_sec_ausencia", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                prof_escolhido = st.selectbox(
                    "Docente Ausente *",
                    df_prof["nome"].tolist() if not df_prof.empty else []
                )
                disc_escolhida = st.selectbox(
                    "Disciplina *",
                    [f"{r['codigo']} - {r['nome']}" for _, r in df_disc.iterrows()] if not df_disc.empty else []
                )
                turma_escolhida = st.selectbox(
                    "Turma Afetada *",
                    [f"{r['codigo']} - {r['curso']}" for _, r in df_turmas.iterrows()] if not df_turmas.empty else []
                )
            with col_b:
                data_falta = st.date_input("Data da Ausência *", datetime.date.today())
                horario_bloco = st.selectbox(
                    "Horário / Bloco *",
                    [
                        "1º Horário (07:30 - 09:10)",
                        "2º Horário (09:30 - 11:10)",
                        "3º Horário (19:00 - 20:40)",
                        "4º Horário (20:50 - 22:30)"
                    ]
                )
                motivo_tipo = st.selectbox(
                    "Categoria do Motivo",
                    [
                        "Problemas de Saúde",
                        "Assuntos Pessoais",
                        "Compromisso Institucional",
                        "Trânsito / Deslocamento",
                        "Outros"
                    ]
                )
                motivo_obs = st.text_area("Observações Adicionais (opcional)")

            if st.form_submit_button("💾 Salvar Registro de Ausência", use_container_width=True):
                if df_prof.empty or df_disc.empty or df_turmas.empty:
                    st.error("Cadastros de apoio incompletos no banco de dados.")
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

    # --------------------------------------------------------------------------
    # TAB 2: GESTÃO DE SUBSTITUIÇÕES E AULAS VAGAS
    # --------------------------------------------------------------------------
    with abas_sec[1]:
        st.subheader("Atribuição de Substituto ou Registro de Aula Vaga")
        pendentes = df_ausencias[df_ausencias["Status"] == "Pendente"] if not df_ausencias.empty else pd.DataFrame()
        if pendentes.empty:
            st.success("🎉 Nenhuma ausência pendente de tratativa no momento.")
        else:
            opcoes_pend = {
                r["ID"]: f"{r['Data']} | {r['Professor']} | {r['Turma']} ({r['Horário']})"
                for _, r in pendentes.iterrows()
            }
            esc_id = st.selectbox(
                "Ausência Pendente:",
                list(opcoes_pend.keys()),
                format_func=lambda x: opcoes_pend[x]
            )
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
                    st.success("Substituição alocada com sucesso!")
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

    # --------------------------------------------------------------------------
    # TAB 3: ANEXO DE ATESTADOS & REPOSIÇÕES
    # --------------------------------------------------------------------------
    with abas_sec[2]:
        st.subheader("Anexo de Atestados e Registro de Reposição Acordada")
        if df_ausencias.empty:
            st.info("Nenhuma ausência registrada para vincular atestado.")
        else:
            opcoes_todas = {
                r["ID"]: f"{r['Data']} — {r['Professor']} — {r['Disciplina']} ({r['Status']})"
                for _, r in df_ausencias.iterrows()
            }
            aus_id = st.selectbox(
                "Selecione a ausência:",
                list(opcoes_todas.keys()),
                format_func=lambda x: opcoes_todas[x]
            )

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
                            st.warning(f"Aviso de anexo: Verifique se o bucket 'atestados' foi criado. Detalhe: {e}")

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

    # --------------------------------------------------------------------------
    # TAB 4: CADASTROS (PROFESSORES & MATÉRIAS)
    # --------------------------------------------------------------------------
    with abas_sec[3]:
        render_cadastros_base(supabase, perfil_usuario="Secretaria")

    # --------------------------------------------------------------------------
    # TAB 5: HISTÓRICO GERAL
    # --------------------------------------------------------------------------
    with abas_sec[4]:
        st.subheader("Histórico Completo de Ausências")
        st.dataframe(df_ausencias, use_container_width=True)
