---
name: deep-research
description: Advanced multi-phase research methodology powered by Exa (semantic/neural search) and Tavily (agentic search, extract, crawl) as primary instruments, with native web_search as fallback. Use whenever the user asks for deep research, thorough investigation, comprehensive analysis, literature review, market research, competitive analysis, due diligence, fact-finding, "pesquisa profunda", "investigue a fundo", "levante tudo sobre", or any task requiring systematic multi-source information gathering with verification and synthesis — even if they don't say "research" but want authoritative, well-sourced answers on complex topics. Also use when the user explicitly asks to search with Exa or Tavily. Do NOT use for single-fact lookups answerable in one search, nor for media coverage analysis (use repercussao-midiatica) or Big Tech intelligence reports (use bigtech-analyst), though this skill can power their retrieval layer.
---

# Deep Research Skill

Systematic methodology for comprehensive research, built around a dual-engine retrieval core: **Exa** (neural/semantic search over a curated index) and **Tavily** (agentic search with built-in context engineering, extraction, and crawling). The two engines have complementary failure modes — running both in parallel and triangulating is the default posture, not an optimization.

## Core Philosophy

1. **Breadth** — cast a wide net across source types and *across engines*
2. **Depth** — drill into primary sources via extraction/crawling
3. **Verification** — cross-reference claims across independent sources *and* independent retrieval systems
4. **Synthesis** — distill findings into reflections as you go; connect them at the end
5. **Transparency** — clear provenance (URL + date + engine) for every claim
6. **Token discipline** — prefer highlights/chunks over raw dumps; distill, don't hoard

## Tool Stack & Routing

Always check whether the Exa and Tavily MCP tools are available (load via `tool_search` if deferred). They are the primary instruments; native `web_search`/`web_fetch` are the fallback when MCPs are unavailable or for quick sanity checks.

**Connected instruments (exact tool IDs):** Exa — `mcp__exa__web_search_exa`, `mcp__exa__web_fetch_exa`. Tavily — `mcp__tavily__tavily_search`, `mcp__tavily__tavily_extract`, `mcp__tavily__tavily_crawl` (now connected at user scope — previously this skill only had the native fallback). Tertiary/fallback: Brave (`mcp__brave-search__brave_web_search`, if keyed) and native `WebSearch`/`WebFetch`.

| Need | First choice | Why |
|------|-------------|-----|
| Exploratory/conceptual discovery, "find me the best X about Y" | `Exa:web_search_exa` | Neural search excels when precise terms are unknown; finds semantically dense, niche content |
| Hard facts, news, current events, recency-sensitive | `Tavily:tavily_search` (`topic: news` or `time_range`) | Date/domain filters, news agent, freshness control |
| Country-specific content (e.g. Brazilian regulatory/news) | `Tavily:tavily_search` with `country` + `search_depth: advanced` | Country boost only exists on Tavily |
| Academic papers | `Exa:web_search_exa` (describe the paper) + Tavily with `include_domains` (arxiv.org, scholar, journals) | Exa has a research-paper index; Tavily pins domains |
| Companies / people / personal blogs | `Exa:web_search_exa` with `category:company` / `category:people` / personal-site phrasing | Exa's in-house specialized indexes |
| Full content of known URLs | `Exa:web_fetch_exa` (batch) or `Tavily:tavily_extract` (`query` reranks chunks; `extract_depth: advanced` for tables/LinkedIn/protected) | Both work; Tavily extract with `query` is more token-efficient for targeted needs |
| Whole docs site / multi-page source | `Tavily:tavily_crawl` with natural-language `instructions` | Only Tavily crawls |
| Managed end-to-end research (escalation) | `Tavily:tavily_research` (`mini` for narrow, `pro` for broad) | Multi-angle search + synthesized cited report in one call |
| MCPs unavailable | native `web_search` + `web_fetch` | Fallback |

**Query style differs radically per engine — this matters more than any parameter:**
- **Exa**: write a semantically rich *description of the ideal page*, as if sharing a link. Declarative, often ending in a colon. ❌ `"LDL apheresis Brazil cost"` → ✅ `"Detailed clinical overview of LDL apheresis availability and cost in Brazil:"`
- **Tavily**: focused question or keyword query **under 400 characters**; break complex questions into multiple sub-queries fired in parallel.

Read `references/exa-playbook.md` and `references/tavily-playbook.md` before the first searches of a session — they contain the full parameter guidance, query patterns, and anti-patterns per engine.

## Research Workflow

```
Phase 1: Scope → Phase 2: Parallel Discovery → Phase 3: Deep Investigation
Phase 4: Verification → Phase 5: Synthesis → Phase 6: Deliverable
```

### Phase 1: Scope Definition

Decompose the query into atomic sub-questions; identify dimensions (historical, current, projections, expert, empirical, contrarian); define success criteria. Each sub-question becomes a Tavily sub-query AND an Exa page-description — write both phrasings up front.

### Phase 2: Parallel Discovery (dual-engine, 4–12 calls)

Fire Exa and Tavily **in parallel on each sub-question** (batch multiple tool calls in a single turn whenever possible):

- Exa: exploratory phrasing, `numResults` 5–10, rely on highlights
- Tavily: `search_depth: advanced` for high-precision questions, `basic` for landscape; add `topic: news`/`time_range` for recency; `country` for geo-specific
- Contrarian pass: at least one query per engine targeting criticism/counterarguments
- Note where the engines *disagree or don't overlap* — that's signal, not noise

After each batch: **distill into 2–4 bullet reflections** (claim + source + confidence). Carry only reflections forward, not raw content. Deduplicate URLs across engines globally.

### Phase 3: Deep Investigation (5–20 calls)

Based on reflections: follow citation chains (extract the cited primary sources), expert deep-dives (Exa `category:people` / personal sites), data hunting (Tavily `include_domains` on official sources), gap filling, contradiction investigation. Use `tavily_extract` with a targeted `query` or `Exa:web_fetch_exa` to pull full content only from the 3–8 highest-value URLs. For documentation-heavy topics, one `tavily_crawl` of the canonical site often beats ten searches.

**Escalation rule**: if after Phase 2 the topic reveals itself as very broad (5+ substantial subtopics), consider delegating a slice to `Tavily:tavily_research` (model `pro`) and integrating its cited output as one more source — then verify its key claims independently with Exa.

### Phase 4: Source Verification

For each key claim: traceable to primary source? Confirmed by ≥2 independent sources (ideally surfaced by *different engines*)? Credible contradictions? Current? Bias/conflicts? Tavily relevance `score` < 0.5 is a weak-evidence flag. See `references/source-evaluation.md`.

### Phase 5: Synthesis

Cluster reflections by theme/timeline/perspective; build the narrative; tag confidence (High/Medium/Low/Uncertain); state limitations explicitly. Only now return to raw sources for exact figures and quotes for the deliverable. See `references/synthesis-patterns.md`.

### Phase 6: Deliverable

Use `scripts/research_tracker.py` to organize findings if the corpus is large. Formats in `references/report-templates.md`. For polished PDF briefings, hand off to the **briefing-designer** skill. Every claim cited with URL; methodology note listing engines and query count.

## Adaptive Patterns

| Topic Type | Engine emphasis |
|------------|----------------|
| Controversial | Both engines, contrarian queries mandatory, note affiliations |
| Technical/docs | Exa exploratory + `tavily_crawl` on official docs; version-aware queries |
| Current events | Tavily `topic: news`, `time_range`; corroborate before asserting |
| Historical/academic | Exa research-paper phrasing + Tavily `include_domains` academic |
| Market/competitive | Exa `category:company` + `category:financial report`; Tavily on sec.gov, IR pages |
| Brazil-specific | Tavily `country: Brazil` + `search_depth: advanced`; Exa for PT-BR think pieces |

## Quality Checkpoints

Before finalizing: all claims sourced? Both engines used (or fallback justified)? Conflicts addressed? Gaps acknowledged? Confidence stated? Primary sources traced? Reflections (not raw dumps) drove the synthesis? Methodology transparent?
