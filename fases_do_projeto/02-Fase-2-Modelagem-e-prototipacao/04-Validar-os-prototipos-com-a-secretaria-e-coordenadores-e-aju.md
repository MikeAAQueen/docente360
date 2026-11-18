# 🔍 04 — Validação Técnica dos Protótipos e Ajustes de Usabilidade Aplicados

**Fase:** 02 — Modelagem e Prototipação  
**Tópico:** 04 — Validação de Usabilidade por Simulação de Perfis e Refinamento das Telas  
**Projeto:** Docente360  

---

## 1. Abordagem de Validação dos Protótipos

> [!NOTE]
> **Nota Metodológica:** Conforme diretriz do projeto, **não foram realizadas sessões de entrevista presencial em faculdade**. A validação dos protótipos foi executada por meio de **inspeção heurística de usabilidade (Heurísticas de Nielsen)** e **simulação prática dos fluxos operacionais** para cada um dos 4 perfis (**Secretaria**, **Professor**, **Coordenador Acadêmico** e **Administrador**).

Essa validação iterativa permitiu identificar oportunidades reais de melhoria na experiência de uso e incorporá-las diretamente às telas definitivas do sistema.

---

## 2. Ajustes e Evoluções Aplicados a Partir da Validação dos Protótipos

| Item Validado no Protótipo | Oportunidade de Melhoria Identificada | Ajuste Aplicado na Interface Final |
| :--- | :--- | :--- |
| **1. Cadastro de Conta (`views/login.py`)** | Risco de erro de digitação ao criar a senha de acesso institucional e dificuldade em conectar o login a um professor já existente. | • Adicionados **dois campos de senha lado a lado** (`Senha` e `Confirmar Senha`) com validação de igualdade.<br>• Adicionado seletor para vincular a conta diretamente a um professor pré-cadastrado pela Secretaria. |
| **2. Lançamento de Falta pela Secretaria (`views/secretaria.py`)** | Em alguns casos a Secretaria já recebe o atestado no ato do aviso; em outros, o professor só enviará o atestado dias depois. | • Criado o **Alternador de Fluxo Duplo** no topo do formulário: *(a) Criar evento para o professor anexar depois* ou *(b) A Secretaria anexa o atestado agora*. |
| **3. Homologação e Recusa de Atestados (`views/secretaria.py` & `views/professor.py`)** | Necessidade de visualizar o PDF sem sair da tela e de orientar o professor quando um atestado for recusado. | • Adicionado preview embutido (`<iframe>` / `st.image`) na aba `✅ Homologação`.<br>• Criado popover `❌ Não Aprovar / Recusar` com justificativa obrigatória que devolve a falta para o professor com alerta vermelho explicativo. |
| **4. Tabela de Histórico da Secretaria (`views/secretaria.py`)** | O protótipo inicial exibia todas as colunas técnicas do DataFrame (IDs, flags internas, URLs brutas), dificultando a leitura rápida. | • Tabela refinada para exibir **apenas as 8 colunas essenciais**: `Data`, `Horário`, `Professor`, `Motivo`, `Status`, `Atestado`, `NomeSubstituto` e `AulaVaga`.<br>• Coluna `Atestado` transformada em botão clicável **`📄 Ver Atestado`** (`LinkColumn`) + visualizador embutido ao selecionar a linha. |
| **5. Alocação de Substitutos (`views/professor.py` & `views/secretaria.py`)** | Depender exclusivamente da Secretaria para procurar substitutos atrasava a cobertura das turmas. | • Criado o **Mural de Substituições Pendentes** na aba `🤝 Substituições` do Portal do Docente, onde qualquer professor disponível vê as faltas abertas, confere o badge `🟢 Horário livre na sua agenda` e se candidata com 1 clique. |
| **6. Barra de Abas do Streamlit (`components/styles.py`)** | O componente padrão de abas do Streamlit cortava textos longos com setas de rolagem horizontal. | • Aplicado CSS customizado transformando as abas em *pills* responsivos com `flex-wrap: wrap` e destaque visual em azul royal (`#1E40AF`) para a aba ativa. |

---

## 3. Conclusão da Fase de Modelagem e Prototipação

Com o modelo relacional de 7 tabelas consolidado em [`banco_dados.sql`](file:///d:/Projects/docente360/banco_dados.sql) e os protótipos refinados para os 4 perfis de usuário, a arquitetura atingiu maturidade completa para a construção dos módulos na **Fase 3**.

