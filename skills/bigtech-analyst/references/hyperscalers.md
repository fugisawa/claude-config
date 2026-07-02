# Domain module: Hyperscalers & the cloud / AI-capex complex

Covers AWS, Microsoft Azure, Google Cloud (the Big Three), Oracle as the fourth pole, the "neocloud" tier (CoreWeave, Nebius, Crusoe, Lambda), and the capital machinery — capex, debt/SPVs, and circular financing — binding them to chipmakers and model labs. Live figures: `landscape_2026.md` §1. Theory of cloud rent: `theoretical_framework.md` (technofeudalism, platform capitalism).

## Contents
- What to track
- Structure & actors
- The critical lens
- Technical substrate
- Fault lines & open questions
- Analytical traps

## What to track
- **Capex** (guidance vs. actual; YoY; as % of operating cash flow; composition chips/physical), and **how it's financed** — retained cash vs. debt vs. equity issuance vs. off-balance-sheet leases and SPVs.
- **Cloud revenue, growth rate, backlog (RPO), and operating margin** per provider — and whether backlog is converting to recognized revenue.
- **Market share** (by revenue *and* by traffic — they disagree) and concentration (Big Three combined; HHI if arguing concentration).
- **Customer concentration** — what share of a provider's (or neocloud's) revenue/backlog rests on one or two counterparties (often a funded one).
- **Compute commitments** (GW contracted, GPU counts, multi-year offtake) vs. what is operational.
- **Egress fees, committed-spend discounts, and switching costs** — the lock-in mechanics.

## Structure & actors
- **Oligopoly with a long tail.** Three firms hold the majority of global cloud infrastructure; the rest are low-single-digit. The moat is capital intensity, custom silicon, global footprint, and the data/identity/billing gravity that makes migration costly.
- **Custom silicon** is now a strategic axis, not a footnote: AWS (Trainium/Inferentia/Graviton), Google (TPU), Microsoft (Maia/Cobalt). It is both a margin play and a hedge against Nvidia dependence; Google's TPUs underpin its cost advantage and its ability to sell compute to labs (including rivals).
- **Oracle** vaulted into relevance as the contracted backbone for OpenAI's Stargate, converting a legacy database vendor into an AI-infrastructure landlord — on heavy debt and concentrated offtake.
- **Neoclouds** (CoreWeave et al.) rent GPU capacity to labs and hyperscalers. They are thinly capitalized relative to their commitments, debt-heavy, and customer-concentrated — and frequently sit inside the financing loop (Nvidia as both shareholder and supplier; a hyperscaler as both tenant and competitor).

## The critical lens
- **Cloud capital as rent (technofeudalism / Srnicek).** The hyperscaler owns the digital ground others must build on and extracts a toll. Ask what is competitive market pricing vs. rent enabled by lock-in. Egress fees, proprietary APIs, and committed-spend contracts are the chokepoints.
- **The entrepreneurial-state subsidy (Mazzucato).** The "private innovation" narrative omits public foundations (DARPA, public research, the grid, now public DOE loans and FERC accommodations for nuclear restarts). Who captures the value of publicly-underwritten infrastructure?
- **Cui bono in the capex story.** Record capex is sold as confidence in demand. Interrogate whose interest the number serves — equity narrative, Nvidia's order book, a partner's backlog — and whether it reflects committed external demand or engineered momentum.
- **Circular financing / round-tripping.** When a supplier invests in a customer that spends the money on the supplier's products, revenue can appear without external value creation. Map the loop explicitly (chip maker → lab → cloud → back to chips), name who sits on multiple sides, and locate the **revenue that originates outside the cohort** — that is the real signal. Historical rhyme: Lucent's vendor financing in the late-1990s telecom bubble.
- **Concentration as systemic risk.** Interlocking AI bets mean one disappointment can cascade (Azure spend → Nvidia revenue → CoreWeave valuation → OpenAI funding). Diversification at the system level is concentration in disguise.
- **Labor and supply chain.** Behind the abstraction sit construction labor, the chip supply chain (TSMC, ASML, HBM from SK Hynix/Samsung/Micron), and the conflict-mineral and e-waste tail. The "cloud" is heavy industry.

## Technical substrate
- A frontier training cluster is tens of thousands of accelerators lashed together with high-bandwidth interconnect (NVLink/InfiniBand or proprietary fabrics); the binding constraints are networking, memory bandwidth (HBM), and power density per rack, not raw FLOPs alone.
- **Inference, not training, is the durable cost** — it scales with usage and increasingly dominates spend; this is why "compute-constrained" can coexist with a possible training-capacity glut.
- The **memory/HBM shortage** is now a first-order driver of capex inflation (Microsoft attributing ~US$25B of 2026 capex to component pricing). Track DRAM/HBM pricing as a leading indicator.
- **PUE/WUE** (power/water usage effectiveness) and rack density (liquid vs. air cooling) connect this module to `data_centers.md`.

## Fault lines & open questions
- **Is the buildout supply-led overshoot or rational pre-positioning?** Evidence both ways; the deciding variable is external (non-circular) demand and utilization of committed compute.
- **Will custom silicon erode Nvidia's pricing power**, and does that *help or hurt* the hyperscalers' own depreciation math?
- **Does Oracle's debt-funded, offtake-concentrated model survive a demand wobble**, and what does CoreWeave's backlog-vs-debt-vs-interest-expense trajectory imply?
- **Antitrust on cloud** is nascent vs. search/ad-tech; watch egress-fee scrutiny (UK CMA, EU) and bundling complaints.

## Analytical traps
- Treating **backlog/RPO as revenue** — it is contracted, not collected, and can be renegotiated or canceled.
- Treating **announced capacity (GW, US$) as operational** — much hasn't broken ground; reserved grid capacity is not paid-for capacity.
- Treating **run-rate or "annualized" as GAAP revenue**, or **guidance as results**.
- Comparing **market-share figures across methodologies** (revenue vs. traffic; IaaS vs. IaaS+PaaS+SaaS) as if identical.
- Accepting a **clean-energy or "AI for good" framing** for a capex/PR document without checking the physical-power reality (`data_centers.md`).
- Reading a **single quarter's capex as the argument** instead of the capex-to-monetizable-revenue ratio over time.
