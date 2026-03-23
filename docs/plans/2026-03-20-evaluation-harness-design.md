# Evaluation Harness Design

## Goal

Build a recipe-driven evaluation harness for AI-generated infographic quality that runs after any change (model swap, prompt tweak, feature addition) and produces trend-trackable scores.

## Chosen Approach

Recipe-driven pipeline. A recipe YAML that orchestrates: generate infographics across predefined test scenarios, evaluate each with OpenAI vision, produce a comparison report. Fully automated, resumable, batch-capable.

## Architecture

### Evaluator

OpenAI vision model (GPT-4o) -- different model family from the Gemini generator to eliminate self-evaluation bias.

### Recipe Stages

1. **Generate** -- For each predefined test scenario, delegate to the infographic-builder agent to create the infographic. Outputs go to a timestamped directory.
2. **Evaluate** -- For each generated image, call the OpenAI vision API with the rubric prompt. Collect structured scores as JSON. Uses single-call evaluation (all 5 dimensions in one prompt) with chain-of-thought reasoning before scoring.
3. **Report** -- Aggregate scores, compare against previous baselines, produce a summary showing quality evolution over time.

### Evaluation Prompt Structure

The evaluator uses chain-of-thought reasoning BEFORE scoring (per Prometheus/ICLR 2024, J1/Meta 2025 research). The prompt includes:
- The image(s) to evaluate
- Topic description and target audience
- Panel type (single or multi-panel with count)
- The full rubric with per-level anchors for all 5 dimensions
- AI-specific failure modes per dimension
- Required JSON output format

### Output Structure

```
eval-results/
  YYYY-MM-DD_HHMMSS/
    dns/
      panel_1.png
      panel_1_scores.json
    https/
      panel_1.png
      panel_1_scores.json
    summary.md
```

## Evaluation Rubric

### 5 Dimensions, 1-5 Scale

| # | Dimension | Weight |
|---|-----------|--------|
| 1 | Content Accuracy | 20% |
| 2 | Narrative Structure | 15% |
| 3 | Visual Explanation | 25% |
| 4 | Typography & Legibility | 20% |
| 5 | Visual Quality & Consistency | 20% |

Plus Prompt Fidelity tracked separately as a controllability metric.

### Composite Score

Formula: `(content x 0.20) + (narrative x 0.15) + (visual_explanation x 0.25) + (typography x 0.20) + (visual_quality x 0.20)`

Interpretive bands:
- 4.0-5.0: High quality -- publish confidently
- 3.0-3.9: Acceptable -- usable with noted caveats
- 2.0-2.9: Below bar -- specific dimensions need remediation
- 1.0-1.9: Failed -- fundamental rework needed

### Scoring Philosophy

Each level has behavioral anchors. The 3-boundary is the critical threshold.

- **1 (Failing):** Fundamental failure
- **2 (Poor):** Serious issues
- **3 (Adequate):** Functional, meets minimum bar
- **4 (Good):** Clearly effective with minor issues
- **5 (Excellent):** Would hold up against professional human-designed work

### Dimension 1: Content Accuracy (20%)

Does the infographic teach the right things?

| Score | Anchor |
|-------|--------|
| 1 | Major factual errors or critical content missing. Viewer would learn something wrong. |
| 2 | Core concept present but significant errors or gaps. Knowledgeable viewer spots multiple problems. |
| 3 | Core content accurate with minor omissions. Viewer learns the right general picture. |
| 4 | Accurate and appropriately complete for audience. No detectable errors. |
| 5 | Comprehensive and precise. Could pass expert review. Appropriate depth. |

AI failure modes: hallucinated content, counting errors, reversed relationships, contradictory text.

### Dimension 2: Narrative Structure (15%)

Does the explanation build logically with a clear reading path?

| Score | Anchor |
|-------|--------|
| 1 | No discernible reading path. Content randomly placed. |
| 2 | Structure exists but logic breaks down. Concepts introduced after needed. |
| 3 | Clear reading path with logical progression. Entry and exit points identifiable. |
| 4 | Effective progressive disclosure. Information chunked well. Transitions natural. |
| 5 | Masterful sequencing making complex concepts intuitive. Clear narrative arc. |

AI failure modes: duplicate sections, arbitrary content boundaries, missing transitions.

### Dimension 3: Visual Explanation (25%)

Do visuals make the concept more understandable than text alone?

| Score | Anchor |
|-------|--------|
| 1 | Visuals purely decorative. No meaningful relationship to concepts. Styled text, not visual explanation. |
| 2 | Visual encoding attempted but ineffective. Generic clipart, spatial relationships don't reflect concepts. |
| 3 | Visuals generally support content. Arrows show flow, grouping shows relatedness. Some value beyond text. |
| 4 | Visual metaphors actively enhance understanding. Relationships encoded visually. High-level concept graspable from visuals alone. |
| 5 | Visual language deeply integrated with content, creating "aha moments." Memorable. |

AI failure modes: decorative elements that look semantic but aren't, generic iconography, arrows leading nowhere.

### Dimension 4: Typography & Legibility (20%)

Can you read it, and does text hierarchy guide attention?

| Score | Anchor |
|-------|--------|
| 1 | Text largely unreadable. Extensive garbling, overlapping, illegible. Functionally useless. |
| 2 | Some text readable but >25% garbled or illegible. Partial information extractable. |
| 3 | Most text (~80%+) readable with clear hierarchy. Minor artifacts. |
| 4 | All text clean and readable. Strong typographic hierarchy. Good contrast. |
| 5 | Typography is a design strength. Hierarchy perfectly calibrated. Every label crisp. |

AI failure modes: character garbling, word-level nonsense, overlapping text, inconsistent rendering, size hierarchy collapse.

### Dimension 5: Visual Quality & Consistency (20%)

Is it polished, appealing, and visually coherent?

| Score | Anchor |
|-------|--------|
| 1 | Visually chaotic -- clashing colors, mixed styles, no whitespace management. Multi-panel: panels look like different infographics. |
| 2 | Below professional standard. Weak colors, inconsistent icons. Dated design: heavy drop shadows, gratuitous gradients, glassmorphism, corporate stock-illustration, clip art. Looks cheap or like a 2015 template. |
| 3 | Clean and professional enough. Reasonable palette, consistent visual language. No major missteps. |
| 4 | Polished and appealing. Harmonious palette, consistent iconography. Modern, confident design. Multi-panel: clearly same series. |
| 5 | Distinctively beautiful with perfect coherence. Contemporary and fresh, not template-driven. Multi-panel: panels indistinguishable in style. |

AI failure modes: style drift across panels, visual artifacts, style collisions, background inconsistency, design era regression (dated corporate aesthetics, heavy glassmorphism, oversaturated neons).

### Evaluation Prompt Template

```
You are evaluating an AI-generated explanatory infographic. For each dimension:
1. Analyze what you observe in the image (chain-of-thought reasoning)
2. Cite specific visual evidence
3. Assign a numeric score (1-5, integers only)
4. If score <= 3, suggest one concrete improvement

TOPIC: {topic_description}
TARGET AUDIENCE: {audience_description}
PANEL TYPE: {single_panel | multi_panel (N panels)}

[Full rubric with per-level anchors inserted here]

Return valid JSON:
{
  "scores": {
    "content_accuracy": { "score": <1-5>, "evidence": "<str>", "improvement": "<str or null>" },
    "narrative_structure": { "score": <1-5>, "evidence": "<str>", "improvement": "<str or null>" },
    "visual_explanation": { "score": <1-5>, "evidence": "<str>", "improvement": "<str or null>" },
    "typography_legibility": { "score": <1-5>, "evidence": "<str>", "improvement": "<str or null>" },
    "visual_quality_consistency": { "score": <1-5>, "evidence": "<str>", "improvement": "<str or null>" }
  },
  "prompt_fidelity": { "score": <1-5>, "evidence": "<str>" },
  "composite_score": <float>,
  "overall_impression": "<str>",
  "top_strength": "<str>",
  "top_weakness": "<str>"
}
```

## Reporting

Markdown summary showing:
- Per-scenario scores across all dimensions
- Composite scores
- Comparison against previous baseline
- Quality trends over time
- Top strengths and weaknesses

## Backlog (Not in v1)

- Pairwise model comparison mode
- Multi-call evaluation (one dimension per API call)

## Open Questions

- What test scenarios should be in the default suite?
- Should there be an approval gate between Generate and Evaluate?
- How long should historical results be retained?
- Should the recipe accept parameters for subset of scenarios?
