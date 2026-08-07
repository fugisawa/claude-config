# Instruções globais

- Avalie a possibilidade do uso de agentes, de servidores MCP e de ferramentas sempre que uma tarefa parecer complexa.
- Na dúvida sobre qual skill/agente/comando usar — ou quando acervos colidirem — consulte o router `/ask-daniel`.
- Regras detalhadas (workflow, estilo de código, testes, segurança, git) vivem em `rules/common/` e são carregadas automaticamente; não as duplique aqui.
- Stack real desta máquina: **uv + pyenv + bun** (sem conda/nvm). No Ubuntu, `bat`=`batcat` e `fd`=`fdfind`. Sem ImageMagick (`magick`/`convert` não existem): operações de imagem via `uv run --with pillow python`.
- **Node do sistema é 18** e vários pacotes npm exigem 20+. Contorno padrão: `bun x --bun <pacote>` (usa o runtime do Bun). Não instale nvm.

## MCPs e recursos próprios (inventário, jul/2026)

- `anki` — cria e revisa flashcards respeitando o FSRS (exige Anki aberto). `mcp-brasil` — 70 fontes públicas BR via 7 tools de entrada; comece sempre por `search_tools`. `youtube-transcript` — legendas de aula em vídeo. Detalhes e limites de cada fonte pública: skill `legislacao-br`.
- Custo/uso da sessão: `bunx ccusage` (histórico) e `ccost` (inclui estimativa de rate-limit).
- **Nunca cite dispositivo legal, artigo ou acórdão de memória** — resolva a fonte pela skill `legislacao-br` ou declare que não conferiu.
- Antes de começar projeto de forecasting/calibração, leia `~/Projects/futebol_forecast` (baseline já medido) — a skill `forecasting-calibration` explica o estado.

## Sobre este diretório (`~/.claude` é um repo git)

- Config versionada com `.gitignore` em **whitelist**: nada entra no git sem liberação explícita. Segredos (`.credentials.json`), `history.jsonl`, `projects/` (transcripts + memória) e caches ficam de fora por design — ao criar arquivo que deva ser versionado, adicione a exceção no `.gitignore`.
- `vendor/mattpocock-skills` é submodule; skills de terceiros entram por **symlink relativo** em `skills/`. Exceção: `skills/diagnosing-bugs` é cópia adaptada (user-invoked) e não acompanha o submodule.
- Ao adicionar/renomear/remover skill user-reachable, atualize o router `skills/ask-daniel/SKILL.md` — um router desatualizado mente.
- **Registro de agentes/skills:** a varredura é recursiva e a identidade vem só do campo `name:` — subpasta não esconde nada e nome duplicado deixa indefinido qual definição roda. Sempre declare `tools:` e `model:` (ausentes = todas as ferramentas e o modelo mais caro). Antes de commitar mexida em `agents/` ou `skills/`, rode `uv run --with pyyaml python scripts/doctor_agents.py`, `scripts/doctor_skills.py` e `scripts/doctor_router.py` (exit 1 = erro; o do router pega citação para skill arquivada ou agente aposentado, que não dá erro nenhum sozinha), e **reinicie o Claude Code** — o watcher só vê diretórios que existiam no início da sessão. Aposentar é **mover** para `agents-archive/` ou `_retired-*/`, nunca apagar: boa parte de `skills/` está fora do git. Detalhes, códigos de diagnóstico e histórico: `docs/manual-registro-agentes-skills.md`.
- **Skills em duas camadas (07/08/2026):** `skills/` é o que carrega (996); `skills-archive/` fica fora da árvore varrida — custo de contexto **zero** e volta com um `mv`. O que está arquivado segue documentado em `docs/skills-inventory.md`, que é a fonte da verdade: como skill de terceiro não é versionada, o arquivamento **não viaja pelo git** e a outra máquina se alinha rodando `scripts/apply_skills_archive.py` (`--restore <nome>` traz de volta). Arquivar, e não apagar, é o que permite ser agressivo sem risco.
- **Antes de instalar skill nova, prefira marketplace/plugin a cópia solta.** Plugin é reinstalável e liga/desliga pelo `enabledPlugins` do `settings.json`, que é versionado; cópia solta não tem nenhuma das duas propriedades — foi assim que `skills/` chegou a 1.291 sem ninguém decidir. Se for cópia solta mesmo assim, ela nasce sem procedência: registre no inventário.
