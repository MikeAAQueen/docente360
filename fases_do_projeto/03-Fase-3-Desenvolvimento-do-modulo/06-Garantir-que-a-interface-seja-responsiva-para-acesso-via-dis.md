# 📱 06 — Design System, Responsividade e Estilização da Interface Web

**Fase:** 03 — Desenvolvimento do Módulo  
**Tópico:** 06 — Responsividade, Componentes Visuais e Estilização CSS Customizada  
**Projeto:** Docente360  

---

## 1. Configuração Global e Layout Fluido ([`app.py`](file:///d:/Projects/docente360/app.py))

A aplicação é inicializada com `st.set_page_config(layout="wide", initial_sidebar_state="expanded")`, aproveitando 100% da largura útil em monitores desktop e adaptando automaticamente os grids de colunas (`st.columns`) em blocos empilhados quando acessada a partir de tablets ou smartphones (**RNF01**).

---

## 2. Design System Centralizado ([`components/styles.py`](file:///d:/Projects/docente360/components/styles.py))

Para superar as limitações visuais padrão do Streamlit, a função `apply_custom_styles()` injeta uma folha de estilos CSS customizada com três pilares de usabilidade:

### 2.1 Abas de Navegação Estilo *Pills* com Quebra Responsiva (`flex-wrap`)
- Por padrão, quando uma tela possui muitas abas no Streamlit, os títulos são truncados ou escondidos sob setas laterais.
- O CSS implementado em [`components/styles.py`](file:///d:/Projects/docente360/components/styles.py#L40-L99) estiliza `div[data-baseweb="tab-list"]` como uma barra moderna de *pills* com `flex-wrap: wrap !important` e `overflow-x: visible !important`, ocultando as setas de corte e destacando a aba ativa em azul royal (`#1E40AF`) com texto branco em negrito.

### 2.2 Badges Semânticos de Identificação de Perfil
Na barra lateral (`render_sidebar_user`), cada perfil autenticado recebe um badge em formato pílula (`border-radius: 9999px`) com paleta cromática exclusiva:
- **Secretaria (`.badge-sec`):** Azul institucional (`#DBEAFE` / `#1E40AF`)
- **Coordenador Acadêmico (`.badge-coord`):** Âmbar/Ouro (`#FEF3C7` / `#92400E`)
- **Professor (`.badge-prof`):** Roxo acadêmico (`#EDE9FE` / `#5B21B6`)
- **Administrador (`.badge-admin`):** Verde esmeralda (`#D1FAE5` / `#065F46`)

### 2.3 Componentes Interativos Nativos de Alta Responsividade
- **Tabelas fluidas (`use_container_width=True`, `hide_index=True`):** Todas as tabelas ajustam sua largura automaticamente à tela do dispositivo, utilizando `st.column_config.LinkColumn` para botões clicáveis (`📄 Ver Atestado`) e `CheckboxColumn` para indicadores booleanos (`AulaVaga`).
- **Visualizadores Embutidos de Documentos:** O preview de atestados médicos adapta-se automaticamente ao container (`use_container_width=True` para imagens e `width="100%"` para `<iframe>` de PDFs), permitindo leitura confortável em qualquer resolução de tela.

