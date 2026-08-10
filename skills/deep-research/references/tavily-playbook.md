# Tavily Playbook

Tavily is a search API **purpose-built for AI agents**, with context engineering on the tool side: instead of dumping raw pages, it returns the most relevant content chunks per source, lowering tokens, latency, and hallucination downstream. It complements Exa: where Exa is semantic discovery, Tavily is precision retrieval with hard filters (dates, domains, country, topic) plus extraction, crawling, and a managed research endpoint.

## Query rules

1. **Under 400 characters.** Tavily degrades on long queries — the opposite of Exa.
2. **Break complex questions into parallel sub-queries.** Instead of one massive query about "company ABC's competitors, financials and recent moves", fire three: `Competitors of ABC`, `Financial performance of ABC`, `Recent developments of ABC`.
3. Focused natural questions or tight keyword phrases both work; no need for Exa-style link-description phrasing.

## MCP tools available

### `Tavily:tavily_search`
- `search_depth`:
  - `advanced` (default for deep research): highest relevance; returns up to 3 semantic chunks per URL with context engineering baked in. Costs more, worth it for precision questions.
  - `basic`: balanced; one NLP summary per URL. Good for landscape mapping.
  - `fast` / `ultra-fast`: latency-critical only; rarely needed in deep research.
- `topic: news`: routes to the news agent; pairs with `time_range` (`day`/`week`/`month`/`year`)
- `start_date` / `end_date` (YYYY-MM-DD): exact windows — unique capability vs Exa
- `country`: boost results from a country (full name, e.g. `Brazil`) — only with `topic: general`. **Default to `country: Brazil` + `search_depth: advanced` for Brazilian regulatory, legal, political, and news content.**
- `include_domains` / `exclude_domains`: pin to trusted sources (e.g. `["sec.gov"]`, `["gov.br", "planalto.gov.br"]`, `["arxiv.org"]`)
- `exact_match: true`: when the query has quoted phrases that must appear verbatim (names, error messages)
- `max_results`: default 5; raise to 8–10 for discovery passes
- Each result carries a relevance `score` — treat `score < 0.5` as weak evidence; use scores to pick extraction targets.

### `Tavily:tavily_extract`
- `urls`: batch list
- `query`: **always set when you know what you're looking for** — reranks and returns only relevant chunks instead of the full page (major token savings)
- `extract_depth: advanced`: for tables, embedded/structured content, LinkedIn, protected sites
- Canonical pipeline: search (advanced) → filter results by `score > 0.5` → dedupe URLs → extract with targeted `query`

### `Tavily:tavily_crawl`
- Crawls a site from a root URL; the only multi-page tool in the stack
- `instructions`: natural language ("Find API docs and migration guides")
- `max_depth` / `max_breadth` / `limit`: keep conservative (depth 1–2, limit ≤ 30) to control volume
- `select_paths`: regex like `/docs/.*` to stay on-topic
- Best for: official documentation, government portals, legislative sites, company knowledge bases

### `Tavily:tavily_research` (managed escalation)
- Full multi-step research workflow in one call: searches from multiple angles, analyzes, returns a structured report with citations
- `model`: `mini` for narrow tasks (few subtopics), `pro` for broad tasks (many subtopics), `auto` to let it decide
- Use as a *component*, not a replacement: delegate a broad slice, then independently verify its key claims (e.g. with Exa) before incorporating
- Rate limit: 20 req/min — don't loop it

## Context-engineering lessons from Tavily's own deep research agent

These shaped this skill's workflow; honor them:
1. **Distill, don't propagate.** After each tool batch, compress outputs into short reflections (claim + source + confidence) and carry only those forward. Return to raw sources only when writing the final deliverable. (Tavily cut token use 66% vs ReAct-style propagation with this pattern.)
2. **Global source deduplication.** Track every URL seen across both engines; never re-read, and notice when new searches stop surfacing new domains — that's the signal to widen or stop.
3. **Don't overfit to one research thread.** If three consecutive batches explore the same subtopic, force a pivot to an untapped dimension.
4. **Small toolset, used well**, beats many tools used confusedly.

## Where Tavily is weaker (route to Exa instead)

- Vague/exploratory queries where you can't articulate keywords — Exa's neural index wins
- Finding niche personal blogs, think pieces, "the best essay about X"
- Entity-centric people/company discovery (Exa's specialized indexes)
