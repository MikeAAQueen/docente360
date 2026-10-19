import os
import streamlit as st
import pandas as pd
from supabase import create_client, Client
# Carrega variáveis do arquivo .env se a biblioteca python-dotenv estiver disponível
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

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
    """Retorna todas as ausências registradas com joins relacionais completos (professores, disciplinas, turmas, substituições e reposições)."""
    try:
        query = """
            id, data_ausencia, horario, motivo, status, professor_id, disciplina_id, turma_id,
            professores!ausencias_professor_id_fkey(id, nome, email),
            disciplinas!ausencias_disciplina_id_fkey(codigo, nome),
            turmas!ausencias_turma_id_fkey(codigo, curso),
            substituicoes(id, aula_vaga, observacoes, professor_substituto_id, professores(nome)),
            reposicoes_atestados(id, atestado_url, data_reposicao, horario_reposicao, comprovada)
        """
        res = supabase.table("ausencias").select(query).order("data_ausencia", desc=True).execute()
        data = []
        for item in res.data or []:
            prof = item.get("professores") or {}
            disc = item.get("disciplinas") or {}
            turma = item.get("turmas") or {}

            # Tratativa / Substituição
            sub_list = item.get("substituicoes") or []
            sub = sub_list[0] if sub_list else {}
            sub_prof = sub.get("professores") or {}
            sub_nome = sub_prof.get("nome") if sub_prof else None
            is_aula_vaga = bool(sub.get("aula_vaga"))
            obs_tratativa = sub.get("observacoes") or ""

            if is_aula_vaga:
                tratativa = f"Aula Vaga ({obs_tratativa})" if obs_tratativa else "Aula Vaga"
            elif sub_nome:
                tratativa = f"Substituto: {sub_nome}"
            else:
                tratativa = "Pendente de tratativa"

            # Reposição & Atestado
            rep_list = item.get("reposicoes_atestados") or []
            rep = rep_list[0] if rep_list else {}
            data_rep = rep.get("data_reposicao")
            hora_rep = rep.get("horario_reposicao")
            atestado_url = rep.get("atestado_url")
            tem_atestado = bool(atestado_url)
            rep_comprovada = bool(rep.get("comprovada"))

            if data_rep:
                info_rep = f"{data_rep} ({hora_rep or 'A combinar'})"
            else:
                info_rep = "Não agendada"

            data.append({
                "ID": item["id"],
                "Data": str(item["data_ausencia"]),
                "Horário": item["horario"],
                "ProfessorID": item.get("professor_id"),
                "Professor": prof.get("nome", "Docente não informado"),
                "EmailProfessor": prof.get("email", ""),
                "Disciplina": f"{disc.get('codigo', '')} - {disc.get('nome', '')}".strip(" -"),
                "CodigoDisciplina": disc.get("codigo", ""),
                "Turma": f"{turma.get('codigo', '')} ({turma.get('curso', '')})".strip(" ()"),
                "CodigoTurma": turma.get("codigo", ""),
                "Curso": turma.get("curso", ""),
                "Motivo": item.get("motivo") or "Não informado",
                "Status": item.get("status", "Pendente"),
                "Tratativa": tratativa,
                "Substituto": sub_nome if sub_nome else ("Aula Vaga" if is_aula_vaga else "-"),
                "AulaVaga": is_aula_vaga,
                "DataReposicao": data_rep or "-",
                "HorarioReposicao": hora_rep or "-",
                "InfoReposicao": info_rep,
                "Atestado": "Sim (Anexado)" if tem_atestado else "Não",
                "AtestadoURL": atestado_url,
                "RepComprovada": "Sim (Homologada)" if rep_comprovada else "Não"
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


# ==============================================================================
# OPERAÇÕES DE CADASTRO BASE (PROFESSORES, DISCIPLINAS E TURMAS)
# ==============================================================================
def cadastrar_professor(supabase: Client, nome: str, email: str, departamento: str = "") -> tuple[bool, str]:
    """Cadastra um novo professor no banco de dados com validações."""
    nome = nome.strip()
    email = email.strip().lower()
    departamento = departamento.strip()

    if not nome or not email:
        return False, "Nome completo e e-mail institucional são obrigatórios."
    if "@" not in email or "." not in email:
        return False, "Por favor, informe um endereço de e-mail válido (ex: docente@escola.edu.br)."

    try:
        supabase.table("professores").insert({
            "nome": nome,
            "email": email,
            "departamento": departamento if departamento else "Geral"
        }).execute()
        return True, f"Professor(a) '{nome}' cadastrado(a) com sucesso!"
    except Exception as e:
        err = str(e)
        if "23505" in err or "professores_email_key" in err or "duplicate key" in err:
            return False, f"Já existe um professor cadastrado com o e-mail '{email}'."
        return False, f"Erro ao cadastrar professor: {err}"


def excluir_professor(supabase: Client, prof_id: str) -> tuple[bool, str]:
    """Exclui um professor caso não haja ausências ou substituições associadas."""
    try:
        supabase.table("professores").delete().eq("id", prof_id).execute()
        return True, "Professor removido com sucesso!"
    except Exception as e:
        err = str(e)
        if "23503" in err or "foreign key" in err:
            return False, "Não é possível remover este docente: existem ausências ou substituições registradas vinculadas a ele."
        return False, f"Erro ao excluir professor: {err}"


def cadastrar_disciplina(supabase: Client, codigo: str, nome: str) -> tuple[bool, str]:
    """Cadastra uma nova matéria / disciplina no banco de dados."""
    codigo = codigo.strip().upper()
    nome = nome.strip()

    if not codigo or not nome:
        return False, "Código e nome da disciplina são obrigatórios."

    try:
        supabase.table("disciplinas").insert({
            "codigo": codigo,
            "nome": nome
        }).execute()
        return True, f"Matéria '{codigo} - {nome}' cadastrada com sucesso!"
    except Exception as e:
        err = str(e)
        if "23505" in err or "disciplinas_codigo_key" in err or "duplicate key" in err:
            return False, f"Já existe uma matéria cadastrada com o código '{codigo}'."
        return False, f"Erro ao cadastrar matéria: {err}"


def excluir_disciplina(supabase: Client, disc_id: str) -> tuple[bool, str]:
    """Exclui uma matéria / disciplina caso não haja registros vinculados."""
    try:
        supabase.table("disciplinas").delete().eq("id", disc_id).execute()
        return True, "Matéria removida com sucesso!"
    except Exception as e:
        err = str(e)
        if "23503" in err or "foreign key" in err:
            return False, "Não é possível remover esta matéria: existem ausências registradas vinculadas a ela."
        return False, f"Erro ao excluir matéria: {err}"


def cadastrar_turma(supabase: Client, codigo: str, curso: str, periodo: str) -> tuple[bool, str]:
    """Cadastra uma nova turma no banco de dados."""
    codigo = codigo.strip().upper()
    curso = curso.strip()
    periodo = periodo.strip()

    if not codigo or not curso or not periodo:
        return False, "Código, curso e turno/período são obrigatórios."

    try:
        supabase.table("turmas").insert({
            "codigo": codigo,
            "curso": curso,
            "periodo": periodo
        }).execute()
        return True, f"Turma '{codigo}' ({curso}) cadastrada com sucesso!"
    except Exception as e:
        err = str(e)
        if "23505" in err or "turmas_codigo_key" in err or "duplicate key" in err:
            return False, f"Já existe uma turma cadastrada com o código '{codigo}'."
        return False, f"Erro ao cadastrar turma: {err}"


def excluir_turma(supabase: Client, turma_id: str) -> tuple[bool, str]:
    """Exclui uma turma caso não haja registros vinculados."""
    try:
        supabase.table("turmas").delete().eq("id", turma_id).execute()
        return True, "Turma removida com sucesso!"
    except Exception as e:
        err = str(e)
        if "23503" in err or "foreign key" in err:
            return False, "Não é possível remover esta turma: existem ausências registradas vinculadas a ela."
        return False, f"Erro ao excluir turma: {err}"
