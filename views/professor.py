import datetime
import streamlit as st
import pandas as pd
from supabase import Client
from services.supabase_service import (
    get_ausencias_do_professor,
    get_substituicoes_do_professor,
    get_substituicoes_disponiveis_para_professor,
    candidatar_substituicao_docente,
    cancelar_substituicao_docente,
    verificar_conflito_substituto,
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
    if user_profile.get("perfil") == "Administrador" and not df_todos_prof.empty:
        opcoes_sim = {r["id"]: f"👨‍🏫 {r['nome']} ({r['email']})" for _, r in df_todos_prof.iterrows()}
        idx_padrao = list(opcoes_sim.keys()).index(professor_id) if professor_id in opcoes_sim else 0
        prof_sim_id = st.selectbox(
            "🔄 Alternar docente visualizado no Portal (Modo Administrador):",
            options=list(opcoes_sim.keys()),
            index=idx_padrao,
            format_func=lambda x: opcoes_sim[x],
            key="admin_sim_prof_select"
        )
        professor_id = prof_sim_id
        user_profile["professor_id"] = prof_sim_id

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

    # Busca ocorrências específicas deste professor e oportunidades de substituição abertas
    df_minhas_ausencias = get_ausencias_do_professor(supabase, professor_id)
    df_minhas_subst = get_substituicoes_do_professor(supabase, professor_id)
    df_subst_disponiveis = get_substituicoes_disponiveis_para_professor(supabase, professor_id)
    df_disc = get_disciplinas(supabase)
    df_turmas = get_turmas(supabase)

    # ==========================================================================
    # CARDS DE RESUMO E INDICADORES
    # ==========================================================================
    total_faltas = len(df_minhas_ausencias) if not df_minhas_ausencias.empty else 0
    sem_atestado = len(df_minhas_ausencias[df_minhas_ausencias["Atestado"] == "Não"]) if not df_minhas_ausencias.empty else 0
    aguardando_homolog = len(df_minhas_ausencias[df_minhas_ausencias["Status"] == "Aguardando Homologação"]) if not df_minhas_ausencias.empty else 0
    homologadas = len(df_minhas_ausencias[df_minhas_ausencias["Status"].isin(["Reposta", "Aprovada"])]) if not df_minhas_ausencias.empty else 0
    qtd_subst_disp = len(df_subst_disponiveis) if not df_subst_disponiveis.empty else 0
    qtd_minhas_subst = len(df_minhas_subst) if not df_minhas_subst.empty else 0

    col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
    col_m1.metric("Minhas Ausências", total_faltas)
    col_m2.metric("Pendentes de Atestado", sem_atestado, delta=None if sem_atestado == 0 else f"{sem_atestado} pendente(s)", delta_color="inverse")
    col_m3.metric("Aguardando Homologação", aguardando_homolog)
    col_m4.metric("Atestados Aprovados", homologadas)
    col_m5.metric(
        "Substituições Pendentes",
        qtd_subst_disp,
        delta=f"{qtd_minhas_subst} assumida(s) por você" if qtd_minhas_subst > 0 else ("Disponíveis para assumir" if qtd_subst_disp > 0 else None)
    )

    # Identifica ausências que foram recusadas pela Secretaria e voltaram a ficar pendentes
    ausencias_recusadas = df_minhas_ausencias[
        df_minhas_ausencias["Motivo"].str.contains(r"\[Recusa da Secretaria:", regex=True, na=False) & 
        (df_minhas_ausencias["Status"] == "Pendente")
    ] if not df_minhas_ausencias.empty else pd.DataFrame()

    if not ausencias_recusadas.empty:
        st.error(
            f"❌ **Atenção:** Você possui **{len(ausencias_recusadas)} atestado(s) que não foram aprovados pela Secretaria**. A ocorrência voltou a ficar pendente para que você anexe o comprovante corrigido. Veja os detalhes abaixo na aba 'Minhas Ausências & Atestados'."
        )

    # Eventos de falta registrados pela Secretaria pendentes de atestado pelo docente ou recusados
    eventos_secretaria = df_minhas_ausencias[
        (
            ((df_minhas_ausencias["RegistradoPor"] == "Secretaria") & (df_minhas_ausencias["Atestado"] == "Não")) |
            (df_minhas_ausencias["Motivo"].str.contains(r"\[Recusa da Secretaria:", regex=True, na=False))
        ) & 
        (~df_minhas_ausencias["Status"].isin(["Reposta", "Aprovada", "Aguardando Homologação"]))
    ] if not df_minhas_ausencias.empty else pd.DataFrame()

    if not eventos_secretaria.empty and ausencias_recusadas.empty:
        st.warning(
            f"🔔 **Atenção:** A Secretaria registrou **{len(eventos_secretaria)} ocorrência(s) de falta** em seu nome aguardando envio de atestado médico comprobatório e indicação de reposição de aula. Confira a seção destacada abaixo."
        )

    if aguardando_homolog > 0:
        st.info(f"⏳ Você possui **{aguardando_homolog} atestado(s)** enviado(s) que estão **pendentes de homologação/aprovação pela Secretaria**.")

    if qtd_subst_disp > 0:
        st.info(
            f"🙋‍♂️ **Oportunidade de Substituição:** Há **{qtd_subst_disp} aula(s) pendente(s) de professor substituto** lançada(s) no sistema. Acesse a aba **'🤝 Substituições ({qtd_subst_disp})'** para se candidatar e assumir a aula!"
        )

    st.markdown("---")

    # ==========================================================================
    # NAVEGAÇÃO EM ABAS
    # ==========================================================================
    label_aba_subst = f"🤝 Substituições ({qtd_subst_disp})" if qtd_subst_disp > 0 else "🤝 Substituições"
    aba_minhas, aba_comunicar, aba_subst = st.tabs([
        "📋 Minhas Ausências & Atestados",
        "📢 Comunicar Ausência (Auto-registro)",
        label_aba_subst
    ])

    # --------------------------------------------------------------------------
    # TAB 1: MINHAS AUSÊNCIAS & ENVIO DE ATESTADOS
    # --------------------------------------------------------------------------
    with aba_minhas:
        st.subheader("Minhas Ocorrências e Envio de Comprovantes")
        st.caption("Consulte suas ausências registradas e envie atestados médicos ou justificativas para homologação da Secretaria.")

        # ======================================================================
        # SEÇÃO 1: EVENTOS DA SECRETARIA / ATESTADOS RECUSADOS PENDENTES
        # ======================================================================
        if not eventos_secretaria.empty:
            st.markdown("#### 🔔 Faltas Aguardando seu Atestado Médico")
            st.info("Abaixo estão as ocorrências que requerem o envio do seu atestado médico e indicação de data/horário para reposição de aula.")

            opcoes_sec = {
                r["ID"]: f"{r['Data']} — {r['Disciplina']} ({r['Turma']} | {r['Horário']})"
                for _, r in eventos_secretaria.iterrows()
            }
            ev_sel_id = st.selectbox(
                "Selecione a ausência para anexar seu atestado:",
                options=list(opcoes_sec.keys()),
                format_func=lambda x: opcoes_sec[x],
                key="sel_evento_secretaria"
            )
            ev_detalhe = eventos_secretaria[eventos_secretaria["ID"] == ev_sel_id].iloc[0]

            # Verifica se essa ocorrência foi recusada anteriormente pela Secretaria
            motivo_completo = str(ev_detalhe.get("Motivo", ""))
            motivo_recusa = ""
            if "[Recusa da Secretaria:" in motivo_completo:
                try:
                    motivo_recusa = motivo_completo.split("[Recusa da Secretaria:")[1].split("]")[0].strip()
                except Exception:
                    motivo_recusa = motivo_completo

            if motivo_recusa:
                st.markdown(f"""
                <div style="background-color: #fef2f2; border: 1.5px solid #ef4444; border-radius: 8px; padding: 14px; margin-bottom: 14px;">
                    <b style="color: #b91c1c; font-size: 15px;">❌ Atestado Anterior Não Aprovado pela Secretaria:</b><br/>
                    <span style="color: #7f1d1d; font-size: 14px;"><i>"{motivo_recusa}"</i></span><br/><br/>
                    <b style="color: #991b1b;">⚠️ A ausência voltou a ficar pendente para você. Por favor, anexe um novo comprovante corrigido abaixo:</b>
                </div>
                """, unsafe_allow_html=True)
            else:
                with st.container():
                    st.markdown(f"""
                    <div style="background-color: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; padding: 12px; margin-bottom: 12px;">
                        <b>📅 Data da Ausência:</b> {ev_detalhe['Data']} ({ev_detalhe['Horário']})<br/>
                        <b>📚 Disciplina & Turma:</b> {ev_detalhe['Disciplina']} — {ev_detalhe['Turma']}<br/>
                        <b>📝 Motivo registrado pela Secretaria:</b> {ev_detalhe['Motivo']}<br/>
                        <b>📌 Status Operacional:</b> {ev_detalhe['Status']}
                    </div>
                    """, unsafe_allow_html=True)

            with st.form("form_prof_anexar_evento_sec"):
                col_u1, col_u2 = st.columns(2)
                with col_u1:
                    arq_atestado_ev = st.file_uploader(
                        "Anexar Atestado Médico / Documento Comprobatório (PDF, PNG, JPG) *",
                        type=["pdf", "png", "jpg", "jpeg"],
                        key="upload_ev_sec"
                    )
                with col_u2:
                    dt_proposta_ev = st.date_input(
                        "Data Sugerida para Reposição da Aula *",
                        datetime.date.today() + datetime.timedelta(days=5),
                        key="dt_rep_ev"
                    )
                    hr_proposta_ev = st.text_input(
                        "Horário e Local Proposto *",
                        placeholder="Ex: Sábado, 09:00 - 10:40 (Sala 102 ou Remoto)",
                        key="hr_rep_ev"
                    )

                btn_txt = "🚀 Reenviar Atestado Corrigido para a Secretaria" if motivo_recusa else "🚀 Enviar Atestado para Homologação da Secretaria"
                if st.form_submit_button(btn_txt, type="primary", use_container_width=True):
                    if not arq_atestado_ev:
                        st.warning("Por favor, selecione o arquivo do atestado ou comprovante.")
                    else:
                        ok_anexo, msg_anexo = anexar_atestado_reposicao(
                            supabase=supabase,
                            ausencia_id=ev_sel_id,
                            doc_file=arq_atestado_ev,
                            data_reposicao=str(dt_proposta_ev),
                            horario_reposicao=hr_proposta_ev
                        )
                        if ok_anexo:
                            st.success(f"✅ {msg_anexo}")
                            st.rerun()
                        else:
                            st.error(f"❌ {msg_anexo}")

            st.markdown("---")

        # ======================================================================
        # SEÇÃO 2: OUTRAS AUSÊNCIAS PENDENTES DE ATESTADO (AUTO-REGISTRADAS)
        # ======================================================================
        outras_pendentes = df_minhas_ausencias[
            (df_minhas_ausencias["RegistradoPor"] != "Secretaria") &
            ((df_minhas_ausencias["Atestado"] == "Não") | (df_minhas_ausencias["Status"] == "Pendente")) &
            (df_minhas_ausencias["Status"] != "Reposta")
        ] if not df_minhas_ausencias.empty else pd.DataFrame()

        if not outras_pendentes.empty:
            with st.expander("📤 **Anexar Atestado para Ausências Auto-registradas**", expanded=False):
                opcoes_outras = {
                    r["ID"]: f"{r['Data']} — {r['Disciplina']} ({r['Turma']} | {r['Horário']})"
                    for _, r in outras_pendentes.iterrows()
                }
                outra_sel_id = st.selectbox(
                    "Selecione a ocorrência comunicada:",
                    options=list(opcoes_outras.keys()),
                    format_func=lambda x: opcoes_outras[x],
                    key="sel_outra_ausencia"
                )
                with st.form("form_prof_anexar_outra"):
                    col_o1, col_o2 = st.columns(2)
                    with col_o1:
                        arq_outra = st.file_uploader(
                            "Anexar Atestado Médico (PDF, PNG, JPG) *",
                            type=["pdf", "png", "jpg", "jpeg"],
                            key="upload_outra"
                        )
                    with col_o2:
                        dt_outra = st.date_input("Data Sugerida para Repor *", datetime.date.today() + datetime.timedelta(days=5), key="dt_outra")
                        hr_outra = st.text_input("Horário e Local Proposto *", placeholder="Ex: Terça-feira, 18:00 - 19:40", key="hr_outra")

                    if st.form_submit_button("🚀 Enviar Atestado", type="primary", use_container_width=True):
                        if not arq_outra:
                            st.warning("Selecione o arquivo do comprovante.")
                        else:
                            ok_anexo, msg_anexo = anexar_atestado_reposicao(
                                supabase=supabase,
                                ausencia_id=outra_sel_id,
                                doc_file=arq_outra,
                                data_reposicao=str(dt_outra),
                                horario_reposicao=hr_outra
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
    # TAB 3: SUBSTITUIÇÕES PENDENTES & MINHAS SUBSTITUIÇÕES
    # --------------------------------------------------------------------------
    with aba_subst:
        st.subheader("🙋‍♂️ Substituições Pendentes — Candidatar-se para Substituir")
        st.caption("Veja abaixo as faltas lançadas que ainda não possuem professor substituto e candidate-se para assumir a aula.")

        if df_subst_disponiveis.empty:
            st.success("🎉 Nenhuma aula de outros docentes aguardando substituto no momento.")
        else:
            st.info(f"Há **{len(df_subst_disponiveis)} aula(s)** disponível(is) aguardando um professor substituto:")

            for _, r_sub in df_subst_disponiveis.iterrows():
                tem_conflito_sub, msg_conflito_sub = verificar_conflito_substituto(
                    supabase=supabase,
                    professor_substituto_id=professor_id,
                    data_ausencia=r_sub["Data"],
                    horario=r_sub["Horário"],
                    ausencia_id_atual=r_sub["ID"]
                )
                badge_agenda = "🔴 Conflito na sua agenda" if tem_conflito_sub else "🟢 Horário livre na sua agenda"

                with st.expander(
                    f"📅 {r_sub['Data']} ({r_sub['Horário']}) — {r_sub['Disciplina']} | Turma: {r_sub['Turma']} — Prof. Ausente: {r_sub['Professor']} [{badge_agenda}]",
                    expanded=True
                ):
                    c_s1, c_s2 = st.columns([2, 1])
                    with c_s1:
                        st.markdown(f"**👨‍🏫 Professor Titular Ausente:** {r_sub['Professor']}")
                        st.markdown(f"**📖 Disciplina & Turma:** {r_sub['Disciplina']} — {r_sub['Turma']}")
                        st.markdown(f"**🕒 Data e Horário da Aula:** {r_sub['Data']} — {r_sub['Horário']}")
                        st.markdown(f"**📝 Motivo da Ausência:** {r_sub['Motivo']}")
                    with c_s2:
                        if tem_conflito_sub:
                            st.error(f"⚠️ {msg_conflito_sub}")
                        else:
                            st.success("✅ Você está disponível neste dia e bloco de horário.")

                        obs_cand = st.text_input(
                            "Observação / Plano de Aula (opcional):",
                            placeholder="Ex: Posso assumir e aplicar o conteúdo da matéria.",
                            key=f"obs_cand_{r_sub['ID']}"
                        )
                        if st.button(
                            "🙋‍♂️ Candidatar-me / Assumir como Substituto",
                            key=f"btn_cand_{r_sub['ID']}",
                            type="primary",
                            use_container_width=True,
                            disabled=tem_conflito_sub
                        ):
                            ok_sub, msg_sub = candidatar_substituicao_docente(
                                supabase=supabase,
                                ausencia_id=r_sub["ID"],
                                professor_substituto_id=professor_id,
                                observacoes=obs_cand
                            )
                            if ok_sub:
                                st.success(f"✅ {msg_sub}")
                                st.rerun()
                            else:
                                st.error(f"❌ {msg_sub}")

        st.markdown("---")
        st.subheader("📋 Minhas Substituições Confirmadas")
        st.caption("Acompanhe as turmas onde você já está alocado como professor substituto (por candidatura própria ou escala da Secretaria).")

        if not df_minhas_subst.empty:
            cols_subst = ["Data", "Horário", "Professor", "Disciplina", "Turma", "Status", "Tratativa"]
            df_exib_sub = df_minhas_subst[cols_subst].rename(columns={
                "Professor": "Professor Titular Ausente",
                "Tratativa": "Detalhes da Substituição"
            })
            st.dataframe(df_exib_sub, use_container_width=True, hide_index=True)

            with st.expander("↩️ Precisa liberar/desistir de uma substituição assumida?"):
                opcoes_cancel = {
                    r["ID"]: f"{r['Data']} ({r['Horário']}) — {r['Disciplina']} | Turma: {r['Turma']} (Titular: {r['Professor']})"
                    for _, r in df_minhas_subst.iterrows()
                }
                id_cancel = st.selectbox(
                    "Selecione a substituição que deseja liberar:",
                    options=list(opcoes_cancel.keys()),
                    format_func=lambda x: opcoes_cancel[x],
                    key="sel_cancel_subst_prof"
                )
                if st.button("Confirmar Liberação da Substituição", type="secondary", key="btn_cancel_subst_prof"):
                    ok_c, msg_c = cancelar_substituicao_docente(supabase, id_cancel, professor_id)
                    if ok_c:
                        st.warning(f"↩️ {msg_c}")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg_c}")
        else:
            st.info("ℹ️ Você ainda não possui nenhuma substituição confirmada em seu nome.")
