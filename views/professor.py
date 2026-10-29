import datetime
import streamlit as st
import pandas as pd
from supabase import Client
from services.supabase_service import (
    get_ausencias_do_professor,
    get_substituicoes_do_professor,
    get_disciplinas,
    get_turmas,
    get_professores,
    anexar_atestado_reposicao,
    registrar_ausencia_docente
)

def render_professor_view(supabase: Client, user_profile: dict):
    """
    Renderiza o Portal do Docente:
    - Consulta de ausências registradas (pela Secretaria ou pelo próprio docente)
    - Envio de atestados médicos e proposta de reposição de aulas
    - Auto-registro de faltas/ausências planejadas
    - Acompanhamento de convocações para substituição
    """
    email_usuario = user_profile.get("email", "").strip().lower()
    nome_usuario = user_profile.get("nome", "Docente")
    professor_id = user_profile.get("professor_id")

    # Fallback se o professor_id não estiver em cache na sessão
    if not professor_id and email_usuario:
        try:
            res_p = supabase.table("professores").select("id, nome").ilike("email", email_usuario).execute()
            if res_p.data and len(res_p.data) > 0:
                professor_id = res_p.data[0]["id"]
                user_profile["professor_id"] = professor_id
        except Exception:
            pass

    # Caso seja o Administrador simulando ou um professor sem vínculo prévio na tabela professores
    df_todos_prof = get_professores(supabase)
    if not professor_id:
        st.warning("⚠️ **Vínculo Docente não localizado automaticamente.**")
        st.info("Para vincular sua conta à grade de docentes, selecione o seu nome de professor cadastrado abaixo:")
        if not df_todos_prof.empty:
            escolha_docente = st.selectbox(
                "Selecione o perfil de docente:",
                df_todos_prof["nome"].tolist()
            )
            if st.button("🔗 Confirmar e Vincular Conta", type="primary"):
                match_id = df_todos_prof[df_todos_prof["nome"] == escolha_docente]["id"].values[0]
                user_profile["professor_id"] = match_id
                try:
                    supabase.table("usuarios").update({"professor_id": match_id}).eq("id", user_profile.get("id")).execute()
                except Exception:
                    pass
                st.success(f"Conta vinculada ao docente {escolha_docente} com sucesso!")
                st.rerun()
            return
        else:
            st.error("Nenhum professor cadastrado no banco de dados. Solicite o cadastro à Secretaria.")
            return

    # Busca ocorrências específicas deste professor
    df_minhas_ausencias = get_ausencias_do_professor(supabase, professor_id)
    df_minhas_subst = get_substituicoes_do_professor(supabase, professor_id)
    df_disc = get_disciplinas(supabase)
    df_turmas = get_turmas(supabase)

    # ==========================================================================
    # CARDS DE RESUMO E INDICADORES
    # ==========================================================================
    total_faltas = len(df_minhas_ausencias) if not df_minhas_ausencias.empty else 0
    sem_atestado = len(df_minhas_ausencias[df_minhas_ausencias["Atestado"] == "Não"]) if not df_minhas_ausencias.empty else 0
    aguardando_homolog = len(df_minhas_ausencias[df_minhas_ausencias["Status"] == "Aguardando Homologação"]) if not df_minhas_ausencias.empty else 0
    homologadas = len(df_minhas_ausencias[df_minhas_ausencias["Status"] == "Reposta"]) if not df_minhas_ausencias.empty else 0

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Minhas Ausências", total_faltas)
    col_m2.metric("Pendentes de Atestado", sem_atestado, delta=None if sem_atestado == 0 else f"{sem_atestado} pendente(s)", delta_color="inverse")
    col_m3.metric("Aguardando Homologação", aguardando_homolog)
    col_m4.metric("Reposições Concluídas", homologadas)

    st.markdown("---")

    # ==========================================================================
    # NAVEGAÇÃO EM ABAS
    # ==========================================================================
    aba_minhas, aba_comunicar, aba_subst = st.tabs([
        "📋 Minhas Ausências & Atestados",
        "📢 Comunicar Ausência (Auto-registro)",
        "🤝 Minhas Substituições"
    ])

    # --------------------------------------------------------------------------
    # TAB 1: MINHAS AUSÊNCIAS & ENVIO DE ATESTADOS
    # --------------------------------------------------------------------------
    with aba_minhas:
        st.subheader("Minhas Ocorrências e Envio de Comprovantes")
        st.caption("Consulte suas ausências registradas e envie atestados médicos ou justificativas para análise da Coordenação.")

        # Se houver ausências sem atestado, destaca um formulário de anexo rápido
        aus_pendentes_anexo = df_minhas_ausencias[
            (df_minhas_ausencias["Atestado"] == "Não") | (df_minhas_ausencias["Status"] == "Pendente")
        ] if not df_minhas_ausencias.empty else pd.DataFrame()

        if not aus_pendentes_anexo.empty:
            with st.expander("📤 **Anexar Atestado / Justificar Falta Pendente**", expanded=True):
                st.info(f"Você possui **{len(aus_pendentes_anexo)}** ocorrência(s) sem atestado ou com reposição pendente.")
                
                opcoes_aus = {
                    r["ID"]: f"{r['Data']} — {r['Disciplina']} ({r['Turma']} | {r['Horário']})"
                    for _, r in aus_pendentes_anexo.iterrows()
                }
                aus_id_sel = st.selectbox(
                    "Selecione a ausência que deseja comprovar / repor:",
                    options=list(opcoes_aus.keys()),
                    format_func=lambda x: opcoes_aus[x]
                )

                with st.form("form_prof_anexar_atestado"):
                    col_u1, col_u2 = st.columns(2)
                    with col_u1:
                        arq_atestado = st.file_uploader(
                            "Anexar Atestado Médico / Documento Comprobatório (PDF, PNG, JPG) *",
                            type=["pdf", "png", "jpg", "jpeg"]
                        )
                    with col_u2:
                        dt_proposta = st.date_input(
                            "Data Sugerida para Reposição da Aula *",
                            datetime.date.today() + datetime.timedelta(days=5)
                        )
                        hr_proposta = st.text_input(
                            "Horário e Local Proposto *",
                            placeholder="Ex: Terça-feira, 18:00 - 19:40 (Sala 204 ou Remoto)"
                        )

                    btn_submeter = st.form_submit_button("🚀 Enviar Atestado e Proposta de Reposição", type="primary", use_container_width=True)
                    if btn_submeter:
                        if not arq_atestado:
                            st.warning("Por favor, selecione o arquivo do atestado ou comprovante.")
                        else:
                            ok_anexo, msg_anexo = anexar_atestado_reposicao(
                                supabase=supabase,
                                ausencia_id=aus_id_sel,
                                doc_file=arq_atestado,
                                data_reposicao=str(dt_proposta),
                                horario_reposicao=hr_proposta
                            )
                            if ok_anexo:
                                st.success(f"✅ {msg_anexo}")
                                st.rerun()
                            else:
                                st.error(f"❌ {msg_anexo}")

        # Tabela com o histórico das ausências do professor
        st.markdown("##### 📜 Histórico Pessoal de Faltas e Reposições")
        if not df_minhas_ausencias.empty:
            cols_exib = [
                "Data", "Horário", "Disciplina", "Turma",
                "Motivo", "Status", "RegistradoPor", "Atestado", "InfoReposicao", "RepComprovada"
            ]
            st.dataframe(df_minhas_ausencias[cols_exib], use_container_width=True, hide_index=True)

            # Link para visualização direta de atestados já anexados
            com_anexo = df_minhas_ausencias[df_minhas_ausencias["AtestadoURL"].notna() & (df_minhas_ausencias["AtestadoURL"] != "")]
            if not com_anexo.empty:
                with st.expander("📎 Ver Meus Atestados Anexados"):
                    for _, r in com_anexo.iterrows():
                        st.markdown(f"• **{r['Data']} — {r['Disciplina']}:** [Acessar Comprovante Anexo]({r['AtestadoURL']}) — *Status: {r['Status']}*")
        else:
            st.success("🎉 Você não possui nenhuma ausência registrada!")

    # --------------------------------------------------------------------------
    # TAB 2: COMUNICAR AUSÊNCIA (AUTO-REGISTRO)
    # --------------------------------------------------------------------------
    with aba_comunicar:
        st.subheader("Comunicar Ausência com Antecedência ou Justificativa")
        st.caption("Comunique à instituição sobre uma ausência programada (consulta, viagem acadêmica ou emergência) para que a Secretaria e a Coordenação possam se organizar.")

        if df_disc.empty or df_turmas.empty:
            st.warning("Disciplinas ou turmas não cadastradas. Entre em contato com a Secretaria.")
        else:
            with st.form("form_prof_auto_ausencia", clear_on_submit=True):
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    disc_sel = st.selectbox(
                        "Matéria / Disciplina *",
                        [f"{r['codigo']} - {r['nome']}" for _, r in df_disc.iterrows()]
                    )
                    turma_sel = st.selectbox(
                        "Turma Afetada *",
                        [f"{r['codigo']} - {r['curso']}" for _, r in df_turmas.iterrows()]
                    )
                    data_prevista = st.date_input("Data da Ausência *", datetime.date.today())

                with col_c2:
                    horario_sel = st.selectbox(
                        "Horário / Bloco *",
                        [
                            "1º Horário (07:30 - 09:10)",
                            "2º Horário (09:30 - 11:10)",
                            "3º Horário (19:00 - 20:40)",
                            "4º Horário (20:50 - 22:30)"
                        ]
                    )
                    cat_motivo = st.selectbox(
                        "Motivo da Ausência *",
                        [
                            "Consulta Médica / Tratamento de Saúde",
                            "Congresso / Evento Acadêmico",
                            "Assuntos Pessoais Inadiáveis",
                            "Problemas de Transporte / Deslocamento",
                            "Outros"
                        ]
                    )
                    detalhe_motivo = st.text_area("Descrição / Observações Adicionais (opcional)")

                st.markdown("##### 📑 Comprovação e Reposição Proposta (Opcional no momento do registro)")
                col_c3, col_c4 = st.columns(2)
                with col_c3:
                    doc_anexo = st.file_uploader(
                        "Já possui atestado ou comprovante? (Opcional)",
                        type=["pdf", "png", "jpg", "jpeg"],
                        key="upload_auto_ausencia"
                    )
                with col_c4:
                    dt_rep = st.date_input("Data Pretendida para Reposição", datetime.date.today() + datetime.timedelta(days=7))
                    hr_rep = st.text_input("Horário e Local Sugerido para Repor", placeholder="Ex: Sábado, 09:00 - 10:40 (Lab 02)")

                btn_salvar_auto = st.form_submit_button("💾 Confirmar e Registrar Ausência", type="primary", use_container_width=True)
                if btn_salvar_auto:
                    cod_d = disc_sel.split(" - ")[0]
                    d_id = df_disc[df_disc["codigo"] == cod_d]["id"].values[0]
                    cod_t = turma_sel.split(" - ")[0]
                    t_id = df_turmas[df_turmas["codigo"] == cod_t]["id"].values[0]

                    motivo_formatado = f"[{cat_motivo}] {detalhe_motivo}".strip()

                    ok_cad, msg_cad = registrar_ausencia_docente(
                        supabase=supabase,
                        professor_id=professor_id,
                        disciplina_id=d_id,
                        turma_id=t_id,
                        data_ausencia=str(data_prevista),
                        horario=horario_sel,
                        motivo=motivo_formatado,
                        doc_file=doc_anexo,
                        data_reposicao=str(dt_rep) if doc_anexo or hr_rep else None,
                        horario_reposicao=hr_rep if hr_rep else None
                    )

                    if ok_cad:
                        st.success(f"✅ {msg_cad}")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg_cad}")

    # --------------------------------------------------------------------------
    # TAB 3: MINHAS SUBSTITUIÇÕES
    # --------------------------------------------------------------------------
    with aba_subst:
        st.subheader("Aulas em que Você foi Alocado como Substituto")
        st.caption("Acompanhe as turmas onde a Secretaria Acadêmica escalou você para cobrir a ausência de outro professor.")

        if not df_minhas_subst.empty:
            cols_subst = ["Data", "Horário", "Professor", "Disciplina", "Turma", "Status"]
            df_exib_sub = df_minhas_subst[cols_subst].rename(columns={"Professor": "Professor Titular Ausente"})
            st.dataframe(df_exib_sub, use_container_width=True, hide_index=True)
        else:
            st.info("ℹ️ Você não possui nenhuma escala de substituição pendente ou confirmada no momento.")
