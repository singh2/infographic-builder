# Backlog

## Planned

### Critic Performance Tracking

**Goal:** Gather data to determine whether the quality review (critic) loop should remain on by default, become opt-in, or be tuned.

**Problem:** The critic runs on every generated image (Step 6 in the agent workflow), adding 1 `analyze` call and up to 1 additional `generate` call per image. In a 4-panel infographic, worst case is 12 Gemini API calls (4 panels x (1 generate + 1 analyze + 1 refinement)). In observed test runs, all panels received PASS across all 5 dimensions with zero refinements triggered — meaning the critic added ~20-30 seconds of latency with no measured benefit.

**Current critic behavior:**
- Evaluates 5 dimensions: content accuracy, layout quality, visual clarity, prompt fidelity, aesthetic fidelity
- Per-dimension rating: PASS or NEEDS_WORK
- Overall verdict: PASS or NEEDS_REFINEMENT (only the overall verdict triggers regeneration, not individual dimension ratings)
- Threshold: substantive issues trigger refinement; minor cosmetic notes are accepted as-is
- Max 1 refinement pass per image; second attempt returned unconditionally
- For multi-panel: Panel 1's quality review is blocking — must pass before Panels 2-N are generated

**Proposed approach:** Append a JSONL entry to `logs/critic-results.jsonl` after every quality review call. Each entry includes:

```json
{
  "ts": "2026-03-26T16:30:00Z",
  "topic": "how DNS resolution works",
  "aesthetic": "Dark Mode Tech",
  "panel": 1,
  "panel_count": 4,
  "content_accuracy": "PASS",
  "layout_quality": "PASS",
  "visual_clarity": "PASS",
  "prompt_fidelity": "PASS",
  "aesthetic_fidelity": "PASS",
  "verdict": "PASS",
  "refinement_triggered": false
}
```

When a refinement IS triggered, a second entry is appended for the same panel with `"attempt": 2` so entries can be correlated.

**Implementation:** Add an instruction to the agent workflow (Step 6 in agents/infographic-builder.md) to emit a structured JSONL line to `logs/critic-results.jsonl` after each quality review. Create `logs/` directory with a `.gitignore` for the log file. No Python code or new tools required — the agent uses bash to append a line.

**Data to collect (target: 50-100 generations):**
- Pass-through rate: what % of images get all-PASS with no refinement triggered?
- Per-dimension failure rates: which dimensions fail most often?
- Refinement effectiveness: when refinement IS triggered, does the second attempt improve the output?

**Decision criteria:**
- If pass-through rate > 90%: make critic opt-in instead of opt-out (latency win for most generations)
- If pass-through rate 50-90%: keep critic on by default, consider tuning specific dimensions
- If pass-through rate < 50%: critic is earning its cost, keep as-is
- If refinements don't measurably improve output: consider removing refinement loop entirely, keep only the evaluation/reporting

**Where to instrument:** agents/infographic-builder.md Step 6, after the `analyze` call and before the "refine or accept" branch decision. This captures the verdict regardless of which path is taken.
