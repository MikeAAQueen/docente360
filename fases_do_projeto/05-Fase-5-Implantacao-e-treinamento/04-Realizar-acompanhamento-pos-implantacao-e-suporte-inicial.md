# 🛡️ 04 — Acompanhamento Pós-Implantação e Guia de Suporte Inicial

**Fase:** 05 — Implantação e Treinamento  
**Tópico:** 04 — Plano de Acompanhamento Pós-Implantação, Manutenção Preventiva e Troubleshooting  
**Projeto:** Docente360  

---

## 1. Rotina de Acompanhamento Pós-Implantação

Para garantir alta disponibilidade e integridade contínua após a entrada em operação do **Docente360**, foram estabelecidas as seguintes práticas de monitoramento:

1. **Auditoria Semanal pelo Painel do Administrador (`views/admin.py`):**
   - Conferência da aba **`👥 Equipe`** para verificar novos usuários sincronizados na tabela `usuarios` e seus respectivos perfis.
   - Acompanhamento da aba **`📊 Métricas`** para monitorar o crescimento da base de docentes, turmas e ocorrências.
2. **Monitoramento de Armazenamento (`Supabase Storage`):**
   - Acompanhamento periódico do volume de arquivos no bucket `atestados` pelo painel do Supabase Cloud.

---

## 2. Guia Rápido de Solução de Problemas (Troubleshooting FAQ)

| Sintoma / Mensagem na Tela | Causa Provável | Solução Recomendada |
| :--- | :--- | :--- |
| **`Credenciais do Supabase ausentes...`** | Arquivo `.env` não encontrado ou variáveis `SUPABASE_URL` / `SUPABASE_KEY` vazias. | Verifique se o arquivo `.env` está na raiz `d:\Projects\docente360\.env` com as chaves válidas do projeto Supabase. |
| **`E-mail ainda não confirmado...`** ao tentar fazer login | A opção *Confirm email* está ativa no painel do Supabase Auth e o link enviado por e-mail não foi clicado. | Confirme o link na caixa de entrada do e-mail ou desative *Confirm email* em *Authentication → Providers → Email* no painel do Supabase. |
| **`O bucket de armazenamento 'atestados' ainda não foi criado...`** | O bloco final do script `banco_dados.sql` referente ao `storage.buckets` não foi executado. | Execute a seção 8 do arquivo [`banco_dados.sql`](file:///d:/Projects/docente360/banco_dados.sql#L180-L205) no SQL Editor do Supabase para criar o bucket `atestados` como público. |
| **`Não é possível remover este docente/matéria/turma: existem ausências vinculadas`** | Comportamento esperado de proteção de integridade referencial (**RN06**). | O sistema protege o histórico contra perda de dados. Mantenha o cadastro base para preservar os relatórios históricos. |
| **`Conflito de Horário (RN01)...`** ao tentar se candidatar ou alocar substituto | O professor selecionado já possui falta própria ou outra substituição confirmada na mesma data e bloco de horário. | Escolha outro docente que esteja com `🟢 Horário livre na sua agenda` naquele bloco de horário. |

