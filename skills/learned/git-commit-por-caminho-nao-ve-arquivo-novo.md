---
name: git-commit-por-caminho-nao-ve-arquivo-novo
description: "`git commit <caminho>` alcança só o que já é RASTREADO ali dentro — arquivo novo é ignorado em silêncio e o commit sai anunciando o que não levou; a defesa é `git add -N` imediatamente antes, e a conferência é `git ls-files`, nunca `git status`"
metadata:
  pattern: error_resolution
  origin: manual_estudo, sessão de 14/08/2026, clone com três sessões simultâneas
  confidence: alta (três arquivos perdidos num commit só, e o defeito só apareceu horas depois)
---

**O padrão.** Commitar por caminhos é a defesa contra publicar trabalho alheio, e ela está
certa. O que quase ninguém percebe é que o mesmo comando tem um **segundo vazamento, na
direção oposta**: `git commit <diretório>` monta o commit a partir do que o git já conhece
naquele caminho, e **arquivo não rastreado não entra**. Não há erro, não há aviso, e o commit
é criado com a mensagem que você escreveu — inclusive quando ela anuncia exatamente o arquivo
que ficou de fora.

O defeito é especialmente cruel porque a **verificação natural falha junto**. Depois de
commitar, olha-se `git status`; o arquivo aparece como `??`, e `??` é o que também aparece
para PNG de QA, saída de build e rascunho de outra sessão. A linha que denuncia a perda é
indistinguível do ruído que se aprendeu a ignorar.

## A ocorrência

O commit `40f3483` do `manual_estudo` tem por assunto *"feat(controle-externo): a folha do
Tópico 5 — o processo inteiro de auditoria, 33 páginas em três sessões"*, descreve o conteúdo
da folha em nove linhas de corpo, e **não contém a folha**. Nem o MD, nem o PDF. Junto foi-se
o PDF do glossário de Direito Constitucional, cujo MD tinha entrado por acaso — ali eu havia
rodado `git add -N` antes, por outro motivo.

Três arquivos, e o repositório ficou num estado pior que "faltando": a trilha apontava o PDF,
o índice o listava, o catálogo de entregáveis o contava, e os verificadores passavam todos,
porque todos leem o **disco de trabalho**. Num clone novo, nada daquilo existiria. O defeito
só apareceu horas depois, quando um `git ls-files` da disciplina mostrou o buraco entre a
folha 04 e a 09.

## As duas regras

**`git add -N <arquivo novo>` imediatamente antes do `git commit <caminhos>`.** O `-N` registra
a *intenção* de adicionar sem colocar conteúdo no índice — de modo que a garantia que fez você
commitar por caminhos continua de pé: uma sessão paralela que commite no intervalo não leva o
seu conteúdo junto. "Imediatamente antes" não é preciosismo: é o que mantém a janela mínima.

**Confira com `git ls-files`, e nunca com `git status`.** A pergunta certa não é "o que está
sujo", é "o que o repositório contém". Num diretório com numeração sequencial, o buraco salta
aos olhos; sem ela, `git show --stat <commit>` responde direto.

## O par, que é a mesma ferramenta vazando ao contrário

Na mesma sessão, uma sessão vizinha cometeu o inverso: `git add -A <diretório>` seguido de
commit, que **capturou 31 arquivos de outra pessoa**. As duas falhas convivem porque atacam
pontas opostas do mesmo comando, e as duas são silenciosas:

| Forma | O que vaza | Sintoma |
|---|---|---|
| `git add -A <dir>` + `commit` | entra o que **não é seu** | mensagem de commit descreve menos do que o diff |
| `git commit <dir>` com arquivo novo | fica de fora o que **é seu** | mensagem de commit descreve mais do que o diff |

Conhecer uma não protege da outra, e é por isso que a regra "commite por caminhos" precisa
vir acompanhada do `-N`. **A conferência que pega as duas é a mesma: leia o `--stat` do
commit antes de empurrar, e compare com o que a mensagem promete.**

Relacionado: [[arvore-suja-pode-nao-ser-sua]] (a outra ponta, com o relógio como sinal) ·
[[verify-claimed-state]] (a mensagem de commit é alegação, não fato)
