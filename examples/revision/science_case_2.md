# Science case 2

Every claim in Section 2.2 is now tied to one or two explicit, rerunnable prompts.
You can cite these prompts (or their logic) in Supplementary Methods without exposing system internals.

This shows how exactly these summaries were obtained.

## prompt 1 

**Purpose:** Create a harmonized basis for cross-taxon comparison.

For all chemicals with toxicity data for algae, crustaceans, and fish,
summarize toxicity values separately for each species group.

For each chemical × species group:
- report the number of toxicity records,
- calculate the geometric mean toxicity value.

Use the same toxicity endpoint type within each species group where possible.
Return results in a table with one row per chemical.

**Is it possible that ETF uses this in upcoming queries?**

### Expected output

- Aggregated toxicity table
  - Geometric means as defensible standard
  - Enables comparable aggregation across taxa
  - Avoids vague “more toxic” phrasing.

## prompt 2

**Purpose:** Detect systematic differences, not just raw values.

Using the aggregated toxicity table,
identify chemicals for which toxicity differs substantially between species groups.

Specifically:
- find chemicals where the geometric mean toxicity in fish
  is at least 10× lower (i.e. more toxic) than in both algae and crustaceans,
- and chemicals where algae or crustaceans are the most sensitive group.

List the top 5 chemicals for each case.

### Expected output

**2B checked before running this prompt:**

- do some chemicals clearly satisfy the 10x criterion (fish or algae)?

  **We hope to get:**

- an explicit and defensible assymetry with the “10×” criterion
- Mirrors the example that finally worked in your workshop feedback.
- interpretable, ranked outputs

## prompt 3

**Purpose:** Show this is not anecdotal.

Summarize how frequently taxon-specific sensitivity asymmetries occur
across the full set of chemicals with multi-taxon toxicity data.

Report:
- the number and proportion of chemicals where fish are most sensitive,
- where algae are most sensitive,
- where crustaceans are most sensitive.

  Briefly describe the overall pattern.

### Expected output

**2B checked before running this prompt:**

- Not all chemicals fall into the “no strong asymmetry” category
- Known herbicides tend to flag algae sensitivity
- Metals or hydrophobic organics plausibly affect fish

**We hope to get:**

- Support for the claim “non-trivial subset”
- proportions, not just examples.
- Allows cautious language (“a substantial subset”, “repeatedly observed”).

## prompt 4

**Purpose:** Tie Section 2.2 back to Section 2.1.

For chemicals showing strong taxon-specific sensitivity asymmetries,
assess whether they also contribute to elevated mixture toxicity (sumTU).

For these chemicals:
- indicate whether they appear as mixture toxicity drivers,
- specify for which species groups and risk classes (chronic, acute).

### Expected output

- support for this statement: "In some cases, fish-specific sensitivity coincides with substances contributing to persistent mixture pressure."
- Strengthens scientific coherence between sections
