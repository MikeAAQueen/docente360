# 📊 04 — Criação do Dashboard do Coordenador com Indicadores e Filtros

**Fase:** 03 — Desenvolvimento do Módulo  
**Tópico:** 04 — Dashboard Analítico da Coordenação Acadêmica com Indicadores em Tempo Real e Filtros Reativos  
**Projeto:** Docente360  

---

## 1. Estrutura do Dashboard Analítico ([`views/coordenador.py`](file:///d:/Projects/docente360/views/coordenador.py))

O painel analítico da Coordenação Acadêmica (**RF05**) foi implementado na Aba 1 (`📊 Dashboard`) de [`views/coordenador.py`](file:///d:/Projects/docente360/views/coordenador.py#L25-L125) utilizando **Pandas** para agregação instantânea em memória e **Plotly Express** para visualização interativa.

---

## 2. Filtros Reativos Combinados

No topo do Dashboard, o Coordenador dispõe de três seletores sincronizados que recalculam todos os KPIs e gráficos em tempo real:
1. **`📅 Período de Análise`:** *Todo o Histórico*, *Mês Atual*, *Últimos 30 Dias* ou *Últimos 7 Dias*.
2. **`🎓 Filtrar por Turma`:** Permite isolar uma turma/curso específico ou analisar todas as turmas da instituição.
3. **`📖 Filtrar por Disciplina`:** Permite isolar uma matéria específica ou visualizar toda a grade curricular.

---

## 3. Cards de Indicadores-Chave de Desempenho (KPIs)

Cinco métricas executivas são apresentadas em cards lado a lado (`st.columns(5)`):
1. **Total de Ausências:** Volume total de faltas no recorte selecionado.
2. **Substituições (com Taxa % de Cobertura):** Quantidade de aulas que receberam professor substituto (por alocação da Secretaria ou candidatura no Portal do Docente) e o percentual sobre o total de ausências.
3. **Aulas Vagas:** Total de ocorrências em que a turma ficou sem cobertura docente (`delta_color="inverse"`).
4. **Aguardando Homologação:** Quantidade de atestados e propostas de reposição pendentes de validação.
5. **Homologadas / Repostas:** Total de ocorrências já regularizadas e aprovadas (`status IN ('Aprovada', 'Reposta')`).

---

## 4. Gráficos Interativos Plotly e Paleta Semântica

Todos os gráficos utilizam um mapeamento semântico consistente de cores (`color_discrete_map`):
- **Verde (`#16A34A`):** `Aprovada` / `Reposta`
- **Azul Royal (`#2563EB`):** `Substituída`
- **Laranja (`#D97706`):** `Aguardando Homologação`
- **Amarelo Escuro (`#CA8A04`):** `Pendente`
- **Vermelho (`#DC2626`):** `Aula Vaga`

### Os 4 Gráficos Renderizados:
1. **Distribuição das Ocorrências por Status (`px.pie` com `hole=0.35`):** Gráfico de rosca exibindo a proporção percentual de cada status operacional.
2. **Frequência de Ausências por Docente (`px.bar`):** Gráfico de barras empilhadas por status identificando os professores com maior volume de faltas.
3. **Ausências por Turma e Curso (`px.bar`):** Identifica visualmente as turmas mais impactadas por ausências e aulas vagas no período.
4. **Frequência por Horário / Bloco de Aula (`px.bar`):** Analisa a concentração de faltas entre o `1º Horário` e o `4º Horário`.

