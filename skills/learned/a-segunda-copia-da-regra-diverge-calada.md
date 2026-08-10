---
name: a-segunda-copia-da-regra-diverge-calada
description: Antes de escrever um limiar ou um parser, procure se o projeto já tem um — a segunda cópia diverge em minutos e o defeito sai como saída errada em silêncio, não como erro
metadata:
  pattern: error_resolution
  origin: manual_estudo, sessão 09/08/2026
  confidence: alta (duas ocorrências na mesma sessão, ambas produzindo saída errada calada)
---

**O padrão.** Uma regra que vale em dois lugares e está escrita em dois lugares **não fica
igual**. E a divergência não estoura: ela produz saída errada que parece certa, porque cada
cópia está internamente coerente. Foi o que aconteceu duas vezes numa sessão só, com poucas
horas de intervalo.

## Ocorrência 1 — o limiar inventado ao lado do limiar existente

Um elemento de documento só funciona quando o texto cabe numa linha. Escrevi a decisão de
forma no conversor com orçamento de **76 caracteres**, medindo a distribuição real do
projeto para chegar lá. O projeto **já tinha esse número**, medido antes, em outro módulo:
**72**, com teto por lado.

Meia hora depois, um par de 75 caracteres passou como "curto" pelo conversor, foi renderizado
na forma que não cabia, e **chegou ao PDF truncado** — o texto acabava em "apenas di". Quem
pegou foi uma verificação independente que compara a resposta do elemento com o texto
extraído do PDF. Sem ela, o material teria ido para a impressora assim.

O conserto não foi ajustar 76 para 72. Foi **mover o número para um lugar só** e fazer o
outro módulo importá-lo, com o motivo escrito ao lado: *enquanto foram duas cópias,
divergiram em meia hora.*

## Ocorrência 2 — dois leitores do mesmo arquivo

Dois comandos liam o mesmo arquivo de fila com expressões regulares próprias. Elas
discordavam sobre **o que é o título de um passo**: uma devolvia o título limpo, a outra
devolvia o título com as etiquetas de categoria coladas no fim e cortado em 52 caracteres.
O usuário via um título na tela e outro no PDF derivado do mesmo arquivo, e a diferença
parecia bug de renderização.

O conserto foi o mesmo: **um leitor canônico**, importado por quem marca e por quem imprime.
O que se marca passou a ser o mesmo passo que se imprime.

## As regras

**Antes de escrever um limiar, procure por ele.** `grep` por números redondos próximos, pelo
nome do conceito, pelo sufixo `LIM_`/`MAX_`/`_THRESHOLD`. Custa uma chamada. Um limiar
duplicado é pior que um limiar errado, porque o errado é consistente.

**Antes de escrever um parser, procure quem já lê aquele formato.** Se dois consumidores
precisam de coisas diferentes do mesmo arquivo, o certo é um leitor com dois métodos, não
dois leitores.

**Quando não der para unificar, escreva a razão junto do número.** O comentário que diz
"este valor também existe em X, e eles divergiram no dia Y" é o que impede a terceira cópia.

## Por que este defeito é dos piores

Ele **não gera exceção**. Cada cópia funciona. O sintoma aparece longe da causa e no
artefato final — texto cortado no PDF, título diferente na tela —, onde parece problema de
formatação. É a família de defeito que só uma verificação que compara **saída contra
intenção** apanha, e não uma que testa cada módulo isolado.

Relacionado: [[checagem-que-nao-pode-falhar]] · [[fronteira-de-arquivo-nao-cria-dono-da-coerencia]]
