# 🎓 Docente360 — Plataforma Integrada de Gestão Acadêmica

O **Docente360** é uma plataforma web desenvolvida em **Python (Streamlit)** e **Supabase (PostgreSQL, Auth & Storage)** para gestão operacional e pedagógica de ausências docentes, alocação e candidatura colaborativa de professores substitutos, homologação de atestados médicos, validação de reposições de aulas e emissão de relatórios gerenciais em PDF e CSV.

---

## ✨ Principais Funcionalidades por Perfil (RBAC)

- **📌 Secretaria Acadêmica ([`views/secretaria.py`](file:///d:/Projects/docente360/views/secretaria.py)):**
  - **Lançamento de Faltas em Fluxo Duplo:** Permite anexar o atestado médico no ato do lançamento ou criar um evento pendente para o professor anexar depois pelo Portal do Docente.
  - **Gestão de Substituições e Aulas Vagas:** Alocação de substituto com checagem automática de conflito de horário (**RN01**) ou classificação como *Aula Vaga*.
  - **Homologação e Devolução de Atestados:** Pré-visualização de PDFs e imagens embutida na tela, aprovação em 1 clique ou recusa com justificativa obrigatória que devolve a pendência ao professor.
  - **Histórico Enxuto e Interativo:** Exibe `Data`, `Horário`, `Professor`, `Motivo`, `Status`, `Atestado` (botão clicável **`📄 Ver Atestado`** + visualizador na tela ao selecionar a linha), `NomeSubstituto` e `AulaVaga`.
  - **Cadastros Base:** Gestão completa de Professores, Matérias/Disciplinas e Turmas com busca em tempo real e proteção de integridade referencial.

- **👨‍🏫 Portal do Docente ([`views/professor.py`](file:///d:/Projects/docente360/views/professor.py)):**
  - **Vínculo Inteligente de Conta:** No cadastro com confirmação dupla de senha ([`views/login.py`](file:///d:/Projects/docente360/views/login.py)), o docente pode vincular seu login a um registro já cadastrado pela Secretaria ou criar novo perfil.
  - **Envio/Reenvio de Atestados e Auto-registro:** Submissão de comprovantes médicos com proposta de reposição e comunicação antecipada de ausências.
  - **Mural de Substituições Pendentes (Candidatura Docente):** Visualização das faltas de outros professores sem substituto, verificação automática de disponibilidade na agenda (`🟢 Horário livre` / `🔴 Conflito`) e candidatura imediata com 1 clique.

- **📊 Coordenação Acadêmica ([`views/coordenador.py`](file:///d:/Projects/docente360/views/coordenador.py)):**
  - **Dashboard Analítico em Tempo Real:** Filtros de período, turma e disciplina, 5 KPIs e 4 gráficos interativos Plotly.
  - **Homologação Pedagógica de Reposições:** Aprovação ou solicitação de ajuste nos planos de reposição de aula.
  - **Central de Relatórios Oficiais ([`utils/pdf_generator.py`](file:///d:/Projects/docente360/utils/pdf_generator.py)):** Exportação filtrada em **PDF Oficial Diagramado em Paisagem** (com cabeçalho institucional, KPIs, tabela analítica, assinaturas e paginação `Página X de Y`) e planilha **CSV**.

- **👥 Administrador ([`views/admin.py`](file:///d:/Projects/docente360/views/admin.py)):**
  - **Navegação Master:** Alternador na barra lateral que permite operar e auditar todos os módulos do sistema, além de consultar equipe, cadastros base, ocorrências e métricas globais.

---

## 📂 Documentação das Fases do Projeto

A documentação completa de engenharia de software está organizada na pasta [`fases_do_projeto/`](file:///d:/Projects/docente360/fases_do_projeto) e nos documentos de governança na raiz:

1. [01 — Fase 1: Levantamento e Requisitos](file:///d:/Projects/docente360/fases_do_projeto/01-Fase-1-Levantamento-e-requisitos.md)
2. [02 — Fase 2: Modelagem e Prototipação](file:///d:/Projects/docente360/fases_do_projeto/02-Fase-2-Modelagem-e-prototipacao.md)
3. [03 — Fase 3: Desenvolvimento do Módulo](file:///d:/Projects/docente360/fases_do_projeto/03-Fase-3-Desenvolvimento-do-modulo.md)
4. [04 — Fase 4: Testes e Validação](file:///d:/Projects/docente360/fases_do_projeto/04-Fase-4-Testes-e-validacao.md)
5. [05 — Fase 5: Implantação e Treinamento](file:///d:/Projects/docente360/fases_do_projeto/05-Fase-5-Implantacao-e-treinamento.md)
6. [06 — Fase 6: Avaliação e Relatório Final](file:///d:/Projects/docente360/fases_do_projeto/06-Fase-6-Avaliacao-e-relatorio-final.md)
- **Documentos Complementares na Raiz:**
  - [Especificação Detalhada de Requisitos (`levantamento_requisitos.md`)](file:///d:/Projects/docente360/levantamento_requisitos.md)
  - [Estado Atual e Rastreabilidade do Projeto (`PROJECT_STATE.md`)](file:///d:/Projects/docente360/PROJECT_STATE.md)
  - [Script DDL do Banco de Dados e Storage (`banco_dados.sql`)](file:///d:/Projects/docente360/banco_dados.sql)

---

## 🚀 Como Executar o Projeto

1. **Instale as dependências:**
   ```powershell
   pip install -r requirements.txt
   ```
2. **Configure o Banco de Dados no Supabase:**
   - Execute o script [`banco_dados.sql`](file:///d:/Projects/docente360/banco_dados.sql) no **SQL Editor** do seu painel Supabase.
3. **Configure as variáveis de ambiente (`.env`):**
   ```env
   SUPABASE_URL="https://<SEU-PROJETO>.supabase.co"
   SUPABASE_KEY="<SUA-ANON-PUBLIC-KEY>"
   ```
4. **Execute a aplicação Streamlit:**
   ```powershell
   streamlit run app.py
   ```

