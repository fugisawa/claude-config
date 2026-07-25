---
name: bash-strict-mode-crashes-shellcheck-misses
description: "Ao revisar bash com set -euo pipefail, caçar 2 crashes que o shellcheck NÃO pega: (1) (( VAR )) com VAR sem default sob set -u = 'unbound variable' fatal — típico em flags só setadas no parse de args; (2) exit dentro de função NÃO é neutralizável com '2>/dev/null && true'. Confirmar com probe de 1 linha antes de afirmar o bug"
metadata:
  pattern: debugging_techniques
  origin: dotfiles v7.1 (25/07/2026) — fixslow crashava desde a v7.0; setup-printing --install morria sob sudo
  confidence: alta (ambos confirmados empiricamente com probes e corrigidos)
---

**Os dois padrões fatais (invisíveis ao shellcheck 0.10):**

1. **Aritmética com var sem default sob `set -u`.** `(( DRY_RUN ))` com `DRY_RUN` nunca
   atribuída → `bash: DRY_RUN: unbound variable` e morte do script. Armadilha clássica:
   a var só é setada dentro do `case` do parse de flags (`-n) DRY_RUN=1`), então o script
   funciona COM a flag e crasha SEM ela — exatamente o caminho não testado. `export VAR`
   de var unset não dispara o erro (não é expansão), o que mascara ainda mais.
   **Caça:** para cada `(( VAR ))`/`$(( VAR ))`, confira se existe `VAR="${VAR:-0}"` antes.
   **Fix:** default no topo do bloco de flags.

2. **`exit` dentro de função não se neutraliza por fora.** `check_not_root 2>/dev/null
   && true` NÃO impede o `exit 1` interno — redirection e lista-E só afetam status, e o
   exit encerra o shell inteiro. Sintoma perverso: um guard "não rode como root" chamado
   "desativado" num caminho que EXIGE sudo mata o script silenciosamente (exit 1, sem
   mensagem, pois o stderr foi suprimido). **Fix:** remover a chamada ou rodar em
   subshell `(fn)` — aí o exit morre no subshell e o status é testável.

**O método que pegou ambos:** antes de afirmar o bug, provar com probe de 1 linha:
`bash -c 'set -euo pipefail; (( X )) && echo sim || echo nao'` → "X: unbound variable".
`bash -c 'f(){ exit 1; }; f 2>/dev/null && true; echo reached'` → "reached" nunca sai.
Custa 2 segundos e evita tanto falso alarme quanto correção errada. shellcheck é
necessário mas não suficiente: esses dois só aparecem lendo o fluxo (qual caminho de
execução deixa a var unset? quem chama a função com exit?).

**Regra de revisão:** em scripts `set -u`, o caminho "sem nenhuma flag" é o mais
provável de estar quebrado e o menos testado — rode `script.sh` pelado (ou trace o
fluxo) antes de dar por revisado.
