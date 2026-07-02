# Example: Academic Research Synthesis

This example shows the academic persona applied to a working-paper-style synthesis of literature or findings.

## When to draw on this example

- User asks for a "working paper", "research note", "literature synthesis", "policy paper" with academic conventions
- Audience: scholars, graduate students, policy researchers
- The output requires: extensive citation, hedged claims, methodological notes, bibliography

## Structural choices to copy

1. **No drop caps.** No pull quotes. No emojis. No endmark (or a discreet `§`).
2. **Abstract on the cover**, ≤250 words, with a Keywords line.
3. **Numbered sections** (Arabic), each opens with a topic sentence then unpacks.
4. **Subsection headings in roman bold**, not italic.
5. **In-text citations** as superscripts mapping to numbered references at the end (or Chicago author-date if the user prefers).
6. **References list at end**, alphabetized, with full bibliographic entries.
7. **Methodology / Limitations** as their own short section before the conclusion.

## Voice notes

- Use first-person plural ("we argue that...") OR remain strictly third-person — choose one and stick with it.
- Sentences average 22–30 words; long sentences are appropriate when the argument is dense.
- Hedge claims with attribution ("Smith (2024) finds that...") rather than with vague modifiers ("It seems that...").
- The conclusion is called "Conclusion", not "Synthesis".

## Required components

- Cover with abstract and keywords
- Sections: Introduction, Background/Literature Review, Argument/Findings, Limitations, Conclusion, References
- At least one figure or table
- Numbered reference list

## Lede formula

> [Topic] [has been studied / poses a question / remains contested] for [X] years. This paper [argues / reviews / synthesizes] [thesis]. We draw on [evidence type] to show that [main claim]. The principal contribution is [one sentence on what's new]. Section 2 surveys the literature; Section 3 develops the argument; Section 4 concludes.

## Sample HTML structure

```html
<body class="persona-academic">
  <!-- COVER (cover-academic variant) -->
  <section class="cover cover-academic">
    <div class="cover-ornament">§</div>
    <div class="cover-kicker">WORKING PAPER · [INSTITUTION]</div>
    <h1 class="cover-title">[Title that names the contribution]</h1>
    <p class="cover-deck">[Subtitle in roman, often the methodological note]</p>
    <div class="cover-author">
      <strong>[Name]</strong><br>
      <em>[Affiliation]</em><br>
      [Date]
    </div>
    <div class="cover-abstract">
      <span class="cover-abstract-label">Abstract</span>
      [≤250 words. State the question, the method, the principal findings, and the contribution.]
    </div>
    <div class="cover-keywords">
      <strong>Keywords:</strong> term1, term2, term3, term4, term5.
    </div>
  </section>

  <!-- BODY -->
  <div class="article-header">
    <div class="kicker">WORKING PAPER · [INSTITUTION] · [DATE]</div>
    <h1>[Title]</h1>
  </div>

  <p class="lede">[Lede formula above]</p>

  <h2>Introduction</h2>
  <p>[Establish the puzzle and stake out the contribution]</p>

  <h2>Literature</h2>
  <p>Existing work falls into three traditions<sup><a href="#ref1">1</a></sup>...</p>

  <h2>Argument</h2>
  <h3>Mechanism A</h3>
  <p>...</p>
  <h3>Mechanism B</h3>
  <p>...</p>

  <h2>Evidence</h2>
  <p>[Description of data, method]</p>
  <figure class="chart-wrap">...</figure>

  <h2>Limitations</h2>
  <p>[Honest assessment — what this paper does NOT show]</p>

  <h2>Conclusion</h2>
  <p>[Restate the contribution; gesture at directions for future work]</p>

  <div class="references">
    <div class="references-title">References</div>
    <ol class="references-list">
      <li id="ref1">Author, A. (2024). <em>Title</em>. Publisher.</li>
      <li id="ref2">Author, B., &amp; Author, C. (2025). Article title. <em>Journal</em>, 42(3), 100–120.</li>
    </ol>
  </div>
</body>
```

## Citation format

Use either:
- **Chicago author-date** in-text: `(Smith 2024)` mapping to alphabetized reference list
- **Numbered superscript**: `<sup><a href="#ref1">1</a></sup>` mapping to numbered list

Pick one. Don't mix.
