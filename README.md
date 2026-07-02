# claude-config

Configuração global versionada do Claude Code (`~/.claude`): skills, agentes, comandos, regras, hooks e skills vendored de terceiros.

## Segurança: whitelist-first

O `.gitignore` ignora tudo (`/*`) e libera item a item. **Nunca entram no git**: `.credentials.json`, `history.jsonl`, `projects/` (transcripts de sessão + memória persistente), `sessions/`, caches, e `skills/notebooklm/{data,.venv}` (perfil de navegador com sessão autenticada). Arquivo novo é ignorado por padrão até ganhar exceção explícita.

## Estrutura

| Caminho | Conteúdo |
|---|---|
| `settings.json` | modelo, plugins/marketplaces, statusline, hooks, effort |
| `rules/common/` | regras globais: dev workflow, coding style, testing, security, git, agents, performance |
| `agents/` | subagentes — curados na raiz (flat); packs de terceiros namespaced em subdirs (`engineering/`, `design/`, …) |
| `commands/` | slash-commands próprios (`/ultraplan`, `/repo-sync`, `/commit`, …) |
| `skills/` | skills próprias (forecasting, streamlit, concurso, LifeOS, …) + symlinks para `vendor/` + router `/ask-daniel` |
| `hooks/` | `block-dangerous-git.sh` (PreToolUse) |
| `vendor/mattpocock-skills` | submodule — adoção seletiva de [mattpocock/skills](https://github.com/mattpocock/skills) |
| `skills/notebooklm` | submodule — [notebooklm-skill](https://github.com/PleasePrompto/notebooklm-skill); `data/` (sessão autenticada) e `.venv/` são locais, nunca versionados |

## Router de acervo

`/ask-daniel` (`skills/ask-daniel/SKILL.md`) mapeia qual skill/agente/comando usar em cada situação e a precedência quando os 4+ acervos (próprios, superpowers, ECC, nativos, vendored) colidem. Manter em dia ao mexer nas skills.

**Manuais de uso**: [`docs/manual-grill-e-router.md`](docs/manual-grill-e-router.md) (grill, CONTEXT.md/ADRs, fluxo ideia→código, router) · [`docs/manual-concurso.md`](docs/manual-concurso.md) (estrategista-concurso × concurso-prep, loop semanal, check-in, mapa web↔CLI).

## Guardrail git (hook)

`hooks/block-dangerous-git.sh` bloqueia `reset --hard`, `clean -f*`, `branch -D`, `checkout .`, `restore .` e `push --force/-f`. **Deliberadamente não bloqueia** `git push` normal nem `--force-with-lease` — o fluxo (vsync, "commita e pusha") depende de push pelo agente.

## Skills vendored

```bash
git -C ~/.claude/vendor/mattpocock-skills pull   # symlinks acompanham
```

Instaladas por symlink relativo: `grilling`, `grill-me`, `grill-with-docs`, `domain-modeling`, `codebase-design`, `writing-great-skills`, `teach`. Exceção: `skills/diagnosing-bugs` é **cópia adaptada** (virou user-invoked para não colidir com `superpowers:systematic-debugging`) — não acompanha o `pull`; reconciliar à mão se o upstream mudar.

## Restaurar em outra máquina

```bash
mv ~/.claude ~/.claude.bak 2>/dev/null   # se existir
git clone --recurse-submodules https://github.com/fugisawa/claude-config.git ~/.claude
claude   # login recria .credentials.json; plugins reinstalam a partir do settings.json
```

Memória persistente (`projects/`) e credenciais são por máquina — não viajam pelo repo.

**Dependência externa:** as skills do LifeOS (`obsidian-note`, `vault-search`, `vault-review`, `daily-capture`) são symlinks absolutos para `~/Documents/LifeOS/.claude/skills/` — resolvem depois de clonar o vault (repo privado `lifeos`) nesse caminho.

## Relação com o pendrive claude-toolkit

Este repo passa a ser a fonte natural de sync da config global entre máquinas; o pendrive `190E-5A26` segue como espelho offline (regenerar o tarball após sincronizar, conforme convenção do toolkit).
