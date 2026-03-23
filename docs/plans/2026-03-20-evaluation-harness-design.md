# Infographic Evaluation Harness Design

## Goal

Build a recipe-driven evaluation harness for AI-generated infographic quality that runs after any change (model swap, prompt tweak, feature addition) and produces trend-trackable scores.

## Background

The infographic-builder generates visual explanations using AI image generation (Gemini). As the system evolves -- new models, prompt refinements, feature additions -- we need a systematic way to answer: "did that change make things better or worse?"

Manual inspection doesn't scale and introduces subjective drift. We need automated, reproducible evaluation with scores that can be compared across runs to track quality over time.

## Approach

**Recipe-driven pipeline.** A recipe YAML orchestrates three stages: generate infographics across predefined test scenarios, evaluate each with OpenAI vision, produce a comparison report. Fully automated, resumable, batch-capable.

We chose this over:
- **Standalone script** -- simpler but manual, no resumability, harder to integrate into workflows
- **Amplifier tool module** -- tighter integration but heavier; evaluation is a periodic batch operation, not an interactive tool

The primary use case is ongoing regression testing after changes, which benefits from full automation and batch execution.

**Cross-model evaluation.** The evaluator (OpenAI GPT-4o) is a different model family from the generator (Gemini). This eliminates self-evaluation bias -- a model grading its own outputs tends to be uncalibrated.

## Architecture


### Recipe Stages

1. **Generate** -- For each predefined test scenario, delegate to the infographic-builder agent to create the infographic. Outputs go to a timestamped directory.
2. **Evaluate** -- For each generated image, call the OpenAI vision API with the rubric prompt. Collect structured scores as JSON. Uses single-call evaluation (all 5 dimensions in one prompt) with chain-of-thought reasoning before scoring.
3. **Report** -- Aggregate scores, compare against any previous baseline, produce a summary showing quality evolution over time.

### Output Structure

```
eval-results/
  2026-03-20/
    dns/
      panel_1.png
      panel_1_scores.json
    https/
      panel_1.png
      panel_1_scores.json
    summary.md
```

## Evaluator Design

- **Model**: OpenAI GPT-4o vision -- different model family from the Gemini generator to eliminate self-evaluation bias.
- **Evaluation approach**: Single-call per infographic with all 5 dimensions in one prompt. Chain-of-thought reasoning BEFORE scoring (research shows this is significantly more reliable than score-then-justify).
- **Output format**: Structured JSON per infographic with scores, evidence, and improvement suggestions per dimension.

### Evaluation Prompt Structure

The evaluator prompt sent to OpenAI vision includes:
- The image(s) to evaluate
- Topic description and target audience
- Panel type (single or multi-panel with count)
- The full rubric with per-level anchors for all 5 dimensions
- AI-specific failure modes to check per dimension
- Instruction to reason through evidence BEFORE assigning scores (chain-of-thought)
- Required JSON output format with scores, evidence, improvement suggestions, composite score, overall impression, top strength, and top weakness

## Evaluation Rubric

### Design Philosophy

The rubric is grounded in research from Edward Tufte, Alberto Cairo (*The Truthful Art*), Stephen Few, Dona Wong (*WSJ Guide to Information Graphics*), Cleveland & McGill, Nigel Holmes, and the Malofiej Awards judging criteria.

Key design decisions:
- **Dropped pure Tufte metrics** (data-ink ratio, lie factor) -- developed for quantitative data display, not explanatory/narrative infographics. The Tufte-equivalent principle becomes: every visual element should serve comprehension or engagement.
- **Split "Layout Quality" into Narrative Structure + Visual Explanation** -- genuinely independent dimensions. You can have excellent structure poorly visualized or poor structure beautifully visualized.
- **Typography gets its own dimension** -- for AI-generated infographics, garbled text is the #1 failure mode. It needs isolated tracking.
- **Merged Aesthetic Execution + Visual Coherence into Visual Quality & Consistency** -- these overlapped; at 10% each they were low-signal. Combined at 20% they carry more weight.
- **Demoted Prompt Fidelity** from core quality to a separate controllability metric -- it measures process compliance, not artifact quality.

Considered and rejected:
- **Cognitive Load** -- emergent property of other dimensions, would double-count
- **Accessibility** -- VLM can't simulate screen readers or color blindness
- **Innovation** -- penalizes consistent quality

### Scoring Philosophy

Each level has behavioral anchors -- concrete, observable criteria. The evaluator reasons through evidence before assigning scores (chain-of-thought before verdict).

| Score | Meaning |
|-------|---------|
| 1 (Failing) | Fundamental failure that makes this dimension non-functional |
| 2 (Poor) | Serious issues that significantly undermine the dimension's purpose |
| 3 (Adequate) | Functional and usable; meets minimum bar; clear room for improvement |
| 4 (Good) | Clearly effective with only minor issues; acceptable for most publishing contexts |
| 5 (Excellent) | Exceptionally effective; would hold up against professional human-designed work |

The 3-boundary is the critical threshold. Below 3 = needs remediation. At 3 = shippable with caveats. Above 3 = genuine quality.

### Dimensions

#### Dimension 1: Content Accuracy (20%)

Does the infographic teach the right things?

| Score | Anchor |
|-------|--------|
| 1 | Major factual errors or critical content missing entirely. A viewer would learn something wrong. |
| 2 | Core concept present but significant errors or gaps. A knowledgeable viewer spots multiple problems. |
| 3 | Core content accurate with minor omissions. Viewer learns the right general picture. |
| 4 | Accurate and appropriately complete for the target audience. No detectable errors. |
| 5 | Comprehensive and precise. Could pass expert review. Appropriate depth -- neither oversimplified nor overwhelming. |

**AI failure modes:** Hallucinated content (fabricated steps, invented statistics), counting errors (prompt says 5 steps but infographic shows 4 or 6), reversed relationships (arrows pointing wrong direction, cause/effect swapped), contradictory text between sections.

#### Dimension 2: Narrative Structure (15%)

Does the explanation build logically with a clear reading path?

| Score | Anchor |
|-------|--------|
| 1 | No discernible reading path. Content feels randomly placed. Viewer can't determine where to start. |
| 2 | Some structure exists (numbered sections) but logical flow breaks down -- concepts introduced after they're needed, ambiguous entry point. |
| 3 | Clear reading path with logical progression. Sections are distinguishable. Entry and exit points are identifiable. It works. |
| 4 | Effective progressive disclosure -- simpler concepts precede complex ones. Information chunked into manageable groups. Transitions feel natural. |
| 5 | Masterful sequencing that makes a complex concept feel intuitive. Clear narrative arc. Viewer arrives at understanding feeling it was obvious. |

**AI failure modes:** Duplicate sections, arbitrary content boundaries between panels, missing transitions between steps.

#### Dimension 3: Visual Explanation (25%)

Do the visuals make the concept more understandable than text alone?

| Score | Anchor |
|-------|--------|
| 1 | Visuals are purely decorative. Icons have no meaningful relationship to concepts. This is styled text, not a visual explanation. |
| 2 | Visual encoding attempted but ineffective. Generic clipart next to text, spatial relationships don't reflect conceptual relationships. |
| 3 | Visuals generally support content. Arrows show flow, grouping shows relatedness, icons are recognizable. Adds some value beyond text. |
| 4 | Visual metaphors actively enhance understanding. Relationships encoded visually, not just textually. Viewer grasps the high-level concept from visuals alone. |
| 5 | Visual language deeply integrated with content, creating "aha moments." Complex relationships made intuitive through metaphor or spatial logic. Memorable. |

**AI failure modes:** Decorative elements that look semantic but aren't, generic iconography, arrows that lead nowhere, spatial relationship errors (containment/overlap implying wrong conceptual relationships).

#### Dimension 4: Typography & Legibility (20%)

Can you read it, and does the text hierarchy guide attention?

| Score | Anchor |
|-------|--------|
| 1 | Text largely unreadable. Extensive garbling, overlapping elements, or illegible sizing. Infographic is functionally useless. |
| 2 | Some text readable but >25% is garbled, malformed, or illegible. Partial information extractable. |
| 3 | Most text (~80%+) readable with clear hierarchy. Minor rendering artifacts -- occasional garbled word, slightly fuzzy characters. |
| 4 | All text clean and readable. Strong typographic hierarchy guides the eye. Good contrast. No rendering artifacts. |
| 5 | Typography is a design strength. Hierarchy perfectly calibrated. Every label crisp. Text sizing and placement actively guide the reading experience. |

**AI failure modes:** Character-level garbling, word-level nonsense, overlapping text, inconsistent rendering quality across regions, size hierarchy collapse.

#### Dimension 5: Visual Quality & Consistency (20%)

Is it polished, appealing, and visually coherent throughout?

| Score | Anchor |
|-------|--------|
| 1 | Visually chaotic -- clashing colors, mixed styles (flat icons next to photorealistic elements), no whitespace management. For multi-panel: panels look like different infographics. |
| 2 | Below professional standard. Weak color choices, inconsistent icon styles, unbalanced composition. Dated design patterns: heavy drop shadows, gratuitous gradients, glassmorphism, stock-illustration corporate aesthetic, clip art style icons. Viewer's impression: "this looks cheap" or "this looks like a 2015 template." |
| 3 | Clean and professional enough. Reasonable palette, consistent enough visual language. No major missteps. Wouldn't embarrass in a professional context. |
| 4 | Polished and appealing. Harmonious palette, consistent iconography and spacing. Strong visual system throughout. Modern, confident design language -- clean whitespace, intentional detail, editorial typography. Multi-panel: clearly the same series. |
| 5 | Distinctively beautiful with perfect coherence. Single unified design artifact. Color, composition, and visual rhythm create an aesthetically rewarding experience. Design feels contemporary and fresh, not template-driven. Multi-panel: panels indistinguishable in style. |

**AI failure modes:** Style drift across panels, visual artifacts, style collisions (3D objects on 2D backgrounds), background inconsistency between panels, design era regression (defaulting to dated corporate aesthetics, heavy glassmorphism, skeuomorphism, oversaturated neon palettes, generic business stock-illustration style).

#### Prompt Fidelity (tracked separately)

Did the output match what was requested? Correct topic, scope, style direction, number of panels. Tracked as a controllability metric outside the quality composite score -- it measures process compliance, not artifact quality.

### Composite Score

**Formula:**

```
composite = (content × 0.20) + (narrative × 0.15) + (visual_explanation × 0.25) + (typography × 0.20) + (visual_quality × 0.20)
```

**Interpretive bands:**

| Range | Interpretation |
|-------|---------------|
| 4.0 - 5.0 | High quality -- publish confidently |
| 3.0 - 3.9 | Acceptable -- usable with noted caveats |
| 2.0 - 2.9 | Below bar -- specific dimensions need remediation |
| 1.0 - 1.9 | Failed -- fundamental rework needed |

## Reporting

Results stored as timestamped JSON files with a markdown summary. The summary shows:

- Per-scenario scores across all dimensions
- Composite scores
- Comparison against previous baseline (if exists)
- Quality trends over time across runs
- Top strengths and weaknesses per scenario

The report should be easy to consume -- a single markdown file that shows how quality has evolved, with clear indication of what improved and what regressed.

## Research Basis

The evaluation approach is informed by:

- **Prometheus framework** (ICLR 2024): Per-level anchored rubrics achieve 0.897 Pearson correlation with human evaluators
- **J1: Thinking-LLM-as-a-Judge** (Meta, 2025): Chain-of-thought before verdict outperforms all baselines
- **MT-Bench** (Zheng et al., 2023): Foundational LLM-as-judge methodology
- **MLLM-as-a-Judge** (ICML 2024): Pairwise comparison more reliable than absolute scoring for visual content
- **Visualization theory**: Tufte, Cairo, Few, Wong, Cleveland & McGill, Holmes, Malofiej Awards

## Backlog (Not in v1)

- **Pairwise model comparison**: Show both model outputs to the evaluator side by side for direct "which is better?" comparison. Research shows VLMs are more reliable at relative judgment for visual content.
- **Multi-call evaluation**: One dimension per API call, run in parallel. Research favors this for score reliability, but single-call is sufficient to start and saves ~2.5x cost.

## Open Questions

- What test scenarios should be in the default suite? (DNS is the existing baseline; need 4-5 more covering different topic types and complexity levels)
- Should there be an approval gate between Generate and Evaluate stages? (Lets you eyeball outputs before spending API credits on scoring)
- How long should historical results be retained? (Needed for trend tracking)
- Should the recipe accept parameters to run a subset of scenarios? (Useful for quick iteration)
