# 🚀 01 — Preparação do Ambiente de Produção e Implantação do Módulo

**Fase:** 05 — Implantação e Treinamento  
**Tópico:** 01 — Preparação do Ambiente de Produção (Supabase Cloud & Streamlit) e Implantação  
**Projeto:** Docente360  

---

## 1. Arquitetura de Implantação (Deploy)

O ambiente de produção do **Docente360** é composto por:
1. **Backend Gerenciado em Nuvem (Supabase Cloud):** Banco de dados PostgreSQL 15+, serviço de autenticação Supabase Auth e bucket de armazenamento `atestados` no Supabase Storage.
2. **Servidor de Aplicação Web (Streamlit):** Execução local ou hospedada em nuvem (Streamlit Community Cloud / Render / Docker) conectada via HTTPS à API do Supabase.

---

## 2. Procedimento Passo a Passo de Implantação

### Passo 1 — Provisionamento do Banco de Dados e Storage no Supabase
1. Acesse o painel do projeto no [Supabase](https://supabase.com/) e abra o **SQL Editor**.
2. Copie todo o conteúdo do script [`banco_dados.sql`](file:///d:/Projects/docente360/banco_dados.sql) e clique em **Run**.
3. O script executa de forma idempotente (`IF NOT EXISTS` / `ON CONFLICT`):
   - Criação das 7 tabelas: `professores`, `disciplinas`, `turmas`, `ausencias`, `substituicoes`, `reposicoes_atestados` e `usuarios`.
   - Ativação das políticas de **Row Level Security (RLS)** para proteção dos dados.
   - Criação da função e trigger `on_auth_user_created` (`public.handle_new_user`) para sincronização automática de novos usuários e vínculo por e-mail com `professores`.
   - Criação automática do bucket público **`atestados`** em `storage.buckets` e de suas políticas de upload/leitura.
   - Carga inicial (*seeds*) de professores, disciplinas e turmas para operação imediata.

### Passo 2 — Configuração do Serviço de Autenticação (Supabase Auth)
1. No painel do Supabase, acesse **Authentication → Providers → Email**.
2. Para ambientes em que se deseja acesso imediato após a criação da conta na tela de cadastro, mantenha a opção **Confirm email** desativada (*off*).

### Passo 3 — Configuração das Variáveis de Ambiente e Dependências
1. Instale os pacotes listados em [`requirements.txt`](file:///d:/Projects/docente360/requirements.txt):
   ```powershell
   pip install -r requirements.txt
   ```
2. Configure as credenciais no arquivo `.env` na raiz do projeto (ou em `.streamlit/secrets.toml` no Streamlit Cloud):
   ```env
   SUPABASE_URL="https://<ID-DO-PROJETO>.supabase.co"
   SUPABASE_KEY="<ANON-PUBLIC-KEY>"
   ```

### Passo 4 — Inicialização da Aplicação
Execute o comando abaixo na raiz do projeto:
```powershell
streamlit run app.py
```
A plataforma estará disponível em `http://localhost:8501` (ou na URL pública do servidor de hospedagem).

