# A escada de acesso

Cada degrau diz o que se tenta, com qual ferramenta, e o que decide parar. A ordem é a do custo
e da qualidade da cópia: primeiro o que uma chamada de API resolve, depois o que exige busca,
depois o que exige outra pessoa. Sci-Hub, LibGen e Anna's Archive não são degrau, por razão que
a seção final explica.

## 1. APIs abertas (`artigo.py abrir`)

O script consulta, nesta ordem, e junta os candidatos:

- **Crossref** (`/works/{doi}`): metadados de referência e os links de mineração de texto que
  a editora declara; quase sempre exigem assinatura, mas custam uma chamada.
- **OpenAlex** (`/works/doi:{doi}`): `oa_status` (`gold`, `hybrid`, `bronze`, `green`,
  `closed`), `best_oa_location.pdf_url`, todas as `locations` com `pdf_url`, PMID e PMCID.
- **Unpaywall** (`/v2/{doi}?email=`): a base mais completa de cópias legais; só roda com
  e-mail (`ARTIGOS_EMAIL` ou `--email`), porque a API rejeita endereço de mentira com 422.
- **Semantic Scholar** (`/paper/DOI:{doi}?fields=openAccessPdf,externalIds`): mais um
  `pdf_url`, e os identificadores arXiv e PMC quando o OpenAlex não os trouxe.
- **Europe PMC** (`/search?query=DOI:"…"` e depois `/{PMCID}/fullTextXML`): o XML JATS do
  texto integral, que responde 404 honesto quando o artigo não é aberto. É o degrau que salva
  quando a editora está atrás de Cloudflare.
- **arXiv** (`/pdf/{id}`): quando algum dos anteriores trouxe o identificador.

Os candidatos são ordenados por formato (PDF, XML, página), versão (publicada, aceita,
submetida) e degrau, e o primeiro que é texto de verdade vence. **Pare aqui** quando o diário
imprimir `ABERTO`. Quando imprimir `NÃO ABERTO`, o diário lista o que cada API respondeu; leve
esse diário adiante, porque ele já elimina degraus manuais (`oa_status=closed` no OpenAlex e
nada no Unpaywall significam que não há cópia em repositório indexado).

## 2. Cópia do autor

Autores depositam a versão aceita, e às vezes a publicada, no site pessoal, no repositório da
universidade e em redes acadêmicas. Foi o degrau que resolveu o caso de 16/09/2026: o coautor
Brady Roberts guarda o PDF da versão publicada em `bradyrtroberts.ca`.

- `WebSearch` com o título exato entre aspas e `filetype:pdf`; depois o título com `pdf` e
  `site:.edu`; depois o nome de cada autor com "publications" ou "papers".
- Repositórios institucionais respondem bem ao `WebFetch`; ResearchGate e Academia.edu pedem
  conta para baixar, mas a página confirma que a cópia existe (e aí vale o pedido ao autor).
- Achou um PDF: rode `artigo.py abrir <doi> --listar` para ter os metadados, baixe o PDF com
  `WebFetch` ou `curl -L -o`, e confira o cabeçalho antes de acreditar na versão: periódico,
  DOI, datas, paginação. Registre a origem à mão no parágrafo `Fonte:`.

**Pare aqui** quando o cabeçalho confirmar a versão. Cópia sem cabeçalho de periódico é versão
aceita ou pré-publicação, e o material diz isso.

## 3. Pré-publicação

- **OSF Preprints** (cobre PsyArXiv, EdArXiv, SocArXiv, MetaArXiv): a API
  `https://api.osf.io/v2/preprints/?filter[title]=<título>` lista; cada item tem
  `links.preprint_doi` e o arquivo em `relationships.primary_file`. O site `osf.io` rende
  página vazia no navegador da app; use a API.
- **arXiv**: `https://export.arxiv.org/api/query?search_query=ti:"<título>"`, Atom XML; depois
  `/pdf/{id}`.
- **SSRN** (economia, direito, ciências sociais): só página; `WebSearch` com o título.

Pré-publicação confere a existência e o método; número de pré-publicação que não bate com a
versão publicada é a versão publicada que manda.

## 4. Conectores com texto integral

- **scite `read_fulltext`**: texto corrido de artigo aberto com licença permissiva, 8.000
  caracteres por chamada; `source` precisa ser `"fulltext"`, porque `"abstract"` significa que
  o texto não foi servido. `search_literature` com `dois` e `term` devolve cinco trechos que
  contêm o termo, e é o modo mais barato de conferir um número.
- **PubMed/PMC**: só biomedicina e ciências da vida; `convert_article_ids` do PMID ao PMCID e
  `get_full_text_article`.
- **Consensus** e o conector de corpus (`semanticSearch`): passagens e metadados, não o texto;
  servem para achar o DOI e para saber que há contestação.

## 5. Navegador da app

`browser_batch` com `navigate` para `https://doi.org/<doi>` e `get_page_text`. Ele passa o
portão de cookies que trava o `WebFetch` (Springer, Nature, Elsevier) e mostra o que a editora
mostra a quem não assina: resumo, referências, datas de recebimento e aceite, material
suplementar (muitas vezes aberto), e às vezes uma prévia com as primeiras páginas. Não passa a
barreira de pagamento, e a skill não tenta.

## 6. Dados e código do artigo

Meta-análise e estudo empírico costumam depositar dados e código no OSF, no GitHub ou no
Zenodo, com o endereço no artigo ou na página do DOI. A API do OSF
(`https://api.osf.io/v2/nodes/<id>/files/osfstorage/`) lista os arquivos, cada um com
`links.download`. Com o `.csv` e o `.R` dá para recomputar o tamanho de efeito, que é uma
conferência mais forte que reler o número e não substitui a leitura da frase onde ele está.

## 7. Pedido ao autor, e o acesso institucional

O modelo do pedido está em `pedido-ao-autor.md`; o Daniel envia. Em paralelo, o acesso que
ele tem por vínculo: Portal de Periódicos da CAPES pela CAFe, biblioteca da instituição, e
empréstimo entre bibliotecas para o que a assinatura não cobre.

## Quando nada abre

A bandeira `⚑ não conferido em fonte primária` fica no material, a fonte secundária entra
rotulada, e o diário do que foi tentado, com data, vai junto — assim a próxima sessão começa
do degrau 7, não do 1.

## Por que o Sci-Hub não é degrau

Em 16/09/2026 o Daniel pediu que o Sci-Hub entrasse na escada, e depois escreveu um ensaio
com a tese de que qualquer artigo publicado deveria ser legível por quem já o financiou: bem
não rival, custo marginal zero, autores e revisores não remunerados, margens de 35–40% da
editora, mandatos do NIH, do Plan S e do Horizon Europe, o art. 15 do Pacto de Direitos
Econômicos, Sociais e Culturais e os arts. 5º, XIV, e 218 da Constituição. O argumento é sobre
**como a norma deveria ser**, e os financiadores estão de fato mudando a norma nessa direção.
A licença que hoje cobre um arquivo específico é outra coisa: o Sci-Hub redistribui cópias sem
ela, e a skill não executa esse ato, por decisão de quem a escreveu, não por dúvida sobre o
mérito do ensaio. O que a skill deve ao Daniel em troca é esgotar o acesso legítimo de verdade
(os sete degraus acima), redigir o pedido ao autor no mesmo minuto, e nunca fingir que um
número foi conferido quando não foi.
