# 📄 05 — Implementação da Geração de Relatórios em PDF e CSV

**Fase:** 03 — Desenvolvimento do Módulo  
**Tópico:** 05 — Motor de Geração de Relatórios Gerenciais em PDF (Paisagem) e Planilhas CSV  
**Projeto:** Docente360  

---

## 1. Central de Emissão de Relatórios ([`views/coordenador.py`](file:///d:/Projects/docente360/views/coordenador.py))

Na Aba 3 (`📄 Relatórios`) do painel da Coordenação Acadêmica (**RF06**), foi desenvolvida uma central completa de filtragem, pré-visualização e exportação documental:

### 1.1 Parâmetros de Filtragem Disponíveis
- **Tipo de Relatório:**
  - `📊 Relatório Consolidado Geral (Todas as Ausências & Tratativas)`
  - `⚠️ Relatório de Aulas Vagas & Pendências de Reposição`
  - `✅ Relatório de Reposições Homologadas & Concluídas`
  - `👨‍🏫 Relatório Individual por Docente`
- **Período Temporal:** *Todo o Histórico*, *Mês Atual*, *Últimos 30 Dias* ou *Intervalo Personalizado* (com seletores de `Data Inicial` e `Data Final`).
- **Filtros Específicos:** *Docente*, *Turma* e *Status Operacional*.

Antes do download, a tela apresenta 4 indicadores-resumo do filtro aplicado e uma tabela interativa de pré-visualização.

---

## 2. Arquitetura do Gerador de PDF Oficial ([`utils/pdf_generator.py`](file:///d:/Projects/docente360/utils/pdf_generator.py))

O módulo [`utils/pdf_generator.py`](file:///d:/Projects/docente360/utils/pdf_generator.py) foi construído com a biblioteca **ReportLab (`reportlab.platypus`)**, gerando o arquivo inteiramente em memória via `io.BytesIO` (sem escrita temporária em disco):

### 2.1 Estrutura Visual do Documento PDF (Formato Paisagem / *Landscape*)
1. **Cabeçalho Institucional:**
   - Título da plataforma, subtítulo dinâmico conforme o tipo de relatório selecionado, data/hora exata da extração, nome e cargo do coordenador emissor (`emitido_por`) e resumo de todos os filtros aplicados.
2. **Quadro Executivo de 5 KPIs Coloridos:**
   - Tabela superior com fundo colorido institucional destacando: *Total de Ausências* (`#1E3A8A`), *Substituições e Taxa %* (`#2563EB`), *Aulas Vagas* (`#DC2626`), *Reposições Concluídas* (`#16A34A`) e *Pendências Operacionais* (`#D97706`).
3. **Tabela Analítica de Ocorrências (8 Colunas, 720pt):**
   - Colunas diagramadas com quebra automática de texto (`Paragraph`) e repetição de cabeçalho a cada nova página (`repeatRows=1`): *Data/Horário*, *Docente Ausente*, *Disciplina & Turma*, *Motivo Informado*, *Tratativa Operacional*, *Status* (com cor semântica), *Reposição* e *Atestado*.
4. **Bloco Duplo de Assinaturas Institucionais (`KeepTogether`):**
   - Campos formais de homologação para a **Coordenação Acadêmica / Direção Pedagógica** e para a **Secretaria Geral e Acadêmica**.
5. **Numeração Dinâmica de Páginas (`NumberedCanvas`):**
   - Subclasse de `canvas.Canvas` que realiza dupla passagem em memória para estampar no rodapé de todas as folhas a linha divisória institucional e a contagem exata **`Página X de Y`**.

---

## 3. Exportação Tabular em CSV

Para auditorias administrativas ou importação em softwares de folha/BI, a central disponibiliza ao lado do botão de PDF o download imediato do DataFrame filtrado em formato **`.csv` codificado em UTF-8**.

