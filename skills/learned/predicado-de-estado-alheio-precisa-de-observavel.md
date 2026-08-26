---
name: predicado-de-estado-alheio-precisa-de-observavel
description: Toda regra cujo predicado é um estado alheio — "o arquivo é de outra sessão", "o agente terminou", "a onda fechou" — precisa de um observável COM UNIDADE, e não de impressão; a regra pode estar certa e o predicado dela ser infalsificável, e aí ela decide sozinha
metadata:
  pattern: user_corrections
  origin: manual_estudo, 19/08/2026 — quatro ocorrências em um dia, com três sessões diferentes
  confidence: alta (uma reversão de conserto, uma onda declarada fechada por engano e três horas e meia de trabalho parado por cortesia)
---

**O núcleo, na formulação da sessão que o achou:**

> *"A minha regra estava certa e o predicado dela era infalsificável."*

**"Em voo" não é propriedade do arquivo. É propriedade do momento — e ela se mede.**

**Custo medido, quatro ocorrências em um dia:**

- uma sessão "consertou" um número de página de outra **contra um valor transitório**, e
  teve de reverter;
- uma onda foi declarada **fechada** com base numa espera que colheu, por azar, o intervalo
  entre dois passes de um agente;
- **duas sessões deixaram de consertar uma disciplina** por achá-la "de alguém" — ela estava
  abandonada havia **três horas e meia**.

⚠ **O enunciado cresceu com a quarta ocorrência, e o crescimento é a parte que importa.**
As três primeiras são sobre *arquivo*: quando é seguro tocar no de outra sessão. A quarta
não tem arquivo nenhum — o predicado infalsificável era *"o agente terminou"*. Quer dizer
que o defeito **não é higiene de arquivo**, e sim toda regra cujo predicado é um estado que
não está sob a sua vista.

## O gatilho

Qualquer regra que comece com uma dessas: *"se o outro estiver mexendo"*, *"quando ele
terminar"*, *"enquanto a onda estiver aberta"*, *"isso é de alguém"*. Elas parecem prudência
e são, mas só depois de o predicado ganhar unidade.

## O remédio

**Troque o predicado por um observável com unidade.** Silêncio de cinco minutos não é
observável; `mtime` de três horas e meia é.

| Predicado infalsificável | Observável com unidade |
|---|---|
| "está em voo" | `mtime` do arquivo, em minutos |
| "o agente terminou" | notificação de término, ou `mtime` estável por N minutos **medidos** |
| "isso é de alguém" | quem o tocou por último, e **há quanto tempo** |
| "a onda fechou" | os arquivos dela pararam de mudar, e o quanto |

E a regra de bolso que sai daí: **cortesia sem medição vira bloqueio.** Deixar de tocar em
algo "porque é de alguém" custa tanto quanto tocar no que está sendo escrito — só que o
custo do primeiro é invisível, porque ninguém reclama de trabalho que não foi feito.

Relacionado: [[arvore-suja-pode-nao-ser-sua]] · [[trabalho-de-agente-morto-esta-no-disco]] ·
[[agentes-paralelos-no-mesmo-scratchpad]] · [[verify-claimed-state]]
