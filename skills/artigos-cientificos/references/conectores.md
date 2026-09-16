# Os conectores e ferramentas desta máquina, e o que cada um alcança

Medido em 16/09/2026, na conferência da meta-análise de Tharumalingam e col. (2025). O que
falhou aqui falha de novo; o que passou é o caminho. Os identificadores dos conectores do
claude.ai começam por `mcp__<uuid>__` e o uuid pode mudar entre instalações: localize pelo
sufixo com `ToolSearch` (`select:` não serve sem o uuid; use a busca por palavra, por
exemplo "search_literature", "read_fulltext", "get_full_text_article").

| Ferramenta | Serve para | Limite medido |
|---|---|---|
| `WebFetch` | página aberta, PDF em repositório aberto | Springer/Nature respondem 303 para `idp.springer.com/authorize` (portão de cookies) e o `WebFetch` devolve o redirecionamento sem seguir. Sites atrás de Cloudflare (PeerJ, `europepmc.org`) devolvem 403 |
| `mcp__fetch__fetch` | — | devolve a casca "A required part of this site couldn't load"; não use para editora |
| Tavily `tavily_extract` | página, com reordenação por consulta | cota do plano estourada em 16/09/2026 ("exceeds your plan's set usage limit") |
| Exa `web_search_exa` / `web_fetch_exa` | busca neural, texto integral de URL | exige OAuth e a sessão não interativa não roda o fluxo; diga ao Daniel que autorize pelo `/mcp` |
| Navegador da app (`mcp__Claude_Browser__browser_batch`, `navigate`, `get_page_text`) | página que o `WebFetch` não abre | passa o portão de cookies e mostra o que a editora mostra a quem não assina: resumo, referências, material suplementar, prévia. A barreira de pagamento fica. `osf.io` rende página vazia; use a API |
| `WebSearch` | achar a cópia do autor: `"<título exato>" filetype:pdf`, `"<título>" pdf site:.edu`, nome do autor + "publications" | só EUA; funciona para inglês. Foi o degrau que resolveu o caso |
| `curl` e o `urllib` dos scripts | APIs abertas (Crossref, OpenAlex, Unpaywall, Semantic Scholar, Europe PMC REST, OSF, arXiv) e repositórios institucionais | sites atrás de Cloudflare (PeerJ, `europepmc.org`) devolvem 403 aos dois, com ou sem agente de usuário de navegador; para esses, o texto vem pelo REST do Europe PMC (XML), por outra localização do Unpaywall ou pelo scite |
| Conector **scite** (`search_literature`, `read_fulltext`, `citation_graph`, `report_citations`, coleções) | busca por termo/DOI com citações classificadas (apoia, contrasta, menciona), avisos editoriais (retratação, correção), texto integral de artigo aberto | `read_fulltext` devolve `source: "fulltext"` só para artigo aberto com licença permissiva; `"abstract"` significa que você NÃO leu o artigo. `search_literature` com `dois` + `term` devolve até 5 trechos de ~500 caracteres por chamada; varie o termo para ler seção por seção |
| Conector **PubMed** (`search_articles`, `get_article_metadata`, `convert_article_ids`, `get_full_text_article`, `get_copyright_status`) | biomedicina e ciências da vida | só o que o PubMed indexa; psicologia da educação, economia e direito ficam de fora. Texto integral só do PMC (`convert_article_ids` PMID → PMCID antes) |
| Conector **Consensus** (`search`) | busca com resumo, contagem de citações, quartil do periódico, tipo de estudo | sem texto integral no plano gratuito; não aplique filtros que o pedido não pediu |
| Conector de corpus (`semanticSearch`) | passagens com citação autor-ano e DOI para uma pergunta em linguagem natural | o corpus não é declarado; trate a passagem como pista para achar o DOI, nunca como leitura do artigo |
| Agente `academic-researcher` | achar e sintetizar literatura com rigor de citação | não tem `Bash`: ele acha e devolve DOIs; abrir e conferir é com esta skill |
| Conector **Gmail** (`create_draft`, `list_drafts`, `get_draft`) | o pedido ao autor como RASCUNHO, com o `to`, `subject` e `body` do `artigo.py pedido` | só rascunho: `send_message` não entra na skill, e quem envia é o Daniel. O conector não acha o e-mail do autor; ele vem da primeira página do artigo ou da página do DOI |
| Conector **Hugging Face** (`hf_fs`) | `cat hf://papers/<arxiv-id>/paper.md` devolve o texto do artigo do arXiv que o Hub indexa, para ler sem baixar | só arXiv, e é pré-publicação: o recibo diz isso |
| CORE (`api.core.ac.uk`) e Open Policy Finder (`v2.sherpa.ac.uk`) | agregador de repositórios; política de compartilhamento e embargo por periódico | medido em 16/09/2026: os dois respondem o desafio do Cloudflare ou 403 a script desta máquina, com ou sem chave; consulte o embargo pelo navegador da app |
| COMUT (IBICT) | cópia paga de artigo pela rede de bibliotecas parceiras | ativo: 971 pedidos em 2025, 61% atendidos, pelo balanço do IBICT de janeiro de 2026; entra só com biblioteca e orçamento no perfil do `SKILL.md` |

## Padrões de uso que funcionam

**Ler um artigo aberto pelo scite, sem despejar tudo no contexto.**
`read_fulltext(doi, offset=0)` e, enquanto `hasMore`, `offset += returnedChars`. Cada página tem
8.000 caracteres. Para conferir um número, prefira `search_literature(dois=[doi], term="playback
speed 2x Hedges")`: cinco trechos que contêm o termo, e nada mais.

**Descobrir se um artigo foi retratado ou corrigido antes de citar.**
`search_literature(dois=[doi])` sem `term` devolve `editorialNotices`; o PubMed devolve o
mesmo em `get_article_metadata`. Correção publicada muda número: confira a versão corrigida.

**Ver quem contesta o resultado.**
`search_literature(dois=[doi])` traz `tally.contrasting` e os trechos; `citation_graph(seeds=[doi],
direction="in", include_intent=true)` traz o grafo com a intenção de cada citação. Um resultado
sem citação contrastante em campo movimentado costuma ser recente demais, não incontroverso.

**Biomédico: do PMID ao texto.**
`search_articles` → PMID → `convert_article_ids` → PMCID → `get_full_text_article`. Só ~6 milhões de
artigos têm texto no PMC; os outros caem na escada normal.

**A página da editora, quando o `WebFetch` bate no portão.**
`browser_batch` com `navigate` para `https://doi.org/<doi>` e `get_page_text`. Serve para ler o
resumo, a lista de referências, as datas (recebido, aceito, publicado) e o material suplementar,
que muitas vezes é aberto mesmo quando o artigo não é.

**Dados e código do artigo (OSF).**
`https://api.osf.io/v2/nodes/<id>/files/osfstorage/` lista os arquivos; cada um tem `links.download`.
Com os dados dá para recomputar o resultado, o que é uma conferência mais forte que reler o
número, e não substitui a leitura do texto.

**O pedido ao autor, sem enviar nada.**
`artigo.py pedido <doi> --tema "…" --para <e-mail> --json` devolve `to`, `subject` e `body`; passe-os
ao `create_draft` do conector Gmail e diga ao Daniel onde o rascunho está. A pendência que o mesmo
comando imprime (`pedido ao autor rascunhado em …; sem resposta, não repetir antes de …`) vai para o
recibo do material com `artigo.py abrir <doi> --pendencia "…" --reavaliar-em <data>`.
