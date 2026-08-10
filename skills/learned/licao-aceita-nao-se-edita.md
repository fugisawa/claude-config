---
name: licao-aceita-nao-se-edita
description: Lição registrada não se reescreve quando muda de ideia — escreve-se a nova declarando qual ela supera, porque editar apaga a evidência que dava autoridade à regra e transforma o acervo em opinião sem procedência
metadata:
  pattern: knowledge_management
  origin: manual_estudo, decisoes/0002 e 0004 — adotado em ~/.claude em 10/08/2026
  confidence: média (padrão provado no manual_estudo; primeira aplicação a este acervo)
---

**O padrão.** Uma lição aqui vale porque traz **o defeito que a originou**: quantas vezes
mordeu, o que custou, o que foi medido. Isso é o que separa "regra que alguém achou boa" de
"regra que o mundo impôs". Quando a conclusão muda e alguém **edita o arquivo no lugar**, a
regra nova herda o tom de autoridade da antiga sem ter pago nada por ele — e a evidência que
justificava a antiga desaparece junto, de modo que ninguém consegue mais reconstruir por que
se acreditava naquilo.

Pior: some a informação de que **houve uma mudança de ideia**. Quem ler daqui a seis meses vê
uma regra lisa e não sabe que ela já foi outra coisa, nem por qual motivo virou esta. É a
diferença entre um acervo atravessável para a frente e uma foto do que se pensa hoje.

## A regra

**Lição aceita não se edita. A nova supera a antiga, e diz isso.**

- A que supera declara no corpo: *supera `[[nome-da-antiga]]`, porque …* — com o que mudou
  no mundo ou o que a medição nova mostrou.
- A superada **fica no lugar**, ganhando uma linha no topo: *superada por
  `[[nome-da-nova]]` em DD/MM/AAAA.* Não se apaga, não se esvazia.
- A cadeia fica atravessável **para a frente**: partindo de qualquer versão antiga chega-se à
  vigente seguindo os links.

**Correção não é supersessão.** Consertar erro de digitação, link quebrado, nome de arquivo
que mudou — isso se edita à vontade. O que não se edita é **a conclusão**: se a regra passou
a dizer outra coisa, é arquivo novo.

## Por que aqui, e não numa pasta `decisoes/`

O `manual_estudo` guarda isso em `decisoes/`, um acervo de ADR próprio. Este repositório
**já tem** o acervo equivalente — `skills/learned/`, com frontmatter, origem, confiança e
links `[[ ]]`. Criar uma pasta paralela seria a segunda cópia do **mecanismo de registro**,
e o defeito da segunda cópia é exatamente o que este acervo mais documenta: ela diverge
calada, e cada metade fica internamente coerente enquanto o conjunto mente.

Relacionado: [[a-segunda-copia-da-regra-diverge-calada]] · [[verify-claimed-state]] ·
[[docs-by-moment-of-use]]
