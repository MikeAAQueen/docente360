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
            st.info("Nenhuma ausência registrada no sistema.")
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
                "Pendente": "#F59E0B",
                "Substituída": "#3B82F6",
                "Aula Vaga": "#EF4444",
                "Aguardando Homologação": "#F97316",
                "Reposta": "#10B981"
            }
            with g1:
                fig_p = px.pie(
                    df_ausencias,
                    names="Status",
                    title="Distribuição por Status",
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
                    title="Frequência por Professor",
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
    # TAB 3: RELATÓRIOS GERENCIAIS
    # --------------------------------------------------------------------------
    with abas_coord[2]:
        st.subheader("Exportação de Relatórios Gerenciais")
        if df_ausencias.empty:
            st.info("Nenhuma ausência registrada.")
        else:
            st.dataframe(df_ausencias, use_container_width=True)
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                pdf = gerar_pdf_relatorio(df_ausencias)
                st.download_button(
                    "📄 Baixar Relatório em PDF",
                    pdf,
                    file_name=f"relatorio_ausencias_{datetime.date.today()}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            with col_d2:
                csv = df_ausencias.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📊 Baixar Planilha em CSV",
                    csv,
                    file_name=f"ausencias_{datetime.date.today()}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
