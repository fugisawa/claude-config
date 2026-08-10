# Search Strategies — Dual-Engine Routing & Fallback Patterns

Engine-specific guidance lives in `exa-playbook.md` and `tavily-playbook.md`. This file covers cross-engine strategy and the fallback path when MCPs are unavailable.

## Parallel triangulation (default posture)

For every research sub-question, write TWO phrasings up front and fire both in the same turn:

| Sub-question | Exa phrasing | Tavily phrasing |
|---|---|---|
| Is omega-3 linked to AF risk? | `Recent cardiology meta-analysis on high-dose omega-3 supplementation and atrial fibrillation risk:` | `omega-3 high dose atrial fibrillation risk meta-analysis` (`include_domains` optional: pubmed/journals) |
| Strix Halo mini-PC market state | `Hands-on review of AMD Strix Halo mini PC for local LLM inference:` | `AMD Strix Halo mini PC release price` (`time_range: month`, `topic: news`) |

Interpretation of overlap:
- **Both engines converge on the same sources/claims** → strong signal, high confidence
- **Engines surface disjoint sources agreeing on the claim** → strongest signal (independent confirmation)
- **Engines disagree** → investigate, don't average; one index may be stale or the topic contested
- **One engine returns nothing useful** → expected occasionally; note it and lean on the other, but rephrase once before giving up

## Iteration strategies (engine-agnostic)

- **Funnel**: landscape query → narrowed aspect → maximum specificity
- **Expansion**: verify a specific claim → understand its context → map adjacent topics
- **Citation chain**: find claim source → extract what it cites → search the primary sources → find who cites the original (Exa is excellent at "papers similar to / citing this idea" via description)
- **Expert discovery**: find names (Tavily) → find their work (Exa `category:people`, personal-site phrasing) → find interviews/talks

## Stop conditions

Stop searching a thread when: (a) two consecutive batches add no new domains or claims, (b) the sub-question is answered with ≥2 independent confirmations, or (c) you've hit ~5 calls on a single sub-question — escalate to extraction/crawl or flag as a gap instead.

## Fallback: native web_search / web_fetch only

When Exa/Tavily MCPs are unavailable, fall back to classic keyword craft:

- Keep queries 1–6 words; start broad, add specificity iteratively
- Source-type targeting by vocabulary: "study", "peer reviewed", "site:.gov"-style terms (as words, not operators, in claude.ai), outlet names, "annual report", "transcript", "interview"
- Contrarian pass: "criticism", "debunked", "problems with", "arguments against"
- Temporal: append the current year; "latest", "recent"
- Use `web_fetch` aggressively on the best results — snippets alone are not deep research
- Quality signals: known publications, author bylines, dates, citations present; caution on undated, unattributed, sensational, or single-source claims

## Result evaluation shortcuts

Read first: primary sources cited by multiple results; recent authoritative publications; comprehensive overviews from quality sources. Read for verification: alternative perspectives, criticism, older foundational sources. Verify surprising results by searching the claim directly, searching for debunking, and checking the source's credibility.
