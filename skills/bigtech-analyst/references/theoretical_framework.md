# Theoretical framework: critical tech analysis

Reference for the lens. Load when an argument needs explicit grounding — naming the mechanism (rent, extraction, accumulation, externalization, enclosure) is what separates analysis from commentary. Use these as tools, not dogma; apply the one that fits the evidence and hold it to the same scrutiny as the claims it critiques.

## Contents
- Foundational authors & concepts (attention, platforms, algorithms)
- Political economy of AI & compute-as-capital
- Data-center extractivism & environmental justice
- The bubble: accumulation, assetization & historical rhymes
- Ghost work & the labor behind "autonomous" systems
- The tech right & Big-Tech–state alignment
- Digital & AI sovereignty, vendor lock-in
- Key figures to profile
- Asset managers & ownership concentration
- Analytical frameworks (power, discourse, geopolitics)
- Source evaluation criteria

## Foundational authors & concepts

### Surveillance capitalism — Shoshana Zuboff, *The Age of Surveillance Capitalism* (2019)
Behavioral surplus: data extracted beyond what a service needs, used to predict and *modify* behavior, sold in behavioral-futures markets. Application: question every "free" service; identify the extraction mechanism and the modification objective. In the AI era, behavioral data is also training feedstock — extraction with a second purpose.

### Platform decay / enshittification — Cory Doctorow; *Chokepoint Capitalism* (2022, w/ Rebecca Giblin)
Platforms serve users, then business customers, then themselves — value is progressively withdrawn from each in turn once they are locked in. Application: track policy changes as enshittification stages; watch switching costs and interoperability fights. Doctorow's remedy emphasis is interoperability and the right to exit.

### Technofeudalism — Yanis Varoufakis, *Technofeudalism* (2023)
"Cloud capital" extracts rent like a feudal lord rather than profit through competitive production; users and businesses are vassals on the platform's land. Application: AWS/Azure/GCP market power, app-store taxes, the AI-compute toll. Critical lens: traditional market dynamics may not describe platform power. Use as a sharp hypothesis to test, not a foregone conclusion.

### Algorithmic governance / opacity — Frank Pasquale, *The Black Box Society* (2015)
Consequential decisions made by opaque, unaccountable algorithmic systems. Application: content moderation, credit/hiring/scoring, recommender systems; accountability gaps and regulatory capture.

### Data colonialism — Nick Couldry & Ulises Mejias, *The Costs of Connection* (2019)
Data relations as a new colonial appropriation: human life converted into a free raw material. Application: North–South data flows, digital-sovereignty debates, platform expansion in the Global South as extraction dressed as development. Core to the skill's decolonial commitment.

### Platform capitalism — Nick Srnicek, *Platform Capitalism* (2016)
Platforms as infrastructure owners extracting rent; typology of advertising, cloud, industrial, product, and lean platforms. Application: classify the platform to understand its business-model logic and where the rent is.

### Algorithmic bias — Safiya Noble, *Algorithms of Oppression* (2018); Cathy O'Neil, *Weapons of Math Destruction* (2016); Ruha Benjamin, *Race After Technology* (2019)
Systems encode and amplify discrimination at scale behind a veneer of neutrality (Noble); opaque, unaccountable, harmful models become "weapons of math destruction" (O'Neil); the "New Jim Code" — discriminatory design presented as objective and even benevolent (Benjamin). Application: audit AI systems for disparate impact; reject "neutral technology" claims.

### Innovation & the state — Mariana Mazzucato, *The Entrepreneurial State* (2013)
Public investment underwrites the foundational research and infrastructure that private tech later monetizes; the "pure private innovation" story omits the public subsidy. Application: counter that narrative across the stack — from the internet and GPS to DOE loans, FERC accommodations, and tax abatements for data centers. Ask who captures the value of publicly-underwritten technology.

### Social media & democracy — Giuliano da Empoli, *Os Engenheiros do Caos* (2019); Max Fisher, *The Chaos Machine* (2022)
Political technologists weaponize social platforms (da Empoli); engagement optimization structurally drives outrage and radicalization (Fisher). Application: electoral manipulation, far-right mobilization, the recommendation-to-extremism pipeline.

### Solutionism — Evgeny Morozov, *To Save Everything, Click Here* (2013)
"Technological solutionism": recasting complex social problems as bugs awaiting a technical fix. Application: the default skeptic's tool against "AI will solve X" framings.

## Political economy of AI & compute-as-capital

### Kate Crawford, *Atlas of AI* (2021)
AI is material: minerals, water, energy, labor, and data, extracted across a planetary supply chain. "AI is neither artificial nor intelligent" — it is embodied infrastructure with a physical and human cost. The connective tissue between `generative_ai.md` and `data_centers.md`: every model run is an extraction event somewhere.

### Compute as the means of production
Frontier capability is gated by access to accelerators, power, and capital more than by ideas, which diffuse quickly. Whoever owns the compute (chipmakers, hyperscalers) sits structurally above whoever rents it (labs, startups). Read lab–cloud–chipmaker relations as a class structure of the AI economy: the labs are often a financial pass-through from investors to the owners of compute. This reframes "AI competition" as competition *for* compute, and explains why integrated owners may out-survive pure-play labs.

### Assetization — Kean Birch & Fabian Muniesa, *Assetization* (2020)
The dominant move in tech capitalism is turning things (data, models, platforms, future revenue, even unbuilt capacity) into *assets* that generate rent and carry a speculative valuation, rather than commodities sold at competitive margin. Application: a private lab's valuation is a *negotiated, narrative-driven asset mark*, not a fundamental; "run-rate" and contracted backlog are devices for assetizing expectation. The skill's run-rate-vs-GAAP discipline is assetization theory in practice.

### Meredith Whittaker / AI Now — power-centered AI critique
The relevant question is not "is the model biased?" but "who holds the power that AI concentrates?" Compute, data, and deployment concentration is the political story; safety and ethics framings can become diversions from the concentration question. Useful corrective when a debate stays narrowly technical.

## Data-center extractivism & environmental justice

The buildout concentrates *burdens* (electricity demand and price, water withdrawal, land, emissions, pollution, noise) on host communities — disproportionately rural, low-income, and Global South — while concentrating *benefits* (compute, profit, shareholder value) elsewhere. The analytical frame:

- **Cost externalization.** Private value capture, socialized cost — higher power bills, stressed watersheds, emissions, subsidized infrastructure. The task is to make the externality legible and name who pays. (See `data_centers.md`.)
- **Cost-causation vs. cost-socialization.** When data-center load drives capacity prices up, is the cost allocated to the cause or smoothed onto all ratepayers? The central regulatory fight.
- **Greenwashing accounting.** "100% renewable / carbon-free / carbon-negative" usually rests on annual matching, unbundled credits, and offsets while the marginal electron is gas. Test claim against delivered mix, accounting method, and *absolute* emissions trend.
- **Environmental-justice geography.** Map who hosts the substation and who consumes the service; the distance between them is the politics.
- **Opacity as strategy.** AI-specific energy/water figures are systematically under-disclosed; the gap between reported and independently-estimated impact is itself a finding.

## The bubble: accumulation, assetization & historical rhymes

Argue the bubble question honestly and at full strength on both sides (template in `generative_ai.md` and `landscape_2026.md` §2). Theoretical anchors:

- **A technology can be real *and* its financing a bubble.** Railways, electrification, telecom fiber, and the dot-com web were genuinely transformative *and* hosted massive speculative over-investment with violent shakeouts. "The tech is real" does not settle "the capital allocation is sound." This is the single most important framing to hold.
- **Circular financing / round-tripping.** When a supplier funds a customer that spends on the supplier's product, revenue appears without external value creation. The signal is **revenue originating outside the cohort**. Historical rhyme: Lucent and Nortel vendor financing in the late-1990s telecom bubble. (Mechanics in `hyperscalers.md`.)
- **Depreciation and the obsolescence clock.** Accelerators obsolesce in a few years; aggressive useful-life assumptions flatter profits across the cohort. Understated depreciation is a quiet bubble-inflator.
- **Speculative assetization.** Marks on unbuilt capacity and unearned revenue (assetized expectation) can detach from cash generation; the deciding variable is durable external demand and utilization of committed compute.

## Ghost work & the labor behind "autonomous" systems

**Mary Gray & Siddharth Suri, *Ghost Work* (2019); Phil Jones, *Work Without the Worker* (2021).** "Autonomous" AI rests on large-scale, often-precarious, often-Global-South human labor: data annotation, RLHF preference rating, red-teaming, and content moderation — frequently piecework, low-paid, and psychologically hazardous. The automation narrative hides relocated and devalued human work rather than eliminating it. Application: behind every "the model learned to…" is a labor question — who labeled it, where, for how much, under what conditions.

## The tech right & Big-Tech–state alignment

A faction of tech capital has moved from libertarian-coded neutrality to overt political alignment with the nationalist right, fusing corporate and state power around AI and crypto.

- **Key figures & network.** Peter Thiel (anti-democratic statements; Palantir/Anduril; backer of JD Vance; intellectual ties to neoreaction / Curtis Yarvin); Elon Musk (X/xAI as owned megaphone; government-contractor turned deregulation actor); Marc Andreessen ("Techno-Optimist Manifesto," framing regulation and "safetyism" as the enemy); David Sacks (administration AI/crypto czar); J.D. Vance (the faction's political vehicle). The cluster is sometimes called the "broligarchy."
- **The pattern.** Roll back AI safeguards and "woke AI"; fast-track data-center permitting; preempt state-level AI regulation; subsidize and protect domestic AI/chip champions; treat AI dominance as national-security industrial policy. Export controls and chip policy become bargaining chips.
- **Alondra Nelson's correction.** What is happening is "not the absence of AI regulation but its *rearrangement*" — deregulation for incumbents alongside coercive use of state power (funding conditions, procurement, enforcement threats) to shape the field. Avoid the lazy "deregulation vs. regulation" binary; analyze *whose* interests the rearrangement serves and which actors are advantaged.
- **Reading the alignment.** Apply discourse analysis to "American AI," "national security," and "anti-woke" framings: what material and competitive interests do they encode? Note the contradiction between anti-government rhetoric and dependence on government contracts, subsidies, and protection.

## Digital & AI sovereignty, vendor lock-in

Especially salient for Brazil and the Global Majority.

- **Sovereignty stack.** Dependence runs through cloud (compute, storage, identity), foundation models (the reasoning layer in public and private decisions), chips (the hardest dependency), and standards. "AI sovereignty" asks who controls each layer a state and its firms rely on.
- **Lock-in mechanics.** Egress fees, proprietary APIs, committed-spend discounts, data gravity, and model/agent integration raise exit costs; "sovereign cloud" offerings can reproduce dependence under a local label (cf. the TikTok-style restructuring in `social_media.md` — nominal control, retained technical dependence). Always ask whether a "sovereign" arrangement transfers real control or just the label.
- **Critical lens.** "AI for development" can be extraction; data-localization can be either genuine sovereignty or protectionist theater. Distinguish dependence-reducing from dependence-relabeling. Watch pressure on jurisdictions (e.g. the EU) to dilute safeguards in exchange for access. Brazil reference points: Marco Civil, LGPD, Pix as sovereign payment infrastructure, and platform-regulation debates.

## Key figures to profile

**Elon Musk** — PayPal-mafia, South-African origin; techno-libertarian with selective "free-speech absolutism"; Tesla, SpaceX, X/xAI (now nested under SpaceX), Neuralink; contradiction of government dependence vs. anti-government rhetoric; owned-platform political influence.

**Peter Thiel** — PayPal-mafia, Palantir; explicit anti-democratic statements ("freedom and democracy incompatible"); Palantir (surveillance), Anduril (defense); network to Vance and neoreaction.

**Mark Zuckerberg** — "move fast and break things" → metaverse → AI/superintelligence; News Feed, Cambridge Analytica, moderation reversals; ~majority voting control of Meta via dual-class shares.

**Marc Andreessen / David Sacks** — venture capital as ideological project; manifesto-driven anti-regulation politics; Sacks bridging the VC world and state AI/crypto policy.

For any figure: separate stated ideology from material interest, note governance control (dual-class voting), and track the contradiction between rhetoric and dependence.

## Asset managers & ownership concentration

**BlackRock, Vanguard, State Street** — combined ownership makes them the largest shareholders across most major tech firms. Critical questions: does concentrated, largely passive ownership shape corporate behavior and competition (common ownership across rivals)? What does index-driven capital allocation mean for accountability? Track stewardship-vote shifts and the politics around ESG.

## Analytical frameworks

### Power analysis (run on any company, deal, policy, or technology)
1. Who owns it? (equity structure, voting rights, control)
2. Who profits? (revenue streams, value capture, rent)
3. Who decides? (governance, key decision-makers, chokepoints)
4. Who is excluded / who pays? (barriers, locked-out stakeholders, externalized costs)

### Discourse analysis (run on corporate/government/sell-side statements)
1. What is claimed? (surface message)
2. What is assumed? (unstated premises)
3. What is obscured? (omissions, euphemisms — "engagement," "efficiency," "responsible," "sovereign")
4. What are the material interests? (cui bono — follow the money and the power)

### Geopolitical lens
- US–China: chips, AI, data, export controls as economic statecraft.
- EU regulatory model: GDPR, DMA, DSA, AI Act — and the pressure to dilute under access leverage.
- Global South / Brazil: digital sovereignty, data localization, Marco Civil, LGPD, Pix, platform-regulation debates; decolonial reading throughout.

## Source evaluation criteria

**High trust:** primary documents (filings, court records, regulator texts); peer-reviewed research; investigative journalism with named sources; demonstrated accuracy and a corrections culture; grid/energy data from operators and the IEA.

**Low trust:** anonymous sources without corroboration; corporate-funded research without disclosure; aggregators without original reporting; outlets with a retraction history.

**Red flags:** think tanks funded by the subjects they assess; undisclosed conflicts; claims that mirror corporate PR verbatim; studies missing methodology; valuations and run-rates presented without disclosure quality. Weight audited figures (10-K/10-Q) far above company-stated run-rates and undisclosed numbers — and say you are doing so.
