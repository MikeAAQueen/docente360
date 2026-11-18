import streamlit as st
import pandas as pd
from supabase import Client
from services.supabase_service import (
    get_ausencias_completas,
    get_usuarios_cadastrados,
    get_professores,
    get_disciplinas,
    get_turmas
)
from components.cadastros import render_cadastros_base

def render_admin_view(supabase: Client, user_profile: dict):
    """Renderiza a visão de administração do sistema, cadastros base e gestão de operadores."""
    df_ausencias = get_ausencias_completas(supabase)
    df_users = get_usuarios_cadastrados(supabase)
    df_prof = get_professores(supabase)
    df_disc = get_disciplinas(supabase)
    df_turmas = get_turmas(supabase)

    abas_admin = st.tabs([
        "👥 Equipe",
        "📚 Cadastros",
        "📋 Ocorrências",
        "📊 Métricas"
    ])

    # --------------------------------------------------------------------------
    # TAB 1: GESTÃO DE USUÁRIOS
    # --------------------------------------------------------------------------
    with abas_admin[0]:
        st.subheader("Equipe Cadastrada no Sistema (Tabela `usuarios`)")
        st.caption("Operadores registrados via Supabase Auth e sincronizados no banco de dados.")
        if not df_users.empty:
            st.dataframe(
                df_users[["nome", "email", "perfil", "cargo", "criado_em"]],
                use_container_width=True
            )
        else:
            st.info("Nenhum usuário listado ou tabela 'usuarios' pendente de sincronização.")

    # --------------------------------------------------------------------------
    # TAB 2: CADASTROS BASE (Professores, Disciplinas, Turmas)
    # --------------------------------------------------------------------------
    with abas_admin[1]:
        render_cadastros_base(supabase, perfil_usuario="Administrador")

    # --------------------------------------------------------------------------
    # TAB 3: VISÃO GERAL DAS OCORRÊNCIAS
    # --------------------------------------------------------------------------
    with abas_admin[2]:
        st.subheader("Ocorrências Registradas no Sistema")
        if not df_ausencias.empty:
            st.caption("💡 Clique em **'📄 Ver Atestado'** na coluna **Atestado** para abrir o documento, ou selecione uma linha para pré-visualizar na tela.")
            df_hist_admin = pd.DataFrame({
                "Data": df_ausencias["Data"],
                "Horário": df_ausencias["Horário"],
                "Professor": df_ausencias["Professor"],
                "Motivo": df_ausencias["Motivo"],
                "Status": df_ausencias["Status"],
                "Atestado": df_ausencias["AtestadoURL"],
                "NomeSubstituto": df_ausencias["NomeSubstituto"],
                "AulaVaga": df_ausencias["AulaVaga"]
            })
            ev_admin = st.dataframe(
                df_hist_admin,
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
            linhas_adm = ev_admin.selection.rows if (ev_admin and hasattr(ev_admin, "selection")) else []
            if linhas_adm:
                reg_adm = df_ausencias.iloc[linhas_adm[0]]
                url_adm = reg_adm.get("AtestadoURL")
                if url_adm:
                    st.markdown("---")
                    st.markdown(f"##### 👁️ Visualização do Atestado — {reg_adm['Professor']} ({reg_adm['Data']} | {reg_adm['Horário']})")
                    st.markdown(f"🔗 **[Abrir / Baixar Atestado em Nova Guia]({url_adm})**")
                    if str(url_adm).lower().split("?")[0].endswith((".png", ".jpg", ".jpeg")):
                        st.image(url_adm, use_container_width=True)
                    else:
                        st.markdown(
                            f'<iframe src="{url_adm}" width="100%" height="500px" style="border: 1px solid #cbd5e1; border-radius: 8px;"></iframe>',
                            unsafe_allow_html=True
                        )
        else:
            st.info("Nenhuma ausência registrada até o momento.")

    # --------------------------------------------------------------------------
    # TAB 4: MÉTRICAS GLOBAIS
    # --------------------------------------------------------------------------
    with abas_admin[3]:
        st.subheader("Métricas Globais da Plataforma")
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Docentes", len(df_prof))
        m2.metric("Disciplinas", len(df_disc))
        m3.metric("Turmas", len(df_turmas))
        m4.metric("Ausências", len(df_ausencias))
        m5.metric("Operadores", len(df_users))
