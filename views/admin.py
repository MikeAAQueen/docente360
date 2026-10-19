import streamlit as st
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
            st.dataframe(df_ausencias, use_container_width=True)
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
