# ✅ 04 — Documento de Especificação de Requisitos (ERS) e Validação de Escopo

**Fase:** 01 — Levantamento e Requisitos  
**Tópico:** 04 — Consolidação da Especificação de Requisitos e Matriz de Validação  
**Projeto:** Docente360  

---

## 1. Escopo Consolidado da Solução

O documento de Especificação de Requisitos de Software (ERS) consolida os módulos, atores e entregas que compõem o **Docente360**, servindo como contrato técnico para as fases seguintes de Modelagem (Fase 2), Desenvolvimento (Fase 3) e Testes (Fase 4).

---

## 2. Matriz de Permissões por Perfil de Acesso (RBAC)

| Funcionalidade / Módulo | Secretaria | Professor | Coordenador Acadêmico | Administrador |
| :--- | :---: | :---: | :---: | :---: |
| Login e Cadastro com Confirmação Dupla de Senha (**RN07**) | ✅ | ✅ | ✅ | ✅ |
| Lançamento de Ausência em Fluxo Duplo (**RF01**) | ✅ | ❌ | ❌ | ✅ *(Master)* |
| Auto-registro / Comunicação de Ausência Própria (**RF01/RF08**) | ❌ | ✅ | ❌ | ✅ *(Master)* |
| Alocação Direta de Substituto e Registro de Aula Vaga (**RF02**) | ✅ | ❌ | ❌ | ✅ *(Master)* |
| Candidatura a Substituições Pendentes no Portal (**RF02**) | ❌ | ✅ | ❌ | ✅ *(Master)* |
| Upload e Reenvio de Atestado Médico e Proposta de Reposição (**RF03/RF04**) | ✅ | ✅ | ❌ | ✅ *(Master)* |
| Homologação Documental e Recusa Comentada de Atestados (**RF03/RN03**) | ✅ | ❌ | ❌ | ✅ *(Master)* |
| Consulta ao Histórico de 8 Colunas com Atestado Clicável (**RF03**) | ✅ | ✅ *(Pessoal)* | ✅ *(Prévia)* | ✅ |
| Homologação Pedagógica de Planos de Reposição (**RF04/RN03**) | ❌ | ❌ | ✅ | ✅ *(Master)* |
| Dashboard Analítico com Filtros e 4 Gráficos Plotly (**RF05**) | ❌ | ❌ | ✅ | ✅ *(Master)* |
| Emissão de Relatórios Oficiais em PDF Paisagem e CSV (**RF06**) | ❌ | ❌ | ✅ | ✅ *(Master)* |
| Gestão de Cadastros Base: Professores, Matérias e Turmas (**RF07**) | ✅ | ❌ | ❌ | ✅ |
| Gestão de Equipe (`usuarios`) e Navegação Master Multi-Setor | ❌ | ❌ | ❌ | ✅ |

---

## 3. Matriz de Rastreabilidade (Requisitos × Artefatos do Sistema)

| Requisito | Módulo / Arquivo de Destino | Entidades do Banco Envolvidas | Critério de Validação |
| :---: | :--- | :--- | :--- |
| **RF01** | `views/secretaria.py`, `views/professor.py`, `services/supabase_service.py` | `ausencias`, `professores`, `disciplinas`, `turmas`, `reposicoes_atestados` | Registro sem duplicidade de horário e suporte ao fluxo duplo de atestado. |
| **RF02** | `views/secretaria.py`, `views/professor.py`, `services/supabase_service.py` | `substituicoes`, `ausencias`, `professores` | Alocação pela Secretaria, registro de Aula Vaga e candidatura pelo Portal do Docente sem conflito (**RN01**). |
| **RF03** | `views/secretaria.py`, `views/professor.py`, `services/supabase_service.py` | `reposicoes_atestados`, `storage.objects (atestados)` | Upload sanitizado, preview embutido, aprovação/recusa comentada e coluna clicável `📄 Ver Atestado` no Histórico. |
| **RF04** | `views/coordenador.py`, `views/professor.py`, `views/secretaria.py` | `reposicoes_atestados`, `ausencias` | Proposta de data/horário de reposição e homologação pedagógica pela Coordenação (`Reposta`). |
| **RF05** | `views/coordenador.py` | `ausencias`, `substituicoes`, `turmas`, `disciplinas` | 5 KPIs e 4 gráficos interativos Plotly respondendo aos filtros de período, turma e disciplina. |
| **RF06** | `views/coordenador.py`, `utils/pdf_generator.py` | Todas as tabelas operacionais | Exportação de PDF Paisagem com `NumberedCanvas` e planilha CSV filtrada. |
| **RF07** | `components/cadastros.py`, `services/supabase_service.py` | `professores`, `disciplinas`, `turmas` | Cadastro com validação de código/e-mail único, busca instantânea e bloqueio de exclusão com FK (**RN06**). |
| **RF08** | `views/login.py`, `views/professor.py`, `services/auth_service.py` | `usuarios`, `professores`, `auth.users` | Vínculo automático por trigger ou seleção assistida no cadastro com confirmação dupla de senha. |

---

## 4. Checklist de Validação Técnica da Fase 1

- [x] Todos os requisitos essenciais solicitados para o controle de ausências, substituições, atestados, reposições, dashboard e relatórios PDF foram formalizados.
- [x] O papel do **Professor** foi expandido com o Portal do Docente para autoatendimento e candidatura a substituições pendentes.
- [x] As regras de negócio de conflito de horário (**RN01**), prazo de 48h (**RN02**), dupla homologação (**RN03**) e integridade referencial (**RN06**) foram claramente delimitadas.
- [x] Os requisitos não funcionais de stack (**Streamlit + Supabase + ReportLab + Plotly**) foram validados para início da Fase 2 (Modelagem e Prototipação).

