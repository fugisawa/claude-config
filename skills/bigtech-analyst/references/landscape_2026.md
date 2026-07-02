# Cenário de partida — Big Tech, snapshot de junho de 2026

**Read the SKILL.md note first.** Every number here is a **prior to re-verify, not a fact to repeat.** Capex guidance, valuations, market share, model releases, and power deals move monthly; re-confirm live before any figure enters a deliverable. Confidence tags: **[C]** confirmed/primary or ≥2 independent, **[R]** reported single-source, **[E]** estimated/modeled, **[?]** contested or thin. Units and dates are explicit on purpose.

## Contents
- The one-paragraph state of play
- 1. Hyperscalers & the capex arms race
- 2. Generative-AI labs, money & the bubble debate
- 3. AI data centers, energy & environment
- 4. Social media & the attention economy
- 5. Regulation, antitrust & the tech right
- 6. Cross-cutting numbers to keep current

## The one-paragraph state of play

The 2024–25 generative-AI boom has hardened into the largest private capital-formation event in history, now visibly **supply-led**: a handful of hyperscalers and chipmakers are financing each other and a few model labs to build compute ahead of demonstrated end demand. The four largest hyperscalers guide to roughly **US$725B of capex in 2026** [C], ~75% of it AI infrastructure, while **monetizable AI revenue is on the order of single-to-low-double-digit billions per quarter** and the **MIT NANDA** finding that ~95% of enterprise GenAI pilots show no P&L impact [C] remains unrefuted. The bull case (real demand, compute-constrained clouds, productivity ahead) and the bear case (depreciation understatement, circular financing, fiber-overbuild echoes) are both well-evidenced; the deciding variable is the share of AI revenue that comes from **outside** the financing circle. The physical bottleneck has shifted from chips to **power, grid, and water**, pushing the cost of the buildout onto ratepayers and stressed watersheds, and the political economy has shifted too: the second Trump administration has fused with the "tech right" to deregulate AI, preempt state law, and treat the US AI stack as an instrument of national power.

---

## 1. Hyperscalers & the capex arms race

- **2026 capex guidance, big four:** ~**US$725B** combined, up ~**77%** YoY from ~US$410B in 2025 [C, multi-source incl. Goldman/Amanda Lynam]. Per company (revised, Q1 2026 calls): Amazon ~US$200B; Microsoft ~US$190B (incl. ~US$25B attributed to higher component pricing, esp. memory) [C]; Alphabet US$180–190B [C]; Meta US$125–145B [C]. Oracle, the de-facto fifth hyperscaler, targets ~US$50B [R].
- **Composition:** Goldman estimates ~**75% of 2026 hyperscaler capex funds AI infrastructure**; of that, only ~25% is chips and ~75% is the physical plant — data centers, power, cooling, networking, land [E]. "The GPU is the brain; the data center is the body, and the body costs more."
- **Cumulative scale:** Goldman's big-four capex estimate FY2025–2030 is ~**US$5.3T** (raised from ~US$4.5T during Q1 earnings) — larger than the GDP of Japan [E]. A broader cross-industry aggregate (compute + DC + power) runs to ~US$7.6T 2026–2031 [E].
- **Cloud market (Synergy via Statista, Q1 2026):** AWS **28%**, Azure **21%**, Google Cloud **14%**; Big Three **>60%** [C]. Quarterly cloud-infra spend ~**US$129B**, **+35% YoY** — the tenth consecutive quarter of accelerating growth and the fastest since 2021 [C]; full-year 2026 on track to exceed **US$500B** [E].
- **Growth divergence (YoY, Q1 2026):** Google Cloud **+63%** (record), Azure **+40%**, AWS **+28%** [C, MindStudio/stocktwits via earnings]. All three describe themselves as **compute-constrained**. GCP's share has roughly doubled in five years.
- **Financing strain:** hyperscalers are pushing capex toward ~**94% of operating cash flow** [E]; Amazon's capex (~US$151B LTM, from US$12B in 2017) now exceeds its operating cash flow, turning free cash flow negative [R]. Alphabet has tapped large debt/equity issuance to fund the buildout [R]. Off-balance-sheet lease commitments are estimated at ~US$662B [E, Burry-adjacent].

→ Depth, lock-in, neoclouds, circular financing: `references/hyperscalers.md`.

---

## 2. Generative-AI labs, money & the bubble debate

**The cohort is two-tiered, not nine-way comparable** [E, Information Matters]. Top tier by scale: OpenAI, Anthropic, Google DeepMind, Meta — combined disclosed run-rate revenue approaching **US$100B** and committed forward compute spend **>US$1T through 2032**. Second tier: Mistral, Cohere (merged with Aleph Alpha, Apr 2026), DeepSeek, xAI, others.

- **Anthropic:** Series H of **US$65B at a US$965B post-money** valuation, announced **28 May 2026** (Altimeter/Dragoneer/Greenoaks/Sequoia) — the highest private valuation any AI company has carried, above OpenAI [C, incl. anthropic.com]. Stated revenue run-rate crossed ~**US$47B** in May (disclosure walk: ~US$9–10B end-2025 → US$14B Feb → US$30B Apr → US$47B May), driven heavily by Claude Code [C/R]. Filed a **confidential draft S-1** on **1 June 2026** [C]; IPO floated for ~Oct 2026 [R]. Compute: Amazon committing up to ~5 GW AWS + up to US$25B total; Google/Broadcom ~3.5–5 GW TPU from 2027; reported access to SpaceX Colossus GPU capacity [R].
- **OpenAI:** ~**US$852B** valuation (late Mar 2026, after a ~US$122B round) [C]; revenue ~US$30B run-rate [R, The Information]; reportedly tracking a ~US$14B loss in 2026 (~3× 2025) and targeting US$100B revenue by 2029 [R]. Stargate compute commitments measured in the hundreds of billions (see §3).
- **xAI:** merged X into itself (Mar 2025), then became a **SpaceX subsidiary (2 Feb 2026)** [C/R]. SpaceX **S-1 filed 20 May 2026** discloses the AI segment: 2025 revenue **US$3.2B**, adjusted EBITDA **−US$1.24B**, capex **US$12.7B**; Q1 2026 AI revenue US$818M, operating loss US$2.47B [C]. GPU depreciation reportedly drove ~62% of the Q1 R&D expense increase [R].
- **Consumer assistants (Sensor Tower "State of AI 2026", 16 Jun):** ChatGPT **46.4%** "true audience" share (first time under 50%; 1.1B+ MAU), Gemini **27.7%** (~662M), Claude **10.3%** (~245M); Grok/Perplexity/DeepSeek/Meta AI under 5% each [R]. Claude has the highest paid-conversion (~13%); DeepSeek over-indexes on time-spent via a free/cheap offering [R].
- **Structural shifts:** Meta abandoned open-weights at the frontier (Llama → closed "Muse Spark" from the new Meta Superintelligence Labs) [R]; Microsoft shipped its own MAI models (vertical integration away from OpenAI dependence) [R]; DeepSeek's V4 reset the open-weight price floor to ~1–2 orders of magnitude below Western frontier APIs, with the US CAISI/NIST evaluation putting the best open weights ~8 months (not years) behind the closed frontier [R].

### The bubble debate (give both sides; name the deciding variable)
- **Capex-to-revenue gap:** the industry is investing on the order of **US$8–10 for every US$1 of current AI revenue** [E]. Bain estimates the industry needs ~**US$2T of annual revenue by 2030** to sustain current spend, with an ~US$800B projected shortfall [E]. A capital-ledger framing: if cumulative AI capex approaches ~US$3T, the system needs ~US$1–1.5T/yr of *monetizable* AI revenue (a ~0.5× hurdle) to earn its keep — "nobody serious puts it near US$1T/yr today" [E].
- **Circular financing:** analysts have identified **>US$800B** of reciprocal investment/offtake among Nvidia, OpenAI, Oracle, CoreWeave, AMD, xAI, Anthropic and Microsoft [E]. The structure can manufacture the appearance of demand; the question is how much revenue comes from *outside* the loop (detail in `hyperscalers.md` and `generative_ai.md`).
- **Depreciation (the Burry thesis):** GPU price-performance doubles roughly every 2.0–2.5 years and real refresh cycles have compressed to 2–3 years, while servers are depreciated over 5–6 years — understating depreciation by ~**US$176B across 2026–2028**, potentially overstating Oracle and Meta profits by ~27% and ~21% by 2028 [E/R, Burry]. Amazon already shortened server life from 6 to 5 years (2025).
- **Adoption reality:** MIT NANDA (2025) — **~95% of 300+ enterprise GenAI initiatives showed zero measurable P&L impact** [C]; Deloitte's 2026 survey — only ~20% of enterprises report AI driving revenue, ~two-thirds stuck in pilots [R]; reports of ~42% of companies scrapping most AI initiatives in 2025 (up from 17%) [R].
- **Buildout reality:** OpenAI's Stargate Texas site reportedly stalled; an estimated one-third to one-half of US data centers planned for 2026 may slip or cancel; JPMorgan notes >60% of 2027 capacity has not broken ground [R].
- **Bull case (steelman):** demand is real and clouds are genuinely compute-constrained (record cloud growth, HBM shortage, GPU sell-through); vendor financing has built capital-intensive industries before; the likely outcome is **dispersion** — strong platforms/semis/power compound, while weakly-financed players, overbuilt projects, and low-differentiation labs face write-downs and consolidation, not a uniform crash [E].

→ Depth on labs, models, unit economics, compute, chips: `references/generative_ai.md`.

---

## 3. AI data centers, energy & environment

- **Power demand (IEA "Energy and AI"):** global data-center electricity ~**415 TWh in 2024** (~1.5% of world total) → **~945 TWh by 2030** (≈ Japan's total today) → ~1,200 TWh by 2035 [C]. AI is the primary driver. The **US accounts for ~half of US electricity-demand growth to 2030**; by decade's end the US is set to use more power for data centers than for aluminum + steel + cement + chemicals + all other energy-intensive goods combined [C].
- **Grid bottleneck:** the IEA estimates ~**20% of planned data-center projects are at risk of delay** from grid constraints [C]. New transmission takes 4–8 years; transformer/cable wait times have doubled in three years; **gas-turbine lead times now run years** (commissioning beyond 2030) [C]. Gartner projects power shortages could restrict ~40% of AI data centers by 2027 [R].
- **The gas reality vs. the clean-energy PR:** **GE Vernova's gas-turbine backlog is ~100 GW** (>3× all US generating capacity added in 2024), ~90% booked through 2028 [R]. The IEA projects **15–27 GW of onsite natural gas** powering US data centers by 2030 (turbines alone) [C]. Oracle–Bloom Energy: **2.8 GW** of fuel cells, the largest onsite-power deal on record [R].
- **Nuclear wave:** ~**9.8 GW across 13 disclosed hyperscaler deals** by mid-2026 — the largest private-sector nuclear procurement wave since the 1970s [E]. Microsoft–Constellation: restart **Three Mile Island Unit 1** (835 MW) as the **Crane Clean Energy Center**, ~US$16B 20-yr PPA, ~US$110–115/MWh (now the PJM reference price for 24/7 carbon-free), first power 2027 [C]. Amazon–Talen (Susquehanna): **1.92 GW to 2042**, restructured to front-of-meter after FERC rejected the behind-the-meter version (Nov 2024) over ratepayer cost-shift [C]; Amazon–X-energy ~US$700M, ~5 GW of SMRs by 2039. Google–Kairos: 500 MW SMR fleet (first US corporate SMR deal) + Commonwealth Fusion 200 MW. **Meta is the largest cumulative procurer (~6.6 GW)** across TerraPower, Oklo, Vistra, Constellation [C]. Caveat: nuclear is mostly a **2030–2035** story; only TMI is 2027.
- **The private grid / off-grid bypass:** megacampuses are being designed to skip the public grid — **Meta Hyperion** (Richland Parish, LA: 8,000 acres, 7+ GW onsite generation, ~US$200B projected — the largest announced AI project in history) [R]; Nscale Monarch (WV: 2 GW gas, Microsoft anchor) [R]. This bypasses utility-commission oversight and ratepayer protections.
- **Ratepayer cost (PJM):** capacity-auction clearing price jumped from **US$28.92/MW-day (2024/25) to US$329.17/MW-day (2026/27)** — roughly **10×** (an 833% one-auction jump) [C]. The independent market monitor attributes ~**63% of the increase to data centers** (~US$9.3B; ~US$13B across the last two auctions) [C]. Estimated **~US$70/month added per PJM household by 2028** [E]; a Bloomberg analysis found wholesale prices up to **+267%** near data-center clusters vs. five years ago [R]. AI data centers were ~4.4% of US electricity in 2023, projected 6.7–12% by 2028 [E].
- **Water:** Microsoft's internal forecast (obtained by the NYT) shows annual data-center water use **tripling to ~28B liters by 2030** (7.9B in 2020, 10.4B in 2024), including in water-stressed Phoenix, Jakarta, and Pune [R]. US data-center water use is projected to rise from ~60B liters (2022) to **150–275B liters by 2028** [E]. A **Gallup poll: 7 of 10 Americans oppose data-center development, with water scarcity the top concern** [R].
- **Emissions:** vs. pre-ChatGPT (late-2022) baselines, latest sustainability reports show emissions up **Meta +64%, Google +51%, Amazon +33%, Microsoft +23%** [R, Bloomberg/FP]. Microsoft is reportedly weighing **abandoning its 2030 carbon-negative / 100-100-0 target** and scaling back its carbon-removal program [R]; Google reports running on carbon-free energy ~two-thirds of the time. A 2024 Guardian analysis found the four firms' owned-data-center emissions for 2020–22 were >7× their official figures [R]. **No major operator discloses AI-specific environmental metrics** — the disclosure gap is itself the story.
- **Community opposition:** organized resistance blocked or delayed ~**US$98B** of projects (Mar–Jun 2025), with ≥25 US projects canceled in 2025 [R].

→ Depth on energy procurement, cooling, siting, regulation: `references/data_centers.md`.

---

## 4. Social media & the attention economy

- **Meta:** Reality Labs lost ~**US$4B in Q1 2026** alone (tens of billions cumulatively) [R]; the stock is down ~12% in 2026 despite a revenue beat, on AI-capex anxiety (~US$130B+) and a possible multibillion-dollar equity raise [R]. Meta AI claims 1B+ users; new Facebook AI search features are pitched as a multi-billion-dollar opportunity [R].
- **TikTok:** **TikTok USDS JV** formed **22 Jan 2026**, valuing the US business ~**US$14B** [C]. Ownership: Oracle/Silver Lake/MGX ~45% (+~5% other), ByteDance-investor affiliates ~30%, **ByteDance 19.9%** (under the 20% foreign-adversary cap) [C]. The recommendation algorithm is **licensed from ByteDance** and retrained on US data in Oracle's cloud; ByteDance retains TikTok Shop and ad operations [C]. Net read: "not banned, not saved — restructured" into an American-managed franchise of Chinese technology.
- **X / xAI:** X folded into xAI (Mar 2025); xAI became a **SpaceX subsidiary (2 Feb 2026)**, consolidating Musk's social platform, frontier lab, and launch/satellite business under one roof (with the Colossus data centers) [C/R]. Anthropic is reportedly renting xAI/Colossus capacity for ~US$1.25B/month [R]. X published its recommendation code (xai-org, Jan/May 2026) — partly transparency, partly a regulatory-defense posture [E].
- **Algorithmic harm (the evidence base):** a **2026 Nature RCT (Gauthier et al.)** found X's "For You" feed shifts users' political opinions to the **right**, with an **asymmetric** effect that **persists after the algorithm is switched off** — echoing a 2022 finding that the platform amplified the political right more than the left in 6 of 7 countries [C]. Frameworks for *how* amplification harms (Goldsmiths' AMPH; Harvard STRIPED exposure/escalation/engagement harms) are maturing into audit tools.
- **Youth safety:** **Australia's under-16 ban took effect December 2025** (world-first; millions of accounts deactivated in the first 100 days) [C]; the European Parliament passed a "Protection of minors online" resolution (483–92, late Nov 2025) [C]; the US route is fragmented and constitutionally contested (NetChoice v. Reyes struck down Utah's law on First-Amendment grounds) [C]. The **Grok deepfake scandal** (sexualized deepfakes of minors) accelerated the legislative push [R].

→ Depth on ad-tech, moderation, governance, the attention economy: `references/social_media.md`.

---

## 5. Regulation, antitrust & the tech right

- **US v. Google (Search):** Judge Mehta found an illegal search monopoly; the **September 2025 remedies were behavioral** — no Chrome/Android divestiture, exclusive-default contracts banned and re-bid annually, limited search-data sharing — with the court explicitly citing **generative-AI competition** as a reason not to break the company up [C]. Widely read as a "slap on the wrist"; DOJ and states are appealing (DC Circuit); no final outcome before ~2027–28 [C].
- **US v. Google (Ad tech):** Judge Brinkema (Apr 2025) found Google illegally monopolized the publisher ad-server and ad-exchange markets; the **remedies decision is pending (early 2026)** and the DOJ is seeking **divestiture of AdX** — which would be the first forced breakup of a major tech platform in decades [C].
- **Other US:** FTC v. Meta (dismissal appealed, Jan 2026); FTC v. Amazon trial scheduled **late 2026** [C].
- **EU:** under the **DSA**, a €45M fine on X (ad-transparency repository) and an order for **Meta to reopen WhatsApp to rival AI chatbots** (Meta appealing as "regulatory overreach"); the General Court upheld **Messenger as a DMA gatekeeper** [C/R]. The DSA/DMA/AI-Act/Data-Act stack is now enforced by 300+ authorities.
- **The tech right & the second Trump administration:** the **AI Action Plan (23 Jul 2025)** and three executive orders — roll back AI safeguards / ban "woke" AI, fast-track data-center permits, and **export the "American AI" stack** [C]. EO 14179 (Jan 2025) revoked Biden's AI order; a **December 2025 EO seeks to preempt state AI laws** after a 10-year congressional moratorium failed twice [C]; Big Tech (Google, Meta, Microsoft, OpenAI, Nvidia) lobbied for that preemption [R]. Nvidia was allowed to resume **H200 sales to China in exchange for a 25% cut to the US government** [R]. Alondra Nelson's framing — "not the absence of AI regulation but its rearrangement" via industrial policy, trade, immigration, and preemption — is the sharpest lens [C]. A bipartisan public recoil is building; AI may be a top issue in 2028.

→ Theory of the tech right, sovereignty, lock-in: `references/theoretical_framework.md`. Where to find rulings and filings: `references/sources_directory.md`.

---

## 6. Cross-cutting numbers to keep current

Re-verify these before use; they anchor most analyses and they all move:

| Metric | Snapshot (Jun 2026) | Conf |
|---|---|---|
| Big-4 hyperscaler 2026 capex | ~US$725B (+~77% YoY) | C |
| Share of capex that is AI infra | ~75% (¾ physical, ¼ chips) | E |
| Cloud market (AWS/Azure/GCP) | 28% / 21% / 14%; >60% combined | C |
| Q1 2026 cloud-infra spend | ~US$129B, +35% YoY | C |
| Circular-financing arrangements identified | >US$800B | E |
| Anthropic valuation / run-rate | US$965B / ~US$47B | C |
| OpenAI valuation / revenue | ~US$852B / ~US$30B run-rate | C/R |
| Capex per US$1 of AI revenue | ~US$8–10 | E |
| Revenue needed by 2030 (Bain) | ~US$2T/yr (~US$800B short) | E |
| Understated depreciation 2026–28 (Burry) | ~US$176B | E |
| Enterprise GenAI pilots w/ no P&L impact | ~95% (MIT NANDA) | C |
| Data-center electricity 2024 → 2030 | ~415 → ~945 TWh | C |
| Hyperscaler nuclear procurement | ~9.8 GW / 13 deals | E |
| GE Vernova gas-turbine backlog | ~100 GW | R |
| PJM capacity price 2024/25 → 2026/27 | US$28.92 → US$329.17 /MW-day | C |
| Added PJM household cost by 2028 | ~US$70/month | E |
| Microsoft data-center water by 2030 | ~28B liters (3× 2020) | R |
| Emissions vs pre-ChatGPT (Meta/Goog/Amzn/MSFT) | +64% / +51% / +33% / +23% | R |
| ChatGPT / Gemini / Claude assistant share | 46.4% / 27.7% / 10.3% | R |
| TikTok USDS valuation / ByteDance stake | ~US$14B / 19.9% | C |

Sources for all of the above are catalogued in `references/sources_directory.md`; trace each to its primary or independent corroboration before publishing.
