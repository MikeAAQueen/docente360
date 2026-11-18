import streamlit as st
import pandas as pd
from supabase import Client
from services.auth_service import handle_login, handle_signup
from services.supabase_service import (
    get_professores,
    get_professores_disponiveis_vinculo,
)


def render_login_view(supabase: Client):
    """Renderiza a tela de login e de cadastro de novas contas institucionais."""
    col_l1, col_l2, col_l3 = st.columns([1, 2.2, 1])
    with col_l2:
        st.markdown(
            """
        <div style="text-align: center; padding: 20px 0 10px 0;">
            <div style="display: inline-flex; align-items: center; justify-content: center; width: 64px; height: 64px; border-radius: 18px; background: linear-gradient(135deg, #1E3A8A, #2563EB); box-shadow: 0 8px 16px rgba(37, 99, 235, 0.25); margin-bottom: 14px;">
                <span style="font-size: 32px;">🎓</span>
            </div>
            <h1 style="font-size: 2rem; font-weight: 800; color: #0F172A; margin: 0; letter-spacing: -0.025em;">Docente360</h1>
            <p style="font-size: 0.95rem; color: #64748B; margin-top: 6px; margin-bottom: 24px;">Plataforma Integrada de Gestão de Ausências, Substituições & Frequência</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        tab_login, tab_cadastro = st.tabs(
            ["🔑 Entrar no Sistema", "📝 Criar Nova Conta"]
        )

        # ABA 1: LOGIN
        with tab_login:
            with st.form("form_login"):
                st.markdown("#### Identificação Institucional")
                st.caption("Acesse com o e-mail institucional e a senha cadastrados.")
                login_email = st.text_input(
                    "E-mail Institucional", placeholder="ex: seu.email@escola.edu.br"
                )
                login_senha = st.text_input(
                    "Senha de Acesso", type="password", placeholder="••••••••"
                )
                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                btn_entrar = st.form_submit_button(
                    "Acessar Painel", use_container_width=True, type="primary"
                )

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
                key="cad_perfil_select",
            )

            # FLUXO ESPECÍFICO PARA O PERFIL PROFESSOR
            if cad_perfil == "Professor":
                df_prof = get_professores_disponiveis_vinculo(supabase)

                modo_prof = st.radio(
                    "Tipo de cadastro docente:",
                    [
                        "🔗 Vincular a um Professor já cadastrado pela Secretaria",
                        "➕ Cadastrar novo Professor (não consto na lista da Secretaria)",
                    ],
                    key="modo_cadastro_docente",
                )

                if modo_prof.startswith("🔗"):
                    if df_prof.empty:
                        st.info(
                            "ℹ️ Não há professores pré-cadastrados pela Secretaria disponíveis para vínculo no momento. Por favor, utilize a opção de novo cadastro abaixo."
                        )
                    else:
                        st.caption(
                            "💡 Selecione seu nome abaixo para conectar seu login às turmas, matérias e faltas já cadastradas pela Secretaria."
                        )

                        opcoes_prof = {
                            r[
                                "id"
                            ]: f"👨‍🏫 {r['nome']} — {r['email']} ({r.get('departamento_limpo', r['departamento']) or 'Geral'})"
                            for _, r in df_prof.iterrows()
                        }
                        prof_sel_id = st.selectbox(
                            "Selecione o seu nome na lista da Secretaria *",
                            options=list(opcoes_prof.keys()),
                            format_func=lambda x: opcoes_prof[x],
                            key="prof_vinculo_id",
                        )
                        prof_sel = df_prof[df_prof["id"] == prof_sel_id].iloc[0]

                        with st.form("form_cadastro_vinculo_prof"):
                            depto_label = (
                                prof_sel.get("departamento_limpo")
                                or prof_sel.get("departamento")
                                or "Geral"
                            )
                            st.markdown(
                                f"""
                            <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px 16px; margin-bottom: 16px;">
                                <div style="font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.03em; color: #64748B;">Docente Pré-Cadastrado pela Secretaria</div>
                                <div style="font-size: 1.05rem; font-weight: 700; color: #0F172A; margin-top: 2px;">👨‍🏫 {prof_sel['nome']}</div>
                                <div style="font-size: 0.85rem; color: #475569; margin-top: 2px;">Departamento / Área: <b>{depto_label}</b></div>
                            </div>
                            """,
                                unsafe_allow_html=True,
                            )

                            email_sugerido = prof_sel["email"]
                            cad_email = st.text_input(
                                "Confirmar E-mail Institucional *", value=email_sugerido
                            )
                            col_s1, col_s2 = st.columns(2)
                            with col_s1:
                                cad_senha = st.text_input(
                                    "Crie sua Senha de Acesso (mínimo 6 dígitos) *",
                                    type="password",
                                )
                            with col_s2:
                                cad_confirma_senha = st.text_input(
                                    "Confirme sua Senha *", type="password"
                                )

                            btn_vincular = st.form_submit_button(
                                "Criar Conta e Vincular",
                                type="primary",
                                use_container_width=True,
                            )
                            if btn_vincular:
                                if (
                                    not cad_email
                                    or not cad_senha
                                    or not cad_confirma_senha
                                ):
                                    st.warning(
                                        "Preencha o e-mail, a senha e a confirmação de senha."
                                    )
                                elif cad_senha != cad_confirma_senha:
                                    st.error(
                                        "❌ As senhas digitadas não coincidem. Por favor, verifique e tente novamente."
                                    )
                                else:
                                    handle_signup(
                                        supabase=supabase,
                                        email=cad_email,
                                        password=cad_senha,
                                        nome=prof_sel["nome"],
                                        perfil="Professor",
                                        cargo=depto_label or "Docente",
                                        professor_id=prof_sel_id,
                                    )
                else:
                    # Novo Professor
                    st.caption(
                        "Preencha seus dados para criar seu registro de professor e seu login de acesso simultaneamente."
                    )
                    with st.form("form_cadastro_novo_prof"):
                        novo_nome = st.text_input(
                            "Nome Completo *",
                            placeholder="Ex: Dr. Carlos Eduardo de Andrade",
                        )
                        novo_email = st.text_input(
                            "E-mail Institucional *",
                            placeholder="Ex: carlos.andrade@escola.edu.br",
                        )
                        novo_depto = st.text_input(
                            "Departamento / Área de Atuação *",
                            placeholder="Ex: Matemática Aplicada / Exatas",
                        )
                        col_ns1, col_ns2 = st.columns(2)
                        with col_ns1:
                            novo_senha = st.text_input(
                                "Senha (mínimo 6 dígitos) *", type="password"
                            )
                        with col_ns2:
                            novo_confirma_senha = st.text_input(
                                "Confirmar Senha *", type="password"
                            )

                        btn_novo_prof = st.form_submit_button(
                            "Cadastrar Novo Professor",
                            type="primary",
                            use_container_width=True,
                        )
                        if btn_novo_prof:
                            if (
                                not novo_nome
                                or not novo_email
                                or not novo_senha
                                or not novo_confirma_senha
                            ):
                                st.warning("Preencha todos os campos obrigatórios (*).")
                            elif novo_senha != novo_confirma_senha:
                                st.error(
                                    "❌ As senhas digitadas não coincidem. Por favor, verifique e tente novamente."
                                )
                            else:
                                handle_signup(
                                    supabase=supabase,
                                    email=novo_email,
                                    password=novo_senha,
                                    nome=novo_nome,
                                    perfil="Professor",
                                    cargo=novo_depto if novo_depto else "Docente",
                                    professor_id=None,
                                )

            # FLUXO PARA OUTROS PERFIS (Secretaria, Coordenação, Administrador)
            else:
                st.caption(
                    f"Preencha as informações para cadastro na equipe de **{cad_perfil}**."
                )
                with st.form("form_cadastro_geral"):
                    cad_nome = st.text_input(
                        "Nome Completo *", placeholder="Ex: Ana Carolina Silva"
                    )
                    cad_email = st.text_input(
                        "E-mail Institucional *",
                        placeholder="Ex: ana.silva@escola.edu.br",
                    )
                    cad_cargo = st.text_input(
                        "Cargo / Função", placeholder="Ex: Secretária Acadêmica"
                    )
                    col_gs1, col_gs2 = st.columns(2)
                    with col_gs1:
                        cad_senha = st.text_input(
                            "Senha (mínimo 6 dígitos) *", type="password"
                        )
                    with col_gs2:
                        cad_confirma_senha = st.text_input(
                            "Confirmar Senha *", type="password"
                        )

                    btn_cadastrar = st.form_submit_button(
                        "Cadastrar Usuário", use_container_width=True
                    )
                    if btn_cadastrar:
                        if (
                            not cad_nome
                            or not cad_email
                            or not cad_senha
                            or not cad_confirma_senha
                        ):
                            st.warning("Preencha todos os campos obrigatórios (*).")
                        elif cad_senha != cad_confirma_senha:
                            st.error(
                                "❌ As senhas digitadas não coincidem. Por favor, verifique e tente novamente."
                            )
                        else:
                            handle_signup(
                                supabase=supabase,
                                email=cad_email,
                                password=cad_senha,
                                nome=cad_nome,
                                perfil=cad_perfil,
                                cargo=cad_cargo,
                            )
