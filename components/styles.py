import streamlit as st
from supabase import Client
from services.auth_service import handle_logout

def apply_custom_styles():
    """Aplica o design system profissional e amadurecido do Docente360."""
    st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

    <style>
        /* =====================================================================
           DESIGN SYSTEM — PALETA E TIPOGRAFIA GLOBAL
           ===================================================================== */
        :root {
            --primary-900: #0F172A;
            --primary-800: #1E293B;
            --primary-700: #334155;
            --brand-600: #2563EB;
            --brand-700: #1D4ED8;
            --brand-50: #EFF6FF;
            --slate-50: #F8FAFC;
            --slate-100: #F1F5F9;
            --slate-200: #E2E8F0;
            --slate-300: #CBD5E1;
            --slate-600: #475569;
            --slate-700: #334155;
            --slate-900: #0F172A;
            --success-500: #10B981;
            --success-50: #ECFDF5;
            --warning-500: #F59E0B;
            --warning-50: #FFFBEB;
            --danger-500: #EF4444;
            --danger-50: #FEF2F2;
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -4px rgba(0, 0, 0, 0.03);
            --radius-md: 10px;
            --radius-lg: 14px;
            --radius-xl: 18px;
        }

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            letter-spacing: -0.011em;
            color: var(--slate-900);
        }

        /* Container principal com respiro elegante */
        .block-container {
            padding-top: 1.8rem !important;
            padding-bottom: 3.5rem !important;
            max-width: 1400px !important;
        }

        /* =====================================================================
           HEADER PREMIUM E BREADCRUMB
           ===================================================================== */
        .app-header-container {
            background: linear-gradient(135deg, #1E3A8A 0%, #1D4ED8 50%, #3B82F6 100%);
            border-radius: var(--radius-lg);
            padding: 22px 28px;
            margin-bottom: 1.8rem;
            box-shadow: var(--shadow-md);
            color: #FFFFFF;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: relative;
            overflow: hidden;
        }

        .app-header-container::after {
            content: "";
            position: absolute;
            right: -20px;
            top: -30px;
            width: 180px;
            height: 180px;
            background: radial-gradient(circle, rgba(255,255,255,0.18) 0%, rgba(255,255,255,0) 70%);
            border-radius: 50%;
            pointer-events: none;
        }

        .app-header-title {
            font-size: 1.65rem;
            font-weight: 800;
            color: #FFFFFF;
            margin: 0;
            line-height: 1.25;
            letter-spacing: -0.02em;
        }

        .app-header-sub {
            font-size: 0.92rem;
            color: rgba(255, 255, 255, 0.88);
            margin-top: 4px;
            font-weight: 400;
        }

        .app-header-pill {
            background: rgba(255, 255, 255, 0.16);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.28);
            padding: 6px 14px;
            border-radius: 9999px;
            font-size: 0.82rem;
            font-weight: 600;
            color: #FFFFFF;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        /* Títulos legados */
        .main-title {
            font-size: 1.65rem;
            font-weight: 800;
            color: var(--primary-900);
            margin-bottom: 0.2rem;
            letter-spacing: -0.02em;
        }
        .sub-title {
            font-size: 0.92rem;
            color: var(--slate-600);
            margin-bottom: 1.2rem;
        }

        /* =====================================================================
           SIDEBAR MODERNA (GLASS & SHADOW)
           ===================================================================== */
        [data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            border-right: 1px solid var(--slate-200) !important;
            box-shadow: 2px 0 12px rgba(15, 23, 42, 0.03);
        }

        [data-testid="stSidebar"] hr {
            margin: 1rem 0 !important;
            border-color: var(--slate-200) !important;
        }

        .sidebar-brand-card {
            background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
            border-radius: var(--radius-md);
            padding: 16px;
            color: #FFFFFF;
            margin-bottom: 12px;
            box-shadow: var(--shadow-sm);
        }

        .sidebar-brand-title {
            font-size: 1.2rem;
            font-weight: 800;
            color: #FFFFFF;
            display: flex;
            align-items: center;
            gap: 8px;
            margin: 0;
        }

        .sidebar-brand-caption {
            font-size: 0.76rem;
            color: #94A3B8;
            margin-top: 2px;
        }

        .user-profile-box {
            background: var(--slate-50);
            border: 1px solid var(--slate-200);
            border-radius: var(--radius-md);
            padding: 14px;
            margin-bottom: 10px;
        }

        .user-badge {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 4px 11px;
            border-radius: 9999px;
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            text-transform: uppercase;
            margin-top: 6px;
        }
        .badge-sec   { background-color: #DBEAFE; color: #1D4ED8; border: 1px solid #BFDBFE; }
        .badge-coord { background-color: #FEF3C7; color: #B45309; border: 1px solid #FDE68A; }
        .badge-admin { background-color: #D1FAE5; color: #047857; border: 1px solid #A7F3D0; }
        .badge-prof  { background-color: #EDE9FE; color: #6D28D9; border: 1px solid #DDD6FE; }

        /* =====================================================================
           ESTILIZAÇÃO DAS ABAS (PILLS REFINADAS & ELEVADAS)
           ===================================================================== */
        div[data-baseweb="tab-list"] {
            gap: 6px !important;
            background-color: var(--slate-100) !important;
            padding: 6px !important;
            border-radius: var(--radius-lg) !important;
            border-bottom: none !important;
            border: 1px solid var(--slate-200) !important;
            flex-wrap: wrap !important;
            overflow-x: visible !important;
            margin-bottom: 1.6rem !important;
        }

        div[data-baseweb="tab-border"],
        div[data-baseweb="tab-highlight"],
        div[data-baseweb="tabs"] button[aria-label="previous"],
        div[data-baseweb="tabs"] button[aria-label="next"] {
            display: none !important;
        }

        button[data-baseweb="tab"] {
            border-radius: var(--radius-md) !important;
            padding: 9px 18px !important;
            font-weight: 600 !important;
            font-size: 0.88rem !important;
            color: var(--slate-600) !important;
            background-color: transparent !important;
            border: none !important;
            transition: all 0.18s ease-in-out !important;
        }

        button[data-baseweb="tab"]:hover {
            background-color: #FFFFFF !important;
            color: var(--slate-900) !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            background-color: #FFFFFF !important;
            color: var(--brand-600) !important;
            box-shadow: 0 2px 6px rgba(15, 23, 42, 0.08), 0 1px 2px rgba(15, 23, 42, 0.04) !important;
            border: 1px solid rgba(226, 232, 240, 0.8) !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] p,
        button[data-baseweb="tab"][aria-selected="true"] span,
        button[data-baseweb="tab"][aria-selected="true"] div {
            color: var(--brand-600) !important;
            font-weight: 700 !important;
        }

        /* =====================================================================
           CARDS DE MÉTRICAS (st.metric) ESTILIZADOS
           ===================================================================== */
        [data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid var(--slate-200);
            border-radius: var(--radius-lg);
            padding: 16px 20px !important;
            box-shadow: var(--shadow-sm);
            transition: all 0.2s ease;
        }

        [data-testid="stMetric"]:hover {
            border-color: var(--slate-300);
            box-shadow: var(--shadow-md);
            transform: translateY(-2px);
        }

        [data-testid="stMetricLabel"] {
            font-size: 0.82rem !important;
            font-weight: 600 !important;
            color: var(--slate-600) !important;
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }

        [data-testid="stMetricValue"] {
            font-size: 1.85rem !important;
            font-weight: 800 !important;
            color: var(--primary-900) !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }

        /* =====================================================================
           FORMULÁRIOS, BOTÕES E INPUTS PREMIUM
           ===================================================================== */
        [data-testid="stForm"] {
            background: #FFFFFF;
            border: 1px solid var(--slate-200);
            border-radius: var(--radius-lg);
            padding: 24px !important;
            box-shadow: var(--shadow-sm);
        }

        /* ---------------------------------------------------------------------
           BORDAS VISÍVEIS E NÍTIDAS PARA CAMPOS DE TEXTO, SENHA E SELEÇÃO
           --------------------------------------------------------------------- */
        /* Container principal de inputs (Texto, Senha, Número, Data, Hora) */
        div[data-baseweb="input"],
        [data-testid="stTextInputRootElement"],
        [data-testid="stNumberInputContainer"] {
            border: 1.5px solid #CBD5E1 !important; /* Borda cinza suave e bem definida */
            border-radius: 8px !important;
            background-color: #FFFFFF !important;
            transition: all 0.2s ease-in-out !important;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04) !important;
        }

        /* Remove duplicidade de bordas internas no BaseWeb */
        div[data-baseweb="input"] div[data-baseweb="base-input"] {
            border: none !important;
            box-shadow: none !important;
            background-color: transparent !important;
        }

        /* Caixas de Texto Grandes (Text Area) */
        div[data-baseweb="textarea"],
        [data-testid="stTextAreaRootElement"] {
            border: 1.5px solid #CBD5E1 !important;
            border-radius: 8px !important;
            background-color: #FFFFFF !important;
            transition: all 0.2s ease-in-out !important;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04) !important;
        }
        div[data-baseweb="textarea"] > div {
            border: none !important;
            background-color: transparent !important;
        }

        /* Caixas de Seleção (Selectbox / Multiselect) */
        div[data-baseweb="select"] > div {
            border: 1.5px solid #CBD5E1 !important;
            border-radius: 8px !important;
            background-color: #FFFFFF !important;
            transition: all 0.2s ease-in-out !important;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04) !important;
        }

        /* Efeito Hover (ao passar o cursor sobre o campo) */
        div[data-baseweb="input"]:hover,
        div[data-baseweb="textarea"]:hover,
        div[data-baseweb="select"] > div:hover,
        [data-testid="stTextInputRootElement"]:hover {
            border-color: #94A3B8 !important;
        }

        /* Efeito Focus (quando o usuário clica para digitar) */
        div[data-baseweb="input"]:focus-within,
        div[data-baseweb="textarea"]:focus-within,
        div[data-baseweb="select"] > div:focus-within,
        [data-testid="stTextInputRootElement"]:focus-within {
            border-color: #2563EB !important; /* Azul institucional vibrante */
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.18) !important;
        }

        /* Tipografia dos valores digitados e preenchidos */
        div[data-baseweb="input"] input,
        div[data-baseweb="textarea"] textarea {
            color: #0F172A !important;
            font-size: 0.95rem !important;
        }

        /* Ícones utilitários internos (ex: botão de exibir/ocultar senha) */
        div[data-baseweb="input"] button {
            color: #64748B !important;
        }
        div[data-baseweb="input"] button:hover {
            color: #1E293B !important;
        }

        /* Rótulos dos campos com peso visual adequado */
        [data-testid="stWidgetLabel"] p,
        [data-testid="stWidgetLabel"] label {
            font-weight: 600 !important;
            color: #1E293B !important;
            font-size: 0.88rem !important;
            margin-bottom: 4px !important;
        }

        /* Estilização dos botões primários */
        button[kind="primary"] {
            background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: var(--radius-md) !important;
            padding: 0.55rem 1.25rem !important;
            font-weight: 600 !important;
            font-size: 0.92rem !important;
            box-shadow: 0 2px 4px rgba(37, 99, 235, 0.25) !important;
            transition: all 0.18s ease-in-out !important;
        }

        button[kind="primary"]:hover {
            background: linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%) !important;
            box-shadow: 0 4px 10px rgba(37, 99, 235, 0.35) !important;
            transform: translateY(-1px);
        }

        /* Botões secundários */
        button[kind="secondary"] {
            background-color: #FFFFFF !important;
            color: var(--slate-700) !important;
            border: 1px solid var(--slate-300) !important;
            border-radius: var(--radius-md) !important;
            font-weight: 600 !important;
            transition: all 0.15s ease !important;
        }

        button[kind="secondary"]:hover {
            background-color: var(--slate-50) !important;
            border-color: var(--slate-400) !important;
            color: var(--slate-900) !important;
        }

        /* Expander moderno */
        [data-testid="stExpander"] {
            background: #FFFFFF;
            border: 1px solid var(--slate-200) !important;
            border-radius: var(--radius-md) !important;
            box-shadow: var(--shadow-sm);
            margin-bottom: 12px;
            overflow: hidden;
        }

        /* Tabelas e Dataframes */
        [data-testid="stDataFrame"] {
            border: 1px solid var(--slate-200);
            border-radius: var(--radius-md);
            overflow: hidden;
            box-shadow: var(--shadow-sm);
        }

        /* Alerts personalizados com acabamento suave */
        div[data-testid="stAlert"] {
            border-radius: var(--radius-md) !important;
            border-width: 1px !important;
            padding: 12px 18px !important;
            font-size: 0.92rem !important;
        }
    </style>
    """, unsafe_allow_html=True)


def render_sidebar_user(supabase: Client, user_profile: dict):
    """Renderiza a barra lateral elegante com identificação do usuário e navegação."""
    usuario = user_profile or {}
    nome_usuario = usuario.get("nome", "Usuário")
    perfil_usuario = usuario.get("perfil", "Secretaria")
    cargo_usuario = usuario.get("cargo", "Equipe")
    email_usuario = usuario.get("email", "")

    with st.sidebar:
        # Card de Marca no topo
        st.markdown("""
        <div class="sidebar-brand-card">
            <div class="sidebar-brand-title">🎓 Docente360</div>
            <div class="sidebar-brand-caption">Gestão Acadêmica, Ausências & Frequência</div>
        </div>
        """, unsafe_allow_html=True)

        badge_class = (
            "badge-sec" if perfil_usuario == "Secretaria"
            else ("badge-coord" if perfil_usuario == "Coordenador Acadêmico"
            else ("badge-prof" if perfil_usuario == "Professor" else "badge-admin"))
        )

        st.markdown(f"""
        <div class="user-profile-box">
            <div style="font-size: 0.72rem; color: #64748B; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em;">Conectado como</div>
            <div style="font-size: 1.02rem; font-weight: 800; color: #0F172A; margin-top: 2px;">{nome_usuario}</div>
            <div style="font-size: 0.78rem; color: #64748B; margin-top: 2px;">{email_usuario}</div>
            <div style="font-size: 0.78rem; color: #475569; margin-top: 2px; font-weight: 500;">💼 {cargo_usuario}</div>
            <span class="user-badge {badge_class}">● {perfil_usuario}</span>
        </div>
        """, unsafe_allow_html=True)

        # Se for Administrador, exibe o seletor de navegação master na barra lateral
        modulo_master = None
        if perfil_usuario == "Administrador":
            st.markdown("##### 🧭 Navegação Master")
            modulo_master = st.radio(
                "Acessar Setor / Módulo:",
                [
                    "📌 Secretaria (Lançamento & Faltas)",
                    "📊 Coordenação (Dashboard & Relatórios)",
                    "👨‍🏫 Portal do Professor (Visão do Docente)",
                    "👥 Painel Geral do Administrador"
                ],
                index=0,
                label_visibility="collapsed"
            )
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        if st.button("🚪 Sair do Sistema", use_container_width=True, type="secondary"):
            handle_logout(supabase)

        st.markdown("<div style='margin-top: 1.5rem; font-size: 0.72rem; color: #94A3B8; text-align: center;'>Docente360 Enterprise • v2.0<br/>Supabase Auth • RLS Ativo</div>", unsafe_allow_html=True)

    return modulo_master


def render_header(perfil_usuario: str, nome_usuario: str, cargo_usuario: str):
    """Renderiza o cabeçalho moderno e profissional com gradiente e identificação contextual."""
    st.markdown(f"""
    <div class="app-header-container">
        <div>
            <div class="app-header-title">Docente360 — Painel da {perfil_usuario}</div>
            <div class="app-header-sub">Sessão ativa de <b>{nome_usuario}</b> ({cargo_usuario})</div>
        </div>
        <div class="app-header-pill">
            🟢 Sistema Operacional
        </div>
    </div>
    """, unsafe_allow_html=True)
