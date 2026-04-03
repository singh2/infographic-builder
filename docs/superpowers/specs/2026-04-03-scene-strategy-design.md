# Design: Multi-Panel Scene Strategy (Varied / Consistent)

**Date:** 2026-04-03
**Status:** Draft

---

## Problem

The infographic builder's multi-panel pipeline is built entirely for visual
consistency — the style brief is copied verbatim into every panel prompt, Panel 1
anchors all subsequent panels via reference image chaining, and the cross-panel
critic flags any visual difference as DRIFT. This produces reliable visual
coherence but at a cost: every panel gets the same background, composition, and
framing regardless of whether that serves the content.

The Claymation Studio aesthetic illustrates this clearly. The Background field
was defined as "Cardboard or craft paper set, visible texture and slight
wrinkles" — so every claymation panel got a flat paper background. But the best
claymation output in the project (the daily routine infographic) accidentally
produced rich 3D environments — a bedroom with oil lamps, a forest trail with
layered trees, a garden with rolling hills — because the narrative content
naturally led the model to build distinct scenes. That happened despite the
system, not because of it.

The system has strong consistency machinery but zero variation machinery.
Consistency and scene diversity are genuinely in tension — a comparison
infographic should look uniform, while a daily routine should feel like scenes
in a movie. The problem is that the agent has no mechanism to make this choice,
and the rest of the pipeline has no way to respect it.

### Catalyst

The Background field for Claymation Studio was updated (commit `3c158ca`) to
give the agent permission to choose between rich 3D environments and simple
backdrops based on content. But this is a per-aesthetic patch. The broader
issue — that the pipeline has no concept of intentional per-panel variation —
applies to all aesthetics and all layout types.

---

## Design

### Core concept: scene strategy

A single field — **scene strategy** — is decided once at the content map stage
and threads downstream to control two things:

1. Whether the content map includes per-panel scene directives
2. Whether the cross-panel critic treats background/environment differences as
   drift or as intentional

Two values:

| Strategy | What it means | When to use |
|---|---|---|
| **`consistent`** | Same visual frame across all panels. Background, composition, and framing stay identical. Critic enforces full 8-dimension consistency. | Comparisons, taxonomies, ranked lists, data breakdowns — where uniform framing highlights content differences |
| **`varied`** | Artistic style stays locked (palette, typography, icon rendering, lighting quality, borders). Environment, props, perspective, and composition vary per panel. Critic enforces style consistency only. | Journeys, daily routines, recipes, multi-step processes with distinct physical settings, historical timelines with era-specific contexts |

`consistent` is exactly how the system works today. No existing behavior
changes. `varied` is the new path.

### Decision heuristic

The agent chooses the scene strategy during content map creation. It is not a
user-facing option — it is a design judgment based on the topic and layout type.

```
Topic arrives → Agent analyzes content
                    │
        Does the content naturally map to
        distinct physical settings per panel?
                    │
    YES                             NO
    (journey, routine,              (comparison, taxonomy,
     recipe, timeline with           data breakdown, ranked
     era shifts, process             list, abstract concepts)
     with distinct locations)
            │                               │
    scene_strategy: varied          scene_strategy: consistent
```

Layout type is a secondary signal:

| Layout Type | Default Strategy | Rationale |
|---|---|---|
| Storyboard Journey | `varied` | Each step happens somewhere different |
| Comparison Grid | `consistent` | Uniform frame highlights content contrast |
| Process Flow | Content-dependent | Physical process → `varied`; abstract → `consistent` |
| Ranked List | `consistent` | Visual sameness emphasizes ranking differences |
| Timeline | Content-dependent | Historical eras → `varied`; project milestones → `consistent` |
| Data Dashboard | `consistent` | Uniform frame for data comparison |

When in doubt, default to `consistent`. This preserves existing behavior and
avoids introducing variation where it doesn't serve the content.

---

## Pipeline threading

### 1. Content Map (style-guide.md)

The content map template gains a scene strategy declaration and optional
per-panel scene directives:

```
CONTENT MAP:
Scene strategy: [varied | consistent]

Panel 1 -- [title]: [concepts/data ONLY in this panel]
  Scene: [only if varied — environment, perspective, key props]
Panel 2 -- [title]: [concepts/data ONLY in this panel]
  Scene: [only if varied — distinct from Panel 1]
...
Shared across panels: [series title, style brief only]
```

When `consistent`, the `Scene:` lines do not exist. Panels share the
aesthetic's default background treatment.

When `varied`, each panel gets a 1-sentence scene directive describing its
distinct environment, camera perspective, or compositional staging. Scene
directives should be concrete and visual — "sunlit forest trail with layered
clay trees, warm morning light filtering through canopy" not "nature scene."

### 2. Style Brief (style-guide.md)

The style brief structure does not change. It remains the consistency lock —
palette, typography, icons, borders, header chrome, aspect ratio.

One adjustment: when the strategy is `varied`, the Background field in the
brief should note `"per scene directive"` rather than specifying a fixed
color/treatment. This prevents the brief from contradicting per-panel scene
directives.

### 3. Prompt Engineering (style-guide.md)

A 7th required element is added to the "always specify" list, for multi-panel
only:

```
7. **Scene directive** (multi-panel varied only) — the distinct environment,
   perspective, or visual setting for THIS panel, drawn from the content map's
   Scene field. Style stays locked; scene changes.
```

For `consistent`, this element does not appear. Prompts work exactly as they
do today.

### 4. Agent Step 5d — Panel 2-N Generation (agent instructions)

Currently each Panel 2-N prompt includes three consistency signals:
1. Opening directive: "This panel MUST match the exact visual style of the
   reference image provided."
2. `reference_image_path` set to Panel 1's output path
3. Reconciled style brief verbatim

For `varied`, a 4th signal is added — the scene directive:

> "This panel's ENVIRONMENT is: [scene description from content map]. The
> artistic STYLE (lighting quality, color palette, typography, icon rendering,
> border treatment) must match Panel 1 exactly. The setting and composition
> are intentionally different from Panel 1."

This gives the model explicit permission to change the environment while
reinforcing that the style stays locked.

### 5. Post-Panel 1 Reconciliation (style-guide.md)

The reconciliation gate does not change structurally. It still captures what
Panel 1 actually rendered and overwrites the style brief.

One scoping note is added: for `varied`, the reconciled brief carries the
style DNA (typography, palette, icon rendering, lighting quality, border
treatment) but the background environment description is Panel 1-specific
and should not be enforced on Panels 2-N. The reconciliation prompt should
note: "The background environment described below is specific to this panel's
scene. Subsequent panels will have different environments but must match all
other style properties exactly."

### 6. Cross-Panel Critic (style-guide.md)

This is the most important change. Currently the cross-panel comparison checks
8 dimensions and flags ANY difference as DRIFT:

```
1. BORDER TREATMENT    5. ICON STYLE
2. BACKGROUND          6. DIVIDER LINES
3. TYPOGRAPHY          7. SPACING/MARGINS
4. COLOR PALETTE       8. RENDERING STYLE
```

For `varied`, the critic prompt gains a scoping preamble:

> "These panels use a VARIED scene strategy — each panel intentionally depicts
> a different environment while sharing the same artistic style. When checking
> BACKGROUND, evaluate only the background STYLE (lighting quality, texture
> approach, depth-of-field treatment) — NOT the background CONTENT (what the
> scene depicts). A forest and a kitchen are not drift if they share the same
> lighting quality, color temperature, and rendering approach. Flag only
> unintended style inconsistencies across all 8 dimensions."

For `consistent`, the critic works exactly as it does today — full 8-dimension
enforcement including background content.

---

## What does not change

- **Single-panel path** — completely untouched. Scene strategy is multi-panel only.
- **Style brief structure** — same fields, same reconciliation gate.
- **Reference image chaining** — Panel 1 still anchors all subsequent panels.
- **Reconciliation gate** — still required, still overwrites the brief.
- **Per-panel quality review** (content accuracy, layout quality, visual clarity,
  prompt fidelity, aesthetic fidelity) — unchanged.
- **Eval rubric** (`eval/rubric.py`) — no immediate changes. The
  `cross_panel_consistency` dimension already evaluates whether panels "look
  like they came from the same designer" which is style consistency, not scene
  identity. Longer term, scenario-level `scene_strategy` metadata could let the
  rubric adjust its consistency expectations.

---

## Naming: why not "cinematic"

An earlier draft used "cinematic" for the varied strategy. This was rejected
because "Cinematic" is already a core concept in the diagram beautifier — it
refers to the presentation-ready output variant in the Polished/Cinematic
dual-output system (full spatial freedom, hero focal points, no reference
image). Reusing the term for a different concept in the infographic builder
would create confusion across the codebase.

`varied` / `consistent` are descriptive, unambiguous, and have no existing
usage in either product.

---

## Eval considerations

### Current gaps

- **No multi-panel claymation scenarios.** All 3 claymation scenarios in
  `eval/scenarios.yaml` are single-panel. Multi-panel claymation scenarios
  are needed to test both scene strategies.
- **No scene diversity measurement.** The rubric's `cross_panel_consistency`
  dimension penalizes style drift but has no signal on whether `varied` panels
  actually achieved distinct scenes. A dedicated `scene_diversity` dimension
  (scored only for `varied` multi-panel scenarios) could fill this gap, asking:
  "Do panels depict meaningfully distinct environments while maintaining
  recognizable artistic unity?"
- **`report.py` drops `cross_panel_consistency`.** The markdown summary table
  iterates single-panel weights, silently excluding multi-panel scores. Should
  be fixed independently.

### Recommended eval additions

1. Add 2-3 multi-panel claymation scenarios to `scenarios.yaml`:
   - A narrative journey topic (e.g., "A day in the life of a barista" — 3
     panels, should trigger `varied`)
   - A conceptual comparison topic (e.g., "Types of coffee drinks" — 3 panels,
     should trigger `consistent`)
2. Add `scene_strategy` as optional metadata on scenarios so the rubric can
   adjust expectations
3. Consider a `scene_diversity` rubric dimension for `varied` scenarios

### A/B testing approach

The `eval report --baseline-dir` comparison already works. The workflow:

1. Run `recipes/evaluate.yaml` with `filter_aesthetic=claymation` before
   implementing — baseline
2. Implement the scene strategy changes
3. Run again — experimental
4. Compare with `python3 -m eval report --run-dir <exp> --baseline-dir <base>`

The pairwise comparison module (`eval/compare.py`) is designed but
unimplemented. It would provide more reliable A/B signals by sending both
runs' images side-by-side to a VLM judge. Implementation is independent of
this design.

---

## Verification criteria

| Criterion | How to verify |
|---|---|
| `consistent` produces identical behavior to current system | Run existing multi-panel scenarios, compare output to pre-change baseline |
| `varied` panels share artistic style | Cross-panel critic passes on style dimensions (typography, palette, icons, borders, rendering style) |
| `varied` panels have distinct environments | Visual inspection; future `scene_diversity` rubric dimension |
| Agent chooses correct strategy | Narrative topics → `varied`; comparison topics → `consistent` |
| No impact on single-panel path | Single-panel scenarios score unchanged |
| No naming collision with diagram beautifier | Grep for `varied`/`consistent` in diagram-beautifier files returns zero design-concept matches |