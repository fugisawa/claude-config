---
name: resultado-de-busca-nao-e-veredito
description: Estende `escopo-do-grep-nao-e-escopo-da-pergunta` por dois mecanismos novos — N acertos não dizem nada sobre SENTIDO (contar ocorrências não é ler), e a ferramenta certa pode responder com precisão à pergunta ERRADA (história e estado são perguntas diferentes)
metadata:
  pattern: debugging_techniques
  origin: manual_estudo, 19–26/08/2026 — duas ocorrências, uma delas quase virou item de issue com prioridade errada
  confidence: alta (as duas foram desfeitas abrindo o artefato que a busca tinha apenas contado)
---

**Estende [[escopo-do-grep-nao-e-escopo-da-pergunta]]**, e não a supera. Aquela cobre *"um
acerto não confirma ausência alhures"* — o escopo da busca não é o escopo da pergunta. Faltam
dois mecanismos, medidos depois, em que a busca responde **certo** e a conclusão sai errada.

## 1 · Contar ocorrências não é ler

**Custo medido.** Contei 7 ocorrências de "CGU" e 2 de "Analista" num guia rápido e conclui
que o arquivo estava **obsoleto** — os dois eram alvos abandonados. As sete diziam *"CGU =
contingência dormente"*, e as duas, *"fora do portfólio desde 08/08"*. Quer dizer: o
documento estava **atualizado justamente por citá-los assim**. A caracterização errada
chegou à sessão de orquestração e quase virou item de issue com prioridade alta.

A lição existente diz que N acertos não provam ausência em outro lugar. Esta acrescenta:
**N acertos não dizem nada sobre o SENTIDO das ocorrências.** Uma palavra pode aparecer
porque o documento a afirma, porque a nega, ou porque a rotula como superada — e a
contagem trata os três casos igual.

⚠ O sinal de alerta é a **frequência virando argumento**: "aparece 7 vezes, logo é sobre
isso". Frequência é sobre presença; a pergunta era sobre postura.

## 2 · A ferramenta certa pode responder a pergunta errada

**Custo medido.** Usei `git log -S` para achar o que tinha quebrado uma guarda. Ele
respondeu **com precisão** quem introduziu a string — um commit de seis dias antes. A causa
real eram **sete renomeações não commitadas**, que o `git status` mostrava, rodado três
minutos depois pela mesma pessoa.

Nada estava errado com a ferramenta nem com a resposta. O que trocou foi a pergunta:
**história e estado são perguntas diferentes**, e o git tem comando separado para cada uma.
`log -S` responde *"quando isto entrou no histórico?"*; a pergunta era *"o que está no disco
agora?"*.

> **Quando a resposta vier limpa e mesmo assim não explicar o sintoma, suspeite de que a
> pergunta trocou — não de que a resposta está errada.**

É o modo mais difícil de pegar, porque uma resposta precisa e plausível não parece um erro.
O tell é o desencaixe: a resposta é boa e o sintoma continua sem explicação.

## O remédio das duas

**Abra o artefato que a busca apenas contou.** Foi o que desfez as duas: ler as sete linhas
do guia rápido, e rodar `git status` ao lado do `git log`. Contagem e histórico são pistas
para escolher o que abrir, nunca o veredito.

Relacionado: [[escopo-do-grep-nao-e-escopo-da-pergunta]] (a raiz) ·
[[negative-finding-vs-broken-probe]] · [[verify-claimed-state]] ·
[[comando-verde-que-fez-menos-do-que-anuncia]]
