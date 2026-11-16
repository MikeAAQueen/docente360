import os
import re
import unicodedata
import mimetypes
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
            id, data_ausencia, horario, motivo, status, registrado_por, professor_id, disciplina_id, turma_id,
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
                "RegistradoPor": item.get("registrado_por", "Secretaria"),
                "Tratativa": tratativa,
                "Substituto": sub_nome if sub_nome else ("Aula Vaga" if is_aula_vaga else "-"),
                "SubstitutoID": sub.get("professor_substituto_id"),
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


def get_ausencias_do_professor(supabase: Client, professor_id: str) -> pd.DataFrame:
    """Retorna o histórico de ausências de um professor específico."""
    df_todas = get_ausencias_completas(supabase)
    if df_todas.empty or not professor_id:
        return pd.DataFrame()
    return df_todas[df_todas["ProfessorID"] == professor_id]


def get_substituicoes_do_professor(supabase: Client, professor_id: str) -> pd.DataFrame:
    """Retorna as aulas onde este docente foi convocado como substituto."""
    df_todas = get_ausencias_completas(supabase)
    if df_todas.empty or not professor_id:
        return pd.DataFrame()
    return df_todas[df_todas["SubstitutoID"] == professor_id]


def sanitizar_nome_arquivo(nome_arquivo: str) -> str:
    """
    Remove acentos, caracteres especiais e espaços de nomes de arquivos
    para compatibilidade com Supabase Storage e chaves S3.
    Exemplo: 'Exercício AST11.pdf' -> 'Exercicio_AST11.pdf'
    """
    if not nome_arquivo:
        return "atestado.pdf"
    partes = nome_arquivo.rsplit(".", 1)
    base = partes[0]
    ext = f".{partes[1].lower()}" if len(partes) > 1 else ""
    base_sem_acento = unicodedata.normalize("NFKD", base).encode("ascii", "ignore").decode("ascii")
    base_limpa = re.sub(r"[^a-zA-Z0-9_-]", "_", base_sem_acento)
    base_limpa = re.sub(r"_+", "_", base_limpa).strip("_")
    return f"{base_limpa or 'atestado'}{ext}"


def anexar_atestado_reposicao(
    supabase: Client,
    ausencia_id: str,
    doc_file=None,
    data_reposicao: str = None,
    horario_reposicao: str = None
) -> tuple[bool, str]:
    """Anexa comprovante médico ao Supabase Storage e registra/atualiza a proposta de reposição."""
    try:
        url_atestado = None
        if doc_file:
            nome_limpo = sanitizar_nome_arquivo(doc_file.name)
            fpath = f"{ausencia_id}_{nome_limpo}"
            mime_type = getattr(doc_file, "type", None) or mimetypes.guess_type(doc_file.name)[0] or "application/pdf"
            try:
                supabase.storage.from_("atestados").upload(
                    fpath,
                    doc_file.getvalue(),
                    file_options={"upsert": "true", "content-type": mime_type}
                )
                url_atestado = supabase.storage.from_("atestados").get_public_url(fpath)
            except Exception as e:
                # Se arquivo já existe ou erro de upload
                err_msg = str(e)
                if "Duplicate" in err_msg or "already exists" in err_msg:
                    url_atestado = supabase.storage.from_("atestados").get_public_url(fpath)
                elif "Bucket not found" in err_msg or "404" in err_msg:
                    return False, "O bucket de armazenamento 'atestados' ainda não foi criado no Supabase. Crie o bucket com o nome 'atestados' (marcado como Public) no menu Storage do seu painel Supabase."
                elif "InvalidKey" in err_msg or "Invalid key" in err_msg:
                    return False, f"Nome de arquivo inválido para o Supabase Storage ({err_msg}). Tente renomear o arquivo sem caracteres especiais."
                else:
                    return False, f"Erro ao anexar arquivo no Supabase Storage: {err_msg}"

        # Verifica se já existe registro em reposicoes_atestados para essa ausência
        rep_existente = supabase.table("reposicoes_atestados").select("id").eq("ausencia_id", ausencia_id).execute()
        
        dados_rep = {
            "ausencia_id": ausencia_id,
            "data_reposicao": str(data_reposicao) if data_reposicao else None,
            "horario_reposicao": horario_reposicao or "A combinar",
            "comprovada": False
        }
        if url_atestado:
            dados_rep["atestado_url"] = url_atestado

        if rep_existente.data and len(rep_existente.data) > 0:
            rep_id = rep_existente.data[0]["id"]
            supabase.table("reposicoes_atestados").update(dados_rep).eq("id", rep_id).execute()
        else:
            supabase.table("reposicoes_atestados").insert(dados_rep).execute()

        # Se havia aviso de recusa anterior, limpa a tag do motivo ao reenviar novo atestado
        try:
            res_aus = supabase.table("ausencias").select("motivo").eq("id", ausencia_id).execute()
            if res_aus.data:
                motivo_ant = res_aus.data[0].get("motivo") or ""
                if "[Recusa da Secretaria:" in motivo_ant:
                    linhas = [l for l in motivo_ant.split("\n") if not l.startswith("[Recusa da Secretaria:")]
                    motivo_limpo = "\n".join(linhas).strip()
                    supabase.table("ausencias").update({"motivo": motivo_limpo}).eq("id", ausencia_id).execute()
        except Exception:
            pass

        # Atualiza o status da ausência para 'Aguardando Homologação'
        supabase.table("ausencias").update({"status": "Aguardando Homologação"}).eq("id", ausencia_id).execute()
        return True, "Atestado e proposta de reposição enviados para homologação da Secretaria!"
    except Exception as e:
        return False, f"Erro ao salvar comprovação: {e}"


def aprovar_atestado_secretaria(supabase: Client, ausencia_id: str) -> tuple[bool, str]:
    """Aprova e homologa o atestado médico de uma ausência pela Secretaria."""
    try:
        supabase.table("ausencias").update({"status": "Aprovada"}).eq("id", ausencia_id).execute()
        supabase.table("reposicoes_atestados").update({"comprovada": True}).eq("ausencia_id", ausencia_id).execute()
        return True, "Atestado aprovado e homologado com sucesso pela Secretaria!"
    except Exception as e:
        return False, f"Erro ao aprovar atestado: {e}"


def recusar_atestado_secretaria(supabase: Client, ausencia_id: str, motivo_recusa: str) -> tuple[bool, str]:
    """
    Não aprova (recusa) o atestado submetido pelo professor.
    Retorna a ausência para o status 'Pendente', registra a justificativa da recusa
    e reseta o anexo para que o professor possa enviar um novo documento corrigido.
    """
    try:
        motivo_recusa = motivo_recusa.strip()
        if not motivo_recusa:
            return False, "Por favor, informe a justificativa da não aprovação para orientar o professor."

        # Busca o motivo atual da ausência
        res_aus = supabase.table("ausencias").select("motivo").eq("id", ausencia_id).execute()
        motivo_atual = res_aus.data[0]["motivo"] if res_aus.data else ""

        # Remove eventual aviso anterior de recusa para não duplicar
        linhas = [linha for linha in motivo_atual.split("\n") if not linha.startswith("[Recusa da Secretaria:")]
        motivo_limpo = "\n".join(linhas).strip()

        novo_motivo = f"{motivo_limpo}\n[Recusa da Secretaria: {motivo_recusa}]".strip()

        # Atualiza a ausência para status 'Pendente' com a justificativa
        supabase.table("ausencias").update({
            "status": "Pendente",
            "motivo": novo_motivo
        }).eq("id", ausencia_id).execute()

        # Reseta o comprovante em reposicoes_atestados para que volte a ficar pendente de envio
        supabase.table("reposicoes_atestados").update({
            "atestado_url": None,
            "comprovada": False
        }).eq("ausencia_id", ausencia_id).execute()

        return True, "Atestado não aprovado. A ocorrência voltou a ficar pendente para o professor com a justificativa informada."
    except Exception as e:
        return False, f"Erro ao recusar atestado: {e}"


def registrar_ausencia_secretaria(
    supabase: Client,
    professor_id: str,
    disciplina_id: str,
    turma_id: str,
    data_ausencia: str,
    horario: str,
    motivo: str,
    anexar_atestado_agora: bool = False,
    doc_file=None,
    data_reposicao: str = None,
    horario_reposicao: str = None
) -> tuple[bool, str]:
    """
    Registra uma ocorrência de falta lançada pela Secretaria.
    - Se anexar_atestado_agora=True e houver arquivo/atestado:
        A Secretaria anexa o comprovante médico no próprio ato do lançamento.
        A ocorrência é encaminhada para o status 'Aguardando Homologação' da Coordenação.
    - Se anexar_atestado_agora=False:
        Cria um evento de falta com status 'Pendente', notificando o professor no
        Portal do Docente para que ele mesmo anexe o atestado e a proposta de reposição.
    """
    try:
        status_inicial = "Aguardando Homologação" if (anexar_atestado_agora and doc_file) else "Pendente"

        # 1. Insere a ausência registrada pela Secretaria
        res = supabase.table("ausencias").insert({
            "professor_id": professor_id,
            "disciplina_id": disciplina_id,
            "turma_id": turma_id,
            "data_ausencia": str(data_ausencia),
            "horario": horario,
            "motivo": motivo,
            "status": status_inicial,
            "registrado_por": "Secretaria"
        }).execute()

        if not res.data:
            return False, "Erro ao registrar ausência no banco de dados."

        ausencia_id = res.data[0]["id"]

        # 2. Se a Secretaria optou por anexar o atestado agora
        if anexar_atestado_agora and doc_file:
            ok_anexo, msg_anexo = anexar_atestado_reposicao(
                supabase=supabase,
                ausencia_id=ausencia_id,
                doc_file=doc_file,
                data_reposicao=data_reposicao,
                horario_reposicao=horario_reposicao
            )
            if not ok_anexo:
                return True, f"Falta registrada, mas houve aviso no upload do atestado: {msg_anexo}"
            return True, "Falta registrada e atestado anexado com sucesso pela Secretaria! Encaminhado para homologação da Coordenação."

        return True, "Evento de falta registrado com sucesso! Foi gerada uma pendência para que o professor anexe o atestado pelo Portal do Docente."
    except Exception as e:
        return False, f"Erro ao registrar ausência: {e}"


def registrar_ausencia_docente(
    supabase: Client,
    professor_id: str,
    disciplina_id: str,
    turma_id: str,
    data_ausencia: str,
    horario: str,
    motivo: str,
    doc_file=None,
    data_reposicao: str = None,
    horario_reposicao: str = None
) -> tuple[bool, str]:
    """Permite ao próprio professor comunicar sua ausência com envio de atestado opcional."""
    try:
        status_inicial = "Aguardando Homologação" if doc_file or data_reposicao else "Pendente"
        
        # 1. Insere ausência
        res = supabase.table("ausencias").insert({
            "professor_id": professor_id,
            "disciplina_id": disciplina_id,
            "turma_id": turma_id,
            "data_ausencia": str(data_ausencia),
            "horario": horario,
            "motivo": motivo,
            "status": status_inicial,
            "registrado_por": "Docente"
        }).execute()

        if not res.data:
            return False, "Erro ao registrar ausência no banco de dados."

        ausencia_id = res.data[0]["id"]

        # 2. Se houver atestado ou proposta de reposição, vincula imediatamente
        if doc_file or data_reposicao:
            anexar_atestado_reposicao(
                supabase=supabase,
                ausencia_id=ausencia_id,
                doc_file=doc_file,
                data_reposicao=data_reposicao,
                horario_reposicao=horario_reposicao
            )

        return True, "Ausência comunicada com sucesso! A Secretaria e a Coordenação já foram notificadas."
    except Exception as e:
        return False, f"Erro ao comunicar ausência: {e}"


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
