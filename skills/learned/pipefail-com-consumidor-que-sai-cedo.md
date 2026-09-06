---
name: pipefail-com-consumidor-que-sai-cedo
description: Sob `set -o pipefail`, um consumidor que sai no primeiro casamento — `grep -q`, `grep -m1`, `head` — mata o produtor com SIGPIPE, e o cano devolve 141 MESMO QUANDO CASOU; o mesmo código acerta num script que use só `set -e`, então a forma é idêntica e quem decide o resultado é o modo do CHAMADOR, o que faz o defeito aparecer só depois de copiar o trecho para outro script
metadata:
  pattern: debugging_techniques
  origin: dotfiles, system-update v7.3 (05/09/2026) — uma seção inteira pulada em silêncio, com o pacote presente
  confidence: alta (reproduzido com probe de uma linha nos dois modos, e corrigido)
---

**O padrão.** `produtor | grep -q PADRÃO` não devolve o status do `grep`. O `grep -q` sai no
primeiro casamento e fecha a ponta de leitura; o produtor recebe `SIGPIPE` e morre com 141; e
o `pipefail` elege o **rightmost não-zero**, que é o 141 do produtor. O cano reprova
justamente porque encontrou.

A perversidade é que o mesmo trecho está certo em metade dos scripts do mundo:

```bash
# set -e apenas → status é o do grep → 0 → PASSA
# set -euo pipefail → status é 141 do produtor → FALHA (tendo casado)
dpkg -l | grep -q '^ii.*fuse '
```

Medido nos dois modos, no mesmo comando, na mesma máquina:

```
set -e            → resultado=0    PIPESTATUS=141 0
set -uo pipefail  → exit=141       PIPESTATUS=141 0
```

## O que custou

Copiei a checagem de FUSE de um wrapper de terceiro — que usa `set -e` puro, e onde ela
funciona — para um script com `set -euo pipefail`. Ela passou a reprovar com o pacote
instalado, e a seção do Cursor foi **pulada em silêncio**: nada falhou, nada acusou, só não
atualizou. Só apareceu porque rodei o script inteiro em vez de confiar no teste isolado que eu
tinha feito antes, no shell interativo — que não tem `pipefail` e por isso passava.

## O conserto

Tire o cano de baixo do predicado. Capture antes e case sobre a variável:

```bash
out=$(dpkg -l 2>/dev/null) || true
if grep -q '^ii.*fuse ' <<<"$out"; then ...
```

Sem cano não há SIGPIPE, e o status é o do `grep`, que é o que a pergunta queria.

## O gatilho

Suspeite sempre que um predicado com cano decidir errado, e principalmente ao **mover trecho
de shell entre scripts**: o comportamento não viaja com o texto, viaja com o `set` do arquivo
de destino. Vale para todo consumidor que sai cedo — `grep -q`, `grep -m1`, `head -n`,
`awk '...{exit}'`. O probe de uma linha resolve em dois segundos:

```bash
bash -c 'set -uo pipefail; seq 1 100000 | grep -q 5; echo "exit=$? PIPESTATUS=${PIPESTATUS[*]}"'
```

**Parentesco.** Mesma família de
[[bash-strict-mode-crashes-shellcheck-misses]] — modo estrito produzindo defeito que o
shellcheck não pega —, com uma diferença que importa: aqueles dois **matam** o script, e este
não. Este devolve resposta errada e o script segue, calmo, pelo ramo errado. E é instância de
[[comando-verde-que-fez-menos-do-que-anuncia]] virada do avesso: aqui o status é vermelho e a
operação deu certo.
