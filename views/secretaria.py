import datetime
import streamlit as st
import pandas as pd
from supabase import Client
from services.supabase_service import (
    get_professores,
    get_disciplinas,
    get_turmas,
    get_ausencias_completas,
    registrar_ausencia_secretaria,
    anexar_atestado_reposicao,
    aprovar_atestado_secretaria,
    recusar_atestado_secretaria,
    verificar_conflito_substituto,
    get_reposicoes
)
from components.cadastros import render_cadastros_base

def render_secretaria_view(supabase: Client, user_profile: dict):
    """Renderiza a visão e as operações diárias da Secretaria."""
    df_prof = get_professores(supabase)
    df_disc = get_disciplinas(supabase)
    df_turmas = get_turmas(supabase)
    df_ausencias = get_ausencias_completas(supabase)

    # Quantidade de atestados aguardando homologação/aprovação da Secretaria
    aguardando_aprovacao = df_ausencias[df_ausencias["Status"] == "Aguardando Homologação"] if not df_ausencias.empty else pd.DataFrame()
    qtd_aguard = len(aguardando_aprovacao)
    badge_homolog = f"✅ Homologação ({qtd_aguard})" if qtd_aguard > 0 else "✅ Homologação"

    abas_sec = st.tabs([
        "📌 Lançamento",
        "🔄 Substituições",
        badge_homolog,
        "📑 Anexo de Atestados",
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

        # Escolha do Fluxo de Atestado
        st.markdown("##### 🩺 Fluxo de Comprovação / Atestado")
        fluxo_atestado = st.radio(
            "Como deseja tratar o atestado médico desta falta?",
            [
                "📅 Criar evento para o professor anexar o atestado depois",
                "📎 A Secretaria anexa o atestado agora"
            ],
            index=0,
            key="sec_fluxo_atestado_escolha",
            help="Defina se a Secretaria já anexará o atestado agora ou se criará um evento para o professor anexar pelo Portal do Docente."
        )

        anexar_agora = (fluxo_atestado == "📎 A Secretaria anexa o atestado agora")

        if anexar_agora:
            st.info("ℹ️ **Modo Secretaria:** A Secretaria já possui o atestado e irá anexá-lo agora ao registro da falta.")
        else:
            st.info("ℹ️ **Modo Evento/Docente:** A falta será registrada como um evento pendente. O professor receberá o alerta no **Portal do Docente** e ele mesmo anexará o atestado e indicará a reposição.")

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

            # Se a Secretaria optou por anexar o atestado agora
            doc_file = None
            data_rep = None
            horario_rep = None
            if anexar_agora:
                st.markdown("---")
                st.markdown("##### 📎 Anexo do Atestado pela Secretaria")
                col_att1, col_att2 = st.columns(2)
                with col_att1:
                    doc_file = st.file_uploader(
                        "Comprovante / Atestado Médico (PDF, PNG, JPG) *",
                        type=["pdf", "png", "jpg", "jpeg"]
                    )
                with col_att2:
                    data_rep = st.date_input("Data Acordada para Reposição (Opcional)", datetime.date.today() + datetime.timedelta(days=7))
                    horario_rep = st.text_input("Horário e Local da Reposição (Opcional)", placeholder="Ex: Sábado, 08:00 - 10:00 (Sala 102)")

            btn_label = "💾 Salvar Falta e Anexar Atestado" if anexar_agora else "💾 Criar Evento de Falta para o Professor"
            if st.form_submit_button(btn_label, type="primary", use_container_width=True):
                if df_prof.empty or df_disc.empty or df_turmas.empty:
                    st.error("Cadastros de apoio incompletos no banco de dados.")
                elif anexar_agora and not doc_file:
                    st.warning("⚠️ Você selecionou 'A Secretaria anexa o atestado agora', mas não selecionou nenhum arquivo. Por favor, selecione o arquivo ou alterne para 'Criar evento para o professor anexar o atestado depois'.")
                else:
                    prof_id = df_prof[df_prof["nome"] == prof_escolhido]["id"].values[0]
                    cod_disc = disc_escolhida.split(" - ")[0]
                    disc_id = df_disc[df_disc["codigo"] == cod_disc]["id"].values[0]
                    cod_turma = turma_escolhida.split(" - ")[0]
                    turma_id = df_turmas[df_turmas["codigo"] == cod_turma]["id"].values[0]
                    motivo_formatado = f"[{motivo_tipo}] {motivo_obs}".strip()

                    ok, msg = registrar_ausencia_secretaria(
                        supabase=supabase,
                        professor_id=prof_id,
                        disciplina_id=disc_id,
                        turma_id=turma_id,
                        data_ausencia=str(data_falta),
                        horario=horario_bloco,
                        motivo=motivo_formatado,
                        anexar_atestado_agora=anexar_agora,
                        doc_file=doc_file,
                        data_reposicao=str(data_rep) if (anexar_agora and data_rep) else None,
                        horario_reposicao=horario_rep if anexar_agora else None
                    )
                    if ok:
                        st.success(f"✅ {msg}")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

    # --------------------------------------------------------------------------
    # TAB 2: GESTÃO DE SUBSTITUIÇÕES E AULAS VAGAS
    # --------------------------------------------------------------------------
    with abas_sec[1]:
        st.subheader("Atribuição de Substituto ou Registro de Aula Vaga")
        st.caption("As faltas pendentes abaixo também ficam visíveis no **Portal do Docente**, onde outros professores disponíveis podem se candidatar para assumir a substituição.")
        pendentes = df_ausencias[
            (df_ausencias["Tratativa"] == "Pendente de tratativa") &
            (df_ausencias["Status"] != "Reposta")
        ] if not df_ausencias.empty else pd.DataFrame()

        if pendentes.empty:
            st.success("🎉 Nenhuma ausência pendente de substituto ou tratativa no momento.")
        else:
            opcoes_pend = {
                r["ID"]: f"{r['Data']} | {r['Professor']} | {r['Disciplina']} — {r['Turma']} ({r['Horário']})"
                for _, r in pendentes.iterrows()
            }
            esc_id = st.selectbox(
                "Ausência Pendente de Substituto:",
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
                    tem_conflito, msg_conflito = verificar_conflito_substituto(
                        supabase=supabase,
                        professor_substituto_id=sub_id,
                        data_ausencia=detalhe["Data"],
                        horario=detalhe["Horário"],
                        ausencia_id_atual=esc_id
                    )
                    if tem_conflito:
                        st.error(f"❌ {msg_conflito}")
                    else:
                        supabase.table("substituicoes").insert({
                            "ausencia_id": esc_id,
                            "professor_substituto_id": sub_id,
                            "aula_vaga": False,
                            "observacoes": "Alocado pela Secretaria"
                        }).execute()
                        if detalhe["Status"] == "Pendente":
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
                    if detalhe["Status"] == "Pendente":
                        supabase.table("ausencias").update({"status": "Aula Vaga"}).eq("id", esc_id).execute()
                    st.warning("Classificada como Aula Vaga.")
                    st.rerun()

        # Exibe também as substituições já assumidas (pelos professores no Portal ou pela Secretaria)
        ja_tratadas = df_ausencias[df_ausencias["Tratativa"] != "Pendente de tratativa"] if not df_ausencias.empty else pd.DataFrame()
        if not ja_tratadas.empty:
            st.markdown("---")
            st.markdown("##### 🤝 Substituições e Tratativas Já Definidas")
            df_tratadas_exib = pd.DataFrame({
                "Data": ja_tratadas["Data"],
                "Horário": ja_tratadas["Horário"],
                "Professor Ausente": ja_tratadas["Professor"],
                "Disciplina": ja_tratadas["Disciplina"],
                "Turma": ja_tratadas["Turma"],
                "NomeSubstituto": ja_tratadas["NomeSubstituto"],
                "AulaVaga": ja_tratadas["AulaVaga"],
                "Status": ja_tratadas["Status"]
            })
            st.dataframe(df_tratadas_exib, use_container_width=True, hide_index=True)

    # --------------------------------------------------------------------------
    # TAB 3: HOMOLOGAÇÃO & APROVAÇÃO DE ATESTADOS PELA SECRETARIA
    # --------------------------------------------------------------------------
    with abas_sec[2]:
        st.subheader("Homologação e Aceitação de Atestados")
        st.caption("Analise os atestados enviados pelos professores e aprove ou recuse a comprovação da ausência.")

        if aguardando_aprovacao.empty:
            st.success("🎉 Nenhum atestado pendente de homologação pela Secretaria no momento.")
        else:
            st.info(f"Há **{qtd_aguard} atestado(s)** aguardando sua análise e homologação.")
            df_rep = get_reposicoes(supabase)

            for _, r in aguardando_aprovacao.iterrows():
                with st.expander(f"📌 {r['Professor']} — {r['Disciplina']} ({r['Turma']}) — Data: {r['Data']}", expanded=True):
                    rep_det = df_rep[df_rep["ausencia_id"] == r["ID"]] if not df_rep.empty else pd.DataFrame()
                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.markdown(f"**Data da Falta:** {r['Data']} ({r['Horário']})")
                        st.markdown(f"**Disciplina & Turma:** {r['Disciplina']} — {r['Turma']}")
                        st.markdown(f"**Motivo Informado:** {r['Motivo']}")
                        st.markdown(f"**Registrado por:** {r.get('RegistradoPor', 'Secretaria')}")
                    with col_info2:
                        atest_url = r.get("AtestadoURL") or (rep_det.iloc[0].get("atestado_url") if not rep_det.empty else None)
                        if atest_url:
                            st.markdown(f"📄 **Comprovante Anexado:** [🔗 Abrir / Baixar Atestado Médico]({atest_url})")
                            with st.expander("👁️ Pré-visualizar Documento na Tela", expanded=False):
                                if str(atest_url).lower().split("?")[0].endswith((".png", ".jpg", ".jpeg")):
                                    st.image(atest_url, use_container_width=True)
                                else:
                                    st.markdown(
                                        f'<iframe src="{atest_url}" width="100%" height="450px" style="border: 1px solid #cbd5e1; border-radius: 8px;"></iframe>',
                                        unsafe_allow_html=True
                                    )
                        else:
                            st.warning("Nenhum arquivo de atestado vinculado.")

                        dt_r = rep_det.iloc[0].get("data_reposicao") if not rep_det.empty else None
                        hr_r = rep_det.iloc[0].get("horario_reposicao") if not rep_det.empty else None
                        st.markdown(f"**Data Proposta para Reposição:** {dt_r or 'Não informada'}")
                        st.markdown(f"**Horário / Local:** {hr_r or 'A combinar'}")

                    st.markdown("---")
                    col_btn1, col_btn2 = st.columns([1, 1])

                    with col_btn1:
                        if st.button("✅ Aprovar / Homologar Atestado", key=f"sec_aprov_{r['ID']}", type="primary", use_container_width=True):
                            ok, msg = aprovar_atestado_secretaria(supabase, r["ID"])
                            if ok:
                                st.success(f"✅ {msg}")
                                st.rerun()
                            else:
                                st.error(f"❌ {msg}")

                    with col_btn2:
                        with st.popover("❌ Não Aprovar / Recusar (Devolver ao Professor)", use_container_width=True):
                            st.markdown("##### Devolver Atestado para o Professor")
                            st.caption("A ausência voltará a ficar pendente para que o professor anexe um novo atestado corrigido.")
                            motivo_recusa_input = st.text_area(
                                "Justificativa da não aprovação (obrigatório):",
                                placeholder="Ex: Atestado ilegível / Sem assinatura ou carimbo do médico / Data divergente da falta.",
                                key=f"motivo_recusa_{r['ID']}"
                            )
                            if st.button("Confirmar Não Aprovação", key=f"btn_recusa_{r['ID']}", type="secondary", use_container_width=True):
                                if not motivo_recusa_input.strip():
                                    st.warning("Por favor, digite a justificativa para orientar o professor.")
                                else:
                                    ok, msg = recusar_atestado_secretaria(supabase, r["ID"], motivo_recusa_input)
                                    if ok:
                                        st.warning(f"⚠️ {msg}")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {msg}")

    # --------------------------------------------------------------------------
    # TAB 4: ANEXO DE ATESTADOS & REPOSIÇÕES
    # --------------------------------------------------------------------------
    with abas_sec[3]:
        st.subheader("Anexo de Atestados e Registro de Reposição Acordada")
        st.caption("A Secretaria pode anexar o atestado médico e a proposta de reposição para qualquer ausência (inclusive as criadas como evento para o professor).")
        if df_ausencias.empty:
            st.info("Nenhuma ausência registrada para vincular atestado.")
        else:
            pendentes_atestado = df_ausencias[df_ausencias["Atestado"] == "Não"]
            filtro_visao = st.radio(
                "Filtrar ausências para anexar atestado:",
                ["Apenas Ausências sem Atestado", "Todas as Ocorrências"],
                horizontal=True
            )
            df_para_anexo = pendentes_atestado if (filtro_visao == "Apenas Ausências sem Atestado" and not pendentes_atestado.empty) else df_ausencias

            if df_para_anexo.empty:
                st.success("🎉 Todas as ausências registradas já possuem atestado anexado!")
            else:
                opcoes_todas = {
                    r["ID"]: f"{r['Data']} — {r['Professor']} — {r['Disciplina']} ({r['Status']} | Reg: {r['RegistradoPor']})"
                    for _, r in df_para_anexo.iterrows()
                }
                aus_id = st.selectbox(
                    "Selecione a ausência:",
                    list(opcoes_todas.keys()),
                    format_func=lambda x: opcoes_todas[x]
                )

                with st.form("form_sec_anexo"):
                    doc_file = st.file_uploader("Anexo do Comprovante (PDF ou Imagem) *", type=["pdf", "png", "jpg", "jpeg"])
                    data_rep = st.date_input("Data Acordada para Reposição", datetime.date.today() + datetime.timedelta(days=7))
                    horario_rep = st.text_input("Horário e Local da Reposição", placeholder="Ex: Sábado, 08:00 - 10:00 (Sala 102)")

                    if st.form_submit_button("Salvar e Enviar para Homologação", type="primary"):
                        if not doc_file:
                            st.warning("Selecione um arquivo de atestado (PDF, PNG ou JPG) para anexar.")
                        else:
                            ok, msg = anexar_atestado_reposicao(
                                supabase=supabase,
                                ausencia_id=aus_id,
                                doc_file=doc_file,
                                data_reposicao=str(data_rep),
                                horario_reposicao=horario_rep
                            )
                            if ok:
                                st.success("✅ Atestado anexado e enviado para homologação!")
                                st.rerun()
                            else:
                                st.error(f"❌ {msg}")

    # --------------------------------------------------------------------------
    # TAB 5: CADASTROS (PROFESSORES & MATÉRIAS)
    # --------------------------------------------------------------------------
    with abas_sec[4]:
        render_cadastros_base(supabase, perfil_usuario="Secretaria")

    # --------------------------------------------------------------------------
    # TAB 6: HISTÓRICO GERAL
    # --------------------------------------------------------------------------
    with abas_sec[5]:
        st.subheader("Histórico Completo de Ausências")
        if df_ausencias.empty:
            st.info("Nenhuma ausência registrada no histórico até o momento.")
        else:
            st.caption("💡 Clique em **'📄 Ver Atestado'** na coluna **Atestado** para abrir o documento em nova guia, ou selecione uma linha da tabela para pré-visualizar o atestado na tela.")

            df_historico = pd.DataFrame({
                "Data": df_ausencias["Data"],
                "Horário": df_ausencias["Horário"],
                "Professor": df_ausencias["Professor"],
                "Motivo": df_ausencias["Motivo"],
                "Status": df_ausencias["Status"],
                "Atestado": df_ausencias["AtestadoURL"],
                "NomeSubstituto": df_ausencias["NomeSubstituto"],
                "AulaVaga": df_ausencias["AulaVaga"]
            })

            evento_sel = st.dataframe(
                df_historico,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row",
                column_config={
                    "Data": st.column_config.TextColumn("Data"),
                    "Horário": st.column_config.TextColumn("Horário"),
                    "Professor": st.column_config.TextColumn("Professor"),
                    "Motivo": st.column_config.TextColumn("Motivo"),
                    "Status": st.column_config.TextColumn("Status"),
                    "Atestado": st.column_config.LinkColumn(
                        "Atestado",
                        display_text="📄 Ver Atestado",
                        help="Clique para abrir o atestado enviado"
                    ),
                    "NomeSubstituto": st.column_config.TextColumn("NomeSubstituto"),
                    "AulaVaga": st.column_config.CheckboxColumn("AulaVaga")
                }
            )

            # Se a secretaria selecionou uma linha na tabela para pré-visualizar na plataforma
            linhas_selecionadas = evento_sel.selection.rows if (evento_sel and hasattr(evento_sel, "selection")) else []
            if linhas_selecionadas:
                idx_sel = linhas_selecionadas[0]
                reg_sel = df_ausencias.iloc[idx_sel]
                url_sel = reg_sel.get("AtestadoURL")
                if url_sel:
                    with st.container():
                        st.markdown("---")
                        st.markdown(f"##### 👁️ Visualização do Atestado — {reg_sel['Professor']} ({reg_sel['Data']} | {reg_sel['Horário']})")
                        st.markdown(f"🔗 **[Abrir / Baixar Atestado em Nova Guia]({url_sel})**")
                        if str(url_sel).lower().split("?")[0].endswith((".png", ".jpg", ".jpeg")):
                            st.image(url_sel, use_container_width=True)
                        else:
                            st.markdown(
                                f'<iframe src="{url_sel}" width="100%" height="500px" style="border: 1px solid #cbd5e1; border-radius: 8px;"></iframe>',
                                unsafe_allow_html=True
                            )
                else:
                    st.info(f"ℹ️ A ocorrência selecionada ({reg_sel['Professor']} em {reg_sel['Data']}) ainda não possui atestado anexado na plataforma.")
