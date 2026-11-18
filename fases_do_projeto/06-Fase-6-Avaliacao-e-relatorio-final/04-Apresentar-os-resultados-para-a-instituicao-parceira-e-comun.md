# 🎤 04 — Roteiro de Apresentação dos Resultados e Demonstração Executiva

**Fase:** 06 — Avaliação e Relatório Final  
**Tópico:** 04 — Estrutura de Apresentação Final e Roteiro de Demonstração do Sistema  
**Projeto:** Docente360  

---

## 1. Estrutura da Apresentação Executiva

Este documento organiza o roteiro oficial para apresentação acadêmica e institucional dos resultados alcançados pelo projeto **Docente360**, dividido em 4 blocos objetivos:

1. **O Problema e a Proposta de Valor (2 min):**
   - Contextualização dos controles manuais descentralizados e apresentação da proposta do **Docente360** como plataforma única para Secretaria, Docentes, Coordenação e Administração.
2. **Arquitetura e Segurança em Nuvem (2 min):**
   - Apresentação da stack **Streamlit + Supabase (PostgreSQL, Auth & Storage)**, destacando o modelo relacional de 7 tabelas, o controle RBAC e o cadastro com confirmação dupla de senha.
3. **Demonstração Prática ao Vivo — Ciclo Ponta a Ponta (5 min):**
   - Execução guiada do fluxo real da plataforma (detalhado na seção 2 abaixo).
4. **Indicadores de Impacto e Conclusão (1 min):**
   - Destaque para a redução superior a 80% no tempo de registro operacional, transparência no envio/homologação de atestados e emissão instantânea de relatórios oficiais em PDF Paisagem.

---

## 2. Roteiro Passo a Passo para Demonstração ao Vivo (Live Demo)

### Ato 1 — Cadastro e Acesso com Segurança (`views/login.py`)
- Mostrar a aba **`📝 Criar Nova Conta de Usuário`** destacando os dois campos de confirmação de senha (`Senha` e `Confirmar Senha`) e a opção de vínculo inteligente de um professor pré-cadastrado pela Secretaria.
- Entrar no sistema com uma conta de **Administrador** para utilizar o menu **`🧭 Navegação Master`** na barra lateral e demonstrar todos os setores sem precisar sair da sessão.

### Ato 2 — Secretaria: Lançamento de Falta (`views/secretaria.py`)
- No módulo da **Secretaria**, mostrar a aba **`📚 Cadastros`** (Professores, Matérias e Turmas).
- Na aba **`📌 Lançamento`**, demonstrar o alternador de fluxo duplo e registrar uma falta no modo **`📅 Criar evento para o professor anexar o atestado depois`**.

### Ato 3 — Portal do Docente: Candidatura a Substituição e Envio de Atestado (`views/professor.py`)
- Alternar para o **`👨‍🏫 Portal do Professor`** simulando um colega docente disponível:
  - Mostrar o card **`Substituições Pendentes`** e a aba **`🤝 Substituições (N)`**.
  - Destacar o indicador **`🟢 Horário livre na sua agenda`** e clicar em **`🙋‍♂️ Candidatar-me / Assumir como Substituto`**.
- Alternar para o professor titular que faltou:
  - Na aba **`📋 Minhas Ausências & Atestados`**, anexar um arquivo PDF de atestado médico e enviar para homologação da Secretaria.

### Ato 4 — Secretaria: Homologação na Tela e Histórico Clicável (`views/secretaria.py`)
- De volta à **Secretaria**, abrir a aba **`✅ Homologação (1)`**, expandir **`👁️ Pré-visualizar Documento na Tela`** (mostrando o PDF aberto dentro do sistema) e clicar em **`✅ Aprovar / Homologar Atestado`** (ou demonstrar o popover de recusa comentada).
- Abrir a aba **`📋 Histórico`**: mostrar a tabela enxuta com as 8 colunas (`Data`, `Horário`, `Professor`, `Motivo`, `Status`, `Atestado`, `NomeSubstituto`, `AulaVaga`), onde já constam o substituto voluntário e o botão clicável **`📄 Ver Atestado`**.

### Ato 5 — Coordenação: Dashboard Analítico e Relatório Oficial PDF (`views/coordenador.py`)
- Alternar para o módulo da **`📊 Coordenação`**:
  - Mostrar os filtros reativos, os 5 KPIs e os 4 gráficos interativos Plotly na aba **`📊 Dashboard`**.
  - Na aba **`📄 Relatórios`**, baixar e abrir o **Relatório Oficial Completo em PDF (formato Paisagem)** com cabeçalho institucional, quadro colorido de KPIs, tabela analítica, assinaturas e paginação `Página X de Y`.

