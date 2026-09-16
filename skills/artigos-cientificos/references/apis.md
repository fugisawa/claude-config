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
- ⚠ Sem chave, 429 aparece cedo em rajada; o script repete três vezes com espera dobrada.

## Europe PMC

- `GET https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:"{doi}"&format=json&resultType=lite`
  → `resultList.result[]{pmcid,…}`.
- `GET …/rest/{PMCID}/fullTextXML` → JATS `<article>`; **404 significa não aberto**, que é a
  resposta honesta (o eFetch do NCBI devolve 200 sem `<body>` no mesmo caso).
- ⚠ Erro vem com HTTP 200 e `errCode` no corpo, sem `resultList`. O script trata ausência de
  `resultList` como "sem resultado".
- ⚠ O site `europepmc.org` (inclusive `?pdf=render`) está atrás de Cloudflare e devolve 403 a
  clientes sem navegador; o REST responde.

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
- Nada de laço sobre centenas de DOIs sem pausa: para lote, a busca é uma consulta com
  `per-page` maior, não cem consultas.
