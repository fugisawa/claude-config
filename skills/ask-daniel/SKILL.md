---
name: ask-daniel
description: Router do acervo do Daniel — mapeia qual skill/agente/comando usar para cada situação, e qual acervo vence quando há sobreposição.
disable-model-invocation: true
---

# Ask Daniel — router do acervo

Você não lembra de todas as skills, então consulte este mapa. Quatro acervos coexistem: **próprios** (`~/.claude/skills`, `~/.claude/commands`, `~/.claude/agents`), **superpowers** (plugin, vários auto-disparam), **ECC** (everything-claude-code), **nativos** do harness, e **mp** (vendored de mattpocock/skills em `~/.claude/vendor/mattpocock-skills`, symlinked).

## Não achou a skill? Ela pode estar arquivada, não perdida

Desde 07/08/2026 o acervo tem **duas camadas**: `skills/` é o que carrega (996) e
`skills-archive/` fica fora da árvore varrida — **295 skills que existem no disco
mas não aparecem na lista da sessão**, a custo zero de contexto. Se procurou algo
de Azure, Odoo, WordPress, Angular, n8n, Apify, three.js, makepad, fp-ts, SEO
(fora `seo-optimizer`), leilão, wiki, conductor, startup ou fal e não achou: está
lá. Consulte `docs/skills-inventory.md` — registra nome, família e o que cada uma
fazia — e traga de volta com
`uv run --with pyyaml python scripts/apply_skills_archive.py --restore <nome>`
(reinicie depois; o watcher só vê diretório que já existia no início da sessão).

**Nada foi apagado.** Arquivar em vez de apagar é o que permite podar sem medo —
e é a razão de este mapa poder ser curto sem esconder nada de você.

## Fluxo principal: ideia → código

1. **Alinhar** — `/grill-with-docs` (com codebase: entrevista + gera `CONTEXT.md` e ADRs via `/domain-modeling`) ou `/grill-me` (sem codebase). `superpowers:brainstorming` auto-dispara antes de trabalho criativo — deixe; grilling é o modo manual de stress-testar um plano já esboçado.
2. **Planejar** — `/ultraplan` (profundo: pesquisa-primeiro, seams, user stories, tracer bullets) para trabalho grande; `ecc:plan` para leve. Agente `planner` (ECC) por baixo.
3. **Implementar** — TDD é mandatório (rule `testing.md`: seams pré-acordados, anti-padrões, fatias verticais). `superpowers:test-driven-development` auto-dispara; `tdd-guide` (ECC) como agente.
4. **Revisar** — `/code-review` nativo para o diff (`ultra` para revisão multi-agente na nuvem); agente `code-reviewer` próprio para relatório dois-eixos (Standards × Spec + smells de Fowler). `/simplify` para limpeza sem caça a bugs.
5. **Verificar** — `/run` nativo (sobe o app de verdade e exercita a mudança, não só os testes); `superpowers:verification-before-completion`.
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
- **Legislação/jurisprudência/dados públicos BR**: `legislacao-br` — mapa verificado de fontes: **texto consolidado sai do `normas.leg.br` (encoding Monovigente, com path fix) e o Planalto é plano B** (funciona com UA de navegador — a entrada antiga dizendo WAF caiu em 07/08/2026). Traz `referencias/extrair-planalto.md` com os 8 modos de corromper o texto ao extrair, e a armadilha do dispositivo **vigente porém superado por norma superior** (LOTCU art. 71 diz 65 anos; a CF, 70, desde a EC 122/2022). Consulte ANTES de tentar Planalto, LexML ou JusBrasil, e sempre que for citar dispositivo legal, acórdão do TCU/STF/STJ ou publicação no DOU. Os dados vêm do MCP `mcp-brasil` (7 tools de entrada, busca BM25 sobre ~435 internas: comece por `search_tools`).
- **Apps**: `streamlit-apps` (inclui verificação visual headless).
- **Concursos**: planejamento/cronograma/check-in/métricas/replanejamento pós-edital: `estrategista-concurso` (o quê/quando/quanto — nunca conteúdo); método/conteúdo (bancas FGV×CEBRASPE, questões, Anki, discursivas, simulados): `concurso-prep`. Aulas em PDF do IGEPP → MD limpo (Obsidian) + PDF imprimível: `igepp-aula-reformat` (instância aterrissada do método genérico). Material de OUTRA origem (apostila, capítulo, norma, paper) → `pdf-to-markdown`. Montar cadernos/simulados no QConcursos (UI Elite ou automação Chrome, filtros e qualidade do lote) e extrair/ler resultado de simulado feito (screenshots de gabarito + caderno manuscrito → placar por banca, erros×confiança, divergências): `qconcursos-simulados`. Fila de estudo por disciplina (união IGEPP × QConcursos × verticalização, formato antidesânimo): `trilha-builder`. Sinais psicológicos: só nomear e proteger o dia — condução é do acervo web (kit-sobrevivencia-atipica). Manual: `~/.claude/docs/manual-concurso.md`. Aprendizado geral stateful (workspace com learning-records): `/teach`.
- **Trilhas de CARREIRA** (≠ concurso): mapa de competências de uma carreira/função — tronco comum + ramos por especialidade, construído a partir de documentos-fonte, renderizado em grafo HTML + MD do Obsidian + PDF: `trilha-carreira`, em `~/trilhas/<trilha>/`. **O discriminador é carreira × concurso, não a palavra "trilha"**: tem edital/banca/disciplina/questões → `trilha-builder`; é "o que preciso dominar para atuar como X" → `trilha-carreira`. Um mapa pode ser percorrido fora de ordem e bifurca; uma fila de concurso não pode nem deve. Publicar a trilha no site roadmap.sh (opcional, custa ~1 min de clique por nó e achata os ramos): `roadmapsh-creator`, que também serve para minerar roadmaps oficiais do roadmap.sh.
- **Documentos → PDF** (duas trilhas + uma a cunhar; decide a **densidade de design**, não o tamanho): (1) texto corrido com citações — acadêmico ABNT/APA, relatório sóbrio, apostila — → perfis pandoc `pandoc doc.md -d abnt|apa|eisvogel|docx|html` (kit: `~/.local/share/pandoc` + `~/Documents/md-export-kit/GUIA.md`; gotchas: `learned/pandoc-pdf-pipeline-gotchas`; YAML do doc vence o perfil). (2) Argumento analítico com design editorial (capa, sidebars, dataviz) p/ gestores/circulação → `briefing-designer` (personas) — NUNCA p/ cheatsheet/ficha, o workflow é pesado demais. (3) Artefatos de ESTUDO memoráveis (cheatsheet, guia rápido, ficha de revisão, aula, acessório de meta-aprendizagem) → **trilha cunhada** em `~/manual_estudo/estudo/` (MD→WeasyPrint; identidade Plex+Lora-itálico, grade Spivak, gramática de 16 elementos, formatos folha/aula/cheatsheet/ficha/**norma** (lei seca do vade mecum, gerada por `normas/`); skill de projeto `artefatos-estudo` + contratos em CONVENTIONS-ESTUDO/TYPOGRAPHY) — em sessão no manual_estudo, a skill dispara sozinha. `docx` p/ Word puro; aula IGEPP → `igepp-aula-reformat`. **PDF de terceiro → MD fiel** (marca d'água, mobília repetida, ênfase perdida, célula embaralhada): `pdf-to-markdown` — método em 7 passos + 3 scripts. **Mecânica de arquivo PDF** (formulário, merge/split, validação de integridade, extração de tabela, OCR): `pdf-processing-pro` — os 9 scripts existem e foram testados em 02/08/2026.
- **Prosa em português** (texto que o Daniel LÊ ou ENTREGA a outro humano): o padrão está sempre carregado em `rules/common/writing-style.md` — toda frase com verbo finito, rótulo com dois-pontos não substitui oração, anglicismo com substituição nomeada, calibração ao leitor por um critério só ("o leitor precisa disto para decidir o próximo passo?"), e a proibição explícita de a regra virar regra de brevidade (pedir concisão de forma cega AUMENTOU a saída medida em 28% no Sonnet 5 e 42% no Opus 4.8; comprimir frase produz o fragmento que a regra proíbe). Revisão de fechamento de qualquer artefato → agente `revisor-prosa-ptbr` (contexto limpo, ferramentas somente-leitura **de propósito**: reporta e propõe correção mínima, quem aplica é quem tem o contexto do projeto). Método de parágrafo é o do Othon Garcia: tópico frasal, unidade, ênfase, coesão referencial e sequencial — e, para reexplicação ruim, mudar o **tipo de desenvolvimento** (confronto, analogia, causa e efeito, exemplificação), não as palavras. **Em `~/manual_estudo/` a parte mecânica já roda no build**: `estudo/prosa.py` emite `W-ANGLICISMO` e `W-SIGLA-NAO-AMARRADA` como AVISO, nunca erro — estilo não bloqueia build, porque reprovar estilo com erro ensina a ignorar o validador. Discriminador entre revisores: prosa que se lê → `revisor-prosa-ptbr`; conformidade ABNT e metodologia → `abnt-academic-reviewer`; solidez do argumento e falácia → `parecerista-2-critico`; código → `code-reviewer`. **O revisor roda em Opus 5, decidido por medição** (08/08/2026): comparado ao Fable 5 em 3 documentos, cada um achava só a sua classe de defeito — Fable a morfologia, Opus a divergência de fato contra o corpus. Escolhido o Opus por assimetria (lista de checagem se instrui em cinco linhas; comportamento investigativo, não) e o perfil ganhou as duas classes; num teste de regressão contra fixtures com defeito conhecido, os **dois** modelos passaram a achar as duas. Ele **confere contra o material do projeto** — glossário, aulas, trilha —, e é daí que sai a classe de achado mais cara: em material já publicado do `~/manual_estudo` foram **cinco divergências de fato**, incluindo um par de recuperação ativa que ensinava `PDC (LRF, art. 17)` quando o art. 17 define o DOCC. Regra dura: **o revisor aponta, a fonte decide** — em 3 dos 5 a correção final não foi a proposta, e norma se confere por `legislacao-br`. Método de parágrafo lido no Othon Garcia, não de segunda mão: tópico frasal como *controle* contra digressão, o **teste do resumo** (extrair a ideia-núcleo de cada parágrafo em ordem; onde a sequência tropeça está o salto), os sete modos de desenvolver, e a definição de analogia — explicar o desconhecido pelo conhecido — como teste objetivo do "exemplo obscuro". Arreio de regressão em `~/manual_estudo/teste-revisor/rodar.py`.
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

Manutenção: ao adicionar/renomear/remover skill user-reachable, atualize este mapa — um router desatualizado mente, e mente em silêncio: até 07/08/2026 ele mandava usar `/verify`, que não existe (o nativo é `/run`), e ninguém percebeu porque router quebrado não dá erro. Antes de commitar mexida em `agents/` ou `skills/`, rode `scripts/doctor_agents.py` e `scripts/doctor_skills.py` (exit 1 = erro). Instalar skill nova: **prefira marketplace/plugin a cópia solta** — plugin é reinstalável e liga/desliga pelo `enabledPlugins` do `settings.json` versionado; cópia solta não tem nenhuma das duas, e foi assim que `skills/` chegou a 1.291 sem ninguém decidir. Atualizar vendored: `git -C ~/.claude/vendor/mattpocock-skills pull` (symlinks acompanham; `diagnosing-bugs` é cópia adaptada, não acompanha).

Manual de uso do paradigma (grill, CONTEXT.md/ADRs, fluxo ideia→código, este router): `~/.claude/docs/manual-grill-e-router.md`.
