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
    """Busca os dados do perfil na tabela 'usuarios', com fallback nos metadados do Supabase Auth."""
    metadata = metadata or {}
    try:
        res = supabase.table("usuarios").select("*").eq("id", user_id).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]
    except Exception:
        pass

    # Fallback se a tabela ainda estiver em processo de sincronização
    return {
        "id": user_id,
        "email": email,
        "nome": metadata.get("nome", email.split("@")[0]),
        "perfil": metadata.get("perfil", "Secretaria"),
        "cargo": metadata.get("cargo", "Equipe Operacional")
    }


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


def handle_signup(supabase: Client, email: str, password: str, nome: str, perfil: str, cargo: str):
    """Cria nova conta no Supabase Auth e insere na tabela de usuários."""
    if len(password) < 6:
        st.error("A senha deve conter no mínimo 6 caracteres.")
        return
    try:
        # 1. Cria usuário no Supabase Auth com metadados
        res = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "nome": nome,
                    "perfil": perfil,
                    "cargo": cargo
                }
            }
        })

        if res.user:
            # 2. Tenta registrar explicitamente na tabela 'usuarios'
            try:
                supabase.table("usuarios").upsert({
                    "id": res.user.id,
                    "nome": nome,
                    "email": email,
                    "perfil": perfil,
                    "cargo": cargo
                }).execute()
            except Exception:
                pass  # A trigger do banco ou o RLS podem tratar

            # Se a sessão já foi iniciada (sem confirmação obrigatória de email)
            if res.session:
                st.session_state["auth_user"] = res.user
                st.session_state["user_profile"] = {
                    "id": res.user.id,
                    "nome": nome,
                    "email": email,
                    "perfil": perfil,
                    "cargo": cargo
                }
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
