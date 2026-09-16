---
description: Safely reconcile a git repo across machines — fetch-before-status, classify divergence, reconcile without losing work (nor another session's), verify against the remote
argument-hint: "[caminho do repo] (default: diretório atual)"
allowed-tools: Bash(git:*), Bash(python3:*), Read
---

# /repo-sync — sincronização segura entre máquinas, em três comandos

Reconcilia este repositório com o remoto (cenário casa↔trabalho, com mais de uma sessão
possivelmente aberta no mesmo clone) **sem perder trabalho, sem passar por cima do trabalho de
outra sessão e sem confiar num status desatualizado.**

Repo alvo: **$ARGUMENTS** (se vazio, use o diretório atual).

## O custo que esta versão existe para não repetir

Medido em 16/09/2026: um "commita e pusha" no `manual_estudo` levou **14 minutos**. O git em si
levou segundos. Cerca de 4 minutos foram guardas do projeto (regenerar derivados, gancho de
commit, gancho de push); o resto foi deliberação em passos separados — classificar, "mostrar o
plano", verificar, cada um numa chamada. A causa da divergência era anterior: duas máquinas
commitaram no mesmo dia sem sincronizar no meio. Daí as três regras desta versão:

1. **O fetch acontece no início da sessão, não no fim.** O gancho `hooks/sync-on-start.sh`
   (SessionStart) já fez `fetch` e avançou o clone quando era seguro. Se ele reportou
   "DIVERGIU" ou "à frente", rode este comando **antes de tocar em arquivo**.
2. **Três chamadas, não dez.** Levantar, reconciliar, verificar. Sem pedir confirmação quando
   não há conflito: rebase limpo e merge limpo são reversíveis (`ORIG_HEAD`, reflog por 90
   dias). Pare e mostre só em conflito real.
3. **Sem ramo de segurança.** `ORIG_HEAD` e o reflog já guardam o estado anterior, e o gancho
   `block-dangerous-git.sh` bloqueia o `branch -D` que apagaria o ramo depois — foi mais um
   passo perdido em 16/09.

## Processo

**1 · Levantar (uma chamada só).** Fetch primeiro: `git status` antes do fetch é o que produz a
"discrepância" fantasma.

```bash
git fetch --all --prune && git status --short && git rev-list --left-right --count @{u}...HEAD \
  && git log --oneline HEAD..@{u} && git log --oneline @{u}..HEAD \
  && base=$(git merge-base HEAD @{u}) \
  && comm -12 <(git diff --name-only "$base" @{u} | sort) <(git diff --name-only "$base" HEAD | sort) \
  && comm -12 <(git diff --name-only "$base" @{u} | sort) <(git status --porcelain | awk '{print $2}' | sort)
```

O `rev-list` imprime `atrás à-frente`. As duas interseções dizem, respectivamente, que arquivos
os dois lados commitaram e que arquivos o remoto toca **que estão sujos aqui**.

**2 · Reconciliar, pela tabela.** "Sujo" é `git status --porcelain --untracked-files=no` não
vazio. Arquivo sujo que você não editou nesta sessão **é de outra sessão**: nunca `stash`,
nunca `--autostash`, nunca commit dele, nunca `checkout` dele.

| Estado | Faça |
|---|---|
| 0 atrás, 0 à frente | nada; siga para o passo 3 |
| só atrás, árvore limpa | `git merge --ff-only @{u}` |
| só atrás, árvore suja | `git merge --ff-only @{u}` se o remoto não toca os sujos; senão pare e mostre |
| só à frente | `git push` |
| divergiu, árvore limpa, interseção vazia | `git rebase @{u}` e `git push` |
| divergiu, árvore limpa, interseção só de **derivados** | `git rebase -X theirs @{u}` (no rebase, *theirs* = os SEUS commits), regenere, commite `chore(sync)` só com os caminhos regenerados, `git push` |
| divergiu, árvore limpa, interseção com **fonte** | `git rebase @{u}`; em conflito, pare e mostre — não invente resolução |
| divergiu, árvore **suja de outra sessão** | commite só os seus caminhos (`git commit <caminhos>`); se o remoto não toca os sujos, `git merge --no-edit @{u}` — merge aceita árvore suja em arquivo que ele não toca, rebase não — e `git push`; se toca, pare e mostre |

Derivado é o que um comando regenera: no `manual_estudo`, índices `00-indice.md`, `ENTREGAVEIS.md`,
`pdf/.frescor.json`, `tamanho-do-material.md`, `build/*.md` gerados e os PDFs de `pdf/`. Ali o
regenerador é `python3 estudo/fechar.py`, que também recusa reescrever arquivo que já estava sujo
antes dele — é a proteção contra a outra sessão, não a contorne.

Os ganchos do projeto fazem parte do custo e não são lentidão do git: o pre-push do
`manual_estudo` roda a suíte inteira e pode levar até 10 minutos — dê esse prazo ao `git push`,
ou o timeout mata o gancho no meio e nada é publicado.

**3 · Verificar contra o servidor, não contra ref em cache.**

```bash
[ "$(git ls-remote origin -h refs/heads/$(git branch --show-current) | cut -f1)" = "$(git rev-parse HEAD)" ] \
  && echo EM_SINCRONIA || echo DIVERGE; git status --short; git rev-list --left-right --count @{u}...HEAD
```

Relate em uma linha: `HEAD` local == remoto (SHA)? O que sobrou sujo, e de quem é? → "pode fechar
a máquina" ou "falta X".

## Segurança
- Nunca descartar mudança não commitada, sua ou de outra sessão.
- Nunca `push --force` (o gancho bloqueia; `--force-with-lease` só com ok explícito do Daniel).
- Em conflito de **fonte**, pare e mostre. Conflito de **derivado** se resolve regenerando.
