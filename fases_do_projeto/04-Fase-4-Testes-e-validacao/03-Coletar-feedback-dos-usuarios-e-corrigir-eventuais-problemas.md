# 🛠️ 03 — Registro de Feedback de Uso e Correções Aplicadas

**Fase:** 04 — Testes e Validação  
**Tópico:** 03 — Coleta de Feedback durante os Testes Práticos e Correção de Problemas Identificados  
**Projeto:** Docente360  

---

## 1. Ciclo Iterativo de Feedback e Refinamento

Durante os testes práticos de uso da plataforma **Docente360**, cada comportamento observado na interface e na integração com o Supabase foi documentado e imediatamente aprimorado no código-fonte. Abaixo estão registrados os principais pontos levantados durante os testes e as soluções implementadas:

---

## 2. Registro de Problemas e Melhorias Implementadas

### 2.1 Upload de Atestados com Acentos e Espaços no Nome do Arquivo
- **Situação Observada:** Ao anexar um PDF cujo nome continha acentos e espaços (ex: `Exercício AST11.pdf`), o Supabase Storage retornava erro `400 InvalidKey`.
- **Correção Implementada:** Criada a função `sanitizar_nome_arquivo()` em [`services/supabase_service.py`](file:///d:/Projects/docente360/services/supabase_service.py#L231-L246), que remove acentos (`NFKD`) e substitui espaços/símbolos por `_` antes do upload no bucket `atestados`.

### 2.2 Retorno Completo dos Joins Relacionais na Tabela de Histórico
- **Situação Observada:** Na consulta `get_ausencias_completas()`, o uso de uma string `select` quebrada em múltiplas linhas (`\n`) fazia a biblioteca PostgREST ignorar os relacionamentos aninhados, exibindo `-` em `Substituto` e `None` em `AtestadoURL` no Histórico.
- **Correção Implementada:** A string `query` foi reestruturada em linha contínua única em [`services/supabase_service.py`](file:///d:/Projects/docente360/services/supabase_service.py#L105-L112), restaurando 100% do carregamento de `Professor`, `NomeSubstituto`, `AulaVaga` e `AtestadoURL`.

### 2.3 Simplificação do Histórico e Visualização Clicável do Atestado
- **Feedback de Uso:** Solicitação para que a aba **`📋 Histórico`** da Secretaria exibisse apenas as 8 colunas principais (`Data`, `Horário`, `Professor`, `Motivo`, `Status`, `Atestado`, `NomeSubstituto`, `AulaVaga`) e permitisse à Secretaria clicar e ver o atestado diretamente quando já estivesse na plataforma.
- **Melhoria Implementada:** Em [`views/secretaria.py`](file:///d:/Projects/docente360/views/secretaria.py#L380-L434) e [`views/admin.py`](file:///d:/Projects/docente360/views/admin.py#L48-L98), a tabela foi filtrada para as 8 colunas exatas, a coluna `Atestado` foi configurada com `st.column_config.LinkColumn` (**`📄 Ver Atestado`**) e foi adicionada a pré-visualização embutida (`<iframe>` / `st.image`) ao selecionar qualquer linha da tabela.

### 2.4 Mural de Substituições Pendentes para Candidatura de Professores
- **Feedback de Uso:** Solicitação para que, quando a Secretaria lançasse uma falta, os demais professores pudessem visualizá-la em seu dashboard e se candidatar como substitutos.
- **Melhoria Implementada:** Criadas as funções `get_substituicoes_disponiveis_para_professor()`, `candidatar_substituicao_docente()` e `cancelar_substituicao_docente()` em [`services/supabase_service.py`](file:///d:/Projects/docente360/services/supabase_service.py#L231-L327) e o mural interativo na aba **`🤝 Substituições`** do Portal do Docente ([`views/professor.py`](file:///d:/Projects/docente360/views/professor.py#L401-L485)) com validação automática de conflito de horário (**RN01**).

### 2.5 Confirmação Dupla de Senha na Criação de Conta
- **Feedback de Uso:** Solicitação para incluir dois campos de senha no cadastro para o usuário confirmar sua senha antes de criar a conta.
- **Melhoria Implementada:** Adicionados os campos `Senha` e `Confirmar Senha` lado a lado nos três formulários de cadastro de [`views/login.py`](file:///d:/Projects/docente360/views/login.py#L71-L155), bloqueando senhas divergentes com mensagem explicativa.

