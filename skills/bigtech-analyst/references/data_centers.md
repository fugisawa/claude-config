# Domain module: AI data centers — energy, grid, water & emissions

Covers the physical substrate of the AI boom: the data-center buildout and its collision with electricity systems, water, land, and climate commitments. This is where the "cloud" abstraction meets megawatts, transmission queues, gas turbines, nuclear restarts, and the people who live next to the substations. Live figures: `landscape_2026.md` §3. Theory of cost externalization and extractivism: `theoretical_framework.md` (data-center extractivism, entrepreneurial state, environmental justice).

## Contents
- What to track
- Structure & actors
- The critical lens
- Technical substrate
- Fault lines & open questions
- Analytical traps

## What to track
- **Electricity demand** — data-center load in TWh and as a share of grid demand, the forecast trajectory, and how much of *national load growth* is attributable to data centers.
- **Power procurement** — PPAs, the energy mix actually delivered (vs. the headline "clean" claim), onsite generation (gas turbines, fuel cells), and behind-the-meter vs. front-of-meter arrangements.
- **Nuclear and SMR deals** — restarts, new contracts, capacity (MW/GW), price (US$/MWh), in-service dates, and how much is operational vs. announced.
- **Grid impact and who pays** — interconnection-queue size and wait, capacity-auction clearing prices, transmission build, and the allocation of cost between data centers and ordinary ratepayers.
- **Water** — withdrawal and consumption (liters), WUE, watershed stress, and whether the site is in a water-scarce region.
- **Emissions** — absolute Scope 1/2/3 trend since the AI ramp, the gap between reported and real emissions, and the status of net-zero / carbon-negative pledges.
- **Siting and opposition** — where campuses land (often in low-income or rural communities), permitting fights, moratoria, subsidies and tax abatements granted, and projects delayed or canceled.

## Structure & actors
- **The hyperscalers** are the demand side, racing to secure power as the binding constraint shifts from chips to electrons. Their published clean-energy and net-zero commitments increasingly diverge from the physical reality of the buildout.
- **Incumbent utilities and grid operators** (e.g. PJM and peers) sit in the middle, fielding unprecedented interconnection requests; capacity-auction prices have spiked, and the operators' allocation choices determine who bears the cost.
- **The power-equipment and gas complex** — gas-turbine makers with multi-year backlogs and near-fully-booked order books — is a quiet winner; "AI demand" is reviving fossil generation behind the clean-energy messaging.
- **The nuclear revival** — restarts of retired plants and a wave of SMR contracts — is the most-publicized supply answer, real but years out and small relative to near-term demand; the largest private nuclear procurement wave in decades.
- **Off-grid / "private grid" megacampuses** — gigawatt-scale sites with dedicated onsite generation — are emerging to bypass the interconnection queue entirely, privatizing power infrastructure and sidestepping the public processes that allocate cost and scrutinize impact.
- **Host communities** are the cost-bearing side: higher power bills, strained water, noise and land-use conflict, large public subsidies, and few permanent local jobs.

## The critical lens
- **Externalization of cost (the core move).** The defining feature of the AI energy story is that private firms capture the value of compute while socializing the costs — higher electricity bills for households, water drawn from stressed basins, emissions, and subsidized infrastructure. The analytical task is to make the externality visible and name who pays.
- **Who pays for the grid?** When capacity prices rise and data-center load drives the increase, the question is whether the cost is allocated to the data centers causing it or smoothed across all ratepayers. Cost-causation vs. cost-socialization is the central regulatory fight; quantify the household impact.
- **Greenwashing vs. physical reality.** "100% renewable," "carbon-negative," and "24/7 carbon-free" claims often rest on annual-matching accounting, unbundled credits (RECs/PPAs), and offsets while the marginal electron is gas. Test the claim against the delivered mix, the accounting method, and the absolute-emissions trend — not the press release.
- **Data-center extractivism / environmental justice.** The buildout concentrates burdens (power, water, land, pollution) on rural and low-income communities and the Global South while concentrating benefits in corporate balance sheets and distant shareholders. Map the geography of who hosts the infrastructure and who consumes the service.
- **Entrepreneurial state, privatized gain (Mazzucato).** Public actors underwrite the buildout — DOE loans, FERC accommodations, tax abatements, public power infrastructure, expedited permitting — while returns are private. Surface the public subsidy the "private investment" narrative omits.
- **Opacity as strategy.** AI-specific energy and water figures are systematically under-disclosed; companies report aggregate sustainability numbers that obscure the AI delta. The disclosure gap is itself a finding — independent estimates often run well above reported figures.

## Technical substrate
- Power is now the gating input. A frontier campus is specified in **gigawatts**, not square feet; the constraint is generation, transmission, and interconnection time, with multi-year queues and transformer/turbine lead times measured in years.
- **Energy effectiveness:** PUE (facility overhead) is mature and near its floor at hyperscale; the live frontiers are WUE (water) and the carbon intensity of the *marginal* electron. A low PUE does not make a gas-powered campus clean.
- **Cooling** is shifting from air to **liquid/direct-to-chip and immersion** as rack densities climb with accelerator power draw; cooling choice drives the water-vs-energy tradeoff (evaporative cooling saves power but consumes water).
- **Onsite generation** — gas turbines and fuel cells deployed for speed-to-power — is reviving fossil generation at the exact sites marketed as clean; behind-the-meter nuclear has run into regulatory resistance, pushing some deals front-of-meter (onto the shared grid and its cost allocation).
- **Embodied impact** beyond operations: the concrete, steel, water, and chips themselves carry a Scope-3 and supply-chain footprint usually left out of the headline number.

## Fault lines & open questions
- **Does demand materialize as forecast, or does a capex pullback / efficiency gain deflate the load curve** — and would gas and nuclear commitments then strand?
- **Who ultimately pays for the grid** — do regulators force cost-causation onto data centers, or do households keep subsidizing via capacity prices and rate base?
- **Can the nuclear/SMR revival deliver at a scale and timeline that matters**, or is it mostly narrative cover for near-term gas?
- **How large is the gap between reported and real AI emissions and water use**, and will disclosure rules (or litigation) close it?
- **Does community opposition meaningfully constrain the buildout**, and do "private grid" off-grid campuses let firms route around both the queue and public accountability?
- **Efficiency paradox:** do model- and chip-efficiency gains reduce footprint, or does Jevons rebound mean efficiency simply expands total compute and total demand?

## Analytical traps
- Accepting **"renewable/carbon-free" claims** without checking the accounting method (annual matching vs. 24/7), the instrument (unbundled RECs/offsets vs. additional generation), and the absolute-emissions trend.
- Treating **announced nuclear/SMR/PPA capacity as delivered power** — most is years out, contingent, or pre-construction; reserved is not operational.
- Confusing a **low PUE with low impact**, ignoring the carbon intensity of the marginal electron and water consumption.
- Reading **aggregate corporate sustainability figures** as AI-specific; the AI delta is usually buried, and reported totals often understate real owned-data-center impact.
- Citing **interconnection-queue or reserved grid capacity as committed load** — queues are heavily speculative and attrition is high.
- Ignoring **who bears the cost** — analyzing the buildout purely as corporate strategy and omitting ratepayers, water basins, and host communities.
- Taking **jobs and tax-revenue claims at face value** without netting out subsidies, abatements, and the small permanent-headcount reality.
