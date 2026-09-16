---
name: compactacao-herda-o-raciocinio-da-sessao
description: O /compact é UMA chamada ao modelo que herda o raciocínio estendido da sessão — com esforço máximo o resumidor pensa por minutos (10 min medidos em 16/09/2026 para ~150 mil tokens), e os ganchos custam 0,2 s. Não cace o gancho — o esforço da sessão é a alavanca, e o contexto fixo (CLAUDE.md de 65 KB) é a outra
metadata:
  pattern: debugging_techniques
  origin: manual_estudo, sessão 16/09/2026 — "4 min para compactar uma conversa curta é inadmissível"
  confidence: alta (medido no transcript e em cada gancho; o mecanismo está em code.claude.com/docs/en/context-window)
---

**O caso.** O Daniel pediu `/compact` numa sessão de três mensagens e esperou. No transcript, o
comando entrou às 14:30:09 e a fronteira de compactação saiu às 14:40:43: **dez minutos e meio**.
A primeira resposta depois dela levou mais quatro e meio. A suspeita natural eram os ganchos do
`everything-claude-code` e do `superpowers`, que rodam antes e depois da compactação.

**O que a medição disse.** Cada gancho, cronometrado com `HOME` falso para não sujar o log:
`pre-compact.js` 0,09 s, `session-start.js` 0,09 s, o `session-start` do superpowers 0,03 s.
Somados, dois décimos de segundo. O observador (`observe.sh`) custa 1,35 s por chamada de
ferramenta, quatro vezes por chamada (duas entradas em `settings.json`, duas no plugin), mas é
assíncrono e não segura a compactação. Não havia log de repetição nem de sobrecarga da API.

**O mecanismo.** A documentação diz que a chamada de resumo "herda a configuração de raciocínio
estendido da sessão". Esta sessão foi aberta pela app com `--effort max` (o `ps` mostra o
argumento). O resumidor recebeu ~150 mil tokens (os cinco PNGs de QA lidos com `Read` valem
~3 mil tokens cada; 129 KB de texto de ferramenta; o contexto fixo de uns 50 mil tokens — o
`CLAUDE.md` do projeto tem 65 KB) e **pensou** antes de escrever o resumo de 4 mil tokens.
Pensamento longo a ~70 tokens por segundo é o que dá minutos, não segundos.

## O que fazer, na ordem em que compensa

1. **Escolher o esforço por sessão.** Sessão de escrita e conferência não precisa de `max`; a
   app expõe o nível ao abrir a sessão (`--effort`), e `/effort <nível>` muda em sessão. O
   `max` fica para o trabalho que paga o tempo. `MAX_THINKING_TOKENS` em `settings.json > env`
   limita o pensamento de TODAS as chamadas, inclusive a de resumo; é a alavanca bruta, e é
   decisão do Daniel, não do agente.
2. **Encolher o contexto fixo**, que entra em toda chamada e em todo resumo. O `CLAUDE.md` do
   `manual_estudo` tem 65 KB (~18 mil tokens), boa parte histórico que já vive em `decisoes/`.
3. **Não despejar arquivo inteiro no contexto**: ler PDF e texto extraído em janelas (`grep -n
   -C`, `Read` com `offset`/`limit`, `artigo.py conferir`). Cada despejo entra no próximo resumo.
4. **Só depois** procurar gancho lento — e procurar medindo, como acima, não desligando.

**O erro a não repetir:** desligar plugin ou gancho por suspeita, sem cronômetro. Nenhum dos
ganchos era o problema, e o registro em `docs/skills-inventory.md` (08/09/2026) já tinha
mostrado o preço de consolidar sem medir.
