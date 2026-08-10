# Tavily in this configuration

*In English, because this page exists to be shared.*

Tavily is the default retrieval engine in this configuration. This page separates what is
Tavily's own work from what is mine, documents the routing rules I converged on, reports
measured usage, and describes the one layer I ended up building by hand.

---

## What is Tavily's

The eight `tavily-*` skills under `skills/` are **official** — cloned from
[tavily-ai/skills](https://github.com/tavily-ai/skills) in July 2026:
`tavily-search`, `tavily-extract`, `tavily-crawl`, `tavily-map`, `tavily-research`,
`tavily-cli`, `tavily-best-practices`, `tavily-dynamic-search`.

They are **not vendored into this repo** — install them from the source. (A separate
`tavily-web` skill is community-authored and unrelated to the official set.)

Worth naming one specifically: `tavily-dynamic-search` isolates search context from the
main agent loop. That is the pattern that keeps a long research run from drowning the
context window in raw page text, and it is the reason a 20-call investigation stays
coherent to the end.

## What is mine

| Path | What it is |
|---|---|
| [`skills/deep-research/references/tavily-playbook.md`](../skills/deep-research/references/tavily-playbook.md) | Routing playbook — parameter defaults, the relevance-score floor, the search→extract pipeline, and where I deliberately route *away* from Tavily |
| [`skills/deep-research/SKILL.md`](../skills/deep-research/SKILL.md) | Six-phase dual-engine research workflow that consumes the playbook |
| [`agents/search-specialist.md`](../agents/search-specialist.md) | Subagent running Exa and Tavily in parallel, triangulated |

## How I route

The playbook is the full version; these are the decisions that mattered most in practice.

**Queries stay under 400 characters, and complex questions get split.** Tavily degrades on
long queries — the opposite of Exa, where a long declarative description of the ideal page
is what works. One question about a company's competitors, financials and recent moves
becomes three parallel calls, not one.

**`country: Brazil` + `search_depth: advanced` is the default for Brazilian regulatory,
legal, political and news content.** This is the single highest-yield setting in the whole
configuration. Two thirds of my calls run at `advanced`; the precision is worth the cost
on any question where a wrong source is worse than no source.

**Relevance score is an evidence floor, not decoration.** `score < 0.5` is treated as weak
evidence and does not get cited. Scores also pick extraction targets, which makes the
canonical pipeline: search at `advanced` → filter by score → deduplicate URLs globally →
`tavily_extract` with a targeted `query` so only relevant chunks come back.

**`include_domains` for official sources, `crawl` for portals.** `["gov.br",
"planalto.gov.br"]` when a claim has to rest on primary law; `tavily_crawl` at depth 1–2
with `limit ≤ 30` for legislative and government sites, which are exactly the sites where
a general search engine returns the news article about the norm instead of the norm.

**`tavily_research` is a component, not a replacement.** I delegate a broad slice to it,
then verify its key claims independently against Exa before anything gets written down.

**Where I route to Exa instead:** vague or exploratory questions where I cannot articulate
the keywords yet, niche personal blogs and essays, and entity-centric people/company
discovery. Naming the weaknesses is what makes the strengths usable.

**The four context-engineering lessons from Tavily's own deep research agent are honored
in the skill**, not just cited: distill each tool batch into claim + source + confidence
rather than propagating raw output; deduplicate sources globally across both engines and
treat "no new domains" as the stop signal; force a pivot when three consecutive batches
explore the same subtopic; keep the toolset small.

## Measured usage

Counted from session transcripts on 30 Jul 2026, over the window 14–24 Jul 2026:

```
485 Tavily calls · 63 sessions · 2 projects · 10 days
448 search · 36 extract · 1 map          66% at search_depth=advanced
2,393 distinct URLs · 596 domains · 68% Brazilian
100 official .gov.br / .leg.br / .jus.br domains, 630 citations
~50% of all retrieval in the window (Tavily 485 · Exa 267 · native 218)
```

The main consumer is a research-grounded study-manual factory for Brazilian federal
civil-service exams (private repo): 18 subject areas, every claim traced to a dated URL,
a source dossier and a methodology note per subject.

**The negative evidence is the honest part.** On 14 Jul the API key hit its usage cap
(HTTP 432) mid-build. Two artifacts are still marked reduced-confidence in that repo
because they could not be cross-checked across engines, and the downgrade is versioned in
git rather than quietly fixed later. That is the most direct measurement I have of what
the tool is worth: what the output looks like without it.

## Field notes on Brazilian official sources

Offered because they are the kind of thing a crawl vendor wants in a bug tracker, and
because they cost me real debugging time. All three are reproducible and covered by test
fixtures in the consuming project.

**Planalto lies in its charset declaration.** `planalto.gov.br` serves
`<meta charset="utf-8">` and delivers **Windows-1252**. Byte `0xEA` breaks UTF-8 decoding
at position 475 of Lei 8.443/1992. Falling back to `latin-1` is only half right: what
latin-1 reads as C1 control characters (`0x91`, `0x93`, `0x94`, `0x96`) are actually curly
quotes and em dashes, which render as tofu downstream and drag a fallback font into the
output. `cp1252` is the correct decode.

**A wrong Planalto path returns HTTP 200 with an error page.** Status code cannot be used
to validate a URL there — the failure is silent. This is why the norm manifest in my
consuming project declares every fallback URL explicitly and never derives one from the
document's URN: Lei 14.133/2021 does not live at the obvious `/ccivil_03/leis/` path, and
guessing produces a confident 200 containing nothing.

**`normas.leg.br` has consolidated ("Current") versions for some norms and not others.**
That has to be a per-norm flag, not a global assumption, with the Planalto URL as declared
reserve when Current is absent.

## The layer I had to build

This is the part I would rather not maintain myself.

Search answers *what does this source say today*. It does not answer *what changed since I
last grounded a claim on it* — and for a corpus where every assertion carries a dated URL,
that second question is the one that decides whether the corpus is still true. Over one
weekend in August 2026 I built three pieces of it:

- **Network freshness** — fetch a known set of source URLs and compare the hash against
  what is on disk. Turns "is this material stale?" from an assumption into an answer.
- **Offline age** — how long since each source was last re-verified, with an explicit
  `null` for "this source does not permit determining currency". Without that null,
  *unmonitored* and *fresh* look identical in the report. Threshold design borrowed from
  `dbt source freshness`: two thresholds, warn before failing, and run the network check
  at twice the frequency of the error threshold.
- **Source-to-derivative drift** — percentage of a source file changed since a derived
  artifact was last confirmed against it. Percentage rather than boolean, because every
  commit raising an alert is the shortest path to nobody reading any alert. The report
  shows *which lines* changed, not just that something did — otherwise re-stamping is
  cheaper than re-reading, and the gate trains you to lie to it.

None of this is exotic. It is the re-verification loop that sits on top of retrieval, and
right now every serious grounded-generation user is writing their own. Tavily already has
`crawl`, `map` and `extract` — the primitive that is missing is *re-check this set of URLs
and tell me what drifted and by how much*.
