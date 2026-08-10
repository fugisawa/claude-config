---
name: agentes-paralelos-no-mesmo-scratchpad
description: Ferramenta que ESVAZIA o diretório de saída antes de escrever destrói o trabalho de outro agente por inteiro, não arquivo a arquivo — com N agentes no mesmo scratchpad, dê subdiretório por tarefa e confira a extração contra a entrada antes de escrever
metadata:
  pattern: workarounds
  origin: manual_estudo, sessão 09/08/2026 — nove agentes convertendo 1.100 páginas
  confidence: alta (dois agentes se salvaram; um chegou a ler material de outro)
---

**O caso.** Nove agentes convertiam aulas em PDF ao mesmo tempo, cada um extraindo o seu.
A ferramenta de folha de contato **esvazia o diretório de saída** antes de escrever, e faz
glob por padrão de nome. Com todos no mesmo scratchpad, **um apaga o material do outro por
inteiro** — não é sobrescrita arquivo a arquivo, é o diretório voltando a zero.

Dois agentes detectaram e refizeram em subdiretório próprio. Um terceiro chegou a **ler
texto de outra aula por alguns minutos**, o que é pior que perder arquivo: ele estava
produzindo conteúdo a partir de material que não era o dele, e nada no texto avisa isso.

## As duas defesas, e elas não são intercambiáveis

**Um subdiretório por tarefa** — previne. Barato, e resolve a colisão antes de existir.

**Diff da extração contra o arquivo de entrada, antes de escrever o resultado** — enxerga
contaminação **já consumada**. O agente que provou estar limpo mediu sobreposição de trechos
de cinco palavras entre cada parágrafo produzido e o dump de origem.

A primeira sozinha não basta, porque ela depende de todo mundo ter lembrado. A segunda pega
inclusive o caso em que alguém esqueceu.

## O que generaliza

**Antes de paralelizar, pergunte de cada ferramenta usada: ela escreve, ou ela limpa e
escreve?** A diferença é invisível na documentação da maioria delas e decisiva aqui. Vale
para diretório de saída, cache, arquivo de índice e qualquer coisa com "clean" implícito.

E o modo de falha que importa não é o arquivo perdido — é o **material trocado sem aviso**.
Perda de arquivo é ruidosa; leitura do material errado é silenciosa e vira conteúdo
publicado.

Relacionado: [[fronteira-de-arquivo-nao-cria-dono-da-coerencia]] · [[teste-que-chama-git-herda-o-repositorio]] — as três são a mesma família: **a ferramenta toca mais coisa do que o comando aparenta.**
