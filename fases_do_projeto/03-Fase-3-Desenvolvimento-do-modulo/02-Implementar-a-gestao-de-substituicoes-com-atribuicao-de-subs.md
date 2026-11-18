# 🔄 02 — Implementação da Gestão de Substituições, Candidatura Docente e Aulas Vagas

**Fase:** 03 — Desenvolvimento do Módulo  
**Tópico:** 02 — Gestão de Substituições com Atribuição de Substitutos, Mural de Candidatura Docente e Classificação de Aulas Vagas  
**Projeto:** Docente360  

---

## 1. Visão Geral da Implementação

A cobertura de sala de aula (**RF02** e **RN01**) foi desenvolvida de forma colaborativa entre dois módulos conectados em tempo real ao banco de dados:
1. **Painel da Secretaria ([`views/secretaria.py`](file:///d:/Projects/docente360/views/secretaria.py#L161-L246) — Aba `🔄 Substituições`)**
2. **Portal do Docente ([`views/professor.py`](file:///d:/Projects/docente360/views/professor.py#L401-L485) — Aba `🤝 Substituições`)**

---

## 2. Fluxos Implementados

### 2.1 Alocação Direta pela Secretaria ou Registro de Aula Vaga
Na aba `🔄 Substituições` da Secretaria:
- O sistema filtra automaticamente todas as ocorrências pendentes de cobertura (`Tratativa == "Pendente de tratativa"` e `Status != "Reposta"`).
- O operador pode escolher entre:
  - **Alocar Docente Substituto:** O seletor lista os professores cadastrados, excluindo automaticamente o próprio professor titular ausente (`df_prof["id"] != detalhe["ProfessorID"]`). Ao confirmar, executa `verificar_conflito_substituto()` e grava em `substituicoes`.
  - **Marcar como Aula Vaga:** Registra `aula_vaga = True` e a justificativa operacional em `observacoes`, atualizando o status da ausência para `"Aula Vaga"`.
- Abaixo do formulário, a Secretaria conta com a tabela **`🤝 Substituições e Tratativas Já Definidas`**, consolidando todas as aulas já cobertas (seja pela Secretaria ou por candidatura de um professor).

### 2.2 Mural de Substituições Pendentes e Candidatura Docente (`candidatar_substituicao_docente`)
Para agilizar a cobertura de faltas sem depender apenas de contatos manuais da Secretaria:
- Sempre que uma falta é lançada e ainda não possui substituto nem foi classificada como Aula Vaga, ela é listada pela função `get_substituicoes_disponiveis_para_professor(supabase, professor_id)` no **Portal do Docente** de todos os demais professores.
- O topo do dashboard do professor exibe o KPI **`Substituições Pendentes`** e um alerta informando quantas aulas estão disponíveis para substituição.
- Na aba **`🤝 Substituições (N)`**:
  - Cada aula disponível exibe o professor ausente, a disciplina, a turma, a data, o horário e um badge dinâmico de disponibilidade: **`🟢 Horário livre na sua agenda`** ou **`🔴 Conflito na sua agenda`**.
  - Ao clicar em **`🙋‍♂️ Candidatar-me / Assumir como Substituto`**, o sistema grava o professor como substituto oficial daquela aula e atualiza imediatamente a coluna **`NomeSubstituto`** no Histórico da Secretaria.
  - Caso o professor substituto tenha um imprevisto posterior, ele também pode liberar a substituição (`cancelar_substituicao_docente`), devolvendo a aula para o mural de pendentes.

### 2.3 Motor de Validação de Conflito de Horário (`verificar_conflito_substituto` — RN01)
Implementado em [`services/supabase_service.py`](file:///d:/Projects/docente360/services/supabase_service.py#L438-L483), valida duas condições antes de confirmar qualquer substituição:
1. Se o professor substituto possui ausência registrada para si mesmo na mesma data e bloco de horário.
2. Se o professor substituto já está alocado para substituir outra turma na mesma data e bloco de horário.

