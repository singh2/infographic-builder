# Multi-Candidate Selection Design

**Date:** 2026-04-03
**Status:** Draft
**Scope:** infographic-builder agent workflow

## Problem

Panel 1 is currently a single deterministic shot — one generation call, one
result. The user gets whatever the model produces. Quality varies due to model
stochasticity; a single generation may produce a mediocre composition when a
re-roll would have been excellent.

For single-panel infographics, this is the entire output — one shot is the
final product.

## Solution

Generate 3 candidates instead of 1. Present all 3 to the user. They pick the
winner. The pipeline continues from there.

This applies to:
- **Single-panel infographics:** 3 candidates, user picks, done.
- **Multi-panel infographics:** 3 Panel 1 candidates, user picks, reconciliation
  and Panels 2-N proceed from the winner.

## Variation Cascade

What we vary depends on what the user already locked in. The principle: vary the
highest-impact axis that hasn't been constrained.

### Tier 1: Vary aesthetic (highest diversity)

**When:** User specified a topic but no aesthetic.

Generate 3 candidates, each in a different curated aesthetic. The agent picks
3 contrasting styles to maximize visual diversity (e.g., Claymation + Dark Mode
Tech + Bold Editorial — not three similar styles).

This replaces the current Step 3d text aesthetic menu. Instead of choosing a
style from a list and then seeing the result, the user sees 3 real images and
picks. The selected image implicitly selects the aesthetic for Panels 2-N.

### Tier 2: Vary based on aesthetic's strength (medium diversity)

**When:** User specified an aesthetic (inline or via reference image).

The variation axis adapts to the aesthetic:

| Aesthetic | Second axis | Why |
|-----------|-------------|-----|
| Claymation Studio | **Environment/setting** | 3D styles produce dramatically different results with different environments (kitchen counter vs workshop vs forest set) |
| Lego Brick Builder | **Environment/setting** | Same — baseplate scenes vary visually more than composition shifts |
| Clean Minimalist | **Composition** | Flat styles differentiate best through spatial arrangement (central focal point vs flowing narrative vs structured grid) |
| Dark Mode Tech | **Composition** | Same |
| Bold Editorial | **Composition** | Same |
| Hand-Drawn Sketchnote | **Composition** | Same |
| Freeform | **Composition** | Default to composition when the aesthetic is user-described |

The agent generates 3 candidates within the locked aesthetic, each with a
different one-line directive for the active variation axis.

**Composition directions** (for non-3D aesthetics):
- Central focal point — hero subject centered, labels radiate outward
- Scene-based — environment tells the story, subject embedded in context
- Structured/diagrammatic — clean sections, data-forward, clear hierarchy

**Environment directions** (for 3D aesthetics):
- Agent picks 3 contrasting settings appropriate to the topic. For "brewing
  espresso": kitchen counter, coffee shop diorama, abstract studio backdrop.
  For "daily routine": bedroom, outdoor trail, garden. The agent uses content
  judgment.

### Tier 3: Model freedom (lowest diversity)

**When:** User specified both aesthetic and layout.

Generate 3 candidates with identical constraints. Each prompt appends a nudge:
"Explore a distinct visual interpretation." Relies on model variance for
diversity. This is the fallback — most specificity from the user means least
control over variation.

## Workflow Integration

### Current workflow (for reference)

```
Step 1: Parse request
Step 2: Decomposition (panel count)
Step 3: Aesthetic selection (3b: reference shortcut, 3c: inline shortcut, 3d: menu)
Step 4: Plan the design
Step 5: Generate (5a: content map + brief, 5b: Panel 1, 5c: reconcile, 5d: Panels 2-N)
Step 6: Quality review
Step 7: Stitch
Step 8: Deliver
```

### Modified workflow

**Step 3 changes:**

When the user did not specify an aesthetic (currently Step 3d — the text menu),
the menu is removed. The aesthetic selection is deferred to the candidate
presentation at Step 5b-ii, where the user picks from real images instead of
a text list.

Steps 3b (reference shortcut) and 3c (inline shortcut) are unchanged — they
still lock the aesthetic immediately when detected.

**Step 4 changes:**

For Tier 1 (vary aesthetic), Step 4 runs once per candidate — 3 lightweight
design plans, each applying a different aesthetic template to the same content.
Layout type may differ per aesthetic if the agent judges a different layout
better suits the style (e.g., a timeline in Bold Editorial vs a numbered flow
in Claymation). For Tiers 2 and 3, Step 4 runs once since the aesthetic is
shared.

**Step 5b becomes three sub-steps:**

- **5b-i: Generate 3 candidates in parallel.** Variation axis determined by the
  cascade above. All 3 calls run concurrently.
- **5b-ii: Quick dealbreaker check on all 3.** See Quality section below.
- **5b-iii: Present all 3 to user, wait for pick.** Show images with a
  one-sentence rationale per candidate describing what makes it different.

**After user picks:**

- **Single-panel:** Done. User's pick is the final output.
- **Multi-panel:** Proceed to 5c (reconcile style brief from winner) and 5d
  (generate Panels 2-N referencing winner). These steps are unchanged.

When the variation axis was aesthetic (Tier 1), the user's pick also determines
which aesthetic template is used for Panels 2-N.

### Reconciliation

Reconciliation (Step 5c) runs only on the selected candidate, not all 3.
The two rejected candidates are discarded.

## Quality Flow

### Quick dealbreaker check (before presenting candidates)

A lightweight binary check on each candidate before the user sees them:

1. **Text legibility** — no garbled or hallucinated words
2. **Core content present** — title and key data points are visible
3. **Aesthetic match** — the output matches the requested/assigned style

This is NOT the full 5-dimension review. It is a fast pass to catch broken
outputs.

**If a candidate fails:** Silently regenerate it once with the same prompt. If
it fails again, drop it from the set. Present 2 candidates instead of 3.
(Minimum: 2 candidates. If only 1 survives, present it with a note that other
candidates failed quality checks.)

### After user picks

| Scenario | After selection |
|----------|----------------|
| Single-panel | No further review. User's choice is the quality gate. |
| Multi-panel | Full 5-dimension review on Panels 2-N only. Cross-panel comparison against Panel 1 (the winner) as usual. |

Panel 1 itself skips the full review — the user already validated it by
selecting it.

## Presentation Format

When presenting 3 candidates, the agent shows:

```
Here are 3 directions for your infographic:

[Image A]
Option A: {one-sentence rationale — e.g., "Claymation Studio — warm plasticine
textures on a kitchen counter set"}

[Image B]
Option B: {one-sentence rationale — e.g., "Dark Mode Tech — neon data
visualization on a dark grid"}

[Image C]
Option C: {one-sentence rationale — e.g., "Bold Editorial — magazine-style
impact with massive serif headlines"}

Pick one, or tell me what you'd like to adjust.
```

The rationale describes what makes each candidate different — the variation
axis, not a generic quality claim. For aesthetic variation: name the aesthetic
and its character. For composition variation: describe the spatial approach.
For environment variation: describe the setting.

If the user asks for adjustments instead of picking, the agent can regenerate
specific candidates with modifications.

## Scope

### In scope

- Multi-candidate generation for Panel 1 (multi-panel) and the single image
  (single-panel)
- Variation cascade (aesthetic → environment/composition → model freedom)
- Quick dealbreaker check before presenting
- Merging Step 3d into candidate presentation
- Presentation format with per-candidate rationale

### Out of scope

- Multi-candidate for Panels 2-N (these are reference-chained and consistency-
  controlled — variation would break coherence)
- Autonomous selection (pairwise comparison without user) — may revisit later
- Changes to reconciliation, quality review, or stitching logic
- Moodboard Canvas integration (separate feature)

## Interaction with Existing Features

**Style Reference Mode (aesthetic_description from reference image):** When the
root session provides an aesthetic_description, the aesthetic is locked (Step 3b
shortcut). Candidates vary on Tier 2 (composition or environment). No conflict.

**Diorama Mode:** When a 3D aesthetic is locked and the user requests "diorama",
all 3 candidates use diorama framing. The variation axis is still environment —
3 different diorama settings.

**Scene Strategy (varied/consistent):** The scene strategy directive applies to
Panels 2-N after the user picks Panel 1. No conflict — the multi-candidate
selection determines the anchor; scene strategy determines how subsequent panels
relate to it.

**Diagram Beautifier:** Unaffected. The diagram-beautifier has its own
4-variant generation pattern. These two features are independent.