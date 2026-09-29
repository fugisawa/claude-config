---
name: fichamento
description: >
  Use quando houver UMA FONTE JÁ ABERTA (texto no disco e ficha FT em fontes/registro.md) para
  LER a serviço do argumento de um artigo, em um destes pedidos: "ficha", "fichamento", "explora
  <fonte> contra o argumento", "que conexões esta fonte tem", "o que <fonte> diz sobre", "responde
  pela fonte", "confere se <fonte> sustenta", "verifica a citação", "checa a alegação", "avalia o
  método", "avalia o argumento de", "sintetiza as leituras". Sinais: FT-…, docs/leituras/, "Do
  modelo", nota de leitura, página. NÃO use para achar, abrir ou registrar a fonte
  (`artigos-cientificos`), para revisar o manuscrito inteiro (agente `parecerista-2-critico`), nem
  para revisão de literatura de vários textos (`deep-research`).
---

# Fichamento: ler uma fonte a serviço do argumento

O autor de um artigo tem, no disco, o texto integral de uma fonte que já passou pela skill
`artigos-cientificos` e tem ficha no registro. Esta skill põe o modelo para **ler** essa fonte
com um propósito declarado e devolver, na nota de leitura da fonte, um bloco que o autor lê
antes de escrever o dele. Ela existe porque ler é diferente de conferir número: a
`artigos-cientificos` diz se o "6% a 11%" está lá; esta diz o que a fonte sustenta, contradiz ou
deixa de fora, e com que força.

Nasceu em 26/09/2026, no projeto `analista_intel`, de três levantamentos guardados em
`references/pesquisa/`: os repositórios de skills que fazem parte disso, os métodos publicados
de leitura e apreciação crítica, e a prática de quem ficha com modelos. O plano que a desenhou
está em `references/pesquisa/plano-2026-09-26.md`.

## A regra que manda

- **O modelo lê e julga; não escreve o artigo.** A política de inteligência artificial do
  periódico-alvo (Taylor & Francis, lida em 23/09/2026) permite ao modelo revisar, sugerir
  referências, explorar ideias e atacar o argumento como revisor, e proíbe que ele escreva o
  manuscrito ou crie e conclua o argumento. Por isso a saída desta skill é sempre **análise
  localizada na fonte**, nunca um parágrafo do artigo. Pedido de "escreve o parágrafo" dentro
  de um fichamento recebe "não": o que sai daqui é o que o autor precisa para escrevê-lo.
- **Tudo com página.** Todo número e todo trecho no bloco carregam `(p. N)` da versão lida,
  `(p. N da cópia)` quando a versão não tem a paginação do periódico, `(p. N do PDF)` quando o
  registro cita a numeração impressa na própria cópia e a página fica fora dela, como a capa, ou
  `(seção …)` quando a cópia não tem página nenhuma, como a que vem de XML ou de HTML. Um bloco
  sem nenhuma âncora, de página ou de seção, e sem nenhum "não consta" é um bloco feito do
  resumo, e o validador o recusa.
- **"Não consta na fonte" é resposta válida**, e muitas vezes a mais útil. A skill nunca completa
  com o que "deveria estar lá".
- **O texto fica no disco; a janela entra no contexto.** O `fichar.py` dá o mapa de seções e
  janelas por página, por termo ou por seção. Ler o `.txt` inteiro no contexto é proibido: um
  artigo de 30 páginas vale uns 30 mil tokens e contamina a compactação seguinte.
- **DOI que o bloco menciona foi resolvido.** Se a fonte cita outra fonte e o bloco a nomeia, o
  DOI passa por `artigo.py resolver` antes de gravar; o `validar` lista os DOIs do bloco. Fonte
  citada só por autor e ano entra assim, com "sem DOI localizado" se o `resolver` por título
  não a achar; nunca se completa o DOI de memória, porque a taxa medida de fabricação de citação
  por modelo chega a metade conforme o modelo.
- **A nota é do autor; o modelo escreve só na sua seção.** Cada corrida acrescenta um bloco
  datado ao fim de `## Do modelo`, e nunca edita bloco anterior nem a seção `## Do autor`. O
  carimbo diz a ferramenta, porque modelos diferentes fichamentam o mesmo texto de modo
  diferente e isso é parte da proveniência.
- **Nada daqui entra no manuscrito sem passar pelo registro.** O modo `verificar` produz uma
  proposta de AF no formato do registro; a aceitação é o autor colá-la e commitar, e o
  verificador do registro é quem a valida.

## Os quatro modos

| Modo | Pergunta que responde | Entrada | O que sai | Procedimento |
|---|---|---|---|---|
| **explorar** | que conexões esta fonte tem com o argumento, e o que ela não cobre? | FT + o argumento (`docs/argumento.md`, uma seção ou uma afirmação) + perguntas abertas do caderno | tipo de fonte, mapa, conexões candidatas rotuladas apoia / contraria / menciona, com página; o que não cobre; perguntas ao autor | `references/explorar.md` |
| **responder** | o que esta fonte diz sobre esta pergunta? | FT + a pergunta | rótulo (sustenta / refuta / misto / insuficiente / não consta), trecho literal com página, contexto, uma pergunta de verificação respondida contra o próprio trecho | `references/responder.md` |
| **verificar** | esta alegação se sustenta nesta fonte? a citação está certa? o método e o argumento aguentam? | FT + a alegação, como o manuscrito ou o argumento a escreve | tipo de fonte e lista de apreciação usada; evidência a favor e contra; veredito em cinco graus com "o que mudaria"; gravidade de erro de citação; nível em que a checagem parou; proposta de AF | `references/verificar.md` |
| **sintetizar** | o que várias leituras, juntas, sustentam, contradizem e deixam faltar no argumento? | várias notas (ou um estágio, ou uma seção do argumento) | por afirmação do argumento: o que sustenta, o que contradiz, a lacuna, com fonte e página | `references/sintetizar.md` |

O modo `explorar` é a primeira passada de Keshav mais a leitura contra o argumento; o
`responder` vai à seção provável e sai com um trecho; o `verificar` é a leitura inteira, com a
lista de apreciação que o tipo de fonte pede; o `sintetizar` só lê blocos já gravados. Em
dúvida entre modos, pergunte ao autor qual é o propósito; ele decide, e o modo decide o
orçamento de leitura.

## O procedimento comum

1. **Localize.** `fichar.py localizar <FT>` diz o DOI, a cópia, o texto extraído, o intervalo
   de páginas impressas no periódico, que vem da referência do registro, e o deslocamento, que é
   o número de páginas que a cópia traz antes do artigo; quando o texto não diz em que página
   está cada linha, a saída traz também o campo `sem_paginas`, com o motivo. Quando o registro
   cita a numeração impressa na própria cópia, e não a do periódico, a saída traz ainda o campo
   `paginas_da_copia`, com a primeira e a última página dessa numeração.

   Quando o recibo da cópia, o `.procedencia.json` que a `artigos-cientificos` grava ao lado dela,
   declara um texto no campo `texto`, é esse o texto lido, mesmo que o caminho gravado ali seja o
   da outra máquina; se ele não está nesta máquina, o script avisa e não lê outro no lugar, porque
   o texto com o nome do DOI pode ser outra versão da fonte.

   Quando nenhum recibo dá o texto nem avisa que ele falta, o script procura a cópia pelo hash. É o
   caso da fonte sem DOI, que não tem recibo porque o `artigo.py registrar` exige um DOI, como o
   relatório, a lei, a página institucional, a tese e o livro; e é o caso da fonte cujo recibo só
   registra a tentativa de abri-la. O parágrafo "Fonte:" do registro guarda os primeiros dígitos do
   SHA-256 do arquivo baixado, e o script fica com o arquivo de `fontes/copias/` cujo hash começa
   por eles; o campo `copia` da saída diz qual é. O texto é o `.txt` de mesmo nome ao lado da
   cópia, ou a própria cópia, quando o que se baixou já é texto, como a página copiada pelo
   navegador. O PDF que ainda não tem `.txt`, como o que o autor pôs na pasta à mão, ganha o texto
   extraído com `pdftotext -layout` na primeira vez, e o comando diz que gravou o arquivo; se a
   extração falha, o script avisa e não deixa `.txt` pela metade.

   Sem cópia local, pare. Se o aviso diz que falta nesta máquina o texto que o recibo declara, ou o
   arquivo com o hash que o registro guarda, traga-o da outra, porque uma nova abertura também
   pode trazer outra versão. Se o aviso cita arquivos que não se leram, a cópia pode ser um deles,
   como o que o Syncthing ainda está gravando: espere a sincronização e rode de novo. Se o aviso diz
   que o texto não se extraiu, a cópia está nesta máquina e só falta o `.txt` de mesmo nome ao lado
   dela: resolva a extração ou grave esse `.txt` por outro meio. Sem nenhum desses avisos, a rota é
   `artigo.py abrir` ou `registrar` da `artigos-cientificos`. Ler o resumo no lugar do texto não é
   opção.
2. **Mapeie.** `fichar.py mapa <FT>` lista as páginas e os cabeçalhos prováveis. É o índice que
   evita ler o arquivo inteiro. A primeira linha diz em que página do PDF está a primeira página
   impressa. Se o registro cita a paginação do periódico, a capa da editora, a folha de rosto do
   repositório e a errata, quando vêm antes do artigo, não ganham número impresso e levam
   `(p. N da cópia)`.

   O deslocamento sai do campo *Versão da cópia* do registro, quando ele declara "a página 2 do
   PDF é a página 268" ou "a página impressa é a do PDF mais 229" (ou "menos 1"); se o registro
   não declara, sai dos números de página que a cópia imprime no cabeçalho e no pé, desde que ao
   menos três páginas concordem; sem nenhum dos dois, supõe-se que a cópia começa na primeira
   página do artigo. O script imprime um aviso em dois casos, e o aviso vai para o autor: quando
   o registro e a cópia discordam, caso em que vale o registro, porque as AF citam pela regra
   dele; e quando a cópia tem mais páginas que o intervalo e nada diz onde o artigo começa, caso
   em que a página citada pode estar deslocada até que a *Versão da cópia* declare a
   correspondência.

   Há cópia que o registro cita pela numeração impressa nela, e não pela do periódico: a
   publicação antecipada, paginada de 1 em diante antes de o fascículo sair, e a reimpressão, em
   outra revista ou no arquivo de publicações do autor. O script a reconhece quando a *Versão da
   cópia* diz "as páginas citadas são as da cópia" ou "as localizações citam a página da cópia"
   (ou "da reimpressão"), e o campo deve usar uma dessas frases, porque o script não reconhece
   outra redação e, sem ela, rotula a cópia pela paginação do periódico.
   Nessa cópia, o rótulo é `(p. N da cópia)`, com o número impresso na página, que é o que o
   registro cita, e a página fora dessa numeração, como a capa, leva `(p. N do PDF)`, que é a
   posição no arquivo; o autor decidiu assim em 28/09/2026. A página do PDF em que a numeração
   começa sai da *Versão da cópia*, quando ela declara "a página 2 do PDF é a página 1"; senão,
   dos números que o cabeçalho e o pé imprimem, desde que ao menos três páginas concordem, como
   quando o registro cita a paginação do periódico. Sem nenhum desses dois indícios, o script
   supõe que a numeração começa na primeira página do PDF: o rótulo continua `(p. N da cópia)`,
   mas o N é a posição da página no arquivo, e um aviso pede que a *Versão da cópia* declare onde
   a numeração começa. A numeração vai até a última página com texto, porque há página cujo
   número impresso não passa para o texto extraído.

   As provas, os manuscritos e as pré-publicações, cuja *Versão da cópia* começa por "prova",
   "manuscrito" ou "pré", seguem a mesma regra desde 29/09/2026, quando o autor decidiu que o
   registro cita nelas o número impresso, e não a posição no PDF: a capa do repositório e a folha
   da editora antes do texto levam `(p. N do PDF)`, e o resto leva `(p. N da cópia)`, com o número
   impresso. A *Versão da cópia* pode declarar mais de uma correspondência, quando a numeração se
   repete ou salta, e cada uma vale da sua página do PDF em diante: a de Costa, Miranda e Melo
   (2022) declara "a página 2 do PDF é a página 1" e "a página 14 do PDF é a página 12", porque a
   página da tabela 2 repete o 12. Nesse caso duas páginas levam o mesmo rótulo, `--pagina 12`
   abre a primeira delas, e o mapa diz em que posição do PDF a correspondência muda. Cada
   correspondência se confere contra os números do cabeçalho e do pé no trecho em que vale, e o
   script avisa quando eles discordam; `--pagina` recusa o número que a numeração salta.

   A declaração vale também quando a referência não traz o intervalo de páginas do periódico, como
   no artigo que a revista identifica por um número (Schoenegger e col., 2024), no relatório lido
   no lugar de um livro e na fonte sem DOI: o rótulo é `(p. N da cópia)`, com o número que a
   declaração dá. A numeração começa na página do PDF que a declaração nomeia, e por isso a
   declaração deve nomear a primeira página do trecho em que a correspondência vale, e não uma do
   meio: a de Treverton (2009) dizia "a página 5 do PDF é a página 7", e as duas páginas antes
   dessa, a terceira e a quarta do PDF, que o registro cita como pp. 5 e 6, saíam `(p. 3 do PDF)` e
   `(p. 4 do PDF)`; hoje ela diz "a página 3 do PDF é a página 5".

   Há texto que não diz em que página está cada linha, e nele o rótulo é `sem paginação`. Isso
   vale para a cópia que o recibo declara em XML, como a do PubMed Central e a do Europe PMC, ou
   em HTML; vale também para o texto sem nenhum form feed, como a transcrição por OCR, salvo
   quando o intervalo do registro tem uma página só. O `pdftotext` fecha toda página com form
   feed; sem ele o texto inteiro é uma página, e numerá-la pelo intervalo do registro daria a
   primeira página impressa a todas as linhas. Nesses casos a primeira linha do mapa começa por "sem paginação" e
   diz o motivo, a janela recusa `--pagina`, que devolveria o texto inteiro, e o bloco cita a
   seção, `(seção …)`.

   Se o texto veio em duas colunas embaralhadas pelo `pdftotext -layout` (o mapa mostra linhas
   com duas frases coladas), use `--corrido` no `mapa` e na `janela`: o script reextrai o PDF sem
   `-layout` uma vez, ao lado da cópia, fora do git.
3. **Leia pelo orçamento do modo.** `explorar` lê resumo, introdução, cabeçalhos e conclusão;
   `responder` lê a seção provável e as janelas dos termos; `verificar` lê o método, os
   resultados e a discussão inteiros, por página, o que num artigo curto é quase tudo: a regra
   proíbe despejar o arquivo de uma vez, não ler o que o modo pede; `sintetizar` não abre a fonte.
   `fichar.py janela <FT> --pagina N` (N é a página impressa: a da cópia, quando o registro cita
   a numeração dela, e senão a do periódico, quando o registro traz o intervalo; fora dessas
   numerações, N é a posição da página no PDF, e o `mapa` diz em que posição está a primeira
   página impressa; na cópia sem paginação, o script recusa `--pagina`), `--termo "x"`
   (repetível; busca tolerante a sinal, vírgula decimal, espaço e hífen de fim de linha) ou
   `--secao "Results"`.
4. **Escreva o bloco** no formato do `reference` do modo, num arquivo fora do repositório.
   Todo trecho literal é curto; o resto é paráfrase com página. O bloco fecha com
   `**Perguntas ao autor:**` e duas ou três perguntas que digam o que ele precisa abrir ou
   decidir, ligadas a algo específico do que foi lido.
5. **Valide.** `fichar.py validar <modo> <arquivo>` confere o contrato: página em todo trecho,
   rótulos do modo, as perguntas, nenhum parágrafo `Fonte:`. Ele imprime os DOIs mencionados;
   resolva cada um com `artigo.py resolver` e corrija o bloco se algum não resolver.
6. **Grave.** `fichar.py gravar <FT> <modo> <arquivo>` acrescenta o bloco carimbado à seção
   `## Do modelo` de `docs/leituras/<FT>.md`. A nota tem de existir; se não existir, rode
   `docs/leituras/gerar_notas.py` do projeto.
7. **Devolva ao autor** o que gravou, em três linhas, e as perguntas. O commit é dele.

## O contrato de todo bloco

- Abre com o que se pediu (a pergunta, a alegação, o alvo da exploração), na forma exata.
- Todo número e todo trecho literal levam a página como a janela a rotula: `(p. N)`, ou
  `(p. N da cópia)` quando a versão lida não tem a paginação do periódico, ou `(p. N do PDF)`
  quando o registro cita a numeração impressa na própria cópia e a página fica fora dela, como a
  capa, ou `(seção …)` quando nem a cópia tem página, como o manuscrito aceito em XML. O rótulo
  `sem paginação` da janela não é âncora, e o validador não o aceita no lugar da seção. Aspas
  duplas são citação de fonte; título, rótulo e nome de seção vão em itálico.
- Os rótulos do modo vêm em negrito, com os valores fixos que o validador conhece.
- Quando a evidência é mista, diz que é mista; quando não há, diz "não consta na fonte".
- Distingue o que a fonte **diz** do que o modelo **infere**; a inferência vem marcada como tal.
- Não traz parágrafo `Fonte:` nem hash: a procedência mora no registro.
- Fecha com `**Perguntas ao autor:**` e duas ou três perguntas.
- Recebe, ao gravar, o carimbo `### <modo> — AAAA-MM-DD` e a linha de ferramenta.

## Por que se abre a primária, e não o resumo

Não é zelo: é taxa medida. Em 46 estudos que conferiram 32.074 citações contra a fonte citada,
16,9% tinham erro e 8,0% erro maior (a fonte não sustenta, é irrelevante ou contradiz), sem
melhora ao longo das décadas (Baethge & Jergas, 2025); numa revisão anterior de 28 estudos, o
total foi 25,4% (Jergas & Baethge, 2015); em história, a área mais próxima da nossa, 24,3% das
citações conferidas tinham erro (Cumberledge, Smith & Riley, 2023). Os DOIs e o que cada
estudo mediu estão em `references/pesquisa/metodos-de-leitura-e-verificacao.md`, seção 3. O
mesmo levantamento mostra que verificadores automáticos servem de triagem e falham por extração
e cobertura, e que as divergências já achadas neste projeto eram todas do tipo que nenhum
verificador de DOI pega: fonte real, número errado.

## Comandos

```bash
F=~/.claude/skills/fichamento/scripts/fichar.py         # roda de dentro do repositório do projeto
python3 $F localizar FT-meissner-kassin-2002
python3 $F mapa FT-meissner-kassin-2002
python3 $F janela FT-meissner-kassin-2002 --termo "d = -0,129" --termo "response bias"
python3 $F janela FT-meissner-kassin-2002 --secao "RESULTS"
python3 $F validar responder <scratch>/bloco.md
python3 $F gravar FT-meissner-kassin-2002 responder <scratch>/bloco.md
python3 -m unittest discover -s ~/.claude/skills/fichamento/tests -q     # sem rede
```

A raiz do projeto sai de `git rev-parse --show-toplevel`, ou de `--raiz`; a skill não carrega
caminho de home, porque o projeto vive em duas máquinas.

## Fora do escopo

Achar, abrir, registrar e conferir números de uma fonte: `artigos-cientificos`. Revisão
adversarial do manuscrito inteiro: agente `parecerista-2-critico`. Revisão de literatura de
vários textos: `deep-research` ou o agente `academic-researcher`. Norma e jurisprudência:
`legislacao-br`. Fonte sem cópia legal: nenhum modo roda; a skill diz qual degrau da escada
falta.
