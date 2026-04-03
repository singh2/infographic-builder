# Evaluation Philosophy

## Purpose

This document defines how we think about evaluation coverage for the
infographic-builder system, why the eval set is structured the way it is,
and how to extend it without losing signal or creating redundancy.

The eval set has two jobs:
1. **Regression detection** — did a change to the agent, style guide, or
   generator break something that was working?
2. **Capability coverage** — does the system handle all input modes and
   output types we claim to support?

A scenario that does neither is dead weight.

---

## Dimension Space

Every scenario sits at a point in a multi-dimensional space. Gaps in that
space are coverage holes. Overcrowding in one region means redundant tests.

### Dimension 1 — Product (separate recipes)

| Value | Recipe | Scenarios |
|-------|--------|-----------|
| `infographic-builder` | `recipes/evaluate.yaml` | All scenarios in `eval/scenarios.yaml` |
| `diagram-beautifier` | `recipes/evaluate-diagrams.yaml` | All files in `eval/diagrams/` |

These are independent pipelines. Never mix them.

---

### Dimension 2 — Prompt Weight (infographic-builder only)

The single most important dimension. Determines how much creative work the
agent has to do vs how much the prompt has already done.

| Value | Definition | Example |
|-------|-----------|---------|
| `minimal` | Named aesthetic + topic only, ≤15 words. Agent decides layout, panel count, content structure, visual metaphors, everything. | `"Make a Claymation Studio infographic about how chocolate is made."` |
| `natural` | Conversational, may hint at domain or rough style, but agent drives all visual decisions. | `"Explain how DNS works. Make it clear for a non-technical audience."` |
| `specified` | Full visual spec — palette, panel count per panel, explicit layout, aesthetic named or described in detail. | Full 150-word prompt with color codes and per-panel content. |

**Why minimal matters most:** Real users write minimal prompts. Quality on
minimal prompts is the actual product quality. Specified prompts measure
execution fidelity, not creative judgment.

**Coverage target:** Every curated aesthetic must have at least one `minimal`
scenario. The minimal column is the regression canary for creative quality.

---

### Dimension 3 — Aesthetic (infographic-builder)

| Value | Description |
|-------|-------------|
| `clean-minimalist` | Clean Minimalist (curated) |
| `dark-mode-tech` | Dark Mode Tech (curated) |
| `bold-editorial` | Bold Editorial (curated) |
| `sketchnote` | Hand-Drawn Sketchnote (curated) |
| `claymation` | Claymation Studio (curated) |
| `lego` | Lego Brick Builder (curated) |
| `freeform` | Custom aesthetic not in the 6 curated (watercolor, materialistic 3D, etc.) |
| `agent-selected` | No aesthetic specified — agent chooses |
| `reference-image` | Aesthetic anchored to a user-provided reference image |
| `content-source` | Image provided as content input, not style anchor |
| `materialistic-3d` | 3D diorama / glossy materialistic rendering |

**Coverage target:** Every curated aesthetic at `minimal` + `specified` weight.
`agent-selected` for natural prompts. At least 1 `reference-image` per mode
(style-anchor-single, style-anchor-multi, content-source).

---

### Dimension 4 — Panel Count (infographic-builder)

| Range | Label | Notes |
|-------|-------|-------|
| 1 | `single` | Tests single-panel path end-to-end |
| 2–3 | `multi-light` | Tests multi-panel consistency without extreme complexity |
| 4–6 | `multi-dense` | Tests panel decomposition, stitch direction, style anchor chaining |

**Coverage target:** At least 2 scenarios at each tier. Dense multi-panel
(`4–6`) primarily in the extended tier.

---

### Dimension 5 — Capability (infographic-builder)

Optional tag on scenarios that exercise a specific feature path.

| Value | What it tests |
|-------|--------------|
| `diorama` | Claymation/Lego diorama sub-mode (characters acting in scene) |
| `reference-image` | Style anchor via user-provided reference image, passed as `reference_image_path` |
| `content-source` | Image treated as content input, analyzed via `content_summary`, NOT passed as style |
| `live-data` | Fetches external data (GitHub, git log) at eval time |
| `materialistic-3d` | 3D rendering path with diorama-style layout |

---

### Dimension 6 — Input Format (diagram-beautifier only)

| Value | How it enters the pipeline |
|-------|--------------------------|
| `.dot` | Graphviz source → `dot -Tpng` render → topology manifest extract → 4 variants |
| `.mmd` | Mermaid source → `mmdc` render → topology manifest extract → 4 variants |
| `.png` | Existing diagram image → topology manifest extract (skip render) → 4 variants |

**Coverage target:** At least 3 files per format. Diversity of Mermaid diagram
types — `flowchart`, `sequenceDiagram`, `classDiagram`, `erDiagram`.

---

### Dimension 7 — Diagram Complexity (diagram-beautifier only)

Controls panel decomposition behavior in `diagram_beautifier/decompose.py`.

| Range | Behavior |
|-------|---------|
| ≤10 nodes | 1 panel |
| 11–25 nodes, multi-subgraph | Up to 3 panels |
| 26–40 nodes | Up to 4 panels |
| 41+ nodes | Up to 6 panels |

Also controls Claymation sub-mode:
- ≤12 nodes, sequential workflow → **Diorama mode** (characters in scene)
- 13+ nodes, or architectural/hierarchical → **Normal Claymation**

**Coverage target:** At least one diagram in each complexity band. Both
diorama and normal Claymation must be triggered.

---

## Coverage Matrix — Infographic Builder

Current state (✓ = covered, ❌ = gap):

### By Aesthetic × Prompt Weight

| Aesthetic | Minimal | Natural | Specified |
|-----------|:-------:|:-------:|:---------:|
| Clean Minimalist | ✓ | ✓ (agile, okr) | ✓ (4 scenarios) |
| Dark Mode Tech | ✓ | ✓ (dns) | ✓ — ⚠️ over-represented (5) |
| Bold Editorial | ✓ | ❌ | ✓ (surfing, star-wars) |
| Sketchnote | ✓ | ❌ | ✓ (sleep-stages) |
| Claymation | ✓ | ❌ | ✓ (devops, espresso) |
| Lego | ✓ | ❌ | ✓ (solar-system) |
| Freeform | ❌ | ✓ (campfire, photosynthesis) | ✓ (coffee-bean, 3D scenarios) |
| Agent-selected | ❌ | ✓ (dns, engineering, repo) | — |

### By Image Input Mode

| Mode | Prompt Weight | Panels | Covered |
|------|:------------:|:------:|:-------:|
| Style ref, single panel | specified | 1 | ✓ (amplifier-delegation, product-metrics) |
| Style ref, multi-panel | specified | 3 | ✓ (reference-image-multi-panel) |
| Content source | natural | 1 | ✓ (content-source-chart) |

---

## Coverage Matrix — Diagram Beautifier

### By Input Format

| Format | Files | Mermaid Types |
|--------|:-----:|--------------|
| `.dot` | 9 | N/A |
| `.mmd` | 6 | flowchart TD, sequenceDiagram, classDiagram, erDiagram |
| `.png` | 6 | mixed AI workflow flowcharts |

### By Diagram Complexity

| Complexity | Node Range | Example | Claymation Sub-mode |
|-----------|:----------:|---------|:------------------:|
| Small | ≤10 nodes | conditional-workflow-v1 (9) | Diorama ✓ |
| Medium | 11–25 | amplifier-module-types (11), recipe-validation (13) | Normal ✓ |
| Large | 21+ | amplifier-session-loop (21, 2 subgraphs) | Normal ✓ |
| Very large | 41+ | ❌ (no test for 4+ panel decomposition) | — |

### Behavior Coverage

| Behavior | Status |
|---------|:------:|
| `.dot` render → beautify | ✓ |
| `.mmd` render → beautify | ✓ |
| PNG direct → beautify | ✓ |
| Diorama sub-mode | ✓ |
| Normal Claymation | ✓ |
| Multi-panel decomposition (3 panels) | ✓ |
| Multi-panel decomposition (4+ panels) | ❌ |
| 4 aesthetic variants generated | ✓ |
| Topology manifest as quality ground truth | ✓ |

---

## Tier System

Scenarios are tagged `tier: core` or `tier: extended`. Run different tiers
for different purposes.

### Core (~18 scenarios) — always run

**Signals:** aesthetic regressions, multi-panel consistency, key capability health.

Composition:
- 6 × minimal (one per curated aesthetic)
- 6 × named aesthetic, medium prompt (one per curated aesthetic)
- 3 × natural, agent-selected
- 2 × reference image (style-anchor + content-source)
- 1 × diorama capability

Run time: ~2 hours. Run on every meaningful change to the agent or style guide.

### Extended (~24 scenarios) — run on demand

**Signals:** edge cases, historical baselines, stress tests, live data.

Composition:
- Heavy specified scenarios (historical comparison baselines)
- Dense multi-panel (4–6 panels)
- Materialistic 3D
- Live data scenarios (GitHub repo fetch)
- Bold Editorial, Sketchnote, Lego natural prompts (not yet added)

Run time: ~3–4 hours. Run before releases or after major architectural changes.

---

## Running Specific Slices

The evaluate recipe accepts filter context variables. All filters are optional;
empty string means "all".

```bash
# Always run — core regression set
amplifier run "execute recipes/evaluate.yaml with filter_tier=core"

# Test a specific aesthetic after style guide changes
amplifier run "execute recipes/evaluate.yaml with filter_aesthetic=claymation"

# Test minimal prompts only
amplifier run "execute recipes/evaluate.yaml with filter_prompt_weight=minimal"

# Full eval
amplifier run "execute recipes/evaluate.yaml"

# Diagram beautifier (no filtering — always runs all)
amplifier run "execute recipes/evaluate-diagrams.yaml"
```

---

## Adding New Scenarios

Before adding a scenario, answer:

1. **Which cell in the matrix does this fill?** If the cell is already covered,
   the scenario is redundant unless it's testing something meaningfully different.

2. **What tier?** Core only if it catches regressions that matter on every run.
   Default to extended.

3. **What prompt weight?** Prefer minimal for new aesthetic coverage. Only add
   specified if you need to test a very specific execution behavior.

4. **Is a capability tag needed?** Add if the scenario exercises a non-default
   code path (reference image, diorama, content source, live data).

Required fields on every scenario:
```yaml
- name: scenario-slug
  tier: core | extended
  prompt_weight: minimal | natural | specified
  aesthetic: <value from Dimension 3>
  capability: []          # omit if empty
  topic: "Human readable title"
  panels: N
  audience: "..."
  style_direction: "..."
  prompt: >
    ...
```

---

## Coverage Health Checks

Run these to catch drift:

```bash
# Count by tier
python3 -c "
import yaml
data = yaml.safe_load(open('eval/scenarios.yaml'))
from collections import Counter
print(Counter(s.get('tier') for s in data['scenarios']))
"

# Count by aesthetic
python3 -c "
import yaml
data = yaml.safe_load(open('eval/scenarios.yaml'))
from collections import Counter
print(Counter(s.get('aesthetic') for s in data['scenarios']))
"

# Find any aesthetic with no minimal scenario
python3 -c "
import yaml
data = yaml.safe_load(open('eval/scenarios.yaml'))
curated = {'clean-minimalist','dark-mode-tech','bold-editorial','sketchnote','claymation','lego'}
minimal_covered = {s['aesthetic'] for s in data['scenarios'] if s.get('prompt_weight')=='minimal'}
print('Missing minimal coverage:', curated - minimal_covered)
"
```

---

## Known Remaining Gaps

| Gap | Priority | Notes |
|-----|:--------:|-------|
| Dark Mode Tech over-represented (5 specified) | Medium | Demote 2–3 to extended tier |
| Bold Editorial, Sketchnote, Claymation, Lego: no natural scenarios | Medium | Add when extending natural tier |
| Very large diagram (41+ nodes) for 4+ panel decomposition | Low | Add one `.dot` with 45+ nodes |
| `.png` diagram content diversity (all flowcharts) | Low | Add ER or network diagram PNG |
