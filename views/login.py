import streamlit as st
from supabase import Client
from services.auth_service import handle_login, handle_signup

def render_login_view(supabase: Client):
    """Renderiza a tela de login e de cadastro de novas contas institucionais."""
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.markdown('<div class="main-title" style="text-align: center;">🎓 Docente360</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-title" style="text-align: center;">Portal de Gestão de Ausências — Secretaria & Coordenação Acadêmica</div>', unsafe_allow_html=True)

        tab_login, tab_cadastro = st.tabs(["🔑 Entrar no Sistema", "📝 Criar Nova Conta de Usuário"])

        # ABA 1: LOGIN
        with tab_login:
            st.markdown("##### Identifique-se com sua conta institucional")
            with st.form("form_login"):
                login_email = st.text_input("E-mail Institucional", placeholder="ex: secretaria@escola.edu.br")
                login_senha = st.text_input("Senha", type="password")
                btn_entrar = st.form_submit_button("Acessar Sistema", use_container_width=True, type="primary")

                if btn_entrar:
                    if not login_email or not login_senha:
                        st.warning("Preencha todos os campos para entrar.")
                    else:
                        handle_login(supabase, login_email, login_senha)

        # ABA 2: CADASTRO
        with tab_cadastro:
            st.markdown("##### Cadastro de Operador (Secretaria ou Coordenação)")
            with st.form("form_cadastro"):
                cad_nome = st.text_input("Nome Completo *", placeholder="Ex: Ana Carolina Silva")
                cad_email = st.text_input("E-mail Institucional *", placeholder="Ex: ana.silva@escola.edu.br")

                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    cad_perfil = st.selectbox("Perfil de Acesso *", ["Secretaria", "Coordenador Acadêmico", "Administrador"])
                with col_c2:
                    cad_cargo = st.text_input("Cargo / Função", placeholder="Ex: Secretária Acadêmica")

                cad_senha = st.text_input("Senha (mínimo 6 dígitos) *", type="password")
                btn_cadastrar = st.form_submit_button("Cadastrar Usuário", use_container_width=True)

                if btn_cadastrar:
                    if not cad_nome or not cad_email or not cad_senha:
                        st.warning("Preencha todos os campos obrigatórios (*).")
                    else:
                        handle_signup(supabase, cad_email, cad_senha, cad_nome, cad_perfil, cad_cargo)
