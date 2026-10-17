import streamlit as st
from supabase import Client
from services.supabase_service import (
    get_ausencias_completas,
    get_usuarios_cadastrados,
    get_professores,
    get_disciplinas,
    get_turmas
)

def render_admin_view(supabase: Client, user_profile: dict):
    """Renderiza a visão de administração do sistema, cadastros base e gestão de operadores."""
    df_ausencias = get_ausencias_completas(supabase)
    df_users = get_usuarios_cadastrados(supabase)
    df_prof = get_professores(supabase)
    df_disc = get_disciplinas(supabase)
    df_turmas = get_turmas(supabase)

    abas_admin = st.tabs([
        "👥 Equipe de Usuários",
        "📚 Cadastros Base",
        "📋 Todas as Ocorrências",
        "📊 Métricas Globais"
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
        st.subheader("Gerenciamento de Cadastros Base")
        tab_p, tab_d, tab_t = st.tabs(["👨‍🏫 Professores", "📖 Disciplinas", "🎓 Turmas"])

        # SUBTAB: PROFESSORES
        with tab_p:
            st.markdown("##### Relação de Professores")
            if not df_prof.empty:
                st.dataframe(df_prof[["nome", "email", "departamento"]], use_container_width=True)
            else:
                st.info("Nenhum professor cadastrado.")

            with st.expander("➕ Cadastrar Novo Professor"):
                with st.form("form_novo_prof", clear_on_submit=True):
                    np_nome = st.text_input("Nome do Professor *")
                    np_email = st.text_input("E-mail Institucional *")
                    np_dep = st.text_input("Departamento", placeholder="Ex: Exatas, Humanas, Tecnologia")
                    if st.form_submit_button("Cadastrar Professor"):
                        if np_nome and np_email:
                            try:
                                supabase.table("professores").insert({
                                    "nome": np_nome,
                                    "email": np_email,
                                    "departamento": np_dep
                                }).execute()
                                st.success("Professor cadastrado com sucesso!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao salvar: {e}")
                        else:
                            st.warning("Preencha nome e e-mail.")

        # SUBTAB: DISCIPLINAS
        with tab_d:
            st.markdown("##### Relação de Disciplinas")
            if not df_disc.empty:
                st.dataframe(df_disc[["codigo", "nome"]], use_container_width=True)
            else:
                st.info("Nenhuma disciplina cadastrada.")

            with st.expander("➕ Cadastrar Nova Disciplina"):
                with st.form("form_nova_disc", clear_on_submit=True):
                    nd_cod = st.text_input("Código da Disciplina *", placeholder="Ex: MAT101")
                    nd_nome = st.text_input("Nome da Disciplina *", placeholder="Ex: Cálculo I")
                    if st.form_submit_button("Cadastrar Disciplina"):
                        if nd_cod and nd_nome:
                            try:
                                supabase.table("disciplinas").insert({
                                    "codigo": nd_cod,
                                    "nome": nd_nome
                                }).execute()
                                st.success("Disciplina cadastrada com sucesso!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao salvar: {e}")
                        else:
                            st.warning("Preencha código e nome.")

        # SUBTAB: TURMAS
        with tab_t:
            st.markdown("##### Relação de Turmas")
            if not df_turmas.empty:
                st.dataframe(df_turmas[["codigo", "curso", "periodo"]], use_container_width=True)
            else:
                st.info("Nenhuma turma cadastrada.")

            with st.expander("➕ Cadastrar Nova Turma"):
                with st.form("form_nova_turma", clear_on_submit=True):
                    nt_cod = st.text_input("Código da Turma *", placeholder="Ex: T-ENG24")
                    nt_curso = st.text_input("Curso *", placeholder="Ex: Engenharia de Software")
                    nt_per = st.selectbox("Período *", ["Matutino", "Vespertino", "Noturno", "Integral"])
                    if st.form_submit_button("Cadastrar Turma"):
                        if nt_cod and nt_curso:
                            try:
                                supabase.table("turmas").insert({
                                    "codigo": nt_cod,
                                    "curso": nt_curso,
                                    "periodo": nt_per
                                }).execute()
                                st.success("Turma cadastrada com sucesso!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao salvar: {e}")
                        else:
                            st.warning("Preencha código e curso.")

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
