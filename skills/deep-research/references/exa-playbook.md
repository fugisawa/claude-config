# Exa Playbook

Exa is a **neural search engine** built on embeddings and "next-link prediction": it predicts which links are most relevant to the *semantic meaning* of your query, not keyword matches. It maintains its own curated, high-quality index with specialized coverage of companies, people, research papers, and personal sites. An internal router (`auto`) decides between neural and keyword retrieval per query.

## The single most important rule: query phrasing

Frame queries as if you're **describing a link to someone** — a natural-language description of the ideal page. Declarative statements outperform questions; many effective prompts end with a colon, mimicking how humans share links.

| Bad (keyword reflex) | Good (Exa-native) |
|---|---|
| `best restaurants SF` | `Here is the best restaurant in San Francisco:` |
| `LangGraph vs PydanticAI` | `In-depth engineering blog post comparing LangGraph and PydanticAI for production agent systems:` |
| `Lp(a) treatment 2026` | `Recent clinical review of emerging therapies targeting elevated lipoprotein(a):` |
| `what is RAG` | `This is the clearest technical explanation of retrieval-augmented generation:` |

Additional phrasing levers:
- Add qualifiers that describe the *kind* of page: "academic paper", "engineering blog post", "official documentation", "long-form investigative article", "contrarian take"
- Add tone/context modifiers: "skeptical", "practitioner-written", "peer-reviewed"
- Longer, semantically rich queries are fine — Exa thrives on them (unlike Tavily)

## MCP tools available

### `Exa:web_search_exa`
- `query` (required): natural-language description per above
- `numResults`: default 10; use 5 for targeted checks, 10+ for landscape mapping
- Category targeting via inline syntax: `category:company` for company research, `category:people` for non-public figures (LinkedIn-backed index). Use sparingly — most queries should omit category. (The underlying API also supports `research paper`, `news`, `personal site`, `financial report` categories; if only company/people work inline, emulate the others through phrasing: "peer-reviewed research paper about…", "SEC filing or earnings report from…", "personal blog post by…")
- Returns highlights (token-efficient excerpts, ~10× fewer tokens than full text). If highlights are insufficient, follow up with `web_fetch_exa` on the best URLs.

### `Exa:web_fetch_exa`
- `urls`: **batch multiple URLs in one call** — never fetch one at a time
- `maxCharacters`: default 3000; raise to 6000–15000 only for the few sources that anchor the analysis

## Where Exa shines (route here)

- Exploratory research where precise terminology is unknown
- Niche, semantically dense content: think pieces, engineering blogs, personal sites
- Entity research: companies (funding, competitors), people (background, expertise)
- Academic discovery by *describing* the paper you wish existed
- Finding "more like this" — pivot off a great source by describing it

## Where Exa is weaker (route to Tavily instead)

- Hard recency filters by exact date ranges (Tavily `start_date`/`end_date`)
- Country-boosted results (Tavily `country`)
- Strict domain inclusion/exclusion lists
- Crawling entire sites
- Proper-noun keyword lookups sometimes do better on Tavily/classic search — if Exa's neural results miss, rephrase or switch engines rather than repeating

## Anti-patterns

1. **Sending keyword queries.** The #1 failure mode for LLMs using Exa. Rephrase as a page description.
2. Repeating a near-identical query after poor results — rephrase substantively or switch engines.
3. Fetching full text of every result — use highlights first, fetch only the anchors.
4. Using category filters on general queries — categories narrow the index; omit unless the query is genuinely entity-centric.
