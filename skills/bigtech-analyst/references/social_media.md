# Domain module: Social media & the attention economy

Covers Meta (Facebook, Instagram, WhatsApp, Threads, Reality Labs), TikTok / ByteDance, X / xAI, and YouTube — as engines that manufacture and sell human attention, and increasingly as distribution and data layers for generative AI. Live figures: `landscape_2026.md` §4. Theory of attention extraction and behavioral modification: `theoretical_framework.md` (surveillance capitalism, Couldry & Mejias data colonialism, Noble/Benjamin on algorithmic bias).

## Contents
- What to track
- Structure & actors
- The critical lens
- Technical substrate
- Fault lines & open questions
- Analytical traps

## What to track
- **Engagement and its quality** — DAU/MAU, time-spent, and *what* is being optimized (watch-time, sessions, "meaningful interactions"), plus the gap between stated and revealed objectives.
- **Ad revenue, ARPU by region, and ad-load** — the real P&L; plus the dependency on a few advertiser verticals and the post-ATT measurement environment.
- **AI capex inside a social-media P&L** — Meta is now as much an AI-infrastructure spender as a social network; track capex, the Reality Labs / Superintelligence Labs burn, and whether ad gains fund it.
- **Algorithmic recommendation changes** — shifts to the ranking system, their measurable effect on what circulates (political content, AI-generated slop, engagement-bait), and who is exposed to what.
- **Content moderation and integrity posture** — staffing, policy reversals, the move from human review to AI moderation, and the trust-and-safety headcount trend (mostly down).
- **Youth-safety exposure** — regulatory bans, age-assurance mandates, litigation, and product changes for minors.
- **Algorithm ownership and data control** — who owns the recommender, where it runs, on whose data it is trained (central to the TikTok restructuring).

## Structure & actors
- **Meta** runs the largest attention pool (billions of DAUs across the family of apps) and is converting it into both an ad machine and an AI distribution channel (Meta AI in WhatsApp/Instagram, AI personas, an AI-content feed). Reality Labs remains a multibillion-dollar quarterly loss; the metaverse bet has been quietly subordinated to the superintelligence bet, and capital intensity has spooked equity holders. Llama's pivot away from open weights toward a closed flagship marks a strategic inflection (see `generative_ai.md`).
- **TikTok / ByteDance** is the attention disruptor that forced every incumbent to short-form video. Its US operation has been **restructured rather than banned**: a US joint venture in which US investors hold the majority, ByteDance sits below the statutory ownership cap, and the recommendation algorithm is *licensed* from ByteDance and retrained on US data in a US cloud. ByteDance retains the lucrative commerce and ads layer. Read the deal as a template for "sovereignty theater" — nominal control transferred, technical and economic dependence retained.
- **X / xAI** folded the social network into the AI lab, and the lab in turn became a subsidiary of a launch company. X is now simultaneously a distribution surface for a frontier model (Grok), a real-time training-data source, and an ideologically-steered public square. Its business remains advertising-impaired relative to the Musk-era peak.
- **YouTube** is the quiet giant — the dominant long-and-short video platform, a top connected-TV destination, and a creator-economy payments rail — usually under-analyzed relative to its scale and political importance.

## The critical lens
- **Attention as the extracted resource (Zuboff).** The product is not the app; it is predicted and modified behavior sold to advertisers and, increasingly, the behavioral data used to train AI. Treat "engagement" as the euphemism for a business model that profits from compulsive use, and ask what the optimization target does to the user and the polity.
- **The algorithm as political actor.** Recommendation systems are not neutral pipes. When peer-reviewed evidence shows a platform's ranking measurably advantages one political direction — asymmetrically, and persistently even after a user opts out — that is a finding about private infrastructure shaping public opinion without accountability. Separate *what the system demonstrably does* from *claims about intent*, and hold both the "neutral platform" defense and the "deliberate manipulation" charge to the evidence.
- **Opening the algorithm as posture, not just transparency.** Publishing recommender code can be genuine transparency *and* a regulatory/ideological maneuver simultaneously; assess what is actually disclosed (the live ranking with weights and signals, or a stripped snapshot) before crediting it.
- **Data colonialism (Couldry & Mejias).** Engagement and behavioral exhaust are appropriated as raw material for ad targeting and model training, disproportionately from users who never meaningfully consented and who are concentrated in the Global South for content-moderation labor.
- **Moderation as outsourced harm.** The "clean feed" rests on low-paid, often-traumatized moderation labor in the Global South and on automated systems that fail unevenly across languages. Cost-cutting and the shift to AI moderation export risk onto the most vulnerable users and the least-resourced languages — a recurring failure in the Global Majority.
- **Youth harm and the duty of care.** Move past "screens are bad" to the specific mechanics: variable-reward loops, social-comparison dynamics, algorithmic delivery of harmful content to minors, and AI features (chatbots, image tools) that generate or enable abuse. The policy question is whether platforms owe an enforceable duty of care; the analytical question is what the product does by design.

## Technical substrate
- A modern recommender is a multi-stage pipeline (candidate generation → heavy ranking → re-ranking) trained on engagement signals; "the algorithm" is really many models plus business rules and integrity overrides. Small changes to the objective function or to a single signal's weight can shift exposure at population scale.
- **Generative AI is now inside the feed on both sides**: as a creation tool (AI video/image, synthetic personas) flooding supply with near-zero-cost content, and as a moderation tool trying to filter that same flood. Track the AI-slop dynamic — content abundance collapsing the value of attention and degrading signal.
- **Provenance and watermarking** (C2PA and platform labels) are the nominal defense against synthetic media; assess coverage and circumvention, not just the announcement.
- Social graphs and real-time engagement data are a **training-data moat** for the parent's AI ambitions — a reason the social asset is strategically retained even when its standalone economics weaken.

## Fault lines & open questions
- **Does Meta's ad engine keep funding an AI-infrastructure bet at this intensity**, or does capex force an equity raise / margin compression that the market punishes?
- **Was the TikTok restructuring a real change of control or a relabeling** — does licensing the algorithm and retaining the commerce/ads layer leave ByteDance economically and technically in command?
- **What is the measurable civic effect of ideologically-steered ranking** on a major platform, and is there any accountability mechanism that bites?
- **Does the youth-safety wave (national bans, age assurance, app-store age gates, litigation) reshape the product**, and does mandatory age verification trade child safety for population-scale identity surveillance?
- **Can moderation survive the synthetic-content flood** at acceptable cost, and in languages outside the well-resourced few?

## Analytical traps
- Equating **engagement with value or wellbeing** — high time-spent can signal compulsion and harm, not satisfaction.
- Accepting **"we just give people what they want"** without examining the optimization target and the supply the system rewards.
- Treating **algorithmic transparency announcements as transparency** without auditing what was actually released, when, and whether it is the system in production.
- Reading a **ban headline as a ban** — restructurings, JVs, and licensing deals often preserve the underlying control and economics the policy meant to sever.
- Generalizing **moderation quality from English/well-resourced markets** to the languages where the platform under-invests and the harm is greatest.
- Conflating **a platform's stated political neutrality with its demonstrated algorithmic behavior** — or assuming intent from outcome without the evidence to bridge them.
- Analyzing the social app **in isolation from the parent's AI and data strategy**, missing why a money-losing asset is strategically indispensable.
