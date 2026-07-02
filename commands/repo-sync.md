---
description: Safely reconcile a git repo across machines — fetch-before-status, classify divergence, reconcile without losing work, verify against the remote
argument-hint: "[caminho do repo] (default: diretório atual)"
allowed-tools: Bash(git:*), Read
---

# /repo-sync — sincronização segura entre máquinas

Reconcilia este repositório com o remoto (cenário casa↔trabalho) **sem perder trabalho e sem confiar num status desatualizado.**

Repo alvo: **$ARGUMENTS** (se vazio, use o diretório atual).

## Processo

1. **Identificar.** `git -C <repo> remote -v` e `git -C <repo> branch --show-current`. Se não for repositório git, pare e avise.

2. **Fetch ANTES de tudo.** `git -C <repo> fetch --all --prune`. O `git status` **não é confiável antes do fetch** — esse é o erro clássico que gera "discrepância" fantasma.

3. **Classificar (após o fetch):**
   - Working tree: limpo? modificações não commitadas? arquivos não rastreados?
   - vs upstream: `git -C <repo> rev-list --left-right --count @{u}...HEAD` → atrás / à frente / divergiu / em sincronia.

4. **Reconciliar — mostre o plano ANTES de executar:**
   - **Mudanças locais não commitadas:** commit (mensagem convencional) ou `stash` — pergunte qual; **nunca descarte**.
   - **Só atrás:** `git pull --ff-only`.
   - **Só à frente:** `git push`.
   - **Divergiu:** `git pull --rebase` (preferido) reaplicando seus commits sobre o remoto; resolva conflitos com cuidado e **mostre-os**. Merge só se rebase não couber.
   - **Nunca** `push --force` sem meu "ok" explícito.

5. **Verificar definitivamente.** `git -C <repo> ls-remote origin -h refs/heads/<branch>` e compare o SHA com o `HEAD` local — consulta o servidor de verdade, não um ref em cache (o teste que evita a falsa "discrepância"). Confirme working tree limpo, incluindo não rastreados.

6. **Relatar.** Estado final em uma linha clara: em sincronia? `HEAD` local == remoto (SHA)? algo pendente? → "pode fechar a máquina" ou "falta X".

## Segurança
- Nunca descartar mudanças não commitadas sem confirmar.
- Nunca `push --force` sem ok.
- Em conflito, **pare e mostre** — não invente resolução.
