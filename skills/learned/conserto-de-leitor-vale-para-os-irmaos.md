---
name: conserto-de-leitor-vale-para-os-irmaos
description: Estende `a-segunda-copia-da-regra-diverge-calada` para quando os leitores do mesmo formato já existem e não dá para unificá-los, porque moram em repositórios diferentes — o defeito achado num leitor está nos irmãos, e consertá-lo só onde doeu faz de cada irmão o defeito da hora seguinte; o plano do conserto lista todos os leitores do formato, leva a regra e o teste a todos no mesmo passo e roda cada um sobre o acervo real antes do commit
metadata:
  pattern: error_resolution
  origin: analista_intel e skills artigos-cientificos e fichamento, 28–29/09/2026 — quatro pares de consertos irmãos em 24 horas
  confidence: alta (quatro pares medidos, quase sempre com cada conserto numa sessão separada; a cadeia seguiu depois da reclamação do Daniel)
---

**Estende [[a-segunda-copia-da-regra-diverge-calada]]**, e não a supera. Aquela manda
procurar quem já lê um formato antes de escrever outro leitor, e unificar quando der; quando
não dá, manda escrever ao lado da regra onde mora a outra cópia. Estes dois dias mostraram que
o comentário não basta quando os leitores já são quatro e moram em dois repositórios.

**O padrão.** O registro de fontes do analista_intel é lido por pelo menos quatro scripts: o
verificador, o exportador para o Zotero, o gerador de notas e o `fichar.py` da skill
fichamento. O recibo de procedência de cada cópia também é lido por quatro: o `abrir` e o
`registrar` da skill artigos-cientificos, o `fichar.py` e o gerador de notas. Cada um tem a sua
maneira de ler, escrita contra o mesmo formato e com as mesmas suposições, e por isso o defeito
que aparece num deles quase sempre está nos outros. Consertado só no leitor que doeu, ele
reaparece no irmão horas depois, numa sessão nova, que o conserta sozinho e descobre o irmão
seguinte.

## Os quatro pares, em 24 horas

| Defeito | Primeiro conserto | Conserto do irmão |
|---|---|---|
| recibo com o caminho de outra máquina | gerador de notas, 28/09 12h18 (4a7cb87) | `fichar.py`, 28/09 14h38 (c006f1b) |
| recibo de outro DOI com o mesmo nome de arquivo | `abrir`, 28/09 17h10 (c719a8c) | `registrar`, 29/09 10h38 (e6ae3c3), cuja mensagem diz "como o abrir já recusava" |
| DOI cortado no parêntese, e cópia sem recibo achada pelo hash | `fichar.py` (78dd2eb) | gerador de notas (eb82d9e), que copiou a regra do `fichar.py`; os dois commits saíram em 29/09 com quatro minutos entre eles, em sessões separadas |
| identificador fora da forma, e título que o leitor pula sem aviso | exportador, 29/09 12h12 (a6146f5) | verificador, 12h33 (d88f700) e logo depois (6fde82f); ficaram outras duas tarefas, para levar a regra do título ao exportador e ao gerador de notas |

**O custo.** Foram nove commits de conserto onde quatro bastariam, quase todos numa sessão
nova, que precisou reler o projeto, combinar a regra e escrever o teste do zero. No fim do
segundo dia o Daniel escreveu: "pelo amor de deus, cada hora um problema. já faz 2 dias isso."

## A regra

1. **Antes do plano, a lista dos leitores.** Uma busca pelo marcador do formato nos
   repositórios que o leem (`### FT-` para o registro, `.procedencia.json` para o recibo) dá a
   lista em um minuto. O plano nomeia cada leitor e diz o que acontece com ele.
2. **A regra vai a todos no mesmo passo.** Dentro de um repositório, ela sobe para uma função
   que todos importam, como o e6ae3c3 acabou fazendo com a `procedencia.de_outro_doi`, que o
   `abrir` e o `registrar` passaram a usar. Entre repositórios, cada leitor recebe o mesmo caso
   de teste, com a mesma entrada e a mesma saída esperada.
3. **Cada leitor roda sobre o acervo real antes do commit**, com a saída comparada à do código
   anterior. É isso que acha o irmão que o teste não previu.
4. **O leitor deixado de fora aparece no relatório com o motivo.** "O gerador de notas fica
   para depois porque X" é uma decisão; o silêncio é o próximo defeito.

## O que o comentário de 09/08 não faz

No d88f700, o verificador ganhou exatamente o comentário que a lição de 09/08 manda escrever:
a forma do identificador "é a mesma do IDENTIFICADOR_FT" do exportador. O comentário amarra
aquela regra ao irmão dela, mas o conserto seguinte, o do título que o leitor pula, era de
outra regra, e nenhum comentário o amarrava. O comentário cobre uma regra; a lista de leitores
cobre o formato.

## Relações

Com [[enumerar-o-territorio-e-nao-o-mapa]]: o título que o leitor pula é o intruso que só a
varredura do território acha. Com [[arquivo-que-viaja-nao-guarda-fato-da-maquina]]: o primeiro
par da tabela é o defeito daquela lição, consertado leitor por leitor.
