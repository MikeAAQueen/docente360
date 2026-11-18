# 📱 06 — Design System, Responsividade e Estilização da Interface Web

**Fase:** 03 — Desenvolvimento do Módulo  
**Tópico:** 06 — Responsividade, Componentes Visuais e Estilização CSS Customizada  
**Projeto:** Docente360  

---

## 1. Configuração Global e Layout Fluido ([`app.py`](file:///d:/Projects/docente360/app.py))

A aplicação é inicializada com `st.set_page_config(layout="wide", initial_sidebar_state="expanded")` e tema configurado via [`.streamlit/config.toml`](file:///d:/Projects/docente360/.streamlit/config.toml) (`primaryColor = "#2563EB"`, `backgroundColor = "#F8FAFC"`), aproveitando 100% da largura útil em monitores desktop e adaptando automaticamente os grids de colunas (`st.columns`) em blocos empilhados quando acessada a partir de tablets ou smartphones (**RNF01**).

---

## 2. Design System Centralizado ([`components/styles.py`](file:///d:/Projects/docente360/components/styles.py))

Para elevar a maturidade visual e superar as limitações padrão do Streamlit, a função `apply_custom_styles()` injeta uma folha de estilos CSS customizada com tipografia profissional (*Plus Jakarta Sans* e *Inter*) e elementos modernos:

### 2.1 Header com Gradiente Executivo e Glassmorphism
- Cabeçalho dinâmico com gradiente azul institucional (`#1E3A8A` a `#3B82F6`), microefeito circular de iluminação e badge translúcido de status do sistema (`🟢 Sistema Operacional`).

### 2.2 Abas de Navegação Estilo *Pills* Elevadas (`flex-wrap`)
- A barra de abas `div[data-baseweb="tab-list"]` adota visual de pílulas flutuantes com fundo neutro suave (`#F1F5F9`), bordas refinadas e `flex-wrap: wrap !important`, eliminando cortes de texto.
- A aba ativa recebe elevação em cartão branco com sombra suave (`box-shadow`), tipografia em negrito e destaque no azul da marca (`#2563EB`).

### 2.3 Cards de Métricas com Elevação Interativa (`st.metric`)
- Os cartões de indicadores ganham fundo branco sólido, bordas sutis e efeito de elevação (*hover lift*) ao passar o mouse, com valores numéricos de alta legibilidade.

### 2.4 Badges Semânticos e Sidebar Moderna
- Barra lateral com card de cabeçalho escuro para a marca institucional, box dedicado de informações do usuário logado e badges semânticos cromáticos para cada perfil:
  - **Secretaria (`.badge-sec`):** Azul institucional (`#DBEAFE` / `#1D4ED8`)
  - **Coordenador Acadêmico (`.badge-coord`):** Âmbar/Ouro (`#FEF3C7` / `#B45309`)
  - **Professor (`.badge-prof`):** Roxo acadêmico (`#EDE9FE` / `#6D28D9`)
  - **Administrador (`.badge-admin`):** Verde esmeralda (`#D1FAE5` / `#047857`)

### 2.5 Componentes Interativos Nativos e Gráficos Plotly
- **Tabelas fluidas (`use_container_width=True`, `hide_index=True`):** Utilizam `st.column_config.LinkColumn` para botões clicáveis (`📄 Ver Atestado`) e `CheckboxColumn` para indicadores booleanos (`AulaVaga`).
- **Visualizadores Embutidos:** Preview de atestados médicos com `<iframe width="100%" height="500px">` e `st.image(use_container_width=True)`.
- **Gráficos Plotly Estilizados:** Fundo transparente integrado, tipografia unificada e paleta de cores consistente em toda a plataforma.

