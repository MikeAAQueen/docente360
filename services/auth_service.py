import streamlit as st
from supabase import Client

# ==============================================================================
# INICIALIZAÇÃO E GERENCIAMENTO DE SESSÃO
# ==============================================================================
def init_session_state():
    """Garante que as chaves de sessão existam no Streamlit."""
    if "auth_user" not in st.session_state:
        st.session_state["auth_user"] = None
    if "user_profile" not in st.session_state:
        st.session_state["user_profile"] = None


def get_profile_data(supabase: Client, user_id: str, email: str, metadata: dict = None) -> dict:
    """Busca os dados do perfil na tabela 'usuarios', com fallback nos metadados do Supabase Auth e resolução de professor_id."""
    metadata = metadata or {}
    profile = None
    try:
        res = supabase.table("usuarios").select("*").eq("id", user_id).execute()
        if res.data and len(res.data) > 0:
            profile = res.data[0]
    except Exception:
        pass

    if not profile:
        profile = {
            "id": user_id,
            "email": email,
            "nome": metadata.get("nome", email.split("@")[0]),
            "perfil": metadata.get("perfil", "Secretaria"),
            "cargo": metadata.get("cargo", "Equipe Operacional"),
            "professor_id": None
        }

    # Se o perfil for Professor mas ainda não tiver professor_id associado, tenta vincular pelo e-mail
    if profile.get("perfil") == "Professor" and not profile.get("professor_id"):
        try:
            prof_res = supabase.table("professores").select("id, departamento").ilike("email", email.strip()).execute()
            if prof_res.data and len(prof_res.data) > 0:
                prof_id = prof_res.data[0]["id"]
                profile["professor_id"] = prof_id
                # Atualiza na tabela usuarios para persistência futura
                supabase.table("usuarios").update({"professor_id": prof_id}).eq("id", user_id).execute()
        except Exception:
            pass

    return profile


def handle_login(supabase: Client, email: str, password: str):
    """Efetua login no Supabase Auth e carrega perfil do usuário."""
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if res.user:
            profile = get_profile_data(supabase, res.user.id, res.user.email, res.user.user_metadata)
            st.session_state["auth_user"] = res.user
            st.session_state["user_profile"] = profile
            st.success(f"Bem-vindo(a), {profile.get('nome')}!")
            st.rerun()
    except Exception as e:
        msg = str(e)
        if "Invalid login credentials" in msg:
            st.error("E-mail ou senha incorretos.")
        elif "Email not confirmed" in msg:
            st.warning("E-mail ainda não confirmado. Verifique sua caixa de entrada no e-mail ou desative a exigência de confirmação no painel do Supabase.")
        else:
            st.error(f"Erro ao autenticar: {msg}")


def handle_signup(
    supabase: Client,
    email: str,
    password: str,
    nome: str,
    perfil: str,
    cargo: str,
    professor_id: str = None
):
    """Cria nova conta no Supabase Auth e insere na tabela de usuários vinculando se for professor."""
    if len(password) < 6:
        st.error("A senha deve conter no mínimo 6 caracteres.")
        return
    try:
        # Se for professor, verifica se já existe na tabela de professores ou cria se não existir
        prof_id = professor_id
        if perfil == "Professor" and not prof_id:
            try:
                prof_busca = supabase.table("professores").select("id").ilike("email", email.strip()).execute()
                if prof_busca.data and len(prof_busca.data) > 0:
                    prof_id = prof_busca.data[0]["id"]
                else:
                    # Cria automaticamente o cadastro de apoio para o novo docente
                    novo_prof = supabase.table("professores").insert({
                        "nome": nome.strip(),
                        "email": email.strip().lower(),
                        "departamento": cargo.strip() if cargo else "Geral"
                    }).execute()
                    if novo_prof.data and len(novo_prof.data) > 0:
                        prof_id = novo_prof.data[0]["id"]
            except Exception:
                pass
        elif perfil == "Professor" and prof_id:
            try:
                # Mantém o e-mail consistente na tabela professores
                supabase.table("professores").update({
                    "email": email.strip().lower()
                }).eq("id", prof_id).execute()
            except Exception:
                pass

        # 1. Cria usuário no Supabase Auth com metadados
        user_meta = {
            "nome": nome,
            "perfil": perfil,
            "cargo": cargo
        }
        if prof_id:
            user_meta["professor_id"] = prof_id

        res = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": user_meta
            }
        })

        if res.user:
            # 2. Registra na tabela 'usuarios'
            dados_usuario = {
                "id": res.user.id,
                "nome": nome,
                "email": email,
                "perfil": perfil,
                "cargo": cargo
            }
            if prof_id:
                dados_usuario["professor_id"] = prof_id

            try:
                supabase.table("usuarios").upsert(dados_usuario).execute()
            except Exception:
                pass

            # Se a sessão já foi iniciada
            if res.session:
                st.session_state["auth_user"] = res.user
                st.session_state["user_profile"] = dados_usuario
                st.success("Conta criada e login realizado com sucesso!")
                st.rerun()
            else:
                st.success("✅ Usuário cadastrado com sucesso! Se a confirmação de e-mail estiver ativa no seu projeto Supabase, confirme o link enviado ao seu e-mail antes de efetuar o login.")
    except Exception as e:
        st.error(f"Erro ao criar conta: {e}")


def handle_logout(supabase: Client):
    """Encerra a sessão no Supabase e limpa o estado local."""
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    st.session_state["auth_user"] = None
    st.session_state["user_profile"] = None
    st.rerun()
