# Design: Diagram Beautifier Dual-Output (Polished + Cinematic)

**Date:** 2026-04-01
**Status:** Approved

---

## Problem

The diagram-beautifier currently operates as an "aesthetic coating" — it takes the original diagram, passes it as `reference_image_path`, and asks the VLM to restyle it. The result inherits the DOT layout algorithm's spatial decisions: node distances, arrow lengths, proportions. Even when the prompt asks for something different, the reference image anchors the spatial character of the generation, not just the topology.

This design transforms the beautifier from aesthetic coating to **visual translation**: extracting the diagram's meaning into a structured topology manifest, then drawing it fresh in the chosen aesthetic. It also introduces a dual-output system that always generates both a **Polished** and **Cinematic** variant simultaneously, so the user responds to what they actually see rather than choosing a mode upfront.

---

## Design

### Core principle: topology manifest as the structural spec

Two layers replace the current single-generation approach:

**Layer 1 — Topology extraction.** Before any generation, extract the pure structure from the diagram source: nodes with semantic types, edges with labels, connectivity profile, flow direction, subgraph groupings, and which nodes are load-bearing. This becomes a structured text manifest — the diagram's specification, divorced from its visual character.

**Layer 2 — Two generation passes, always both:**
- **Polished**: topology manifest as the structural spec + reference image (PNG input only) passed with explicit instructions it is for completeness verification only. For DOT/Mermaid source input: no reference image at all.
- **Cinematic**: topology manifest only. No reference image ever (for any input type). Full aesthetic vocabulary. Full spatial freedom.

Both are quality reviewed independently. Both are presented side-by-side. No upfront mode choice.

---

## Semantic extraction layer

A new extraction phase produces the **topology manifest** before any generation.

**For DOT/Mermaid source input** — extracted from the parser output (already available):

| Field | Description |
|---|---|
| Node inventory | Every node with its semantic type — `terminal` (start/end), `decision` (diamond), `process` (rectangle), `subprocess` (subgraph members) |
| Connectivity profile | Which nodes have high in-degree or out-degree (load-bearing nodes worth emphasizing) |
| Critical path | Main trunk from entry terminal to exit terminal, distinct from branches |
| Semantic legend | If the source has a color-coded legend, map each category to its node names explicitly |
| Hero candidate | The highest-connectivity decision point, or the node where branches converge — designated as the visual focal point for Cinematic |
| Subgroup structure | Any clusters that could inform visual grouping |
| Edge labels | All text on connectors |

**For PNG input** — the existing `nano-banana analyze` prompt is upgraded to extract the same fields: not just labels, but node shapes, visible groupings, and edge label text.

The manifest is plain text. Example:

> *"13-node top-to-bottom pipeline. Two decision diamonds — 'All clean?' and 'Issues found?' — are the pivot points and the hero candidate. Critical path: Start → [five validation nodes] → Classify Quality → All clean? → Done. Seven Script Steps (cyan), two AI Agent Steps (purple), two Condition diamonds (green), two terminals (gray)."*

This manifest drives both generation prompts. The reference image never plays the structural spec role again.

---

## Polished generation path

Prompt assembled in four parts in this order:

1. **Quality bar directive** (always first): *"This should be dramatically more visually impressive than the source — publication quality, not a recolored version."*

2. **Aesthetic template**: the full set of properties for the selected aesthetic — background, typography, node style, lighting, texture, mood — plus the per-aesthetic connector and shape guidance from `diagram-style-guide.md`.

3. **Topology manifest**: the structured text description from the extraction step. Every node name, type, edge, semantic legend mapping, hero candidate.

4. **Reference image guard** (PNG input only): the original diagram is passed as `reference_image_path` with the instruction: *"The reference image is provided ONLY to verify that no nodes or connections have been missed. Do not replicate its proportions, spacing, arrow lengths, visual style, or layout algorithm. Draw this fresh."* For DOT/Mermaid source input: no `reference_image_path` is passed.

The result: a skilled designer given the diagram's spec sheet and asked to draw it in the chosen aesthetic. Layout direction is respected (top-to-bottom stays top-to-bottom), connections are correct, but node distances, connector curvature, and spatial composition are drawn fresh — with breathing room, appropriate connector styles, and visual hierarchy from the topology manifest's hero candidate rather than the DOT grid.

---

## Cinematic generation path

No reference image is passed — ever, for any input type.

Prompt construction:

1. **Strong quality bar**: *"Create something visually striking and memorable — not a diagram that looks better, but something that makes someone stop and look. The structure is the script. The aesthetic is the medium. Treat this as a visual composition, not a technical document."*

2. **Hero element designation**: called out explicitly by name from the manifest: *"'[hero candidate]' is the visual focal point of this composition. Give it emphasis, scale, or treatment that surrounding nodes don't have."*

3. **Aesthetic template**: same as Polished.

4. **Connector vocabulary**: fully expressive and aesthetic-native:
   - Clean Minimalist: sweeping arcs rather than orthogonal segments — clean but with movement
   - Dark Mode Tech: glowing bezier curves tracing from one node's color to the next
   - Sketchnote: wobbly ink arrows with gestural quality
   - Claymation: rope or ribbon connectors
   - Lego: rigid brick-peg connector rods
   - Bold Editorial: heavy directional strokes

5. **Topology manifest**: same text spec as Polished.

6. **Spatial freedom statement**: *"Node positions should serve the visual composition and the chosen aesthetic. You are not bound by the original diagram's layout proportions, spacing, or flow algorithm."*

For Claymation and Lego, the Cinematic path leans into the environmental dimension — nodes exist inside an actual scene, not floating in a background.

---

## Updated workflow

The existing 9-step workflow is restructured. Step 4 (Render to plain PNG) is removed entirely. Steps 6 and 7 split into parallel variants.

| Step | Description | Change |
|---|---|---|
| 1 | **Parse / analyze + semantic extraction** — existing parse/analyze logic runs, then the new extraction layer produces the topology manifest. Stored for both variants. | Modified |
| 2 | **Dependency check** — source input only. | Unchanged |
| 3 | **Aesthetic selection** — user picks one aesthetic. Both Polished and Cinematic are interpretations of that same aesthetic. | Note added |
| ~~4~~ | ~~Render to plain PNG~~ | **Removed** |
| 5 | **Panel decomposition** — runs once, result applies to both variants. | Note added |
| 6a | **Beautify — Polished** — topology manifest + aesthetic template + reference image guard (PNG input only). | New |
| 6b | **Beautify — Cinematic** — topology manifest + aesthetic template, no reference image. Runs in parallel with 6a. | New |
| 7a | **Quality review — Polished** — same 8 dimensions, run independently. Max one refinement pass. | New |
| 7b | **Quality review — Cinematic** — same 8 dimensions, topology manifest as sole ground truth. Max one refinement pass. | New |
| 8 | **Assemble** — for multi-panel diagrams, stitch panels per variant separately. | Unchanged |
| 9 | **Present side-by-side** — both variants shown together, labelled "Polished" and "Cinematic", each with a two-sentence design rationale. User picks one, asks for refinement, or requests a different aesthetic. | Modified |

### Why Step 4 is removed

The topology manifest replaces the rendered PNG's structural role entirely. For DOT/Mermaid source, the manifest is richer and more reliable than anything inferred from a rendered image. The quality review (Step 7) catches any completeness gaps. There is no remaining function for the rendered PNG.

For PNG input, the user's provided PNG still serves as Polished's reference (with the guard instruction). For source input, neither variant uses a rendered reference.

### Confidence in the reference-free Cinematic path

Three layers work together to ensure full topology fidelity without a reference image:

1. **Explicit topology manifest** — the model follows a text spec, not a visual inference. LLMs follow explicit text constraints reliably. Validated: v2 Cinematic-style generations returned 13/13 nodes, PASS on label fidelity and structural accuracy without a reference image.
2. **Quality review with manifest as ground truth** — Step 7b checks every node name in the generated output against the manifest. Because there is no reference image fallback, this review is the primary confidence mechanism.
3. **One refinement pass** — if any node is missing, the re-prompt includes *"the following nodes are missing: [list]"* and regenerates.

For very large diagrams (40+ nodes with complex parallel subgraphs), the Cinematic path may use the refinement pass more frequently than Polished. This is acceptable and expected.

---

## Files to change

### `agents/diagram-beautifier.md` — major restructure

| Step | Change |
|---|---|
| Step 1 | Gains semantic extraction phase — after parsing/analyzing, produces the topology manifest |
| Step 3 | Note added that the selected aesthetic applies to both variants |
| Step 4 | Removed |
| Step 5 | Note added that decomposition result applies to both variants |
| Step 6 | Splits into 6a (Polished) and 6b (Cinematic) with full prompt construction spec for each |
| Step 7 | Splits into 7a and 7b; Cinematic review explicitly notes the topology manifest is the sole ground truth and that the quality review is the primary confidence mechanism for the reference-free path |
| Step 9 | Updated to describe side-by-side output format with two-sentence design rationale per variant |

### `docs/diagram-style-guide.md` — additive

- New **Polished vs Cinematic** section explaining the two-path philosophy and what distinguishes them
- Per-aesthetic **Cinematic guidance** — what makes the Cinematic interpretation of each aesthetic distinctive:

| Aesthetic | Cinematic character |
|---|---|
| Clean Minimalist | Sweeping arcs, scale variation, some nodes larger than others |
| Dark Mode Tech | Environmental depth, holographic node quality, glowing bezier edges |
| Bold Editorial | Dramatic color blocking, nodes as graphic elements |
| Sketchnote | Gestural connectors, organic spacing, nodes with hand-drawn character |
| Claymation | Full scene, rope connectors, nodes as sculpted characters in an environment |
| Lego | Nodes as brick constructions in a full baseplate scene |

### Tests

**`tests/test_diagram_beautifier_agent.py`** — new assertions:

| Assertion | Validates |
|---|---|
| Step 1 mentions "topology manifest" or "semantic extraction" | Extraction phase is specified |
| Step 6 contains both "Polished" and "Cinematic" labelled sections | Dual-output structure exists |
| Cinematic section in Step 6 contains "no reference image" or equivalent | Reference-free Cinematic path is explicit |
| Step 7 Cinematic review mentions manifest as ground truth | Confidence mechanism is documented |
| Step 9 mentions "side-by-side" | Presentation format is specified |

**`tests/test_diagram_style_guide.py`** — new assertions:

| Assertion | Validates |
|---|---|
| "Polished" and "Cinematic" appear in the guide | Two-path philosophy is documented |
| Per-aesthetic Cinematic guidance exists for Dark Mode Tech | Cinematic guidance is not generic |
| Per-aesthetic Cinematic guidance exists for Clean Minimalist | Coverage across aesthetics |

---

## What does NOT change

- The infographic-builder flow is entirely unchanged.
- Text-only prompts (no image) still route through analyze-first as before.
- The 8 quality review dimensions remain the same — they are applied independently to each variant rather than being modified.
- Panel decomposition logic is unchanged — it runs once and both variants use the same decomposition.
- The aesthetic selection menu and inline style shortcut are unchanged — the user picks one aesthetic, and both variants interpret it.