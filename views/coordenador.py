import datetime
import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import Client
from services.supabase_service import get_ausencias_completas, get_reposicoes
from utils.pdf_generator import gerar_pdf_relatorio

def render_coordenador_view(supabase: Client, user_profile: dict):
    """Renderiza a visão analítica e pedagógica da Coordenação Acadêmica."""
    df_ausencias = get_ausencias_completas(supabase)
    user_info = user_profile or {}
    nome_emissor = user_info.get("nome", "Coordenação Acadêmica")
    cargo_emissor = user_info.get("cargo", "Coordenador Acadêmico")

    abas_coord = st.tabs([
        "📊 Dashboard Analítico de Indicadores",
        "✅ Homologação de Reposições",
        "📄 Relatórios Gerenciais em PDF"
    ])

    # --------------------------------------------------------------------------
    # TAB 1: DASHBOARD ANALÍTICO
    # --------------------------------------------------------------------------
    with abas_coord[0]:
        st.subheader("Painel de Indicadores de Frequência e Aulas Vagas")
        if df_ausencias.empty:
            st.info("Nenhuma ausência registrada no sistema até o momento.")
        else:
            total = len(df_ausencias)
            subst = len(df_ausencias[df_ausencias["Status"] == "Substituída"])
            vagas = len(df_ausencias[df_ausencias["Status"] == "Aula Vaga"])
            aguard = len(df_ausencias[df_ausencias["Status"] == "Aguardando Homologação"])
            repostas = len(df_ausencias[df_ausencias["Status"] == "Reposta"])
            taxa = (subst / total * 100) if total > 0 else 0.0

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Total de Ausências", total)
            c2.metric("Substituições", subst, f"{taxa:.1f}%")
            c3.metric("Aulas Vagas", vagas, delta_color="inverse")
            c4.metric("Aguardando Homologação", aguard)
            c5.metric("Aulas Repostas", repostas)

            st.markdown("---")
            g1, g2 = st.columns(2)
            cores = {
                "Pendente": "#CA8A04",
                "Substituída": "#2563EB",
                "Aula Vaga": "#DC2626",
                "Aguardando Homologação": "#D97706",
                "Reposta": "#16A34A"
            }
            with g1:
                fig_p = px.pie(
                    df_ausencias,
                    names="Status",
                    title="Distribuição das Ocorrências por Status",
                    color="Status",
                    color_discrete_map=cores,
                    hole=0.35
                )
                st.plotly_chart(fig_p, use_container_width=True)
            with g2:
                fig_b = px.bar(
                    df_ausencias,
                    x="Professor",
                    color="Status",
                    title="Frequência de Ausências por Docente",
                    color_discrete_map=cores
                )
                st.plotly_chart(fig_b, use_container_width=True)

    # --------------------------------------------------------------------------
    # TAB 2: HOMOLOGAÇÃO DE REPOSIÇÕES
    # --------------------------------------------------------------------------
    with abas_coord[1]:
        st.subheader("Homologação Pedagógica de Reposições de Aula")
        pendentes_homolog = df_ausencias[df_ausencias["Status"] == "Aguardando Homologação"] if not df_ausencias.empty else pd.DataFrame()

        if pendentes_homolog.empty:
            st.success("✨ Nenhuma reposição pendente de homologação no momento.")
        else:
            df_rep = get_reposicoes(supabase)
            for _, r in pendentes_homolog.iterrows():
                with st.expander(f"📌 {r['Professor']} — {r['Disciplina']} ({r['Turma']})"):
                    rep_det = df_rep[df_rep["ausencia_id"] == r["ID"]] if not df_rep.empty else pd.DataFrame()
                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.write(f"**Data da Falta:** {r['Data']} ({r['Horário']})")
                        st.write(f"**Motivo:** {r['Motivo']}")
                    with col_info2:
                        if not rep_det.empty:
                            st.write(f"**Data Proposta para Reposição:** {rep_det.iloc[0].get('data_reposicao')}")
                            st.write(f"**Horário:** {rep_det.iloc[0].get('horario_reposicao')}")
                            if rep_det.iloc[0].get("atestado_url"):
                                st.markdown(f"📎 [Visualizar Atestado Anexo]({rep_det.iloc[0]['atestado_url']})")

                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button("✅ Homologar Reposição", key=f"ap_{r['ID']}", type="primary"):
                            supabase.table("ausencias").update({"status": "Reposta"}).eq("id", r["ID"]).execute()
                            supabase.table("reposicoes_atestados").update({"comprovada": True}).eq("ausencia_id", r["ID"]).execute()
                            st.success("Reposição homologada com sucesso!")
                            st.rerun()
                    with b2:
                        if st.button("❌ Recusar / Solicitar Ajuste", key=f"rec_{r['ID']}"):
                            supabase.table("ausencias").update({"status": "Pendente"}).eq("id", r["ID"]).execute()
                            st.warning("Retornado para status Pendente.")
                            st.rerun()

    # --------------------------------------------------------------------------
    # TAB 3: CENTRAL DE EMISSÃO DE RELATÓRIOS GERENCIAIS (PDF & CSV)
    # --------------------------------------------------------------------------
    with abas_coord[2]:
        st.subheader("📑 Central de Emissão de Relatórios Gerenciais")
        st.caption("Filtre, analise e extraia relatórios oficiais em formato PDF diagramado (paisagem) e planilhas CSV com sumário executivo e histórico completo.")

        if df_ausencias.empty:
            st.info("Nenhuma ocorrência registrada no sistema para gerar relatórios.")
        else:
            # BLOCO DE FILTROS REATIVOS
            with st.container():
                st.markdown("##### 🔍 Parâmetros e Filtros do Relatório")
                col_f1, col_f2 = st.columns([2, 1])

                with col_f1:
                    tipo_rel = st.selectbox(
                        "Tipo de Relatório:",
                        [
                            "📊 Relatório Consolidado Geral (Todas as Ausências & Tratativas)",
                            "⚠️ Relatório de Aulas Vagas & Pendências de Reposição",
                            "✅ Relatório de Reposições Homologadas & Concluídas",
                            "👨‍🏫 Relatório Individual por Docente"
                        ]
                    )
                with col_f2:
                    periodo_sel = st.selectbox(
                        "Período Temporal:",
                        ["Todo o Histórico", "Mês Atual", "Últimos 30 Dias", "Intervalo Personalizado"]
                    )

                col_f3, col_f4, col_f5 = st.columns(3)
                with col_f3:
                    lista_prof = ["Todos os Docentes"] + sorted(list(df_ausencias["Professor"].dropna().unique()))
                    prof_sel = st.selectbox("Docente:", lista_prof)
                with col_f4:
                    lista_turmas = ["Todas as Turmas"] + sorted(list(df_ausencias["Turma"].dropna().unique()))
                    turma_sel = st.selectbox("Turma:", lista_turmas)
                with col_f5:
                    status_opcoes = ["Todos os Status", "Pendente", "Substituída", "Aula Vaga", "Aguardando Homologação", "Reposta"]
                    status_sel = st.selectbox("Status Operacional:", status_opcoes)

                # Seletor de data personalizada quando aplicável
                dt_inicio, dt_fim = None, None
                if periodo_sel == "Intervalo Personalizado":
                    col_dt1, col_dt2 = st.columns(2)
                    with col_dt1:
                        dt_inicio = st.date_input("Data Inicial", datetime.date.today() - datetime.timedelta(days=30))
                    with col_dt2:
                        dt_fim = st.date_input("Data Final", datetime.date.today())

            # APLICAÇÃO DOS FILTROS NO DATAFRAME
            df_filtrado = df_ausencias.copy()

            # Filtro por tipo de relatório
            titulo_relatorio = "Relatório Consolidado de Ocorrências Docentes"
            if tipo_rel.startswith("⚠️"):
                df_filtrado = df_filtrado[df_filtrado["Status"].isin(["Aula Vaga", "Aguardando Homologação", "Pendente"])]
                titulo_relatorio = "Relatório de Aulas Vagas e Reposições Pendentes"
            elif tipo_rel.startswith("✅"):
                df_filtrado = df_filtrado[df_filtrado["Status"] == "Reposta"]
                titulo_relatorio = "Relatório Oficial de Reposições de Aula Homologadas"
            elif tipo_rel.startswith("👨‍🏫"):
                titulo_relatorio = f"Relatório Analítico de Frequência — {prof_sel}"

            # Filtro de Docente
            if prof_sel != "Todos os Docentes":
                df_filtrado = df_filtrado[df_filtrado["Professor"] == prof_sel]

            # Filtro de Turma
            if turma_sel != "Todas as Turmas":
                df_filtrado = df_filtrado[df_filtrado["Turma"] == turma_sel]

            # Filtro de Status
            if status_sel != "Todos os Status":
                df_filtrado = df_filtrado[df_filtrado["Status"] == status_sel]

            # Filtro Temporal
            if periodo_sel == "Mês Atual":
                hoje = datetime.date.today()
                df_filtrado["_dt"] = pd.to_datetime(df_filtrado["Data"], errors="coerce").dt.date
                df_filtrado = df_filtrado[(df_filtrado["_dt"] >= datetime.date(hoje.year, hoje.month, 1)) & (df_filtrado["_dt"] <= hoje)]
            elif periodo_sel == "Últimos 30 Dias":
                limite = datetime.date.today() - datetime.timedelta(days=30)
                df_filtrado["_dt"] = pd.to_datetime(df_filtrado["Data"], errors="coerce").dt.date
                df_filtrado = df_filtrado[df_filtrado["_dt"] >= limite]
            elif periodo_sel == "Intervalo Personalizado" and dt_inicio and dt_fim:
                df_filtrado["_dt"] = pd.to_datetime(df_filtrado["Data"], errors="coerce").dt.date
                df_filtrado = df_filtrado[(df_filtrado["_dt"] >= dt_inicio) & (df_filtrado["_dt"] <= dt_fim)]

            # Limpa coluna temporária se existir
            if "_dt" in df_filtrado.columns:
                df_filtrado = df_filtrado.drop(columns=["_dt"])

            # RESUMO EXECUTIVO DOS DADOS FILTRADOS
            st.markdown("---")
            st.markdown("##### 📊 Resumo dos Dados no Relatório")
            q_total = len(df_filtrado)
            q_subst = len(df_filtrado[df_filtrado["Status"] == "Substituída"])
            q_vagas = len(df_filtrado[df_filtrado["Status"] == "Aula Vaga"])
            q_repostas = len(df_filtrado[df_filtrado["Status"] == "Reposta"])
            taxa_f = (q_subst / q_total * 100) if q_total > 0 else 0.0

            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Ocorrências no Filtro", q_total)
            r2.metric("Substituições", f"{q_subst} ({taxa_f:.1f}%)")
            r3.metric("Aulas Vagas", q_vagas)
            r4.metric("Aulas Repostas", q_repostas)

            # TABELA DE PRÉ-VISUALIZAÇÃO
            st.markdown("##### 📋 Pré-visualização das Ocorrências")
            colunas_exibicao = [
                "Data", "Horário", "Professor", "Disciplina", "Turma",
                "Motivo", "Tratativa", "Status", "InfoReposicao", "Atestado"
            ]
            st.dataframe(df_filtrado[colunas_exibicao], use_container_width=True)

            # METADADOS PARA O PDF
            periodo_txt = periodo_sel
            if periodo_sel == "Intervalo Personalizado" and dt_inicio and dt_fim:
                periodo_txt = f"{dt_inicio.strftime('%d/%m/%Y')} até {dt_fim.strftime('%d/%m/%Y')}"

            filtros_dict = {
                "periodo": periodo_txt,
                "professor": prof_sel,
                "turma": turma_sel,
                "status": status_sel
            }

            # BOTÕES DE EXTRAÇÃO (PDF E CSV)
            st.markdown("---")
            col_b1, col_b2 = st.columns(2)

            with col_b1:
                pdf_bytes = gerar_pdf_relatorio(
                    df=df_filtrado,
                    titulo=titulo_relatorio,
                    filtros_info=filtros_dict,
                    emitido_por=f"{nome_emissor} ({cargo_emissor})"
                )
                nome_pdf = f"relatorio_docente360_{datetime.date.today()}.pdf"
                st.download_button(
                    label="📄 Baixar Relatório Oficial Completo em PDF",
                    data=pdf_bytes,
                    file_name=nome_pdf,
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )

            with col_b2:
                csv_bytes = df_filtrado[colunas_exibicao].to_csv(index=False).encode('utf-8')
                nome_csv = f"dados_ausencias_{datetime.date.today()}.csv"
                st.download_button(
                    label="📊 Baixar Planilha Consolidada em CSV",
                    data=csv_bytes,
                    file_name=nome_csv,
                    mime="text/csv",
                    use_container_width=True
                )
