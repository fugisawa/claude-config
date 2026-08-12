# Git Workflow

## Commit Message Format
```
<type>: <description>

<optional body>
```

Types: feat, fix, refactor, docs, test, chore, perf, ci

**Atribuição desligada, e agora as chaves existem** (11/08/2026). Em `settings.json`:
`attribution: {commit: "", pr: ""}` — a forma atual — e `includeCoAuthoredBy: false`,
que é depreciada e fica só para cobrir CLI mais antigo na outra máquina. As duas dizem
a mesma coisa, então não têm como divergir; medido no binário 2.1.228, `attribution`
vence quando definida e o `includeCoAuthoredBy` só vale na ausência dela.

Até 11/08/2026 esta linha dizia "*Attribution disabled globally via
`~/.claude/settings.json`*" e **nenhuma das duas chaves existia em lugar nenhum** — nem
no `settings.json`, nem no `settings.local.json`, nem no `~/.claude.json`. O padrão do
Claude Code é incluir o trailer, então a regra descrevia um estado que ninguém tinha
ligado: **8 dos 50 commits anteriores levaram `Co-Authored-By`, dois deles no próprio
dia 11/08**. Nada acusou, porque afirmação em prosa não é configuração — é a lição
[`referencia-declarada-sem-validador`](../../skills/learned/referencia-declarada-sem-validador.md),
e esta foi a quarta ocorrência dela em vinte e quatro horas.

Por isso a linha nomeia as chaves em vez de dizer "via settings.json": nome de chave se
confere com um `grep`, e alegação de estado não se confere com nada.

## Pull Request Workflow

When creating PRs:
1. Analyze full commit history (not just latest commit)
2. Use `git diff [base-branch]...HEAD` to see all changes
3. Draft comprehensive PR summary
4. Include test plan with TODOs
5. Push with `-u` flag if new branch

## Regras duras (cada uma custou um defeito medido)

Origem: `~/manual_estudo/decisoes/0007-git-com-duas-sessoes.md`. Valem em dobro aqui, porque
`~/.claude` e `~/dotfiles` são clones em **mais de uma máquina**.

- **`git commit <caminhos>` — nunca `git add` solto seguido de `git commit`.** O `commit`
  publica o **índice inteiro**, não o que você acabou de adicionar. Com duas sessões (ou dois
  agentes) no mesmo clone, uma faz `add` e vai redigir a mensagem enquanto a outra commita no
  intervalo, e o commit leva junto trabalho alheio. **Aconteceu quatro vezes.**
- **Encadeie verificação com `&&`, nunca com `;`.** Com `;` o comando seguinte roda mesmo
  depois do vermelho: a checagem existe, roda, imprime o erro — e não reprova nada. Seis
  variações do mesmo defeito em trinta horas.
- **O que precisa sobreviver a um clone é arquivo versionado.** `git notes` mora em
  `refs/notes/*`, que o refspec padrão do `clone` **não traz**; gancho em `.git/hooks/` não
  viaja; `~/.claude/plans/` e a memória em `projects/` (gitignorada) também não. Plano,
  diagnóstico, convenção, recado para a outra máquina: **arquivo versionado, ou não existe**.
- **Gancho é versionado em `githooks/` e se instala uma vez por clone:**
  `git config core.hooksPath githooks`. Mantenha-o em ~1s — gancho lento vira gancho
  desligado com `--no-verify` na primeira pressa. Suíte longa vai no `pre-push`.

Já registradas em `skills/learned/`, não repetir aqui:
[`git-desfazer-restaura-do-indice`](../../skills/learned/git-desfazer-restaura-do-indice.md)
(`checkout --` restaura do índice; desfazer é `git checkout HEAD -- <arquivo>`) ·
[`renomeacao-em-massa-ancorada`](../../skills/learned/renomeacao-em-massa-ancorada.md) ·
[`teste-que-chama-git-herda-o-repositorio`](../../skills/learned/teste-que-chama-git-herda-o-repositorio.md).

> For the full development process (planning, TDD, code review) before git operations,
> see [development-workflow.md](./development-workflow.md).
