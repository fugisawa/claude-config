# continuous-learning-v2 (runtime do hook — não é skill invocável)

Cópia de `plugins/marketplaces/ecc/skills/continuous-learning-v2/` (v2.1.0), criada em
11/08/2026. **Sem `SKILL.md` de propósito**, pelo mesmo motivo do v1 ao lado: aqui vive só
o runtime que os hooks do `settings.json` chamam, e um `SKILL.md` faria o acervo registrar
uma segunda definição.

## Por que copiado, e não pelo plugin

O plugin ECC estava declarado como habilitado no `settings.json` sob o id
`everything-claude-code@everything-claude-code` — **marketplace que não existe**: ele foi
renomeado para `ecc` lá em cima e a entrada nunca acompanhou. Resultado: `true` no arquivo,
nada carregado, silenciosamente, desde a renomeação.

Habilitar o plugin de verdade (`ecc@ecc`) traria 281 skills e **17 colisões reais de
`name:`** contra as 1.014 já carregadas — e nome duplicado deixa indefinido qual definição
roda. O custo não paga: o que se queria daqui era o observador, não o catálogo.

## O que fica de fora, e é decisão consciente

Os comandos `/instinct-status`, `/evolve`, `/promote`, `/instinct-export` e `/instinct-import`
vêm do plugin e **não existem** nesta instalação. Para inspecionar os instintos à mão:

    python3 ~/.claude/skills/continuous-learning-v2/scripts/instinct-cli.py --help

## O v1 continua, e não é redundância

O v1 (ao lado, hook `Stop`) escreve **lição em prosa** em `~/.claude/skills/learned/`, que é
**versionado** — 26 arquivos, todos rastreados, e atravessam o `git clone` para a outra
máquina. O v2 escreve **instinto com pontuação de confiança** em
`~/.local/share/ecc-homunculus/`, que **está fora do repositório e não atravessa**.

São unidades diferentes em destinos diferentes. O v2 não substitui o v1; a alegação do ECC
de que é "strict superset" é verdadeira quanto ao mecanismo e falsa quanto ao que sobrevive
a um clone — que é a regra que este acervo aplica desde o `git notes`.

Ao atualizar o marketplace, re-copiar `hooks/`, `scripts/`, `agents/` e `config.json` se
mudarem.
