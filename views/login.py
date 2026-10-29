import streamlit as st
import pandas as pd
from supabase import Client
from services.auth_service import handle_login, handle_signup
from services.supabase_service import get_professores

def render_login_view(supabase: Client):
    """Renderiza a tela de login e de cadastro de novas contas institucionais."""
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.markdown('<div class="main-title" style="text-align: center;">🎓 Docente360</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-title" style="text-align: center;">Portal Integrado de Gestão Acadêmica — Secretaria, Coordenação & Docentes</div>', unsafe_allow_html=True)

        tab_login, tab_cadastro = st.tabs(["🔑 Entrar no Sistema", "📝 Criar Nova Conta de Usuário"])

        # ABA 1: LOGIN
        with tab_login:
            st.markdown("##### Identifique-se com sua conta institucional")
            with st.form("form_login"):
                login_email = st.text_input("E-mail Institucional", placeholder="ex: seu.email@escola.edu.br")
                login_senha = st.text_input("Senha", type="password")
                btn_entrar = st.form_submit_button("Acessar Sistema", use_container_width=True, type="primary")

                if btn_entrar:
                    if not login_email or not login_senha:
                        st.warning("Preencha todos os campos para entrar.")
                    else:
                        handle_login(supabase, login_email, login_senha)

        # ABA 2: CADASTRO
        with tab_cadastro:
            st.markdown("##### Cadastro de Usuário Institucional")
            
            cad_perfil = st.selectbox(
                "Selecione o seu Perfil de Acesso *",
                ["Professor", "Secretaria", "Coordenador Acadêmico", "Administrador"],
                key="cad_perfil_select"
            )

            # FLUXO ESPECÍFICO PARA O PERFIL PROFESSOR
            if cad_perfil == "Professor":
                df_prof = get_professores(supabase)
                
                modo_prof = st.radio(
                    "Tipo de cadastro docente:",
                    [
                        "🔗 Vincular a um Professor já cadastrado pela Secretaria",
                        "➕ Cadastrar novo Professor (não consto na lista da Secretaria)"
                    ],
                    key="modo_cadastro_docente"
                )

                if modo_prof.startswith("🔗"):
                    if df_prof.empty:
                        st.info("ℹ️ Não há professores pré-cadastrados no sistema ainda. Por favor, utilize a opção de novo cadastro.")
                    else:
                        st.caption("💡 Selecione seu nome abaixo para conectar seu login às turmas, matérias e faltas já cadastradas.")
                        
                        opcoes_prof = {
                            r["id"]: f"👨‍🏫 {r['nome']} — {r['email']} ({r['departamento'] or 'Geral'})"
                            for _, r in df_prof.iterrows()
                        }
                        prof_sel_id = st.selectbox(
                            "Selecione o seu nome na lista da Secretaria *",
                            options=list(opcoes_prof.keys()),
                            format_func=lambda x: opcoes_prof[x],
                            key="prof_vinculo_id"
                        )
                        prof_sel = df_prof[df_prof["id"] == prof_sel_id].iloc[0]

                        with st.form("form_cadastro_vinculo_prof"):
                            st.markdown(f"**Docente:** {prof_sel['nome']}")
                            st.markdown(f"**Departamento / Área:** {prof_sel['departamento'] or 'Geral'}")
                            
                            email_sugerido = prof_sel["email"]
                            cad_email = st.text_input("Confirmar E-mail Institucional *", value=email_sugerido)
                            cad_senha = st.text_input("Crie sua Senha de Acesso (mínimo 6 dígitos) *", type="password")
                            
                            btn_vincular = st.form_submit_button("Criar Conta e Vincular", type="primary", use_container_width=True)
                            if btn_vincular:
                                if not cad_email or not cad_senha:
                                    st.warning("Preencha o e-mail e a senha.")
                                else:
                                    handle_signup(
                                        supabase=supabase,
                                        email=cad_email,
                                        password=cad_senha,
                                        nome=prof_sel["nome"],
                                        perfil="Professor",
                                        cargo=prof_sel["departamento"] or "Docente",
                                        professor_id=prof_sel_id
                                    )
                else:
                    # Novo Professor
                    st.caption("Preencha seus dados para criar seu registro de professor e seu login de acesso simultaneamente.")
                    with st.form("form_cadastro_novo_prof"):
                        novo_nome = st.text_input("Nome Completo *", placeholder="Ex: Dr. Carlos Eduardo de Andrade")
                        novo_email = st.text_input("E-mail Institucional *", placeholder="Ex: carlos.andrade@escola.edu.br")
                        novo_depto = st.text_input("Departamento / Área de Atuação *", placeholder="Ex: Matemática Aplicada / Exatas")
                        novo_senha = st.text_input("Senha (mínimo 6 dígitos) *", type="password")
                        
                        btn_novo_prof = st.form_submit_button("Cadastrar Novo Professor", type="primary", use_container_width=True)
                        if btn_novo_prof:
                            if not novo_nome or not novo_email or not novo_senha:
                                st.warning("Preencha todos os campos obrigatórios (*).")
                            else:
                                handle_signup(
                                    supabase=supabase,
                                    email=novo_email,
                                    password=novo_senha,
                                    nome=novo_nome,
                                    perfil="Professor",
                                    cargo=novo_depto if novo_depto else "Docente",
                                    professor_id=None
                                )

            # FLUXO PARA OUTROS PERFIS (Secretaria, Coordenação, Administrador)
            else:
                st.caption(f"Preencha as informações para cadastro na equipe de **{cad_perfil}**.")
                with st.form("form_cadastro_geral"):
                    cad_nome = st.text_input("Nome Completo *", placeholder="Ex: Ana Carolina Silva")
                    cad_email = st.text_input("E-mail Institucional *", placeholder="Ex: ana.silva@escola.edu.br")
                    cad_cargo = st.text_input("Cargo / Função", placeholder="Ex: Secretária Acadêmica")
                    cad_senha = st.text_input("Senha (mínimo 6 dígitos) *", type="password")
                    
                    btn_cadastrar = st.form_submit_button("Cadastrar Usuário", use_container_width=True)
                    if btn_cadastrar:
                        if not cad_nome or not cad_email or not cad_senha:
                            st.warning("Preencha todos os campos obrigatórios (*).")
                        else:
                            handle_signup(
                                supabase=supabase,
                                email=cad_email,
                                password=cad_senha,
                                nome=cad_nome,
                                perfil=cad_perfil,
                                cargo=cad_cargo
                            )
