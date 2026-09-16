---
name: artigos-cientificos
description: >
  Use quando houver artigo científico para ACHAR, ABRIR ou CONFERIR: buscar literatura sobre um
  tema ("tem estudo sobre…", "qual a meta-análise de…"), resolver um DOI ou uma citação, obter o
  texto integral (PDF ou XML) de um artigo, e conferir número, tabela ou afirmação dentro do texto
  antes de citar ("os valores batem com o artigo?", "abre a fonte primária", "confere na fonte").
  Sinais: DOI, "paper", "artigo", "meta-análise", "revisado por pares", "pré-publicação",
  "preprint", "paywall", "Sci-Hub", "quem cita", "foi retratado". Produz a cópia COM procedência
  (de onde veio, versão, hash, data) e o parágrafo "Fonte:" que entra no material. NÃO use para
  lei, jurisprudência ou dado público brasileiro (`legislacao-br`), pesquisa web geral
  (`deep-research`, `search-specialist`), PDF já em mãos para virar Markdown (`pdf-to-markdown`)
  nem foto de página (`ocr-com-evidencia`).
---

# Artigos científicos, com procedência

Um artigo só vale como fonte quando foi **aberto** — o texto, na versão certa — e quando quem
ler o material consegue repetir o caminho até ele. Esta skill produz três coisas, e nunca uma
sem as outras: os metadados que identificam o artigo, a cópia com o registro de procedência
(degrau que a achou, endereço, versão, hash, data), e a conferência do que se vai citar, feita
no texto e não no resumo.

Ela nasceu do caso de 16/09/2026: quatro tamanhos de efeito de uma meta-análise (Tharumalingam
e col., 2025) estavam no material com a bandeira "não conferidos em fonte primária". A página da
Springer mostrava só o resumo; o `WebFetch` bateu num portão de cookies; o Tavily estava sem
cota; o Exa exigia OAuth; o navegador da app passou o portão e parou na barreira de pagamento; a
cópia veio do site de um coautor, e a conferência achou uma divergência entre a tabela e o texto
que o resumo jamais mostraria. Cada ferramenta foi tentada às cegas. **A ordem que sobrou dessa
sessão é a escada abaixo.** Pediu-se então que o Sci-Hub entrasse no caminho; ele não entra, e a
seção *A regra que manda* diz por quê e o que entra no lugar.

## A regra que manda

- **Nunca cite o que não abriu.** Resumo, comentário de questão, texto de divulgação e a memória
  do modelo não são o artigo. O que não abriu fica com a bandeira `⚑ não conferido em fonte
  primária`, e fonte secundária entra rotulada como secundária.
- **Diga qual versão leu.** Publicada (diagramada pela editora, com paginação e DOI no cabeçalho)
  vale mais que aceita (manuscrito do autor depois da revisão por pares), que vale mais que
  pré-publicação. O número pode mudar entre elas.
- **Sci-Hub, LibGen, Anna's Archive e espelhos não entram**, nem quando o pedido vem com a
  autorização do Daniel. Eles redistribuem cópias que a licença da editora não permite
  redistribuir, e a skill não faz esse ato. O argumento de que o acesso deveria ser livre é
  sério e está registrado (`references/escada-de-acesso.md`, seção final): ele descreve a norma
  que os financiadores estão adotando, não a licença que hoje cobre o arquivo. O que a skill faz
  é esgotar o acesso legítimo, que no caso de 16/09 bastou, e deixar a bandeira quando não basta.
- **O e-mail do Daniel só vai para Crossref, OpenAlex e Unpaywall**, que o usam como
  identificação de cortesia (o Unpaywall o exige), e só se `ARTIGOS_EMAIL` estiver definido ou
  `--email` for passado. Nunca fixado no código, nunca em outro serviço.
- **Nada de despejar o artigo no contexto.** O texto extraído fica no disco; o que entra na
  conversa são as linhas que o `conferir` devolve, ou uma janela de `grep -n -C`. Um artigo de
  27 páginas vale ~25 mil tokens, e cada despejo entra na próxima compactação.

## Três pedidos, três rotas

| Pedido | Rota | O que sai |
|---|---|---|
| "Tem estudo sobre X?", "qual a meta-análise de Y?" | `buscar` (OpenAlex) e os conectores scite e Consensus; para síntese com rigor de citação, o agente `academic-researcher` | lista com ano, DOI, situação de acesso, citações |
| "Abre este artigo", "acha o PDF de <DOI ou citação>" | `resolver` → `abrir` → degraus manuais da escada | PDF ou XML + `.txt` + `.procedencia.json` + parágrafo `Fonte:` |
| "Confere se os números batem", "isso está mesmo no artigo?" | `abrir` → `conferir` → `references/conferencia.md` | relatório por expressão, com linha e contexto; a frase do material com a data da conferência |

## Comandos

```bash
S=~/.claude/skills/artigos-cientificos/scripts
export ARTIGOS_EMAIL="…"          # opcional: liga o Unpaywall e o polite pool (Daniel decide)
python3 $S/artigo.py resolver "https://doi.org/10.1007/s10648-025-10003-9"     # metadados (Crossref + OpenAlex)
python3 $S/artigo.py buscar "video lecture playback speed test performance" --desde 2020 -n 10
python3 $S/artigo.py abrir 10.1007/s10648-025-10003-9 --destino <scratch>/artigos --listar    # só lista os candidatos
python3 $S/artigo.py abrir 10.7717/peerj.4375 --destino <scratch>/artigos --conferido-em 2026-09-16
python3 $S/artigo.py conferir <scratch>/artigos/10-7717-peerj-4375.txt "g = -0,36" "k = 48" "p < .001"
python3 -m unittest discover -s ~/.claude/skills/artigos-cientificos/tests -q        # 40 testes, sem rede
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

## A escada, resumida (o detalhe está em `references/escada-de-acesso.md`)

| # | Degrau | Quem faz | Para quando |
|---|---|---|---|
| 1 | APIs abertas: Unpaywall, OpenAlex, Semantic Scholar, Europe PMC, arXiv, TDM da Crossref | `abrir` | o diário diz `ABERTO` |
| 2 | Cópia do autor: `WebSearch "<título exato>" filetype:pdf`, página pessoal, repositório da universidade, ResearchGate | você | achou PDF com cabeçalho do periódico (versão publicada) ou manuscrito aceito |
| 3 | Pré-publicação: OSF Preprints, PsyArXiv, EdArXiv, arXiv, SSRN | você, pela API do OSF ou `WebSearch` | achou; e anote que é pré-publicação |
| 4 | Conectores com texto: scite `read_fulltext` (`source` tem de ser `"fulltext"`), scite `search_literature` com `dois` + `term`, PubMed/PMC (biomédico) | você | o trecho que interessa apareceu |
| 5 | Navegador da app na página do DOI | você | leu resumo, referências, datas, suplemento — nunca passa a barreira |
| 6 | Dados e código do artigo (OSF, GitHub, Zenodo) | você, pela API | dá para recomputar o número, não para ler o texto |
| 7 | Pedido ao autor (`references/pedido-ao-autor.md`) e acesso institucional do Daniel (CAPES via CAFe, biblioteca) | o Daniel | a cópia chegou |

Em cada degrau que abre: pare, vá para a conferência. Se nenhum abre: a bandeira fica, e o
diário do que foi tentado vai para o material ou para o registro da sessão, com data.

## Ferramentas desta máquina

O que cada conector e ferramenta alcança, com os limites **medidos** em 16/09/2026 (portão de
cookies da Springer, cota do Tavily, OAuth do Exa, 403 do Cloudflare, o que o scite entrega e o
que só diz que entrega): `references/conectores.md`. Os identificadores dos conectores do
claude.ai carregam um uuid que muda entre instalações; localize pelo sufixo com `ToolSearch`.

## Conferência

O protocolo de seis passos (versão, texto e não resumo, os companheiros do número, texto contra
tabela, a ressalva dos autores, a data), a forma do parágrafo `Fonte:` e a regra do que entra no
repositório estão em `references/conferencia.md`. As APIs, seus parâmetros e as armadilhas que
respondem HTTP 200 com erro dentro estão em `references/apis.md`.

## Fora do escopo

Lei, acórdão, dado público: `legislacao-br`. Pesquisa web geral e relatório multi-fonte:
`deep-research`, `search-specialist`, `research-orchestrator`. Síntese de literatura com
avaliação de qualidade: agente `academic-researcher` (ele acha e devolve DOIs; abrir e conferir
é aqui). PDF já baixado que precisa virar Markdown fiel: `pdf-to-markdown`. Foto ou
digitalização sem camada de texto: `ocr-com-evidencia`.
