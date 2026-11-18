# 🧪 01 — Execução de Testes Unitários e de Integração

**Fase:** 04 — Testes e Validação  
**Tópico:** 01 — Testes Unitários e de Integração para Validar as Funcionalidades do Módulo  
**Projeto:** Docente360  

---

## 1. Escopo dos Testes Unitários e de Integração

A bateria de testes técnicos validou isoladamente as funções críticas de regras de negócio e, de forma integrada, a comunicação em tempo real entre a aplicação Python e os três serviços do **Supabase** (*Auth*, *PostgreSQL/PostgREST* e *Storage*).

---

## 2. Testes Unitários Executados

| ID | Função / Unidade Testada | Módulo | Entrada de Teste | Saída Obtida | Status |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **TU01** | `sanitizar_nome_arquivo()` | `services/supabase_service.py` | `"Exercício Atestado Médico (João).pdf"` | `"Exercicio_Atestado_Medico_Joao.pdf"` | ✅ **Passou** |
| **TU02** | `calcular_prazo_atestado()` (Dentro do prazo) | `services/supabase_service.py` | `data_ausencia = hoje`, `tem_atestado = False`, `status = "Pendente"` | `(False, 0, "🕒 No Prazo (<48h)")` | ✅ **Passou** |
| **TU03** | `calcular_prazo_atestado()` (Atraso > 48h úteis) | `services/supabase_service.py` | `data_ausencia = 5 dias úteis atrás`, `tem_atestado = False`, `status = "Pendente"` | `(True, 5, "⚠️ Atrasado (5d úteis > 48h)")` | ✅ **Passou** |
| **TU04** | `gerar_pdf_relatorio()` | `utils/pdf_generator.py` | `pd.DataFrame` com 5 ocorrências de teste e dicionário de filtros | Buffer `BytesIO` válido contendo PDF em formato Paisagem (`%PDF-1.4`) | ✅ **Passou** |
| **TU05** | Compilação de Sintaxe (`py_compile`) | Todos os 11 arquivos `.py` do projeto | `python -m py_compile app.py services/*.py views/*.py components/*.py utils/*.py` | Código de saída `0` (Zero erros de sintaxe ou importação) | ✅ **Passou** |

---

## 3. Testes de Integração com o Supabase

| ID | Integração Testada | Operação Executada | Resultado Verificado no Banco / Storage | Status |
| :---: | :--- | :--- | :--- | :---: |
| **TI01** | **Supabase Auth + Trigger SQL** | `handle_signup()` com confirmação dupla de senha | Usuário criado em `auth.users` e replicado automaticamente em `public.usuarios` com `professor_id` vinculado. | ✅ **Passou** |
| **TI02** | **Join Relacional PostgREST** | `get_ausencias_completas(supabase)` | Retorno completo em requisição única trazendo os dados de `ausencias`, `professores`, `disciplinas`, `turmas`, `substituicoes` e `reposicoes_atestados`. | ✅ **Passou** |
| **TI03** | **Supabase Storage (`atestados`)** | `anexar_atestado_reposicao()` com arquivo PDF real | Upload concluído com sucesso no bucket `atestados`, `atestado_url` gravada na tabela `reposicoes_atestados` e acessível via URL pública. | ✅ **Passou** |
| **TI04** | **Validação de Conflito de Horário (RN01)** | `verificar_conflito_ausencia()` e `verificar_conflito_substituto()` | Consultas no banco identificaram com precisão choques de data e bloco de horário, bloqueando duplicidades e substituições conflitantes. | ✅ **Passou** |
| **TI05** | **Proteção de Chave Estrangeira (RN06)** | `excluir_professor()` em docente com faltas vinculadas | Exceção `23503 (foreign_key_violation)` capturada e convertida em mensagem amigável sem queda da aplicação. | ✅ **Passou** |

