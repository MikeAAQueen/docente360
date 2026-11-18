# 📑 03 — Desenvolvimento do Controle de Atestados, Homologação e Reposições

**Fase:** 03 — Desenvolvimento do Módulo  
**Tópico:** 03 — Controle de Atestados e Reposições com Upload no Supabase Storage, Pré-visualização e Dupla Homologação  
**Projeto:** Docente360  

---

## 1. Upload Seguro e Sanitização no Supabase Storage (`bucket: atestados`)

O envio de comprovantes médicos (`.pdf`, `.png`, `.jpg`, `.jpeg`) pode ser realizado tanto pelo **Professor** ([`views/professor.py`](file:///d:/Projects/docente360/views/professor.py)) quanto pela **Secretaria** ([`views/secretaria.py`](file:///d:/Projects/docente360/views/secretaria.py)) por meio da função centralizada `anexar_atestado_reposicao()` em [`services/supabase_service.py`](file:///d:/Projects/docente360/services/supabase_service.py#L249-L316):

- **Sanitização de Nomes (`sanitizar_nome_arquivo`):** Remove acentuação (`unicodedata.normalize("NFKD")`), espaços e caracteres especiais do nome original do arquivo, gerando uma chave S3 limpa no formato `{ausencia_id}_{nome_limpo}.pdf`.
- **Upsert e URL Pública:** Realiza o upload no bucket `atestados` com `content-type` apropriado, grava a URL pública em `reposicoes_atestados.atestado_url` juntamente com `data_reposicao` e `horario_reposicao`, e atualiza o status da ausência para **`"Aguardando Homologação"`**.

---

## 2. Homologação Documental e Fluxo de Devolução pela Secretaria

Na aba **`✅ Homologação (N)`** da Secretaria ([`views/secretaria.py`](file:///d:/Projects/docente360/views/secretaria.py#L248-L320)):
1. **Pré-visualização Embutida na Tela:**
   - Além do link direto para abrir/baixar o arquivo, o operador conta com o expansor `👁️ Pré-visualizar Documento na Tela`, que renderiza imagens via `st.image()` e documentos PDF via `<iframe src="{atest_url}" width="100%" height="450px">`.
2. **Aprovação (`aprovar_atestado_secretaria`):**
   - Atualiza `ausencias.status = "Aprovada"` e `reposicoes_atestados.comprovada = True`.
3. **Recusa e Devolução ao Professor (`recusar_atestado_secretaria`):**
   - Por meio de um `st.popover`, a Secretaria informa obrigatoriamente a justificativa da não aprovação (ex: *"Atestado ilegível ou data divergente"*).
   - O sistema acrescenta `[Recusa da Secretaria: <motivo>]` à ocorrência, limpa o `atestado_url` inválido, retorna o status para **`"Pendente"`** e exibe um alerta vermelho prioritário no **Portal do Docente** para que o professor envie o documento corrigido.

---

## 3. Histórico Enxuto com Abertura de Atestado em 1 Clique

Na aba **`📋 Histórico`** da Secretaria ([`views/secretaria.py`](file:///d:/Projects/docente360/views/secretaria.py#L380-L434)) e **`📋 Ocorrências`** do Administrador ([`views/admin.py`](file:///d:/Projects/docente360/views/admin.py#L48-L98)):
- A tabela foi configurada para exibir exclusivamente as **8 colunas operacionais solicitadas**:
  `Data` | `Horário` | `Professor` | `Motivo` | `Status` | `Atestado` | `NomeSubstituto` | `AulaVaga`
- **Acesso ao Atestado na Tabela:**
  - A coluna **`Atestado`** utiliza `st.column_config.LinkColumn("Atestado", display_text="📄 Ver Atestado")`: quando o atestado já está na plataforma, basta clicar em **`📄 Ver Atestado`** para abrir o PDF/imagem imediatamente.
  - Adicionalmente, ao clicar/selecionar qualquer linha da tabela (`on_select="rerun"`), o documento é renderizado logo abaixo da tabela dentro da própria plataforma.

---

## 4. Homologação Pedagógica de Reposições pela Coordenação

Na aba **`✅ Homologação`** da Coordenação Acadêmica ([`views/coordenador.py`](file:///d:/Projects/docente360/views/coordenador.py#L130-L165)):
- O Coordenador avalia a data e horário propostos para a reposição da aula, podendo consultar o atestado anexo e clicar em **`✅ Homologar Reposição`** (concluindo o status como `"Reposta"` e `comprovada = True`) ou **`❌ Recusar / Solicitar Ajuste`**.

