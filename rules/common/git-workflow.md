# Git Workflow

## Commit Message Format
```
<type>: <description>

<optional body>
```

Types: feat, fix, refactor, docs, test, chore, perf, ci

Note: Attribution disabled globally via ~/.claude/settings.json.

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
