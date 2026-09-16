---
name: artigos-cientificos
description: >
  Use quando houver UM artigo científico para ACHAR, ABRIR, REGISTRAR, CONFERIR ou PEDIR: resolver
  um DOI, uma URL de editora ou uma citação; obter o texto integral pelo caminho legal mais
  rápido ("me consegue esse paper", "acha o PDF de", "não consigo abrir esse artigo", "texto
  integral", "está atrás de paywall", DOI ou URL de editora colados); redigir o pedido ao autor
  como rascunho no Gmail ("escreve pro autor"); e conferir número, tabela ou afirmação no texto
  antes de citar ("os valores batem com o artigo?", "confere na fonte"). Sinais: DOI, "paper",
  "artigo", "meta-análise", "revisado por pares", "preprint", "Sci-Hub", "foi retratado". Produz a
  cópia COM procedência (rota e etiqueta A–D, versão, hash, data) e o parágrafo "Fonte:" do
  material. NÃO use para revisão de literatura ou síntese de vários artigos (`deep-research`,
  agente `academic-researcher`), lei e jurisprudência (`legislacao-br`), PDF já em mãos para
  virar Markdown (`pdf-to-markdown`) nem foto de página (`ocr-com-evidencia`).
---

# Artigos científicos, com procedência

Um artigo só vale como fonte quando foi **aberto** — o texto, na versão certa — e quando quem
ler o material consegue repetir o caminho até ele. Esta skill produz três coisas, e nunca uma
sem as outras: os metadados que identificam o artigo, a cópia com o registro de procedência
(rota e etiqueta, endereço, versão, hash, data), e a conferência do que se vai citar, feita no
texto e não no resumo. Quando nenhuma via legal abre, ela diz isso num recibo datado, com as
pendências e a data de voltar, em vez de improvisar.

Ela nasceu do caso de 16/09/2026: quatro tamanhos de efeito de uma meta-análise (Tharumalingam
e col., 2025) estavam no material com a bandeira "não conferidos em fonte primária". A página da
Springer mostrava só o resumo; o `WebFetch` bateu num portão de cookies; o Tavily estava sem
cota; o Exa exigia OAuth; o navegador da app passou o portão e parou na barreira de pagamento; a
cópia veio do site de um coautor, e a conferência achou uma divergência entre a tabela e o texto
que o resumo jamais mostraria. **A ordem que sobrou dessa sessão é a escada abaixo.** Pediu-se
então que o Sci-Hub entrasse no caminho; ele não entra, e a seção *A regra que manda* diz por
quê e o que entra no lugar.

## A regra que manda

- **Nunca cite o que não abriu.** Resumo, comentário de questão, texto de divulgação e a memória
  do modelo não são o artigo. O que não abriu fica com a bandeira `⚑ não conferido em fonte
  primária`, e fonte secundária entra rotulada como secundária.
- **Diga qual versão leu.** Publicada (diagramada pela editora, com paginação e DOI no cabeçalho)
  vale mais que aceita (manuscrito do autor depois da revisão por pares), que vale mais que
  pré-publicação. O número pode mudar entre elas, e o recibo traz a ressalva sozinho.
- **Pelo caminho legal mais rápido, e no máximo duas chamadas por degrau.** A escada para no
  primeiro sucesso; o que ela tentou fica no diário, e a etiqueta (A–D, abaixo) diz com que
  direito a cópia se lê.
- **Sci-Hub, LibGen, Anna's Archive e espelhos não entram**, nem quando o pedido vem com a
  autorização do Daniel. É a rota D: redistribuem cópias que a licença da editora não permite
  redistribuir, e a skill não faz esse ato. O argumento de que o acesso deveria ser livre é
  sério e está registrado (`references/escada-de-acesso.md`, seção final, com a base legal
  brasileira conferida): ele descreve a norma que os financiadores estão adotando, não a
  licença que hoje cobre o arquivo. O que a skill faz é esgotar o acesso legítimo, que no caso
  de 16/09 bastou, e deixar o recibo quando não basta.
- **A skill nunca envia e-mail.** O pedido ao autor vira rascunho no Gmail (`create_draft`), e
  quem envia é o Daniel, depois de ler. `send_message` não aparece em lugar nenhum daqui, e um
  teste o garante.
- **O e-mail do Daniel só vai para Crossref, OpenAlex e Unpaywall**, que o usam como
  identificação de cortesia (o Unpaywall o exige), e só se `ARTIGOS_EMAIL` estiver definido ou
  `--email` for passado. Nunca fixado no código, nunca em outro serviço. Desde 16/09/2026 a
  variável mora no `env` do `~/.claude/settings.local.json`, fora do git.
- **Nada de despejar o artigo no contexto.** O texto extraído fica no disco; o que entra na
  conversa são as linhas que o `conferir` devolve, ou uma janela de `grep -n -C`. Um artigo de
  27 páginas vale ~25 mil tokens, e cada despejo entra na próxima compactação.

## Perfil de acesso

Os degraus 7 e 8 da escada existem só para quem tem o acesso. A skill lê daqui; campo vazio é
degrau pulado, sem perguntar e sem tentar credencial nenhuma. Segredo não entra neste arquivo.

- Vínculo institucional: nenhum
- Acesso CAFe ao Portal de Periódicos da CAPES: não
- Bibliotecas com cadastro (empréstimo entre bibliotecas, COMUT): nenhuma
- Orçamento para compra ou aluguel de artigo: nenhum; a skill cita o preço e não compra
- Assinatura do pedido ao autor: `ARTIGOS_ASSINATURA`, ou "Daniel Fugisawa"
- E-mail para as APIs de cortesia (Crossref, OpenAlex, Unpaywall): `ARTIGOS_EMAIL`, autorizado pelo
  Daniel em 16/09/2026 para esses três serviços e para mais nenhum. Mora no bloco `env` do
  `~/.claude/settings.local.json`, que não é versionado: cada máquina precisa da sua linha, e sem
  ela o Unpaywall é pulado e o diário diz isso

## Cinco pedidos, cinco rotas

| Pedido | Rota | O que sai |
|---|---|---|
| "Tem estudo sobre X?", "qual a meta-análise de Y?" | `buscar` (OpenAlex) e os conectores scite e Consensus | lista com ano, DOI, situação de acesso, citações — uma lista, não uma revisão; revisão é `deep-research` ou o agente `academic-researcher` |
| "Abre este artigo", "me consegue esse paper", "acha o PDF de <DOI>" | `resolver` → `abrir` → degraus manuais da escada | PDF ou XML + `.txt` + `.procedencia.json` + parágrafo `Fonte:` com rota e etiqueta |
| "Achei o PDF no site do autor", "o autor mandou a cópia" | `registrar` | a mesma procedência, com a etiqueta que você declara (A ou C) |
| "Escreve pro autor" | `pedido` → `create_draft` no Gmail | o rascunho, nunca o envio; a pendência para o recibo |
| "Confere se os números batem", "isso está mesmo no artigo?" | `abrir` → `conferir` → `references/conferencia.md` | relatório por expressão, com linha e contexto; a frase do material com a data |

## Comandos

```bash
S=~/.claude/skills/artigos-cientificos/scripts
# ARTIGOS_EMAIL vem do bloco env do ~/.claude/settings.local.json (autorizado em 16/09/2026): liga o Unpaywall e o polite pool
python3 $S/artigo.py resolver "https://doi.org/10.1007/s10648-025-10003-9"     # metadados (Crossref + OpenAlex)
python3 $S/artigo.py buscar "video lecture playback speed test performance" --desde 2020 -n 10
python3 $S/artigo.py abrir 10.1007/s10648-025-10003-9 --destino <scratch>/artigos --listar    # só lista os candidatos
python3 $S/artigo.py abrir 10.7717/peerj.4375 --destino <scratch>/artigos --conferido-em 2026-09-16
python3 $S/artigo.py abrir 10.1007/s10648-025-10003-9 --destino <scratch>/artigos \
    --pendencia "pedido ao autor rascunhado em 2026-09-16 para E. Tharumalingam; sem resposta, não repetir antes de 2026-10-16" \
    --reavaliar-em 2026-10-16                                # o recibo de quem NÃO abriu, gravado e impresso
python3 $S/artigo.py registrar 10.1007/s10648-025-10003-9 --arquivo <scratch>/artigos/copia.pdf \
    --url "https://bradyrtroberts.ca/…" --origem "site do coautor Brady Roberts" --etiqueta C --versao publicada
python3 $S/artigo.py pedido 10.1007/s10648-025-10003-9 --tema "velocidade de reprodução de videoaulas" \
    --para <e-mail lido na primeira página> --json      # to/subject/body para o create_draft do Gmail; o --tema no idioma do pedido
python3 $S/artigo.py conferir <scratch>/artigos/10-7717-peerj-4375.txt "g = -0,36" "k = 48" "p < .001"
python3 -m unittest discover -s ~/.claude/skills/artigos-cientificos/tests -q        # sem rede
```

`--json` em qualquer comando devolve o dicionário inteiro. Códigos de saída: `0` abriu ou
achou tudo; `2` não abriu, ou faltou expressão no `conferir`; `1` erro de uso ou de ambiente
(`pdftotext` ausente: `apt install poppler-utils`). As cópias vão para `--destino`, que deve
ser o diretório de trabalho da sessão, nunca o repositório (ver *O que vai para o repositório*
em `references/conferencia.md`).

O `abrir` é a parte automatizável da escada: consulta Crossref, OpenAlex, Unpaywall (com
e-mail), Semantic Scholar, Europe PMC e arXiv; ordena os candidatos por formato (PDF, XML,
página), versão (publicada, aceita, submetida) e degrau; baixa o primeiro que é texto de verdade
(magic bytes do PDF, ou JATS); extrai o texto com `pdftotext -layout`; grava o hash e o diário
de tudo o que tentou. Página de pouso só serve se trouxer `citation_pdf_url` no cabeçalho. Sites
atrás de Cloudflare (PeerJ, `europepmc.org`) devolvem 403 a qualquer cliente sem navegador; o
script contorna pelo REST do Europe PMC (XML) quando há PMCID.

## As quatro etiquetas

| Etiqueta | O que é | Exemplos |
|---|---|---|
| **A** licenciada | quem serve o arquivo tem licença para servi-lo | acesso aberto em qualquer cor; manuscrito aceito em repositório; Share Link; cópia enviada pelo autor; assinatura própria; COMUT |
| **B** exceção legal | trecho, não obra (Lei 9.610, art. 46, II e III) | o trecho do scite, a janela do `grep`; nunca o PDF inteiro por esta via |
| **C** cinzenta | cópia posta em público por quem não é o titular; lê-se sem redistribuir | o PDF da editora no site do autor ou no ResearchGate; cópia encaminhada por colega |
| **D** excluída | redistribuição sem licença, credencial alheia, contorno de medida técnica (art. 107) | biblioteca-sombra e espelhos; a skill não usa, não cita endereço, não instrui |

Degrau automático é sempre A; degrau manual é A ou C, e quem registra declara. O recibo mostra a
etiqueta, e a base legal de cada uma, conferida em 16/09/2026, está em
`references/escada-de-acesso.md`.

## A escada, resumida (o detalhe está em `references/escada-de-acesso.md`)

| # | Degrau | Quem faz | Etiqueta | Para quando |
|---|---|---|---|---|
| 1 | APIs abertas: Unpaywall, OpenAlex (cobre SciELO, HAL, Zenodo, RePEc e repositórios), Semantic Scholar, Europe PMC, arXiv, TDM da Crossref | `abrir` | A | o diário diz `ABERTO` |
| 2 | Cópia do autor: `WebSearch "<título exato>" filetype:pdf`, página pessoal, repositório da universidade, ResearchGate; depois `registrar` | você | A ou C | achou PDF com cabeçalho do periódico (versão publicada) ou manuscrito aceito |
| 3 | Pré-publicação: OSF Preprints, PsyArXiv, EdArXiv, arXiv (também `hf://papers/<id>/paper.md`), SSRN, SciELO Preprints | você, pela API do OSF ou `WebSearch` | A | achou; e anote que é pré-publicação |
| 4 | Conectores com texto: scite `read_fulltext` (`source` tem de ser `"fulltext"`), scite `search_literature` com `dois` + `term`, PubMed/PMC (biomédico) | você | A (B, se for trecho) | o trecho que interessa apareceu |
| 5 | Navegador da app na página do DOI | você | — | leu resumo, referências, datas, suplemento — nunca passa a barreira |
| 6 | Dados e código do artigo (OSF, GitHub, Zenodo) | você, pela API | — | dá para recomputar o número, não para ler o texto |
| 7 | O acesso do perfil: CAFe, biblioteca, COMUT, compra ou aluguel com orçamento e preço citado antes | o Daniel | A | o perfil declara o acesso; vazio, pule |
| 8 | Pedido ao autor: `pedido` → rascunho no Gmail; Share Link quando a editora é a Elsevier; em paralelo, o botão de pedido do ResearchGate | você redige, o Daniel envia | A | a cópia chegou; enquanto não chega, a pendência no recibo |

Em cada degrau que abre: pare, vá para a conferência. Se nenhum abre: o `abrir` imprime o recibo
`não obtido por via legal`, com o diário; passe `--pendencia` e `--reavaliar-em` para que ele
carregue o pedido rascunhado e a data de voltar (fim do embargo, quando a política da editora o
diz). O Open Policy Finder, que registra os embargos, responde 403 a script desta máquina;
consulte-o pelo navegador da app.

## O recibo

Por artigo, o `.procedencia.json` e o parágrafo `Fonte:` trazem: título, DOI, versão obtida,
licença, rota e etiqueta, onde está salvo, hash, páginas, data da tentativa e da conferência; e,
quando não abriu, o diário, as pendências e a data de reavaliar. Uma linha de ressalva entra
sozinha quando a versão não é a publicada, e outra quando a rota é C.

## Ferramentas desta máquina

O que cada conector e ferramenta alcança, com os limites **medidos** em 16/09/2026 (portão de
cookies da Springer, cota do Tavily, OAuth do Exa, 403 do Cloudflare no PeerJ, no CORE e no Open
Policy Finder, o que o scite entrega e o que só diz que entrega, o rascunho no Gmail, o
`hf://papers`): `references/conectores.md`. Os identificadores dos conectores do claude.ai
carregam um uuid que muda entre instalações; localize pelo sufixo com `ToolSearch`.

## Conferência

O protocolo de seis passos (versão, texto e não resumo, os companheiros do número, texto contra
tabela, a ressalva dos autores, a data), a forma do parágrafo `Fonte:` e a regra do que entra no
repositório estão em `references/conferencia.md`. As APIs, seus parâmetros e as armadilhas que
respondem HTTP 200 com erro dentro estão em `references/apis.md`. O pedido ao autor, com as
regras e os modelos, em `references/pedido-ao-autor.md`.

## Fora do escopo

Revisão de literatura e síntese de vários artigos: `deep-research` (web e relatório multi-fonte)
e o agente `academic-researcher` (acha, avalia e devolve DOIs, sem Bash: abrir e conferir é
aqui). Lei, acórdão, dado público: `legislacao-br`. Pesquisa web geral: `search-specialist`,
`research-orchestrator`. PDF já baixado que precisa virar Markdown fiel: `pdf-to-markdown`. Foto
ou digitalização sem camada de texto: `ocr-com-evidencia`.
