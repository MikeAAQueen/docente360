# 👥 02 — Testes de Usabilidade por Simulação de Perfis Operacionais

**Fase:** 04 — Testes e Validação  
**Tópico:** 02 — Testes de Usabilidade nos Fluxos da Secretaria, Coordenação Acadêmica e Docentes  
**Projeto:** Docente360  

---

## 1. Metodologia dos Testes de Usabilidade

> [!NOTE]
> **Nota Metodológica:** Como **não foram realizadas entrevistas ou sessões presenciais em uma faculdade**, os testes de usabilidade foram conduzidos por meio de **simulação estruturada de cenários ponta a ponta (*Role-Playing Testing*)**, utilizando contas reais para cada perfil e o recurso de **Navegação Master** do Administrador para cronometrar e avaliar a fluidez das tarefas.

Foram avaliados três critérios principais em cada tarefa:
1. **Completude:** Capacidade de concluir a tarefa sem erros ou dúvidas de navegação.
2. **Eficiência Temporal (RNF04):** Conclusão dos fluxos operacionais em menos de **60 segundos**.
3. **Clareza Visual (RNF01):** Legibilidade das tabelas, feedbacks de confirmação/erro e acesso direto aos documentos anexos.

---

## 2. Cenários de Usabilidade Simulados e Resultados

| Cenário | Perfil Simulado | Tarefa Executada na Interface | Tempo Médio Aferido | Avaliação de Usabilidade |
| :---: | :--- | :--- | :---: | :--- |
| **CU01** | **Todos os Perfis** | Criar nova conta na aba `📝 Criar Nova Conta de Usuário` preenchendo os dois campos de senha (`Senha` e `Confirmar Senha`). | **~22s** | Layout em duas colunas para confirmação de senha evita erros de digitação e fornece feedback imediato. |
| **CU02** | **Secretaria** | Lançar uma falta na aba `📌 Lançamento` gerando um evento pendente para o professor anexar o atestado posteriormente. | **~28s** | Muito abaixo da meta de 60s (RNF04). O rádio de escolha do fluxo duplo deixa claro o comportamento do sistema. |
| **CU03** | **Professor** | Visualizar o alerta de falta pendente no Portal do Docente, fazer upload do PDF do atestado e sugerir data de reposição. | **~35s** | O alerta no topo direciona o professor imediatamente ao formulário de envio sem precisar procurar a falta. |
| **CU04** | **Secretaria** | Acessar a aba `✅ Homologação`, pré-visualizar o PDF enviado na própria tela e aprovar (ou recusar com justificativa). | **~18s** | O `<iframe>` embutido elimina a necessidade de baixar o arquivo no computador para conferência. |
| **CU05** | **Secretaria** | Consultar o `📋 Histórico` de 8 colunas e clicar em `📄 Ver Atestado` ou selecionar a linha para abrir o documento. | **~5s** | A redução para apenas 8 colunas essenciais tornou a leitura limpa e o acesso ao atestado instantâneo. |
| **CU06** | **Professor (Substituto)** | Acessar a aba `🤝 Substituições`, verificar o badge `🟢 Horário livre na sua agenda` e clicar em `🙋‍♂️ Candidatar-me / Assumir como Substituto`. | **~15s** | Fluxo intuitivo de 1 clique que já atualiza o nome do substituto no Histórico da Secretaria. |
| **CU07** | **Coordenador Acadêmico** | Filtrar os gráficos do `📊 Dashboard` e emitir o Relatório Oficial em PDF Paisagem na aba `📄 Relatórios`. | **~12s** | Filtros reativos sem atraso perceptível; PDF gerado pronto para impressão e assinatura. |

