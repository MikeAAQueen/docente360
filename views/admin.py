import streamlit as st
from supabase import Client
from services.supabase_service import get_ausencias_completas, get_usuarios_cadastrados

def render_admin_view(supabase: Client, user_profile: dict):
    """Renderiza a visão de administração do sistema e gestão de operadores."""
    df_ausencias = get_ausencias_completas(supabase)

    abas_admin = st.tabs([
        "👥 Usuários da Secretaria & Coordenação",
        "📌 Visão Geral da Operação",
        "📊 Dashboard Global"
    ])

    # --------------------------------------------------------------------------
    # TAB 1: GESTÃO DE USUÁRIOS
    # --------------------------------------------------------------------------
    with abas_admin[0]:
        st.subheader("Equipe Cadastrada no Sistema (Tabela `usuarios`)")
        df_users = get_usuarios_cadastrados(supabase)
        if not df_users.empty:
            st.dataframe(
                df_users[["nome", "email", "perfil", "cargo", "criado_em"]],
                use_container_width=True
            )
        else:
            st.info("Nenhum usuário listado ou tabela 'usuarios' pendente de execução no SQL Editor do Supabase.")

    # --------------------------------------------------------------------------
    # TAB 2: VISÃO GERAL DAS OCORRÊNCIAS
    # --------------------------------------------------------------------------
    with abas_admin[1]:
        st.subheader("Ocorrências Registradas no Sistema")
        st.dataframe(df_ausencias, use_container_width=True)

    # --------------------------------------------------------------------------
    # TAB 3: DASHBOARD GLOBAL
    # --------------------------------------------------------------------------
    with abas_admin[2]:
        st.subheader("Métricas Globais do Sistema")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total de Ausências Registradas", len(df_ausencias))
        with col2:
            st.metric("Total de Operadores Ativos", len(get_usuarios_cadastrados(supabase)))
