import streamlit as st
from supabase import Client
from services.auth_service import handle_logout

def apply_custom_styles():
    """Aplica o tema visual e estilos CSS personalizados do Docente360."""
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

        /* =====================================================================
           ESTILIZAÇÃO MODERNA DAS ABAS (TABS / PILLS) - SEM CORTE DE TEXTO
           ===================================================================== */
        /* Barra container das abas com visual moderno estilo pills */
        div[data-baseweb="tab-list"] {
            gap: 6px !important;
            background-color: #F1F5F9 !important;
            padding: 6px !important;
            border-radius: 10px !important;
            border-bottom: none !important;
            flex-wrap: wrap !important;
            overflow-x: visible !important;
            margin-bottom: 1.2rem !important;
        }

        /* Oculta as linhas de borda padrão do Streamlit */
        div[data-baseweb="tab-border"] {
            display: none !important;
        }
        div[data-baseweb="tab-highlight"] {
            display: none !important;
        }

        /* Oculta as setas de scroll lateral que cortavam a visão das abas */
        div[data-baseweb="tabs"] button[aria-label="previous"],
        div[data-baseweb="tabs"] button[aria-label="next"] {
            display: none !important;
        }

        /* Botão individual de cada aba */
        button[data-baseweb="tab"] {
            border-radius: 8px !important;
            padding: 8px 18px !important;
            font-weight: 600 !important;
            font-size: 0.92rem !important;
            color: #475569 !important;
            background-color: transparent !important;
            border: none !important;
            transition: all 0.2s ease-in-out !important;
        }

        button[data-baseweb="tab"]:hover {
            background-color: #E2E8F0 !important;
            color: #0F172A !important;
        }

        /* Aba ativa selecionada com destaque em azul royal */
        button[data-baseweb="tab"][aria-selected="true"] {
            background-color: #1E40AF !important;
            color: #FFFFFF !important;
            box-shadow: 0 2px 4px rgba(30, 64, 175, 0.2) !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] p,
        button[data-baseweb="tab"][aria-selected="true"] span,
        button[data-baseweb="tab"][aria-selected="true"] div {
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }
    </style>
    """, unsafe_allow_html=True)


def render_sidebar_user(supabase: Client, user_profile: dict):
    """Renderiza a barra lateral com os dados do usuário conectado e botão de logout."""
    usuario = user_profile or {}
    nome_usuario = usuario.get("nome", "Usuário")
    perfil_usuario = usuario.get("perfil", "Secretaria")
    cargo_usuario = usuario.get("cargo", "Equipe")
    email_usuario = usuario.get("email", "")

    with st.sidebar:
        st.markdown("### 🎓 **Docente360**")
        st.caption("Sistema de Gestão de Ausências e Substituições")
        st.markdown("---")

        st.markdown("#### 👤 Usuário Conectado")
        st.markdown(f"**{nome_usuario}**")
        st.caption(f"📧 {email_usuario}")
        st.caption(f"💼 Cargo: {cargo_usuario}")

        badge_class = (
            "badge-sec" if perfil_usuario == "Secretaria"
            else ("badge-coord" if perfil_usuario == "Coordenador Acadêmico" else "badge-admin")
        )
        st.markdown(f'<span class="user-badge {badge_class}">{perfil_usuario}</span>', unsafe_allow_html=True)

        # Se for Administrador, exibe o seletor de navegação master na barra lateral
        modulo_master = None
        if perfil_usuario == "Administrador":
            st.markdown("---")
            st.markdown("#### 🧭 Navegação Master")
            modulo_master = st.radio(
                "Acessar Setor / Módulo:",
                [
                    "📌 Secretaria (Lançamento & Faltas)",
                    "📊 Coordenação (Dashboard & Relatórios)",
                    "👥 Painel Geral do Administrador"
                ],
                index=0
            )

        st.markdown("---")
        if st.button("🚪 Sair do Sistema (Logout)", use_container_width=True):
            handle_logout(supabase)

        st.markdown("---")
        st.caption("🟢 Supabase Auth: **Autenticado**")

    return modulo_master


def render_header(perfil_usuario: str, nome_usuario: str, cargo_usuario: str):
    """Renderiza o cabeçalho padrão para as telas logadas."""
    st.markdown(f'<div class="main-title">Docente360 — Painel da {perfil_usuario}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-title">Sessão ativa de <b>{nome_usuario}</b> ({cargo_usuario})</div>', unsafe_allow_html=True)
