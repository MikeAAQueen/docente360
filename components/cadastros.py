import streamlit as st
import pandas as pd
from supabase import Client
from services.supabase_service import (
    get_professores,
    get_disciplinas,
    get_turmas,
    cadastrar_professor,
    excluir_professor,
    cadastrar_disciplina,
    excluir_disciplina,
    cadastrar_turma,
    excluir_turma
)

def render_cadastros_base(supabase: Client, perfil_usuario: str = "Secretaria"):
    """
    Renderiza o painel completo de gestão dos cadastros base (Professores, Matérias e Turmas).
    Pode ser utilizado tanto pela Secretaria quanto pelo Administrador.
    """
    df_prof = get_professores(supabase)
    df_disc = get_disciplinas(supabase)
    df_turmas = get_turmas(supabase)

    # Métricas resumidas no topo
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("👨‍🏫 Docentes Cadastrados", len(df_prof))
    col_m2.metric("📖 Matérias / Disciplinas", len(df_disc))
    col_m3.metric("🎓 Turmas Ativas", len(df_turmas))

    st.markdown("---")

    subtab_prof, subtab_disc, subtab_turma = st.tabs([
        "👨‍🏫 Professores",
        "📖 Matérias / Disciplinas",
        "🎓 Turmas"
    ])

    # ==========================================================================
    # SUBTAB 1: PROFESSORES
    # ==========================================================================
    with subtab_prof:
        st.subheader("Gestão do Corpo Docente")
        st.caption("Cadastre e gerencie os professores aptos para lecionar e realizar substituições.")

        with st.expander("➕ Cadastrar Novo Professor", expanded=df_prof.empty):
            with st.form("form_novo_professor", clear_on_submit=True):
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    nome_prof = st.text_input(
                        "Nome Completo do Docente *",
                        placeholder="Ex: Carlos Eduardo de Andrade"
                    )
                    email_prof = st.text_input(
                        "E-mail Institucional *",
                        placeholder="Ex: carlos.andrade@escola.edu.br"
                    )
                with col_p2:
                    departamentos_sugeridos = [
                        "Exatas",
                        "Humanas",
                        "Biológicas & Saúde",
                        "Tecnologia & Informática",
                        "Linguagens & Comunicação",
                        "Gestão & Negócios",
                        "Outro"
                    ]
                    dep_sel = st.selectbox("Departamento / Área de Atuação", departamentos_sugeridos)
                    if dep_sel == "Outro":
                        dep_final = st.text_input("Especifique o Departamento:", placeholder="Ex: Engenharia Civil")
                    else:
                        dep_final = dep_sel

                btn_salvar_prof = st.form_submit_button("💾 Salvar Professor", use_container_width=True)
                if btn_salvar_prof:
                    ok, msg = cadastrar_professor(supabase, nome_prof, email_prof, dep_final)
                    if ok:
                        st.success(f"✅ {msg}")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

        # Busca e listagem de professores
        st.markdown("##### 📋 Docentes Cadastrados")
        if not df_prof.empty:
            busca_prof = st.text_input(
                "🔍 Filtrar docentes por nome, e-mail ou departamento:",
                placeholder="Digite para filtrar em tempo real...",
                key="filtro_docente"
            ).strip().lower()

            df_prof_exibir = df_prof.copy()
            if busca_prof:
                df_prof_exibir = df_prof_exibir[
                    df_prof_exibir["nome"].str.lower().str.contains(busca_prof, na=False) |
                    df_prof_exibir["email"].str.lower().str.contains(busca_prof, na=False) |
                    df_prof_exibir["departamento"].fillna("").str.lower().str.contains(busca_prof, na=False)
                ]

            df_tabela_prof = df_prof_exibir[["nome", "email", "departamento"]].rename(columns={
                "nome": "Nome do Docente",
                "email": "E-mail Institucional",
                "departamento": "Departamento / Área"
            })
            st.dataframe(df_tabela_prof, use_container_width=True, hide_index=True)

            # Opção de Exclusão Segura
            with st.expander("🗑️ Excluir Docente"):
                st.caption("A exclusão só é permitida caso o professor não possua ausências ou substituições registradas.")
                opcoes_prof_del = {
                    r["id"]: f"{r['nome']} ({r['email']})"
                    for _, r in df_prof.iterrows()
                }
                prof_del_id = st.selectbox(
                    "Selecione o professor a ser excluído:",
                    options=list(opcoes_prof_del.keys()),
                    format_func=lambda x: opcoes_prof_del[x],
                    key="sel_del_prof"
                )
                if st.button("Confirmar Exclusão de Professor", type="secondary", key="btn_del_prof"):
                    ok_del, msg_del = excluir_professor(supabase, prof_del_id)
                    if ok_del:
                        st.success(f"✅ {msg_del}")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg_del}")
        else:
            st.info("ℹ️ Nenhum professor cadastrado ainda. Preencha o formulário acima para começar.")

    # ==========================================================================
    # SUBTAB 2: MATÉRIAS / DISCIPLINAS
    # ==========================================================================
    with subtab_disc:
        st.subheader("Gestão da Grade de Matérias / Disciplinas")
        st.caption("Cadastre as matérias lecionadas na instituição para vinculação no registro de faltas.")

        with st.expander("➕ Cadastrar Nova Matéria / Disciplina", expanded=df_disc.empty):
            with st.form("form_nova_disciplina", clear_on_submit=True):
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    cod_disc = st.text_input(
                        "Código da Matéria *",
                        placeholder="Ex: MAT101, PROG204, HIS102"
                    )
                with col_d2:
                    nome_disc = st.text_input(
                        "Nome da Matéria / Disciplina *",
                        placeholder="Ex: Cálculo Diferencial e Integral I"
                    )

                btn_salvar_disc = st.form_submit_button("💾 Salvar Matéria", use_container_width=True)
                if btn_salvar_disc:
                    ok, msg = cadastrar_disciplina(supabase, cod_disc, nome_disc)
                    if ok:
                        st.success(f"✅ {msg}")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

        # Busca e listagem de matérias
        st.markdown("##### 📋 Matérias Cadastradas")
        if not df_disc.empty:
            busca_disc = st.text_input(
                "🔍 Filtrar matéria por código ou nome:",
                placeholder="Digite para filtrar em tempo real...",
                key="filtro_materia"
            ).strip().lower()

            df_disc_exibir = df_disc.copy()
            if busca_disc:
                df_disc_exibir = df_disc_exibir[
                    df_disc_exibir["codigo"].str.lower().str.contains(busca_disc, na=False) |
                    df_disc_exibir["nome"].str.lower().str.contains(busca_disc, na=False)
                ]

            df_tabela_disc = df_disc_exibir[["codigo", "nome"]].rename(columns={
                "codigo": "Código",
                "nome": "Nome da Matéria / Disciplina"
            })
            st.dataframe(df_tabela_disc, use_container_width=True, hide_index=True)

            # Opção de Exclusão Segura
            with st.expander("🗑️ Excluir Matéria"):
                st.caption("A exclusão só é permitida caso a matéria não possua registros de ausências vinculadas.")
                opcoes_disc_del = {
                    r["id"]: f"{r['codigo']} — {r['nome']}"
                    for _, r in df_disc.iterrows()
                }
                disc_del_id = st.selectbox(
                    "Selecione a matéria a ser excluída:",
                    options=list(opcoes_disc_del.keys()),
                    format_func=lambda x: opcoes_disc_del[x],
                    key="sel_del_disc"
                )
                if st.button("Confirmar Exclusão de Matéria", type="secondary", key="btn_del_disc"):
                    ok_del, msg_del = excluir_disciplina(supabase, disc_del_id)
                    if ok_del:
                        st.success(f"✅ {msg_del}")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg_del}")
        else:
            st.info("ℹ️ Nenhuma matéria cadastrada ainda. Preencha o formulário acima para começar.")

    # ==========================================================================
    # SUBTAB 3: TURMAS
    # ==========================================================================
    with subtab_turma:
        st.subheader("Gestão de Turmas")
        st.caption("Cadastre as turmas e turnos afetados pelas ocorrências docentes.")

        with st.expander("➕ Cadastrar Nova Turma", expanded=df_turmas.empty):
            with st.form("form_nova_turma_base", clear_on_submit=True):
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    cod_turma = st.text_input(
                        "Código da Turma *",
                        placeholder="Ex: T-ENG24, T-ADS25"
                    )
                    curso_turma = st.text_input(
                        "Nome do Curso *",
                        placeholder="Ex: Engenharia de Software"
                    )
                with col_t2:
                    periodo_turma = st.selectbox(
                        "Turno / Período *",
                        ["Matutino", "Vespertino", "Noturno", "Integral"]
                    )

                btn_salvar_turma = st.form_submit_button("💾 Salvar Turma", use_container_width=True)
                if btn_salvar_turma:
                    ok, msg = cadastrar_turma(supabase, cod_turma, curso_turma, periodo_turma)
                    if ok:
                        st.success(f"✅ {msg}")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

        # Busca e listagem de turmas
        st.markdown("##### 📋 Turmas Cadastradas")
        if not df_turmas.empty:
            busca_turma = st.text_input(
                "🔍 Filtrar turmas por código, curso ou turno:",
                placeholder="Digite para filtrar em tempo real...",
                key="filtro_turma"
            ).strip().lower()

            df_turmas_exibir = df_turmas.copy()
            if busca_turma:
                df_turmas_exibir = df_turmas_exibir[
                    df_turmas_exibir["codigo"].str.lower().str.contains(busca_turma, na=False) |
                    df_turmas_exibir["curso"].str.lower().str.contains(busca_turma, na=False) |
                    df_turmas_exibir["periodo"].str.lower().str.contains(busca_turma, na=False)
                ]

            df_tabela_turma = df_turmas_exibir[["codigo", "curso", "periodo"]].rename(columns={
                "codigo": "Código",
                "curso": "Curso",
                "periodo": "Turno / Período"
            })
            st.dataframe(df_tabela_turma, use_container_width=True, hide_index=True)

            # Opção de Exclusão Segura
            with st.expander("🗑️ Excluir Turma"):
                st.caption("A exclusão só é permitida caso a turma não possua ausências vinculadas.")
                opcoes_turma_del = {
                    r["id"]: f"{r['codigo']} — {r['curso']} ({r['periodo']})"
                    for _, r in df_turmas.iterrows()
                }
                turma_del_id = st.selectbox(
                    "Selecione a turma a ser excluída:",
                    options=list(opcoes_turma_del.keys()),
                    format_func=lambda x: opcoes_turma_del[x],
                    key="sel_del_turma"
                )
                if st.button("Confirmar Exclusão de Turma", type="secondary", key="btn_del_turma"):
                    ok_del, msg_del = excluir_turma(supabase, turma_del_id)
                    if ok_del:
                        st.success(f"✅ {msg_del}")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg_del}")
        else:
            st.info("ℹ️ Nenhuma turma cadastrada ainda. Preencha o formulário acima para começar.")
