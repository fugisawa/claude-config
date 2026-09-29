---
name: arquivo-que-viaja-nao-guarda-fato-da-maquina
description: Arquivo que vai para a outra máquina, pelo git ou pela pasta sincronizada, não guarda caminho absoluto nem o que o script achou na máquina onde rodou — o recibo com o caminho de casa fez a máquina do trabalho perder de vista 52 cópias presentes, e a nota regenerada em casa apagou o caminho de uma cópia que só existia no trabalho; o arquivo guarda o que não depende da máquina (hash, DOI, caminho relativo a uma raiz declarada), o caminho se resolve na leitura, e quem regenera não troca o que não consegue ver
metadata:
  pattern: error_resolution
  origin: analista_intel e skills artigos-cientificos e fichamento, 28–29/09/2026 — os dois primeiros dias do projeto rodando em duas máquinas
  confidence: alta (quatro consertos em 24 horas, em dois leitores e um gerador; um deles apagou dado versionado)
---

**O padrão.** Um script grava num arquivo o caminho que recebeu, ou o que encontrou na
máquina onde rodou. Enquanto o projeto vive numa máquina só, isso não se distingue de um
fato. Quando o arquivo vai para a segunda máquina, pelo git ou pela pasta sincronizada, ele
passa a afirmar lá o que só vale aqui, e o leitor do outro lado conclui que a coisa não
existe. Pior: se o outro lado regenera o arquivo, grava o fato dele por cima do fato daqui, a
próxima regeneração daqui desfaz de novo, e o que só existe numa das máquinas some do arquivo
sem que nenhum comando reclame.

## As ocorrências, em 24 horas

O analista_intel passou a rodar na máquina do trabalho em 28/09/2026. O recibo de procedência
de cada cópia viaja pela pasta sincronizada, e as notas de leitura viajam pelo git.

| Quando | Onde | O que o arquivo guardava | O que aconteceu |
|---|---|---|---|
| 28/09, 09h28 | `fichar.py` (c9bcaa9) | o recibo, com o caminho da cópia relativo a uma base que ele não declara | o leitor resolvia o caminho contra a pasta corrente, e quatro comandos da skill quebravam |
| 28/09, 12h18 | gerador de notas (4a7cb87) | o recibo, com o caminho absoluto de casa ou o da pasta temporária do download | no trabalho, 52 cópias presentes em `fontes/copias/` não foram achadas, e as notas foram reescritas dizendo que a cópia "não está nesta máquina"; em casa, 26 notas já diziam isso pela pasta temporária |
| 28/09, 14h38 | `fichar.py` (c006f1b) | o recibo, com "arquivo" e "texto" como o comando os recebeu: nome solto, relativo à raiz ou absoluto da outra máquina | 30 das 77 fontes com texto declarado respondiam "sem cópia local" com o texto ao lado do recibo |
| 29/09, 09h50 | gerador de notas (15e245c) | a linha "Cópia local" de cada nota versionada, com o que o gerador achou na máquina onde rodou | a nota de Dhami e Careless (2015), regenerada em casa, perdeu o caminho da cópia que só existe no trabalho; regenerar todas as notas em casa apagaria todos esses caminhos |

As três primeiras linhas são o mesmo defeito, no mesmo recibo, consertado em dois leitores
com cinco horas entre o primeiro e o último conserto. A quarta é a mais cara, porque apagou
dado versionado, e foi achada quando só duas notas tinham sido regeneradas.

## A regra

1. **O arquivo que viaja guarda identificador, e não localização:** o hash, o DOI, o nome
   relativo a uma raiz que o formato declara. O caminho de origem pode ficar como informação,
   mas nenhum leitor o toma como verdade.
2. **O caminho se resolve na leitura**, na máquina onde se lê. O leitor procura pelo
   identificador (o nome ao lado do recibo, o hash na pasta das cópias) e só depois diz que não
   achou.
3. **Quem regenera não troca o que não consegue ver.** Se a máquina não tem a cópia, a linha
   antiga fica como estava; ela só muda quando o gerador acha a cópia aqui e o caminho antigo
   não existe aqui. É a regra do 15e245c, com três testes escritos antes dela.
4. **"Nesta máquina" não entra em texto que viaja.** A frase é verdadeira numa máquina e falsa
   na outra, e nada a mede. É o mesmo defeito que o `CLAUDE.md` global registrou em 10/08/2026
   sobre a prosa das instruções, em que a frase sobre "esta máquina" já tinha errado três de
   quatro afirmações.

## O gatilho

Ao planejar um script que grava arquivo, pergunte de cada campo: **esse valor seria o mesmo
se o script rodasse na outra máquina?** Se não for, o campo sai do arquivo ou vira um
identificador que se resolve na leitura. A pergunta custa um minuto no plano, e as quatro
ocorrências custaram quatro consertos e o caminho de uma cópia apagado de uma nota.

## Relações

Não é [[referencia-declarada-sem-validador]], que trata de identificador escrito à mão em
configuração, como id de plugin ou caminho de gancho, que nenhum comando confere; aqui o valor
é escrito por script e está certo na máquina onde nasce. Também não é [[verify-claimed-state]],
sobre documento que afirma um estado. É vizinha de [[conserto-de-leitor-vale-para-os-irmaos]]:
as três primeiras ocorrências são um defeito só, e ele foi consertado leitor por leitor.
