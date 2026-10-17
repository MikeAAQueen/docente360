import streamlit as st
from services.supabase_service import init_supabase
from services.auth_service import init_session_state
from components.styles import apply_custom_styles, render_sidebar_user, render_header
from views.login import render_login_view
from views.secretaria import render_secretaria_view
from views.coordenador import render_coordenador_view
from views.admin import render_admin_view

# ==============================================================================
# CONFIGURAÇÃO GERAL DA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Docente360 — Gestão Acadêmica",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização visual moderna e semântica
apply_custom_styles()

# Inicialização de conexões e gerenciamento de sessão
supabase = init_supabase()
init_session_state()

# ==============================================================================
# CONTROLE DE ACESSO (PORTAL NÃO AUTENTICADO)
# ==============================================================================
if st.session_state["auth_user"] is None:
    render_login_view(supabase)
    st.stop()

# ==============================================================================
# SISTEMA PRINCIPAL (USUÁRIO AUTENTICADO)
# ==============================================================================
user_profile = st.session_state.get("user_profile") or {}
nome_usuario = user_profile.get("nome", "Usuário")
perfil_usuario = user_profile.get("perfil", "Secretaria")
cargo_usuario = user_profile.get("cargo", "Equipe")

# Barra lateral com identificação do usuário e logout
render_sidebar_user(supabase, user_profile)

# Cabeçalho da interface
render_header(perfil_usuario, nome_usuario, cargo_usuario)

# Roteamento baseado no Perfil de Acesso (RBAC)
if perfil_usuario == "Secretaria":
    render_secretaria_view(supabase, user_profile)
elif perfil_usuario == "Coordenador Acadêmico":
    render_coordenador_view(supabase, user_profile)
elif perfil_usuario == "Administrador":
    render_admin_view(supabase, user_profile)
else:
    st.warning(f"Perfil de acesso '{perfil_usuario}' não reconhecido.")