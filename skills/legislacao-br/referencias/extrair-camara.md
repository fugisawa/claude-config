# Extrair o Regimento da Câmara do Legin sem corromper o texto

Medido em 07/10/2026, capturando o Regimento Interno (Resolução nº 17/1989) e o Código de
Ética e Decoro Parlamentar (Resolução nº 25/2001) das páginas "norma atualizada" do Legin,
para o corpus do `~/manual_estudo/normas/`. Como no Planalto, cada item abaixo **falha em
silêncio**: o download dá 200, o parser não reclama, e o erro só aparece na leitura. Um
deles só apareceu quando alguém leu a letra para escrever um capítulo.

Os contratos estão em `~/manual_estudo/normas/tests/test_fonte_direta.py`, um teste por
item, todos offline.

## 1. A página empilha normas, e o recorte precisa de marco em HTML

A página do Regimento traz, em sequência, a Resolução nº 17/1989, o Regimento que ela
aprova, a Resolução nº 25/2001 e o Código de Ética que ela institui. São quatro numerações
próprias, e o art. 1º existe quatro vezes. Sem recorte, o corpus grava os quatro como uma
norma só, e quem procura o art. 1º do Regimento acha o da resolução.

O corte se faz no HTML, antes do parse, entre dois marcos. **O marco precisa aparecer uma
vez exatamente**, e o texto puro não garante isso: "REGIMENTO INTERNO DA CÂMARA DOS
DEPUTADOS" aparece duas vezes na página, mas `<b>REGIMENTO INTERNO DA CÂMARA DOS
DEPUTADOS</b>`, com a tag, aparece uma. O marco final do Regimento é
`<b>RESOLUÇÃO\nNº 25, DE 2001</b>`, com a quebra de linha que a fonte põe dentro do
negrito. Marco ausente ou repetido tem de ser erro, nunca "o primeiro que aparecer": marco
ausente é mudança de marcação na fonte, e marco repetido deixaria o corte à sorte da ordem.

## 2. A anotação vem pelo tipo do dispositivo, não pelo verbo

O Planalto anota com o verbo na frente: "(Redação dada pela…)", "(Incluído pela…)". A
Câmara começa pelo tipo do dispositivo:

- "(Inciso acrescido pela Resolução nº 10, de 2009)"
- "(“Caput” do artigo com redação dada pela…)"
- "(Primitivo § 3º renumerado para § 4º pela…)"
- e as notas de adaptação, com "adaptado".

Um padrão de anotação escrito para o Planalto deixa todas essas no texto do dispositivo,
que sai impresso com a procedência no meio da norma. Foram cerca de 400 no Regimento; dos
2.240 dispositivos capturados, 515 levam alguma anotação.

**O padrão novo precisa do tipo no início E de um verbo de alteração** (redação,
acrescido, revogado, renumerado, transformado, incluído, suprimido, adaptado). Só o tipo
não basta, porque o próprio texto normativo usa parênteses que começam assim: "(art. 17)"
e "(Parágrafo único do art. 5º)" são norma, não procedência.

## 3. Designador e nome da divisão vêm no mesmo bloco

No Planalto o designador ("CAPÍTULO II") e o nome ("DAS METAS FISCAIS…") vêm em dois
blocos (`extrair-planalto.md`, item 5). Na Câmara eles vêm numa lista solta entre
parágrafos:

```html
<ol><li><h1>CAPÍTULO IV</h1><li><h1>DOS LÍDERES</h1></ol>
```

Isso traz dois defeitos, e o segundo esconde o primeiro.

**A fronteira de bloco precisa valer espaço.** É o oposto da regra de `span` do Planalto
(`extrair-planalto.md`, item 3b). Sem o espaço, o par sai "CAPÍTULO IVDOS LÍDERES", que
nenhum padrão de designador reconhece. Com ele, sai "CAPÍTULO IV DOS LÍDERES", que ainda
assim não casa com um padrão que exija o designador sozinho no bloco. O par então colava
no dispositivo anterior, 31 vezes no Regimento.

**O designador ganha letra quando a Câmara insere capítulo sem renumerar**
("CAPÍTULO II-A"), e às vezes com travessão curto no lugar do hífen ("CAPÍTULO III–F",
uma ocorrência). O padrão aceita hífen, travessão curto e travessão longo antes da letra.

Para que um inciso que comece citando "Capítulo II do Título…" continue sendo inciso, o
reconhecimento exige caixa alta no designador e no nome, ou "Seção"/"Subseção" com inicial
maiúscula seguidas do numeral romano, que é a grafia da Câmara para essas duas.

## 4. Rótulo no plural: "Arts. 245 a 248."

A Câmara revoga vários artigos num bloco só:

```
Arts.
245 a 248. (Revogados pela Resolução nº 25, de 2001)
```

Um padrão de artigo que só conhece o singular ("Art. 244") não reconhece o bloco, que cola
no artigo anterior. O art. 244, vigente, passava então a carregar a anotação "Revogados", e
o corpus afirmava revogado um artigo em vigor. É o pior modo da lista, porque o erro é de
fato e não de forma, e nenhuma contagem o acusa: o número de artigos parece plausível.

Quem pegou foi o redator do capítulo de Deputados, ao conferir o art. 244 na letra. O
conserto trata o rótulo no plural como dispositivo próprio, "Arts. 245 a 248", e o padrão
precisa aceitar a quebra de linha que a fonte põe entre "Arts." e o número.

## O que no Legin NÃO acontece, ao contrário do Planalto

Medido na mesma página, para não importar limpeza que não tem o que limpar:

- **Não há redação vencida**: zero `<strike>` e zero `line-through`. A vigente é a única.
- **Não há script com token de sessão**: os bytes vêm idênticos entre duas buscas, e o
  hash do conteúdo bruto já é estável.
- **O charset declarado é verdadeiro**: UTF-8 estrito decodifica o arquivo inteiro, sem
  erro. Decodificar como `cp1252`, que é o certo no Planalto, aqui corromperia todo
  caractere acentuado.
- **Não precisa de User-Agent**: responde 200 sem ele.
