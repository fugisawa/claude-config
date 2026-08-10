---
name: checagem-que-nao-pode-falhar
description: Verificador cuja saída limpa afirma cobertura que não existe é pior que verificador nenhum — toda checagem nova nasce com um teste que a vê REPROVAR, e a exclusão se declara por regra verificável, nunca por lista de nomes
metadata:
  pattern: debugging_techniques
  origin: manual_estudo, sessão 08-09/08/2026
  confidence: alta (quatro ocorrências medidas, duas delas contra o próprio autor)
---

**O padrão.** Um verificador que não consegue reprovar produz o pior estado possível:
**silêncio que parece aprovação**. Quem lê a saída limpa conclui que está coberto, e a
conclusão é falsa. Verificador ausente é honesto; verificador cego mente.

## Quatro ocorrências, no mesmo projeto, em dois dias

**O curinga que cobria tudo.** Uma checagem de cobertura varria o documento e colhia
`pdftoppm -png -r 130 * *` de um comando de terminal — com aquele curinga, **ela não podia
falhar**: 688 nomes casavam com 18 padrões. Restrita ao escopo certo, caiu para 82 e 6.

**O intervalo que sumia.** A mesma checagem não casava o formato `2–4` e a linha
**desaparecia da verificação em silêncio**, sem erro nenhum.

**O padrão que se desligaria sozinho.** `<Matéria>-<NN>-<Assunto>` colapsava em `*-*-*`,
padrão sem nenhum segmento literal, que cobriria o disco inteiro.

**O universo vazio.** Um verificador de frescor examinava 21 pares e era cego em 35, saindo
zero. Não estava errado; estava afirmando pouco e parecendo afirmar tudo.

## As três regras que ficaram

**Toda checagem nova nasce com um teste que a vê reprovar.** Não "um teste que passa quando
está certo" — um que **falhe** quando está errado. É a única prova de que ela é capaz de
falhar.

**A exclusão se declara por regra verificável, nunca por lista de nomes.** Excluir por sufixo
de nome cria a dívida que a checagem existe para medir: o primeiro item que mudar de forma
passa despercebido. A regra honesta é conferível no disco — "existe um `.typ` ao lado", "o
produtor declarou no manifesto". Quando não houver regra, **dívida declarada com teto**, e um
teste que reprova se a lista crescer.

**O universo verificado precisa ter tamanho conhecido.** Um teste que assegure que há o que
conferir — `assertGreater(len(alvos), 50)` — impede o pior modo de falha, que é passar por
vacuidade.

## O corolário sobre falso positivo, que puxa para o lado oposto

Falso positivo é o recurso mais escasso do sistema: ele dá **licença para ignorar tudo**. O
Tricorder do Google põe em prova o analisador cuja taxa de "não-útil" passa de 10% e o
desliga acima de 25%. Layman e Roden mediram que o grupo com 50% de falso alarme foi 39%
mais rápido que o de 96%.

As duas regras convivem porque atacam pontas diferentes: **a checagem precisa ser capaz de
falhar, e precisa falhar só quando deve**. Ser conservador na entrada vale mais que ser
completo — três checagens de prosa foram medidas e reprovadas antes de entrar, com o motivo
escrito no código para não voltarem por simetria.

Relacionado: [[negative-finding-vs-broken-probe]] · [[verify-claimed-state]]
