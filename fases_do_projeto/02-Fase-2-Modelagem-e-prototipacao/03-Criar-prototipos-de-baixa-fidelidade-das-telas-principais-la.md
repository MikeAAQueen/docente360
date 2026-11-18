# 🎨 03 — Criação de Protótipos de Baixa Fidelidade das Telas Principais

**Fase:** 02 — Modelagem e Prototipação  
**Tópico:** 03 — Protótipos Estruturais (Wireframes) de Lançamento, Substituições, Portal do Docente e Dashboard  
**Projeto:** Docente360  

---

## 1. Diretrizes de Design dos Protótipos

Os protótipos estruturais de baixa fidelidade foram elaborados para organizar a hierarquia visual das telas antes da codificação em Streamlit, definindo:
- **Barra Lateral Fixa:** Identificação do operador logado, badge semântico do perfil, botão de logout e, para o Administrador, o seletor **Navegação Master**.
- **Navegação Principal em Abas (*Pills*):** Agrupamento lógico das tarefas de cada setor sem necessidade de recarregar páginas externas.

---

## 2. Wireframes Estruturais das Telas Principais

### 2.1 Protótipo 1 — Tela de Login e Cadastro com Confirmação Dupla de Senha (`views/login.py`)
```plaintext
+-----------------------------------------------------------------------------------+
|                                  🎓 Docente360                                    |
|          Portal Integrado de Gestão Acadêmica — Secretaria, Coordenação & Docentes|
|                                                                                   |
|   [ 🔑 Entrar no Sistema ]   [ 📝 Criar Nova Conta de Usuário (Ativa) ]          |
|  +-----------------------------------------------------------------------------+  |
|  | Perfil de Acesso *: [ Professor                                         v ] |  |
|  | (o) 🔗 Vincular a um Professor já cadastrado pela Secretaria                |  |
|  | ( ) ➕ Cadastrar novo Professor                                             |  |
|  |                                                                             |  |
|  | Selecione seu nome na lista *: [ 👨‍🏫 Carlos Andrade - carlos@escola.edu.br v]|  |
|  | Confirmar E-mail Institucional *: [ carlos@escola.edu.br                  ] |  |
|  |                                                                             |  |
|  | Crie sua Senha (mín. 6) *:          Confirme sua Senha *:                   |  |
|  | [ ********************** ]          [ ********************** ]              |  |
|  |                                                                             |  |
|  |                  [      Criar Conta e Vincular (Primary)     ]              |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

### 2.2 Protótipo 2 — Painel da Secretaria: Lançamento Duplo e Histórico Interativo (`views/secretaria.py`)
```plaintext
+-----------------------------------------------------------------------------------+
| [📌 Lançamento] [🔄 Substituições] [✅ Homologação (2)] [📑 Anexo] [📚 Cadastros] [📋 Histórico] |
+-----------------------------------------------------------------------------------+
| ABA: 📌 LANÇAMENTO DIÁRIO                                                         |
|  🩺 Fluxo de Comprovação / Atestado:                                              |
|  (o) 📅 Criar evento para o professor anexar o atestado depois                    |
|  ( ) 📎 A Secretaria anexa o atestado agora                                       |
|  +--------------------------------------+--------------------------------------+  |
|  | Docente Ausente *: [ Selecionar   v] | Data da Ausência *: [ 18/11/2026   ] |  |
|  | Disciplina *:      [ MAT101       v] | Horário / Bloco *:  [ 1º Horário   v]|  |
|  | Turma Afetada *:   [ T-ENG24      v] | Categoria Motivo:   [ Saúde        v]|  |
|  +--------------------------------------+--------------------------------------+  |
|  |           [ 💾 Criar Evento de Falta para o Professor ]                     |  |
|  +-----------------------------------------------------------------------------+  |
|                                                                                   |
| ABA: 📋 HISTÓRICO (Visão Enxuta de 8 Colunas + Visualizador de Atestado)          |
|  +------------+-------------+---------------+----------+----------+-----------------+----------------+----------+
|  | Data       | Horário     | Professor     | Motivo   | Status   | Atestado        | NomeSubstituto | AulaVaga |
|  +------------+-------------+---------------+----------+----------+-----------------+----------------+----------+
|  | 2026-11-18 | 1º Horário  | Prof. Mike    | Saúde    | Aprovada | 📄 Ver Atestado | -              | [ ]      |
|  | 2026-10-17 | 1º Horário  | Carlos Andrade| Saúde    | Substit. | -               | Mariana Lima   | [ ]      |
|  +------------+-------------+---------------+----------+----------+-----------------+----------------+----------+
|  | 👁️ Visualização do Atestado (Ao clicar/selecionar a linha):                    |
|  | [                   IFRAME / IMAGEM DO ATESTADO MÉDICO                      ]  |
+-----------------------------------------------------------------------------------+
```

### 2.3 Protótipo 3 — Portal do Docente: Mural de Substituições Pendentes (`views/professor.py`)
```plaintext
+-----------------------------------------------------------------------------------+
| [Minhas Ausências: 1] [Pendentes Atestado: 0] [Aguard. Homolog: 0] [Aprovados: 1] [Substituições Pendentes: 2] |
+-----------------------------------------------------------------------------------+
| [📋 Minhas Ausências & Atestados]  [📢 Comunicar Ausência]  [🤝 Substituições (2) - Ativa] |
+-----------------------------------------------------------------------------------+
| 🙋‍♂️ Substituições Pendentes — Candidatar-se para Substituir                       |
|  +-----------------------------------------------------------------------------+  |
|  | 📅 2026-11-18 (1º Horário) — PRG301 | Turma: T-ADS24 [🟢 Horário livre]      |  |
|  |-----------------------------------------------------------------------------|  |
|  | 👨‍🏫 Prof. Ausente: Prof. Mike        | ✅ Você está disponível neste horário |  |
|  | 📖 Disciplina: Programação Python    | Observação: [ Posso assumir a aula  ] |  |
|  | 📝 Motivo: [Problemas de Saúde]      | [ 🙋‍♂️ Candidatar-me como Substituto ] |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

### 2.4 Protótipo 4 — Painel do Coordenador: Dashboard e Relatórios PDF (`views/coordenador.py`)
```plaintext
+-----------------------------------------------------------------------------------+
| [ 📊 Dashboard (Ativa) ]      [ ✅ Homologação ]      [ 📄 Relatórios ]            |
+-----------------------------------------------------------------------------------+
| Filtros: [📅 Período: Todo o Histórico v] [🎓 Turma: Todas v] [📖 Disciplina: Todas v] |
|                                                                                   |
| [Total Ausências] [Substituições (%)] [Aulas Vagas] [Aguard. Homolog] [Repostas]  |
|                                                                                   |
| +---------------------------------------+ +-------------------------------------+ |
| |   Gráfico 1: Rosca por Status         | |   Gráfico 2: Barras por Docente     | |
| +---------------------------------------+ +-------------------------------------+ |
| +---------------------------------------+ +-------------------------------------+ |
| |   Gráfico 3: Ausências por Turma      | |   Gráfico 4: Frequência por Horário | |
| +---------------------------------------+ +-------------------------------------+ |
+-----------------------------------------------------------------------------------+
```

