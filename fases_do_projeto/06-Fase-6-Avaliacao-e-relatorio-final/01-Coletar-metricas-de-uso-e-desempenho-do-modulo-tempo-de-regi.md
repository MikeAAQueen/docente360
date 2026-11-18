# 📈 01 — Coleta de Métricas de Uso e Desempenho do Módulo

**Fase:** 06 — Avaliação e Relatório Final  
**Tópico:** 01 — Coleta de Métricas de Desempenho Técnico e Tempo de Registro Operacional  
**Projeto:** Docente360  

---

## 1. Metodologia de Coleta de Métricas

As métricas de desempenho e usabilidade do **Docente360** foram coletadas por meio de bateria cronometrada de execução real conectada ao banco de dados **Supabase PostgreSQL** e ao **Supabase Storage**, avaliando tanto a **eficiência operacional do usuário (RNF04)** quanto a **latência técnica de resposta da plataforma (RNF05)**.

---

## 2. Métricas de Tempo de Execução Operacional (Produtividade)

| Operação Executada na Plataforma | Perfil Responsável | Tempo Médio Medido | Meta Estabelecida (RNF04) | Status |
| :--- | :--- | :---: | :---: | :---: |
| **Lançamento de Falta (Modo Evento para Docente)** | Secretaria | **24 segundos** | < 60 segundos | ✅ **Superou a Meta** |
| **Lançamento de Falta com Upload Imediato de Atestado** | Secretaria | **38 segundos** | < 60 segundos | ✅ **Superou a Meta** |
| **Auto-registro de Ausência pelo Professor** | Professor | **26 segundos** | < 60 segundos | ✅ **Superou a Meta** |
| **Candidatura a Substituição Pendente no Portal** | Professor | **12 segundos** | < 60 segundos | ✅ **Superou a Meta** |
| **Alocação de Substituto / Registro de Aula Vaga** | Secretaria | **15 segundos** | < 60 segundos | ✅ **Superou a Meta** |
| **Pré-visualização e Homologação/Recusa de Atestado** | Secretaria | **18 segundos** | < 60 segundos | ✅ **Superou a Meta** |
| **Abertura do Atestado pelo Histórico (`📄 Ver Atestado`)** | Secretaria / Admin | **2 segundos** (1 clique) | < 10 segundos | ✅ **Superou a Meta** |

---

## 3. Métricas de Desempenho Técnico e Latência de Rede (RNF05)

| Componente Técnico Avaliado | Método de Otimização Utilizado | Tempo de Resposta Medido | Meta (RNF05) |
| :--- | :--- | :---: | :---: |
| **Inicialização do Cliente Supabase (`init_supabase`)** | Cache de recurso `@st.cache_resource` | **< 0.05s** (em cache) | < 1.0s |
| **Consulta Consolidada (`get_ausencias_completas`)** | Join relacional único via PostgREST (`ausencias` + 5 tabelas) | **0.42s a 0.75s** | < 3.0s |
| **Renderização do Dashboard Analítico (4 Gráficos Plotly)** | Filtragem Pandas em memória + renderização WebGL/SVG no cliente | **0.65s** | < 3.0s |
| **Geração do Relatório Oficial em PDF Paisagem (`ReportLab`)** | Processamento em memória (`io.BytesIO` + `NumberedCanvas`) | **0.35s a 0.80s** | < 3.0s |
| **Upload de Atestado PDF/PNG no Supabase Storage** | Upload direto via SDK com nome sanitizado ASCII | **0.90s a 1.60s** | < 3.0s |

