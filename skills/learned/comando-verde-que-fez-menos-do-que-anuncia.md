---
name: comando-verde-que-fez-menos-do-que-anuncia
description: O código de saída responde "o processo terminou?" e não "ele fez o que eu pedi?" — onde as duas perguntas divergem o comando sai verde tendo feito menos do que a mensagem dele anuncia, e a única defesa é medir o EFEITO (o PNG da página, o `git status` depois do commit, os dois lados do denominador) em vez do retorno
metadata:
  pattern: debugging_techniques
  origin: manual_estudo, 25–26/08/2026 — seis instâncias medidas em vinte e quatro horas, em quatro ferramentas que não se falam
  confidence: alta (duas delas custaram trabalho publicado; nenhuma foi encontrada lendo o comando)
---

**O padrão.** Um comando termina, **não dá erro**, e fez menos do que a mensagem dele
anuncia. Nenhuma das instâncias abaixo é apanhada por `set -e`, por `check=True` ou por
leitura do código de saída — e o motivo é o mesmo nas seis: o status responde *"o processo
terminou?"*, e a pergunta que interessa é *"ele fez o que eu pedi?"*.

| Onde | O que anunciava | O que fazia |
|---|---|---|
| `cmd \| tail` | o status do comando | o status do `tail`, que de arquivo existente é **sempre 0** |
| `pdftotext` | extração bem-sucedida | **código 0 sobre uma página sem uma palavra**, com `Syntax Error` só no stderr |
| `pdfinfo` | contagem de páginas | código 0 escrevendo `Syntax Error`; **seis chamadores** raspavam o stdout dele |
| uma guarda do projeto | "conferi as páginas declaradas" | uma declaração **por campo**, com `search` no lugar de `finditer` — 65 declaradas, 63 lidas |
| `git commit <caminhos>` | os caminhos nomeados | só os **rastreados** |
| `git commit -- <c> -m "…"` | commit com mensagem | **nada**: o `--` faz o `-m` e a mensagem virarem pathspec |

**O que custou.** Duas viraram trabalho publicado. O `pdftotext` deixou uma página **em
branco** num PDF da prateleira — caixas e fios pintados, nenhuma palavra — e o build
imprimiu `OK`. E o `git commit <caminhos>` fez dois commits nascerem **sem os quatorze
capítulos que os títulos anunciavam**: o gancho passou, a mensagem saiu como escrita, e os
arquivos ficaram no disco.

⚠ **A última instância pegou o commit que registrava a família.** O arquivo era novo, o
`git commit -m "…" -- <caminho>` não o alcançou, o `git log` não mudou, e nenhum erro
apareceu. A regra reprovou o commit que a registrava.

## O gatilho

Toda vez que uma decisão depender de *"o comando funcionou"*, pergunte qual das duas
perguntas o retorno está respondendo. Elas divergem sempre que:

- há **cano**, e o status é o do último estágio;
- o erro vai para o **stderr** e o programa sai 0 assim mesmo — comum em ferramenta de
  PDF, que prefere entregar o que conseguiu a falhar;
- o comando tem **filtro implícito** que a mensagem não menciona (rastreado × novo);
- a sintaxe muda o significado de um argumento (`--` transformando opção em caminho);
- a guarda **conta** ocorrências e a pergunta era sobre **todas** elas.

## O remédio, e ele é sempre o mesmo

**Meça o efeito, não o retorno.** Foi assim que as seis apareceram, sem exceção:

| O que se queria saber | O que responde |
|---|---|
| o PDF tem texto? | abrir o **PNG** da página, não o código de saída do renderizador |
| o commit levou o que eu disse? | `git status` **depois** de commitar, não a mensagem antes |
| a guarda conferiu tudo? | comparar **os dois números** — quantas existem, quantas ela leu |
| a suíte passou? | rodar sem cano, ou ler o veredito e não a cauda |

E há um teste barato que separa as duas perguntas antes de custar caro: **descreva em voz
alta o que o comando faria se falhasse.** Se a resposta for "sairia igual", o retorno não
serve de evidência.

## O que isto NÃO é

Não é a regra de encadear com `&&` em vez de `;` — aquela é sobre **sequência**, e resolve
o caso em que a verificação roda e o próximo passo ignora o vermelho. Aqui a verificação
**não fica vermelha**: ela devolve verde tendo visto menos.

Também não é desconfiança geral de ferramenta. As seis instâncias vieram de quatro famílias
independentes — extração de PDF, o próprio git, uma guarda escrita no projeto e o cano do
shell —, e é isso que a torna regra em vez de anedota: **padrão que aparece em ferramentas
que não se falam não é defeito de uma delas.**

Relacionado: [[git-commit-por-caminho-nao-ve-arquivo-novo]] (a quinta instância, com o
remédio detalhado) · [[checagem-que-nao-pode-falhar]] · [[portao-que-pula-esconde-o-defeito]] ·
[[referencia-declarada-sem-validador]] · [[verify-claimed-state]]
