---
name: ask-daniel
description: Router do acervo do Daniel — mapeia qual skill/agente/comando usar para cada situação, e qual acervo vence quando há sobreposição.
disable-model-invocation: true
---

# Ask Daniel — router do acervo

Você não lembra de todas as skills, então consulte este mapa. Quatro acervos coexistem: **próprios** (`~/.claude/skills`, `~/.claude/commands`, `~/.claude/agents`), **superpowers** (plugin, vários auto-disparam), **ECC** (everything-claude-code), **nativos** do harness, e **mp** (vendored de mattpocock/skills em `~/.claude/vendor/mattpocock-skills`, symlinked).

## Fluxo principal: ideia → código

1. **Alinhar** — `/grill-with-docs` (com codebase: entrevista + gera `CONTEXT.md` e ADRs via `/domain-modeling`) ou `/grill-me` (sem codebase). `superpowers:brainstorming` auto-dispara antes de trabalho criativo — deixe; grilling é o modo manual de stress-testar um plano já esboçado.
2. **Planejar** — `/ultraplan` (profundo: pesquisa-primeiro, seams, user stories, tracer bullets) para trabalho grande; `ecc:plan` para leve. Agente `planner` (ECC) por baixo.
3. **Implementar** — TDD é mandatório (rule `testing.md`: seams pré-acordados, anti-padrões, fatias verticais). `superpowers:test-driven-development` auto-dispara; `tdd-guide` (ECC) como agente.
4. **Revisar** — `/code-review` nativo para o diff (`ultra` para revisão multi-agente na nuvem); agente `code-reviewer` próprio para relatório dois-eixos (Standards × Spec + smells de Fowler). `/simplify` para limpeza sem caça a bugs.
5. **Verificar** — `/verify` nativo (exercita o fluxo de verdade); `superpowers:verification-before-completion`.
6. **Entregar** — `/commit`, `/create-pr`; `/repo-sync` para reconciliar casa↔trabalho sem perder trabalho.

## Debug

- Bug comum: `superpowers:systematic-debugging` auto-dispara.
- Bug difícil, flaky, ou regressão de performance: **`/diagnosing-bugs`** (user-invoked) — constrói um feedback loop *red-capable* antes de qualquer hipótese. Invoque à mão; ele não dispara sozinho de propósito.

## Design e arquitetura

- Vocabulário de módulos profundos (module/interface/seam/depth/leverage/locality): `/codebase-design`.
- Glossário de domínio + ADRs: `/domain-modeling` (formatos em CONTEXT-FORMAT.md e ADR-FORMAT.md).
- Decisão arquitetural: agente `ecc:architect`; docs formais: `/create-architecture-documentation`.

## Pesquisa

- Relatório profundo multi-fonte verificado: `/deep-research` (vence `ecc:search-first` e o `research` do mp).
- Big Tech / economia política de plataformas: `bigtech-analyst`.
- Acadêmico: agente `academic-researcher`; técnico/repos: `technical-researcher`; web geral: `search-specialist`.

## Domínios do Daniel

- **Forecasting/DS**: `forecasting-calibration` (aponta para o repo real `~/Projects/futebol_forecast`, com baseline já medido — leia antes de recomeçar do zero), `senior-data-scientist`, agente `football-forecaster`; visualização: `dataviz` + `dataviz-storytelling`.
- **Legislação/jurisprudência/dados públicos BR**: `legislacao-br` — mapa verificado de fontes (o que funciona por API, o que está bloqueado por WAF, o que dá metadado mas não texto). Consulte ANTES de tentar Planalto, LexML ou JusBrasil, e sempre que for citar dispositivo legal, acórdão do TCU/STF/STJ ou publicação no DOU. Os dados vêm do MCP `mcp-brasil` (7 tools de entrada, busca BM25 sobre ~533 internas: comece por `search_tools`).
- **Apps**: `streamlit-apps` (inclui verificação visual headless).
- **Concursos**: planejamento/cronograma/check-in/métricas/replanejamento pós-edital: `estrategista-concurso` (o quê/quando/quanto — nunca conteúdo); método/conteúdo (bancas FGV×CEBRASPE, questões, Anki, discursivas, simulados): `concurso-prep`. Aulas em PDF do IGEPP → MD limpo (Obsidian) + PDF imprimível: `igepp-aula-reformat` (instância aterrissada do método genérico). Material de OUTRA origem (apostila, capítulo, norma, paper) → `pdf-to-markdown`. Montar cadernos/simulados no QConcursos (UI Elite ou automação Chrome, filtros e qualidade do lote) e extrair/ler resultado de simulado feito (screenshots de gabarito + caderno manuscrito → placar por banca, erros×confiança, divergências): `qconcursos-simulados`. Fila de estudo por disciplina (união IGEPP × QConcursos × verticalização, formato antidesânimo): `trilha-builder`. Sinais psicológicos: só nomear e proteger o dia — condução é do acervo web (kit-sobrevivencia-atipica). Manual: `~/.claude/docs/manual-concurso.md`. Aprendizado geral stateful (workspace com learning-records): `/teach`.
- **Trilhas de CARREIRA** (≠ concurso): mapa de competências de uma carreira/função — tronco comum + ramos por especialidade, construído a partir de documentos-fonte, renderizado em grafo HTML + MD do Obsidian + PDF: `trilha-carreira`, em `~/trilhas/<trilha>/`. **O discriminador é carreira × concurso, não a palavra "trilha"**: tem edital/banca/disciplina/questões → `trilha-builder`; é "o que preciso dominar para atuar como X" → `trilha-carreira`. Um mapa pode ser percorrido fora de ordem e bifurca; uma fila de concurso não pode nem deve. Publicar a trilha no site roadmap.sh (opcional, custa ~1 min de clique por nó e achata os ramos): `roadmapsh-creator`, que também serve para minerar roadmaps oficiais do roadmap.sh.
- **Documentos → PDF** (duas trilhas + uma a cunhar; decide a **densidade de design**, não o tamanho): (1) texto corrido com citações — acadêmico ABNT/APA, relatório sóbrio, apostila — → perfis pandoc `pandoc doc.md -d abnt|apa|eisvogel|docx|html` (kit: `~/.local/share/pandoc` + `~/Documents/md-export-kit/GUIA.md`; gotchas: `learned/pandoc-pdf-pipeline-gotchas`; YAML do doc vence o perfil). (2) Argumento analítico com design editorial (capa, sidebars, dataviz) p/ gestores/circulação → `briefing-designer` (personas) — NUNCA p/ cheatsheet/ficha, o workflow é pesado demais. (3) Artefatos de ESTUDO memoráveis (cheatsheet, guia rápido, ficha de revisão, aula, acessório de meta-aprendizagem) → **trilha cunhada** em `~/manual_estudo/estudo/` (MD→WeasyPrint; identidade Plex+Lora-itálico, grade Spivak, gramática de 12 elementos; skill de projeto `artefatos-estudo` + contratos em CONVENTIONS-ESTUDO/TYPOGRAPHY) — em sessão no manual_estudo, a skill dispara sozinha. `docx` p/ Word puro; aula IGEPP → `igepp-aula-reformat`. **PDF de terceiro → MD fiel** (marca d'água, mobília repetida, ênfase perdida, célula embaralhada): `pdf-to-markdown` — método em 7 passos + 3 scripts. **Mecânica de arquivo PDF** (formulário, merge/split, validação de integridade, extração de tabela, OCR): `pdf-processing-pro` — os 9 scripts existem e foram testados em 02/08/2026.
- **LifeOS/Obsidian**: `obsidian-note` (19 tipos), `vault-search`, `vault-review`, `daily-capture`, comandos `/obsidian:*`.
- **Treino**: `training-protocol`. **LLM eng**: `langchain-stack`, `claude-api`, `senior-prompt-engineer`.

## Meta (construir o próprio acervo)

- Criar/editar skills: `superpowers:writing-skills` (processo: testar antes de publicar) + `/writing-great-skills` (teoria: context load vs cognitive load, leading words, progressive disclosure, invocação). Agentes: `agent-development`.
- Configurar harness/hooks/permissões: `update-config`. Guardrail git destrutivo já ativo em `~/.claude/hooks/block-dangerous-git.sh`.
- Recorrência: `/loop`, `/schedule`; orquestração: `workflow-orchestrator` ou tool `Workflow` (exige opt-in).

## Precedência quando acervos colidem

- TDD → rule local + superpowers (auto). Não invocar dois TDDs na mesma tarefa.
- Review de diff → `/code-review` nativo; relatório estruturado dois-eixos → agente `code-reviewer`.
- Debug → superpowers auto; `/diagnosing-bugs` só à mão, para os difíceis.
- Pesquisa → `/deep-research` primeiro; agentes de pesquisa para tarefas delegadas paralelas.
- Obsidian → suíte própria (obsidian-note/vault-*) vence plugin `obsidian:*` genérico para o LifeOS.

Manutenção: ao adicionar/renomear/remover skill user-reachable, atualize este mapa — um router desatualizado mente. Atualizar vendored: `git -C ~/.claude/vendor/mattpocock-skills pull` (symlinks acompanham; `diagnosing-bugs` é cópia adaptada, não acompanha).

Manual de uso do paradigma (grill, CONTEXT.md/ADRs, fluxo ideia→código, este router): `~/.claude/docs/manual-grill-e-router.md`.
