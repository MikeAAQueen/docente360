# 📌 01 — Desenvolvimento do Painel de Lançamento Diário de Ausências

**Fase:** 03 — Desenvolvimento do Módulo  
**Tópico:** 01 — Painel de Lançamento Diário de Ausências com Seleção de Professor, Disciplina, Turma e Horário  
**Projeto:** Docente360  

---

## 1. Visão Geral da Implementação

O módulo de lançamento diário de ausências foi implementado em [`views/secretaria.py`](file:///d:/Projects/docente360/views/secretaria.py) (Aba 1: `📌 Lançamento`) e estendido para o autoatendimento do docente em [`views/professor.py`](file:///d:/Projects/docente360/views/professor.py) (Aba 2: `📢 Comunicar Ausência`), utilizando as funções de persistência e validação de [`services/supabase_service.py`](file:///d:/Projects/docente360/services/supabase_service.py).

---

## 2. Funcionalidades Técnicas Desenvolvidas

### 2.1 Seletores Dinâmicos Sincronizados ao Banco (`professores`, `disciplinas`, `turmas`)
- O formulário carrega dinamicamente do PostgreSQL os cadastros ativos por meio de `get_professores()`, `get_disciplinas()` e `get_turmas()`.
- Caso algum cadastro novo seja necessário durante o expediente, o operador conta com a aba integrada **`📚 Cadastros`** ([`components/cadastros.py`](file:///d:/Projects/docente360/components/cadastros.py)) para adicionar docentes, matérias ou turmas sem sair do sistema.

### 2.2 Alternador de Fluxo Duplo de Atestado na Secretaria (`registrar_ausencia_secretaria`)
Antes de submeter o formulário de ausência, a Secretaria escolhe entre dois modos operacionais:
1. **`📅 Criar evento para o professor anexar o atestado depois`:**
   - Registra a ocorrência na tabela `ausencias` com `status = "Pendente"` e `registrado_por = "Secretaria"`.
   - O professor ausente recebe automaticamente um alerta em destaque ao abrir seu **Portal do Docente** para anexar o comprovante médico e propor a reposição.
2. **`📎 A Secretaria anexa o atestado agora`:**
   - Habilita no próprio formulário o componente `st.file_uploader` (para arquivos `.pdf`, `.png`, `.jpg`, `.jpeg`) e os campos opcionais de data e horário acordados para reposição.
   - Salva a falta, realiza o upload imediato no bucket `atestados` do Supabase Storage e já encaminha a ocorrência para `status = "Aguardando Homologação"`.

### 2.3 Auto-registro de Ausência pelo Docente (`registrar_ausencia_docente`)
- No **Portal do Docente**, o professor autenticado já tem seu `professor_id` identificado automaticamente na sessão.
- Ele seleciona apenas a matéria, turma, data, bloco de horário (`1º ao 4º Horário`) e motivo, podendo opcionalmente anexar o comprovante no ato (`registrado_por = "Docente"`).

### 2.4 Validação Automática contra Lançamento Duplicado (`verificar_conflito_ausencia`)
- Antes de inserir qualquer registro na tabela `ausencias`, o serviço executa `verificar_conflito_ausencia(supabase, professor_id, data_ausencia, horario)`.
- Caso o docente já possua uma ausência registrada na mesma data e bloco de horário, o sistema bloqueia a duplicidade e informa a turma e o status da ocorrência já existente (**RF01**).

