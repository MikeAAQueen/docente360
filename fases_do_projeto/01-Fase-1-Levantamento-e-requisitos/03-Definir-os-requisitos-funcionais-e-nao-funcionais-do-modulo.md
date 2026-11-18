# 📑 03 — Definição dos Requisitos Funcionais, Regras de Negócio e Requisitos Não Funcionais

**Fase:** 01 — Levantamento e Requisitos  
**Tópico:** 03 — Especificação de Requisitos Funcionais (RF), Regras de Negócio (RN) e Não Funcionais (RNF)  
**Projeto:** Docente360  

---

## 1. Requisitos Funcionais (RF)

### [RF01] Lançamento Diário de Ausências (Fluxo Duplo & Auto-registro Docente)
- **Prioridade:** Essencial (*Must Have*)
- **Atores:** Secretaria, Professor
- **Descrição:** Permitir o registro estruturado de ausências docentes vinculando professor, disciplina, turma, data, bloco de horário (`1º ao 4º Horário`) e motivo categorizado.
- **Especificações:**
  - **Fluxo Duplo na Secretaria:** O operador escolhe entre *(a) Criar evento para o professor anexar o atestado depois* (`status = 'Pendente'`) ou *(b) Anexar o atestado agora* (`status = 'Aguardando Homologação'`).
  - **Auto-registro no Portal do Docente:** O próprio professor pode comunicar uma falta programada ou emergencial (`registrado_por = 'Docente'`).
  - **Prevenção de Duplicidade:** Valida automaticamente se o docente já possui falta registrada na mesma data e bloco de horário (`verificar_conflito_ausencia`).

### [RF02] Gestão de Substituições, Candidatura Docente e Aulas Vagas
- **Prioridade:** Essencial (*Must Have*)
- **Atores:** Secretaria, Professor
- **Descrição:** Controlar a cobertura de sala de aula para cada ausência registrada.
- **Especificações:**
  - **Alocação pela Secretaria:** Permite atribuir um professor substituto disponível ou classificar formalmente a ocorrência como `"Aula Vaga"` com justificativa.
  - **Candidatura pelo Professor no Portal do Docente:** Todas as faltas sem substituto ficam visíveis na aba `"🤝 Substituições"` dos demais professores, que podem verificar sua disponibilidade de horário e **candidatar-se/assumir a substituição com 1 clique** (`candidatar_substituicao_docente`), além de poderem liberar a substituição em caso de imprevisto (`cancelar_substituicao_docente`).

### [RF03] Controle, Pré-visualização e Homologação de Atestados Médicos
- **Prioridade:** Essencial (*Must Have*)
- **Atores:** Professor, Secretaria, Coordenador Acadêmico
- **Descrição:** Gerenciar o upload, armazenamento seguro, visualização embutida e validação de atestados e documentos comprobatórios.
- **Especificações:**
  - Upload de arquivos `.pdf`, `.png`, `.jpg`, `.jpeg` no bucket `atestados` do Supabase Storage com sanitização automática do nome do arquivo (`sanitizar_nome_arquivo`).
  - Pré-visualização embutida na tela (`st.image` e `<iframe>` para PDF) na aba `"✅ Homologação"` da Secretaria.
  - Fluxo de **Aprovação** (`status = 'Aprovada'`, `comprovada = True`) ou **Recusa com Justificativa Obrigatória** (insere tag `[Recusa da Secretaria: ...]`, limpa o anexo inválido e devolve ao professor como `"Pendente"`).
  - Tabela de **Histórico** enxuta com 8 colunas (`Data`, `Horário`, `Professor`, `Motivo`, `Status`, `Atestado`, `NomeSubstituto`, `AulaVaga`) contendo link clicável **`📄 Ver Atestado`** e abertura do documento ao selecionar a linha.

### [RF04] Planejamento e Homologação Pedagógica de Reposição de Aulas
- **Prioridade:** Essencial (*Must Have*)
- **Atores:** Professor, Secretaria, Coordenador Acadêmico
- **Descrição:** Permitir o registro da data e horário/local propostos para reposição da aula perdida e sua avaliação pela Coordenação Acadêmica (`"✅ Homologar Reposição"` atualizando para `"Reposta"`, ou `"❌ Recusar / Solicitar Ajuste"`).

### [RF05] Dashboard de Indicadores em Tempo Real
- **Prioridade:** Essencial (*Must Have*)
- **Atores:** Coordenador Acadêmico, Administrador
- **Descrição:** Painel analítico com filtros reativos (Período, Turma e Disciplina), 5 cards de KPIs (*Total de Ausências*, *Substituições e Taxa %*, *Aulas Vagas*, *Aguardando Homologação*, *Homologadas/Repostas*) e 4 gráficos interativos Plotly (*Distribuição por Status*, *Frequência por Docente*, *Ausências por Turma/Curso* e *Frequência por Horário/Bloco*).

### [RF06] Central de Emissão de Relatórios Gerenciais (PDF Paisagem & CSV)
- **Prioridade:** Essencial (*Must Have*)
- **Atores:** Coordenador Acadêmico, Administrador
- **Descrição:** Extração sob demanda de relatórios filtrados (por tipo de relatório, período, docente, turma e status) com pré-visualização em tela, geração de **PDF Oficial em Paisagem** (`ReportLab` com `NumberedCanvas`, cabeçalho, KPIs coloridos, tabela de 8 colunas e assinaturas) e download em **CSV**.

### [RF07] Gestão de Cadastros Base (Professores, Matérias e Turmas)
- **Prioridade:** Essencial (*Must Have*)
- **Atores:** Secretaria, Administrador
- **Descrição:** Interface para cadastro, busca em tempo real, validação de duplicidade e exclusão segura (protegida contra violação de chave estrangeira) de professores, disciplinas e turmas.

### [RF08] Portal do Docente e Vínculo Inteligente de Contas
- **Prioridade:** Essencial (*Must Have*)
- **Atores:** Professor
- **Descrição:** Ambiente dedicado ao docente com vinculação de conta no cadastro ou primeiro acesso ao registro de `professores`, KPIs individuais e alertas visuais de pendências, recusas de atestado e oportunidades de substituição.

---

## 2. Regras de Negócio (RN)

| Código | Nome da Regra | Descrição Técnica |
| :---: | :--- | :--- |
| **RN01** | **Validação de Conflito de Horário** | O professor ausente não pode substituir a si mesmo, e nenhum docente pode assumir substituição se possuir falta própria ou outra substituição no mesmo dia e bloco de horário (`verificar_conflito_substituto`). |
| **RN02** | **Prazo de 48h Úteis para Atestado** | O sistema calcula os dias úteis decorridos desde a falta (`calcular_prazo_atestado`) para identificar ocorrências com mais de 48h úteis (2 dias úteis) sem comprovante. |
| **RN03** | **Dupla Homologação** | A Secretaria homologa a validade documental do atestado (`Aprovada` / `Recusada`), enquanto a Coordenação homologa a execução pedagógica da reposição (`Reposta`). |
| **RN04** | **Alertas Prioritários de Pendência** | Ausências sem substituto, sem atestado ou com atestado recusado geram banners de alerta e contadores dinâmicos nas abas operacionais. |
| **RN05** | **Conformidade e Sigilo (LGPD)** | Os links diretos dos atestados médicos ficam restritos aos fluxos operacionais autenticados, não sendo impressos nos relatórios públicos gerais. |
| **RN06** | **Integridade Referencial Histórica** | Cadastros base (`professores`, `disciplinas`, `turmas`) com ocorrências vinculadas não podem ser excluídos (`erro 23503` tratado). |
| **RN07** | **Segurança no Cadastro e Vínculo** | Todo cadastro exige confirmação dupla de senha idêntica (`Senha` e `Confirmar Senha`, mín. 6 dígitos) e sincroniza com `public.usuarios` via trigger SQL. |

---

## 3. Requisitos Não Funcionais (RNF)

| Código | Categoria | Requisito |
| :---: | :--- | :--- |
| **RNF01** | **Usabilidade e UI** | Interface em **Streamlit** com layout `wide`, abas estilo *pills* sem corte de texto e visualização embutida de documentos. |
| **RNF02** | **Banco de Dados** | **PostgreSQL 15+ (Supabase)** com chaves estrangeiras, constraints de unicidade, triggers e políticas RLS. |
| **RNF03** | **Storage em Nuvem** | **Supabase Storage** (`bucket: atestados`) com sanitização ASCII de nomes de arquivos e detecção de MIME type. |
| **RNF04** | **Produtividade** | Conclusão de lançamentos de faltas ou candidaturas de substituição em menos de **60 segundos** (redução > 50% vs. processo manual). |
| **RNF05** | **Desempenho** | Carregamento de dashboards e geração de PDF em memória (`BytesIO`) em menos de **3 segundos**. |
| **RNF06** | **Segurança e RBAC** | Autenticação oficial via **Supabase Auth**, confirmação dupla de senha e segregação estrita de telas por perfil. |

