# Pairwise Model Comparison Design

## Goal

Add a pairwise model comparison capability to the evaluation harness. Given two evaluation run directories (each from a different model), produce a side-by-side comparison report that shows which model is better on each dimension for each scenario, with an overall winner based on aggregate win rates.

## Background

The evaluation harness (designed in the [2026-03-20 evaluation harness design](2026-03-20-evaluation-harness-design.md)) scores individual model outputs on an absolute 1–5 scale. This works well for tracking a single model's quality over time, but comparing two models by their absolute scores is unreliable — research (MLLM-as-a-Judge, ICML 2024) shows VLMs are more reliable at relative judgment than absolute scoring for visual content.

When evaluating a new model candidate (e.g., swapping `gemini-3-pro-image-preview` for `gemini-3.1-flash-image-preview`), we need a direct "which is better?" answer across the full scenario suite, not a comparison of independently-assigned numbers.

## Approach

**True pairwise judge.** For each scenario present in both runs, send images from both models to GPT-5.4 side by side and ask "which is better on each dimension and why?" This gives relative judgment, which the research shows is more reliable than comparing absolute scores.

We chose this over:
- **Absolute score comparison** — comparing the independent per-dimension scores from each run. Simpler (no new API calls) but less reliable. Absolute scores have higher variance and calibration drift across calls. A model scoring 3.8 in one run and 3.6 in another may not reflect a real quality difference.
- **Composite-image comparison** — stitching all panels into a single composite per model. Composites for high panel-count scenarios (6+ panels stitched vertically at 9:16) produce very tall images that risk degraded analysis quality from the evaluator.

## Architecture

### Image Selection

- For **single-panel scenarios**: send 1 image per model (2 images total per comparison call).
- For **multi-panel scenarios**: send Panel 1 and Panel 2 from each model (4 images total per comparison call). This captures both individual panel quality and cross-panel consistency without overwhelming the evaluator with 12+ images for high panel-count scenarios.

Panel 1 is the style anchor — it establishes the visual language for the entire set. Panel 2 provides the cross-panel consistency signal. Together they give the evaluator enough to judge both quality and coherence.

### Scenario Matching

The comparison only processes scenarios that exist in **both** run directories. Scenarios present in only one run are listed at the bottom of the report as "skipped."

A scenario is "present" if its subdirectory contains at least one PNG file and a scores JSON file.

### Pairwise Judge Prompt

For each matched scenario, a single GPT-5.4 API call receives:
- **Context:** scenario topic, audience, panel count
- **Images:** labeled "Model A - Panel 1", "Model A - Panel 2", "Model B - Panel 1", "Model B - Panel 2"
- **Instruction:** evaluate both models on 6 dimensions (the standard 5 plus cross-panel consistency for multi-panel scenarios; standard 5 only for single-panel scenarios)

**Critical: rationale before verdict.** The evaluator must provide rationale BEFORE selecting a winner for each dimension. This is chain-of-thought before verdict — the model reasons its way to a conclusion rather than picking a winner and post-hoc justifying it. The JSON structure enforces `rationale` first, `winner` second. This applies within a single call — no separate reasoning step needed.

### Pairwise Judge Output Format

```json
{
  "dimensions": {
    "content_accuracy": {
      "rationale": "Model A includes the authoritative nameserver step with a clear icon and dedicated section. Model B skips this step entirely, jumping from TLD to IP return.",
      "winner": "model_a"
    },
    "narrative_structure": {
      "rationale": "Both models have a clear 2-panel progression from lookup to answer. Neither has a significant structural advantage.",
      "winner": "tie"
    },
    "visual_explanation": {
      "rationale": "Model B uses more distinct icons per step and spatial encoding that makes the DNS flow graspable from visuals alone. Model A relies more heavily on text labels.",
      "winner": "model_b"
    },
    "typography_legibility": {
      "rationale": "Model B has cleaner text rendering with no artifacts. Model A has minor garbling in the footer text.",
      "winner": "model_b"
    },
    "visual_quality_consistency": {
      "rationale": "Model B has a more contemporary palette and consistent visual language. Model A's design feels slightly dated with heavier gradients.",
      "winner": "model_b"
    },
    "cross_panel_consistency": {
      "rationale": "Both maintain consistent style across their two panels. Typography, icons, and palette are stable in both.",
      "winner": "tie"
    }
  },
  "overall_rationale": "Model B is stronger overall, winning on visual explanation, typography, and visual quality while Model A only wins on content accuracy.",
  "overall_winner": "model_b"
}
```

- `winner` values: `"model_a"`, `"model_b"`, or `"tie"`
- `cross_panel_consistency` dimension is only included for multi-panel scenarios (panels > 1)
- `overall_rationale` appears before `overall_winner` — rationale-first at every level

## Components

### eval/compare.py (new file)

Core comparison logic with four public functions:

#### `build_pairwise_prompt(scenario, image_paths_a, image_paths_b, label_a, label_b) -> str`

Constructs the pairwise judge prompt. Includes:
- Labeled image references ("Model A - Panel 1", etc.)
- Scenario context (topic, audience, panel count)
- The 5 or 6 rubric dimensions with descriptions
- Rationale-first instruction
- Required JSON output schema

#### `parse_pairwise_result(raw_json_str) -> dict`

Validates the pairwise JSON output:
- All expected dimensions present
- Each dimension has both `rationale` (non-empty string) and `winner` (valid enum value)
- `overall_rationale` and `overall_winner` present
- Winner values are one of `"model_a"`, `"model_b"`, `"tie"`

#### `compare_scenario(scenario, image_paths_a, image_paths_b, label_a, label_b) -> dict`

Sends images to GPT-5.4 and returns the parsed pairwise result. Handles the API call, image encoding, and response parsing.

#### `generate_comparison_report(results, label_a, label_b, skipped) -> str`

Produces the full markdown report from all scenario comparison results:
- Header with model labels, scenario counts, overall winner
- Aggregate dimension win-rate table
- Per-scenario result tables with rationale
- Skipped scenarios section

### eval/cli.py (modified)

Add `compare` subcommand. The command:

1. Scans both run directories for scenario subdirectories
2. Matches scenarios by name, identifies skipped scenarios
3. For each matched scenario, loads the scenario metadata from `scenarios.yaml`, collects Panel 1 and Panel 2 images from each run directory
4. Calls `compare_scenario()` for each matched scenario
5. Calls `generate_comparison_report()` to produce the markdown output
6. Saves the comparison JSON results alongside the markdown report

### Image Selection Logic

For each scenario:
1. Find all `panel_*.png` or `{scenario_name}*.png` files in the scenario subdirectory
2. Sort them by name (lexicographic ensures panel ordering)
3. Take the first 2 for multi-panel scenarios (Panel 1 and Panel 2)
4. Take the first 1 for single-panel scenarios
5. If a scenario subdirectory has 0 PNGs, skip it

## CLI Interface

```bash
python3 -m eval compare \
  --run-a eval-results/2026-03-24_125604 \
  --run-b eval-results/2026-03-26_170000 \
  --label-a "Nano Banana Pro" \
  --label-b "Nano Banana 2" \
  --output eval-results/comparison-pro-vs-flash.md
```

| Argument | Required | Description |
|----------|----------|-------------|
| `--run-a` | Yes | Path to first model's eval-results run directory |
| `--run-b` | Yes | Path to second model's eval-results run directory |
| `--label-a` | Yes | Human-readable name for Model A (used in report) |
| `--label-b` | Yes | Human-readable name for Model B (used in report) |
| `--output` | Yes | Output path for the comparison markdown report |
| `--scenario-file` | No | Path to scenarios YAML (default: `eval/scenarios.yaml`) |

## Data Flow

```
eval-results/run-a/         eval-results/run-b/
  dns/                        dns/
    panel_1.png                 panel_1.png
    panel_2.png                 panel_2.png
  https/                      https/
    panel_1.png                 panel_1.png

        │                           │
        └─────────┬─────────────────┘
                  ▼
       Scenario Matching (by directory name)
                  │
                  ▼
       For each matched scenario:
       ┌──────────────────────────┐
       │  Select Panel 1 & 2     │
       │  from each run          │
       │          │               │
       │          ▼               │
       │  Build pairwise prompt  │
       │  (images + rubric)      │
       │          │               │
       │          ▼               │
       │  GPT-5.4 API call       │
       │  (4 images + prompt)    │
       │          │               │
       │          ▼               │
       │  Parse JSON response    │
       └──────────────────────────┘
                  │
                  ▼
       Aggregate all results
                  │
          ┌───────┴───────┐
          ▼               ▼
   comparison.md    comparison.json
```

## Comparison Report Format

```markdown
# Pairwise Model Comparison

**Model A:** Nano Banana Pro (gemini-3-pro-image-preview)
**Model B:** Nano Banana 2 (gemini-3.1-flash-image-preview)
**Scenarios compared:** 20 of 23
**Overall winner:** Model B (wins 12, loses 5, ties 3)

## Dimension Win Rates

| Dimension              | Model A Wins | Model B Wins | Ties |
|------------------------|-------------|-------------|------|
| Content Accuracy       | 8           | 9           | 3    |
| Narrative Structure    | 5           | 10          | 5    |
| Visual Explanation     | 7           | 11          | 2    |
| Typography & Legibility| 6           | 10          | 4    |
| Visual Quality         | 4           | 13          | 3    |
| Cross-Panel Consistency| 3           | 9           | 2    |

## Per-Scenario Results

### dns (2 panels)

| Dimension              | Winner  | Rationale                              |
|------------------------|---------|----------------------------------------|
| Content Accuracy       | Model A | Includes authoritative NS step...      |
| Narrative Structure    | Tie     | Both have clear 2-panel progression... |
| Visual Explanation     | Model B | Icons are more distinct per step...    |
| Typography & Legibility| Model B | Cleaner text rendering, no artifacts...|
| Visual Quality         | Model B | More contemporary palette...           |
| Cross-Panel Consistency| Tie     | Both maintain style across panels...   |
| **Scenario winner**    | **Model B** |                                    |

### campfire (2 panels)
...

## Skipped Scenarios

The following scenarios were present in only one run and could not be compared:
- saas-metrics-dashboard (only in Run A)
- okr-cascade (only in Run B)
```

## Error Handling

| Condition | Behavior |
|-----------|----------|
| Scenario exists in both runs but one has 0 images | Skip with warning |
| GPT-5.4 API call fails for a scenario | Skip with error message, continue to next scenario |
| Pairwise JSON is malformed | Skip with error message, include raw response in debug output |
| All scenarios skipped | Report generated with empty results and full skipped list |

All skipped scenarios (for any reason) are listed in the report footer with the reason for skipping.

## Testing Strategy

- **Unit tests for `build_pairwise_prompt()`** — verify image labels, dimension list varies by panel count, rationale-first instruction present, JSON schema instruction present
- **Unit tests for `parse_pairwise_result()`** — valid JSON accepted, missing dimensions rejected, invalid winner values rejected, rationale-before-winner ordering enforced
- **Unit tests for `generate_comparison_report()`** — win rates calculated correctly, per-scenario tables formatted properly, skipped scenarios section included, overall winner derived from dimension wins
- **Integration test with mocked OpenAI response** — full flow from scenario matching through report generation, verifying end-to-end pipeline without real API calls

## Cost Estimate

- ~23 API calls to GPT-5.4 (one per matched scenario)
- Each call sends 2–4 images (base64 high detail) + rubric prompt
- Estimated total: $1–2 per full comparison run
- This is a one-off comparison unless a new model launches

## Open Questions

- Should the comparison JSON results be saved alongside the markdown report for programmatic access? (Recommended: yes, save as `comparison-results.json`)
- Should the report include the independent absolute scores from each run alongside the pairwise winners? (Would make the report longer but more informative)
