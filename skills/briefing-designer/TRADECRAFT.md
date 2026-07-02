# Tradecraft — Analytic Rigor & Argument Architecture

This file governs **how the briefing argues**, not how it looks. It adapts two traditions — intelligence-community analytic standards and the consulting pyramid method — into plain language. The reader of the finished PDF is an intelligent layperson: the discipline must be present, the jargon must not.

## Table of contents

1. The plain-language rule
2. Calibrated uncertainty vocabulary
3. Likelihood vs. confidence (never in the same sentence)
4. The "Avaliações principais" box
5. Indicators — "what would change this assessment"
6. Argument architecture (answer-first, SCQA, MECE)
7. Self-checks before drafting is "done"

---

## 1. The plain-language rule

The disciplines below come from formal analytic standards. **Never expose their jargon to the reader.** Forbidden in the rendered document: "ICD 203", "WEP", "words of estimative probability", "key judgments", "MECE", "SCQA", "BLUF", "analytic tradecraft", "structured analytic techniques". Use the natural-language equivalents in the document's language (Section 2 and 4 give the exact phrasing). The reader should experience clear, honest, calibrated prose — not a compliance exercise.

---

## 2. Calibrated uncertainty vocabulary

Every probabilistic claim in the brief uses one term from a single fixed ladder, so that "provável" always means the same thing across the document. The ladders below are translations of one underlying scale; pick the row for the document's language and **never mix synonyms from outside the ladder** ("possivelmente", "talvez", "pode ser que", "maybe", "perhaps" are banned in analytic claims — they carry no calibrated meaning).

| Faixa | pt-BR | en | es | fr |
|---|---|---|---|---|
| 01–05% | quase nenhuma chance | almost no chance | casi ninguna posibilidad | presque aucune chance |
| 05–20% | muito improvável | very unlikely | muy improbable | très improbable |
| 20–45% | improvável | unlikely | improbable | improbable |
| 45–55% | chances aproximadamente iguais | roughly even chance | posibilidades casi iguales | chances à peu près égales |
| 55–80% | provável | likely | probable | probable |
| 80–95% | muito provável | very likely | muy probable | très probable |
| 95–99% | quase certo | almost certain | casi seguro | presque certain |

Conventions:

- **Anchor at least the first use** of a ladder term with its range in parentheses: "é provável (55–80%) que...". Subsequent uses of the same term may drop the range.
- Add a one-line note in the sources/methodology area, in plain words, e.g. (pt-BR): *"Os termos de probabilidade neste documento seguem uma escala fixa: improvável (20–45%), provável (55–80%), quase certo (95–99%), e assim por diante."* This is the calibration legend — write it naturally, not as a compliance table.
- If a claim genuinely cannot be placed on the ladder (neither certain nor impossible, but unrateable), say "é possível" **without any modifier** and say *why* it cannot be rated.
- Reserve verbs in the indicative ("será", "vai", "is", "will") for near-certainties; pair ladder terms with the event, not with hedged verbs ("é provável que tente", not "talvez possa tentar").

---

## 3. Likelihood vs. confidence — never in the same sentence

Two different things, two different sentences:

- **Likelihood** rates the *event*: "É muito provável (80–95%) que a medida seja aprovada até março."
- **Confidence** rates the *basis of the judgment* — quality, quantity and convergence of the evidence: "Essa avaliação tem confiança alta: baseia-se em fontes múltiplas e independentes que convergem."

Mixing them in one sentence ("temos confiança alta de que é provável...") confuses the reader about what is being rated. The validator flags this as an error.

Plain-language confidence scale (adapt to document language):

| Nível | What it means — say it in these terms |
|---|---|
| **Confiança alta** | fontes múltiplas, de boa qualidade, independentes entre si, com pouca ou nenhuma contradição. Ainda assim não é certeza. |
| **Confiança média** | informação crível e plausível, mas com corroboração insuficiente ou fontes que divergem em pontos relevantes. |
| **Confiança baixa** | informação escassa, fragmentada ou de credibilidade incerta; a inferência é frágil. |

State confidence **only for the major judgments** (the ones in the Avaliações principais box), each time followed by a clause explaining *why* ("porque..."). Confidence without a reason is theater.

---

## 4. The "Avaliações principais" box

For argumentative and prescriptive briefs (the default stances), open the body — immediately after the lede — with a boxed list of the 2–4 major judgments. Component markup is in `COMPONENTS.md` (component 12). Naming by language: **"Avaliações principais"** (pt-BR), **"Key assessments"** (en), **"Evaluaciones principales"** (es), **"Évaluations principales"** (fr).

Each entry is one complete sentence that could stand alone: it names the judgment, carries its ladder term with range, and (for the most consequential ones) is followed by a confidence sentence. Example entry (pt-BR):

> É muito provável (80–95%) que a tarifa seja prorrogada além de 2026, deslocando o ajuste para o câmbio. Confiança média: a base documental é sólida, mas depende de declarações de intenção ainda não testadas.

The box is the document's contract with the reader: everything after it argues for what it promises. Descriptive briefs (pure landscape surveys with no judgments) may omit it.

---

## 5. Indicators — "what would change this assessment"

Strong analysis names its own falsifiers. Near the synthesis section, include a short component (see `COMPONENTS.md`, component 13) listing 3–5 concrete, observable developments that would strengthen or weaken the major judgments — e.g. "a publicação do edital antes de agosto enfraqueceria a avaliação central". Title it naturally: **"O que mudaria esta avaliação"** / "What would change this assessment" / "Qué cambiaría esta evaluación" / "Ce qui changerait cette évaluation".

Rules: each indicator must be observable (an event, a number crossing a threshold, a document being published), not a vibe ("se a situação piorar" is not an indicator). Tie each one to the judgment it affects and the direction (strengthens/weakens).

---

## 6. Argument architecture (answer-first, SCQA, MECE)

The brief leads with its answer and earns it afterwards. Internalize three devices — and keep all three invisible as devices:

**a. The lede is the answer.** The lede paragraph states the central judgment up front, not the topic. The reader who stops after the lede knows *what you concluded*; the reader who continues learns *why*. Never structure the document as a mystery that reveals its conclusion at the end.

**b. Open with situation → complication → question → answer.** The lede (and the cover abstract) follows this arc compressed into 4–6 sentences: one sentence of shared context the reader already accepts; one or two naming what changed or what is at stake; the implicit question this raises; then the answer — the central judgment. This is why a good lede feels inevitable rather than abrupt. In an executive-summary box, the answer portion should dominate (roughly two-thirds of the text); context is throat-clearing past two sentences.

**c. Sections are non-overlapping reasons.** The 3–9 body sections each develop one distinct line of support for the central judgment. Test the section plan before drafting: do any two sections argue the same thing in different words (merge them)? Does an obvious counter-consideration have no home (add one — ideally a section that takes the strongest opposing case seriously before answering it)? Section *titles* state the section's claim where the persona allows it ("A tarifa muda o câmbio, não o comércio"), never the mere topic ("Aspectos cambiais").

A brief that needs more than four top-level reasons usually has an unstructured argument: group, don't list.

---

## 7. Self-checks before drafting is "done"

Run mentally before assembling the HTML (the validator catches some of these mechanically, but not all):

- [ ] Could a reader reconstruct the entire argument from: lede + Avaliações principais + section titles + synthesis? If not, the architecture leaks.
- [ ] Does every probabilistic claim use a ladder term? Any stray "talvez/possivelmente/maybe"?
- [ ] Is at least the first use of each ladder term anchored with its range?
- [ ] Is confidence stated only for major judgments, in its own sentence, with a "porque"?
- [ ] Is there one section (or sustained passage) that takes the strongest opposing view seriously?
- [ ] Are the indicators observable and tied to specific judgments?
- [ ] Did any forbidden jargon (Section 1) leak into the rendered text?
