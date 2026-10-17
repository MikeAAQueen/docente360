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

        st.markdown("---")
        if st.button("🚪 Sair do Sistema (Logout)", use_container_width=True):
            handle_logout(supabase)

        st.markdown("---")
        st.caption("🟢 Supabase Auth: **Autenticado**")


def render_header(perfil_usuario: str, nome_usuario: str, cargo_usuario: str):
    """Renderiza o cabeçalho padrão para as telas logadas."""
    st.markdown(f'<div class="main-title">Docente360 — Painel da {perfil_usuario}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-title">Sessão ativa de <b>{nome_usuario}</b> ({cargo_usuario})</div>', unsafe_allow_html=True)
