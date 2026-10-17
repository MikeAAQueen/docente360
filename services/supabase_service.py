import os
import streamlit as st
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env se presente
load_dotenv()

# ==============================================================================
# INICIALIZAÇÃO DO CLIENTE SUPABASE
# ==============================================================================
@st.cache_resource
def init_supabase() -> Client:
    """Inicializa e armazena em cache o cliente oficial do Supabase."""
    url = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY", "")
    if not url or not key:
        st.error("Credenciais do Supabase ausentes em `.streamlit/secrets.toml` ou variáveis de ambiente.")
        st.stop()
    return create_client(url, key)


# ==============================================================================
# CONSULTAS A TABELAS DE APOIO
# ==============================================================================
def get_professores(supabase: Client) -> pd.DataFrame:
    """Retorna lista de professores cadastrados."""
    try:
        res = supabase.table("professores").select("*").order("nome").execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame(columns=["id", "nome", "email", "departamento"])
    except Exception as e:
        st.warning(f"Erro ao buscar professores: {e}")
        return pd.DataFrame()


def get_disciplinas(supabase: Client) -> pd.DataFrame:
    """Retorna lista de disciplinas cadastradas."""
    try:
        res = supabase.table("disciplinas").select("*").order("nome").execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame(columns=["id", "codigo", "nome"])
    except Exception as e:
        st.warning(f"Erro ao buscar disciplinas: {e}")
        return pd.DataFrame()


def get_turmas(supabase: Client) -> pd.DataFrame:
    """Retorna lista de turmas cadastradas."""
    try:
        res = supabase.table("turmas").select("*").order("codigo").execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame(columns=["id", "codigo", "curso", "periodo"])
    except Exception as e:
        st.warning(f"Erro ao buscar turmas: {e}")
        return pd.DataFrame()


# ==============================================================================
# CONSULTAS DE OPERAÇÃO E OCORRÊNCIAS
# ==============================================================================
def get_ausencias_completas(supabase: Client) -> pd.DataFrame:
    """Retorna todas as ausências registradas com joins relacionais (professores, disciplinas e turmas)."""
    try:
        query = """
            id, data_ausencia, horario, motivo, status, professor_id, disciplina_id, turma_id,
            professores!ausencias_professor_id_fkey(id, nome, email),
            disciplinas!ausencias_disciplina_id_fkey(codigo, nome),
            turmas!ausencias_turma_id_fkey(codigo, curso)
        """
        res = supabase.table("ausencias").select(query).order("data_ausencia", desc=True).execute()
        data = []
        for item in res.data or []:
            prof = item.get("professores") or {}
            disc = item.get("disciplinas") or {}
            turma = item.get("turmas") or {}
            data.append({
                "ID": item["id"],
                "Data": item["data_ausencia"],
                "Horário": item["horario"],
                "ProfessorID": item.get("professor_id"),
                "Professor": prof.get("nome", "Docente não informado"),
                "EmailProfessor": prof.get("email", ""),
                "Disciplina": f"{disc.get('codigo', '')} - {disc.get('nome', '')}".strip(" -"),
                "Turma": f"{turma.get('codigo', '')} ({turma.get('curso', '')})".strip(" ()"),
                "Motivo": item.get("motivo") or "Não informado",
                "Status": item.get("status", "Pendente")
            })
        return pd.DataFrame(data)
    except Exception as e:
        st.warning(f"Erro ao buscar ausências: {e}")
        return pd.DataFrame()


def get_reposicoes(supabase: Client) -> pd.DataFrame:
    """Retorna dados de reposições e atestados cadastrados."""
    try:
        res = supabase.table("reposicoes_atestados").select("*").execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception as e:
        st.warning(f"Erro ao buscar reposições: {e}")
        return pd.DataFrame()


def get_usuarios_cadastrados(supabase: Client) -> pd.DataFrame:
    """Retorna a relação de usuários cadastrados na tabela 'usuarios'."""
    try:
        res = supabase.table("usuarios").select("*").order("nome").execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception as e:
        st.warning(f"Erro ao buscar usuários: {e}")
        return pd.DataFrame()
