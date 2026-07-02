# Instruções globais

- Avalie a possibilidade do uso de agentes, de servidores MCP e de ferramentas sempre que uma tarefa parecer complexa.
- Na dúvida sobre qual skill/agente/comando usar — ou quando acervos colidirem — consulte o router `/ask-daniel`.
- Regras detalhadas (workflow, estilo de código, testes, segurança, git) vivem em `rules/common/` e são carregadas automaticamente; não as duplique aqui.
- Stack real desta máquina: **uv + pyenv + bun** (sem conda/nvm). No Ubuntu, `bat`=`batcat` e `fd`=`fdfind`.

## Sobre este diretório (`~/.claude` é um repo git)

- Config versionada com `.gitignore` em **whitelist**: nada entra no git sem liberação explícita. Segredos (`.credentials.json`), `history.jsonl`, `projects/` (transcripts + memória) e caches ficam de fora por design — ao criar arquivo que deva ser versionado, adicione a exceção no `.gitignore`.
- `vendor/mattpocock-skills` é submodule; skills de terceiros entram por **symlink relativo** em `skills/`. Exceção: `skills/diagnosing-bugs` é cópia adaptada (user-invoked) e não acompanha o submodule.
- Ao adicionar/renomear/remover skill user-reachable, atualize o router `skills/ask-daniel/SKILL.md` — um router desatualizado mente.
