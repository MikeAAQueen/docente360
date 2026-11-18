# 📋 01 — Levantamento de Domínio e Análise dos Perfis Operacionais (Secretaria, Coordenação e Docentes)

**Fase:** 01 — Levantamento e Requisitos  
**Tópico:** 01 — Análise das Necessidades da Secretaria, Coordenação Acadêmica e Corpo Docente  
**Projeto:** Docente360  

---

## 1. Metodologia de Levantamento Utilizada

> [!NOTE]
> **Nota Metodológica:** Para o desenvolvimento do projeto **Docente360**, **não foram realizadas entrevistas presenciais ou de campo em uma faculdade**. O levantamento de necessidades foi conduzido por meio de **análise de domínio acadêmico**, **estudo de cenários operacionais reais de instituições de ensino**, **revisão de fluxos administrativos de controle de frequência docente** e **modelagem de personas (Secretaria, Coordenação Acadêmica, Professores e Administração)**.

Essa abordagem permitiu mapear de forma abrangente e estruturada todas as dores comuns à rotina escolar e universitária, garantindo uma solução genérica, completa e adaptável a qualquer instituição de ensino.

---

## 2. Análise das Personas e Atores do Domínio Acadêmico

A partir da análise de domínio, foram modelados quatro perfis fundamentais que interagem no ciclo de uma ausência docente:

### 2.1 Secretaria Acadêmica (Operação Diária)
- **Contexto de Trabalho:** Recebe notificações de faltas de última hora ou programadas, precisa providenciar rapidamente um professor substituto para que a turma não fique desassistida e recebe atestados médicos para conferência e arquivamento.
- **Principais Necessidades Levantadas:**
  - Registrar uma ausência em menos de 1 minuto, podendo anexar o atestado imediatamente (caso já o tenha em mãos) ou gerar uma pendência automática para o professor anexar depois.
  - Visualizar quais ausências ainda não possuem professor substituto alocado e poder atribuir um substituto sem choque de horário ou classificar a aula como *"Aula Vaga"*.
  - Avaliar a validade formal dos atestados enviados pelos professores (com pré-visualização na própria tela), podendo aprovar ou recusar com justificativa para que o professor reenvie o documento corrigido.
  - Consultar um histórico limpo e objetivo (`Data`, `Horário`, `Professor`, `Motivo`, `Status`, `Atestado`, `NomeSubstituto`, `AulaVaga`) com acesso ao documento do atestado em 1 clique.

### 2.2 Corpo Docente / Professores (Autoatendimento e Colaboração)
- **Contexto de Trabalho:** Precisa avisar quando não poderá comparecer a uma aula, entregar o atestado médico comprobatório dentro do prazo institucional (48h úteis), propor uma data de reposição e, frequentemente, tem disponibilidade para substituir colegas ausentes em horários livres.
- **Principais Necessidades Levantadas:**
  - Ter um **Portal do Docente** próprio onde possa vincular sua conta de login ao seu cadastro de professor na instituição.
  - Receber alertas claros quando a Secretaria registrar uma falta em seu nome aguardando atestado ou quando um atestado enviado for recusado por ilegibilidade/divergência.
  - Comunicar ausências diretamente pelo sistema (auto-registro).
  - Visualizar um **Mural de Substituições Pendentes**, onde possa ver faltas de outros professores que estão precisando de substituto e **candidatar-se para assumir a aula com 1 clique**, desde que esteja com o horário livre.

### 2.3 Coordenação Acadêmica (Gestão Pedagógica e Indicadores)
- **Contexto de Trabalho:** Acompanha o cumprimento da carga horária das disciplinas, avalia o impacto das faltas por turma/curso, homologa pedagogicamente os planos de reposição de aula e presta contas à direção por meio de relatórios.
- **Principais Necessidades Levantadas:**
  - Ter um **Dashboard Analítico em Tempo Real** com filtros por período, turma e disciplina, exibindo taxas de substituição, volume de aulas vagas e frequência de ausências por docente.
  - Homologar ou solicitar ajustes nas propostas de reposição de aulas submetidas pelos professores.
  - Emitir relatórios oficiais diagramados em **PDF (formato Paisagem)** prontos para assinatura institucional e exportar dados consolidados em **CSV**.

### 2.4 Administrador do Sistema (Governança e Supervisão)
- **Contexto de Trabalho:** Gerencia os cadastros estruturais da instituição e presta suporte a todos os setores.
- **Principais Necessidades Levantadas:**
  - Manter a base de dados de professores, matérias/disciplinas e turmas sem risco de exclusão acidental de registros com histórico.
  - Possuir uma **Navegação Master** que permita visualizar e operar qualquer módulo do sistema para auditoria e suporte.

---

## 3. Síntese dos Problemas Identificados pelo Levantamento de Domínio

| Problema no Modelo Tradicional | Impacto na Instituição de Ensino | Solução Proposta no Docente360 |
| :--- | :--- | :--- |
| Avisos de falta dispersos em mensagens e e-mails | Perda de histórico e demora na reação da Secretaria | Registro centralizado em fluxo duplo (Secretaria e Portal do Docente) |
| Demora para encontrar um professor substituto | Aumento de turmas ociosas ("Aulas Vagas") | Mural de **Substituições Pendentes** no Portal do Docente com autocandidatura em 1 clique |
| Atestados em papel ou arquivos soltos sem validação | Extravio de documentos e falta de retorno ao docente | Upload no **Supabase Storage**, preview embutido e fluxo de aprovação/recusa comentada |
| Consolidação manual de indicadores no fim do mês | Horas gastas montando planilhas para reuniões | Dashboard Plotly em tempo real e gerador automático de relatórios PDF Paisagem |

