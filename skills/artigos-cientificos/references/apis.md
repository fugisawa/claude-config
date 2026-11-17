# As APIs, o que se pede a cada uma, e como elas falham com HTTP 200

Nenhuma exige chave. Onde há e-mail, ele é identificação de cortesia; o script só o envia se
`ARTIGOS_EMAIL` ou `--email` existir. As armadilhas marcadas com ⚠ foram adaptadas do
`paper-lookup` da K-Dense (MIT, conferido em 16/09/2026) e do caso do dia; as demais são as
que os testes desta skill cobrem.

## Crossref

- `GET https://api.crossref.org/works/{doi}?mailto=…` → `message` com `title[]`,
  `author[]{given,family}`, `container-title[]`, `issued.date-parts`, `volume`, `issue` (ou
  `journal-issue.issue`), `page` ou `article-number`, `is-referenced-by-count`, `license[]`,
  `link[]{URL,content-type}`.
- Busca por citação solta: `GET /works?query.bibliographic=<citação>&rows=5` (o script não usa;
  o `buscar` vai pelo OpenAlex).
- ⚠ O `link` com `content-type: application/pdf` é o endereço de mineração de texto da editora,
  e para Springer ele responde HTML de portão a quem não assina. O script o tenta por último.

## OpenAlex

- `GET https://api.openalex.org/works/doi:{doi}?mailto=…` → `open_access{is_oa,oa_status,oa_url}`,
  `best_oa_location{pdf_url,version,license,is_oa}`, `locations[]`, `ids{pmid,pmcid}`,
  `biblio{volume,issue,first_page,last_page}`, `cited_by_count`, `authorships[]`.
- `GET /works?search=<consulta>&per-page=10&filter=from_publication_date:2020-01-01&select=…`:
  busca com relevância; `select` reduz a resposta, que sem ele é grande.
- ⚠ `ids.pmcid` vem **sem** o prefixo `PMC` (`…/pmc/articles/5815332`); o Europe PMC exige
  `PMC5815332`. O script normaliza.
- ⚠ `locations[]` inclui localizações fechadas; só as com `is_oa: true` interessam.
- ⚠ O resumo vem como índice invertido (`abstract_inverted_index`), não como texto.
- Busca custa cota (uso gratuito diário); consulta por DOI é livre.

## Unpaywall

- `GET https://api.unpaywall.org/v2/{doi}?email=<real>` → `is_oa`, `oa_status`,
  `best_oa_location{url_for_pdf,url_for_landing_page,version,license,host_type}`,
  `oa_locations[]`.
- ⚠ E-mail de mentira (`test@example.com`) devolve 422. Sem e-mail, o script pula o degrau e
  escreve isso no diário.
- ⚠ O `/v2/search` anda instável; não é usado.
- `version` é o que diz qual versão a cópia é: `publishedVersion`, `acceptedVersion`,
  `submittedVersion`.

## Semantic Scholar

- `GET https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=title,openAccessPdf,externalIds,isOpenAccess`
  → `openAccessPdf{url,license}`, `externalIds{ArXiv,PubMed,PubMedCentral,DOI}`.
- ⚠ Sem chave, 429 aparece cedo em rajada; o script tenta três vezes ao todo, com espera dobrada.

## Europe PMC

- `GET https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:"{doi}"&format=json&resultType=lite`
  → `resultList.result[]{pmcid,…}`.
- `GET …/rest/{PMCID}/fullTextXML` → JATS `<article>`; **404 significa não aberto**, que é a
  resposta honesta (o efetch do NCBI devolve 200 sem `<body>` no mesmo caso; ver a seção dele).
- ⚠ O `fullTextXML` respondeu **500**, em 02/10/2026, a PMC4076289, um manuscrito do autor que o
  efetch do NCBI serviu inteiro. Diante do 5xx, o script tenta três vezes ao todo, com espera
  dobrada, e passa ao candidato seguinte.
- ⚠ Erro vem com HTTP 200 e `errCode` no corpo, sem `resultList`. O script trata ausência de
  `resultList` como "sem resultado".
- ⚠ O site `europepmc.org` (inclusive `?pdf=render`) está atrás de Cloudflare e devolve 403 a
  clientes sem navegador; o REST responde.

## E-utilities do NCBI (efetch)

- `GET https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={PMCID sem o prefixo}`
  → o artigo em JATS, dentro de `<pmc-articleset><article>…</article></pmc-articleset>`, com a
  folha de rosto (`<front>`: título, autores e resumo), o corpo (`<body>`) e as referências
  (`<back>`). Aceita o `id` também com o prefixo `PMC` (medido em 02/10/2026). É a única chamada
  do degrau: o PMCID vem do OpenAlex, do Semantic Scholar ou da busca do Europe PMC, e sem PMCID
  o degrau é pulado.
- A documentação das E-utilities pede dois parâmetros de cortesia, `&tool=artigos-cientificos&email=…`.
  O script só os acrescenta com `ARTIGOS_EMAIL` ou `--email`, e só ao endereço do pedido; o
  endereço que o recibo grava sai sem eles, mesmo quando o NCBI redireciona o pedido, porque vai
  para o parágrafo `Fonte:`, que entra no repositório, e o e-mail não pode entrar.
- ⚠ Artigo cuja editora não libera o XML devolve **200 sem `<body>`**: só a folha de rosto, com o
  resumo, e o comentário `The publisher of this article does not allow downloading of the full
  text in XML form` (PMC4121776, medido em 02/10/2026). O script recusa, e o diário diz
  `XML sem o corpo do artigo`.
- ⚠ PMCID inexistente devolve **200** com `<pmc-articleset><error id="…">The following PMCID is
  not available</error></pmc-articleset>`; como também não traz `<body>`, o script o recusa.
- ⚠ O manuscrito do autor depositado no PMC pelo programa de acesso público do NIH (NIH Public
  Access), como o de Reyna e col. (2014), PMC4076289, vem com `pmc-prop-manuscript` igual a `yes`
  em `<custom-meta>`; o XML do Europe PMC traz a mesma declaração como `is-manuscript` (visto só
  com `no`, em três XMLs do projeto; o `yes` não foi medido num manuscrito real). O texto é a versão aceita,
  não a publicada, e o recibo diz isso, com a ressalva. O identificador NIHMS
  (`<article-id pub-id-type="manuscript-id">`) não serve de marca: ele fica no XML depois que a
  editora substitui o manuscrito pela versão publicada, que vem com `pmc-prop-manuscript` igual a
  `no` (medido em 02/10/2026 em dois XMLs do projeto, um da Sage Choice e um da Springer).
- Em 02/10/2026 foi o degrau que abriu quando `europepmc.org` deu 403, o REST do Europe PMC deu
  500 e a página `pmc.ncbi.nlm.nih.gov` pediu reCAPTCHA a script.
- Sem chave, as E-utilities aceitam três pedidos por segundo, e o script faz um por artigo.

## arXiv

- `GET https://export.arxiv.org/api/query?id_list={id}` (Atom) e `GET https://arxiv.org/pdf/{id}`.
- ⚠ Parâmetro malformado devolve `totalResults: 1` com uma entrada chamada `Error`; espere 3 s
  entre chamadas seguidas.

## OSF

- `GET https://api.osf.io/v2/nodes/{id}/files/osfstorage/` → `data[]{attributes.name,links.download}`.
- `GET https://api.osf.io/v2/preprints/?filter[title]=…` para pré-publicações.
- ⚠ O site rende página vazia no navegador da app; use a API.

## Cortesia e limites

- Agente de usuário `artigos-cientificos/1.0 (skill do Claude Code) mailto:…`; `Accept`
  coerente com o que se quer (`application/json` nas APIs, `application/pdf,…` nos arquivos).
- Três tentativas com espera dobrada em 429 e 5xx; 4xx devolve na hora.
- No NCBI, `tool` e `email` vão só no endereço do pedido; o endereço que o recibo guarda sai sem eles.
- Nada de laço sobre centenas de DOIs sem pausa: para lote, a busca é uma consulta com
  `per-page` maior, não cem consultas.
