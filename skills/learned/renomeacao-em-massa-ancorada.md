---
name: renomeacao-em-massa-ancorada
description: Busca-e-substituição de renomeação se ancora no nome de arquivo INTEIRO com extensão — padrão que casa "dois dígitos e hífen" também casa data e URN, e o estrago é silencioso porque nenhum teste quebra
metadata:
  pattern: error_resolution
  origin: manual_estudo, sessão 09/08/2026
  confidence: alta (74 arquivos tocados quando eram 14; URN de lei e data de captura corrompidas)
---

**O caso.** Ao consertar um prefixo duplicado em nomes de arquivo, o padrão usado foi

```
(?:\d\d-)+(\d\d-)   →   \1
```

Ele **parece** falar de prefixo numérico de arquivo. Casa qualquer par de números separado
por hífen. Tocou **74 arquivos em vez de 14** e destruiu, sem que nada quebrasse:

```
urn:lex:br:federal:lei.complementar:2023-08-30;200  →  ...:2008-30;200
agora=lambda: "2026-08-07"                           →  "2008-07"
```

**O que torna isso pior que um bug comum:** nada falha de imediato. O teste continua passando
com a data errada, e a URN só falharia no dia em que alguém recapturasse a norma — parecendo
defeito da fonte, não nosso. O corolário: **teste verde não é prova depois de renomeação em
massa.**

## O que fazer

Ancorar no nome inteiro, com extensão:

```python
RX = re.compile(r'(?:00-)+(00-(?:glossario|indice)[\w-]*\.md)')   # 14, não 74
```

E, antes de aplicar, **listar o que vai mudar e conferir a contagem** contra o que se
esperava. A diferença entre 14 e 74 era visível antes de escrever uma linha.

## Duas armadilhas no desfazer

Descartar com `git stash push` — ele deixa o desfazer recuperável enquanto se confere que os
valores voltaram. O outro comando de descarte restaura do índice e pode não desfazer nada
(ver [[git-desfazer-restaura-do-indice]]).

E conferir o desfazer **pelos valores**, não pelo `git status`: procurar a URN e a data
íntegras no arquivo, porque foi exatamente isso que se perdeu.

## Em prosa não há âncora, e a defesa é outra

O conselho acima — ancorar no nome inteiro, com extensão — só existe porque **nome de
arquivo tem extensão**. Em texto corrido não há nada equivalente, e o mesmo defeito
reaparece sem que a mesma defesa sirva.

Aconteceu no mesmo dia, com outra pessoa e outro alvo: ao mudar o tempo verbal de duas
erratas de presente para passado, uma substituição mecânica **quebrou a gramática de quatro
frases** — *"A aula 2 trazia o lista como sociedade de economia mista"*. O padrão parecia
falar de tempo verbal e falava de qualquer ocorrência da palavra. Foi cometido por quem
estava documentando esse mesmo defeito o dia inteiro.

**A defesa que substitui a âncora é rodar em modo de listagem primeiro e LER as
ocorrências.** O número já denuncia: quando um padrão que devia tocar quatro frases casa
quinze, o problema aparece antes de o dano existir. É a mesma conferência de contagem que
salvou o caso do nome de arquivo — 14 contra 74 —, e é a única que funciona quando não há
o que ancorar.

## A raiz, que é maior que a regex

Derivar de texto livre reintroduz o palpite. No mesmo dia, o mesmo projeto descobriu que o
nome de um PDF derivado do `titulo:` divergia do disco em 38 de 52 casos, e a correção foi
derivá-lo do **nome do arquivo**, que é convenção e não prosa. As duas coisas são a mesma:
**prefira a fonte estruturada à fonte redigida**, sempre que as duas existirem.
