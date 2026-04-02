# Diagram Style Guide

> **Scope:** This guide applies ONLY to diagram beautification via the
> `diagram-beautifier` agent. Infographic generation does not reference
> this file.

For general aesthetic templates (background, typography, color palette,
lighting, texture, mood), see `docs/style-guide.md` — the curated
aesthetic definitions there are the source of truth for both infographics
and diagrams. This file extends those templates with diagram-specific
node shape and connector guidance.

---

## Polished vs Cinematic

Every beautification produces two variants simultaneously.

**Polished** is document-ready: faithful aesthetic application, better
spacing/typography/colors/node shapes, coherent with professional
expectations. The result should feel like "yes, that's what I meant, but
beautiful." Clean connectors. Fresh but not surprising spatial composition.

**Cinematic** is presentation-ready: topology is the script, aesthetic is
the medium. Editorial choices about emphasis, atmosphere, and depth. The
hero candidate gets visual prominence. Full expressive connector vocabulary.
Spatial composition serves the visual over the functional — the viewer
should stop and look.

**Shared between both variants:**
- Same aesthetic selection
- Same topology manifest
- Same quality review dimensions

**Key differences:**

| Dimension | Polished | Cinematic |
|---|---|---|
| Reference image use | Guard instruction — use to confirm topology | None |
| Connector style | Clean | Expressive |
| Spatial freedom | Fresh but coherent | Fully compositional |
| Quality bar language | "Professional and polished" | "Cinematic and arresting" |

---

## Node Shapes

Apply the per-aesthetic shape spec when constructing generation prompts.

| Aesthetic | Script Step | AI Agent Step | Condition | Start / End |
|---|---|---|---|---|
| **Clean Minimalist** | Rounded rect, 12px radius | Rounded rect, 12px radius | Diamond | Stadium / pill |
| **Dark Mode Tech** | Rounded rect, 6px radius | Hexagon | Diamond | Stadium / pill |
| **Bold Editorial** | Bold rect with thick color border | Bold rect with thick color border | Diamond with bold border | Bold stadium |
| **Hand-Drawn Sketchnote** | Wobbly outlined rounded rect | Wobbly outlined rounded rect | Wobbly diamond | Wobbly oval |
| **Claymation Studio** | Sculpted clay blob | Sculpted clay blob | Rounded clay blob | Clay oval |
| **Lego Brick Builder** | Brick-built rectangular construction | Brick-built rectangular construction | Brick diamond | Brick oval |

---

## Connector Styling

| Aesthetic | Connector style | Special constraints |
|---|---|---|
| **Clean Minimalist** | Orthogonal only (H/V segments, 4px rounded joins). **Diagonal edges strictly forbidden.** | Canvas must contain EXACTLY N diagram nodes. Legend must use text + colored squares only — no floating sample nodes. |
| **Dark Mode Tech** | Curved bezier paths; gradient glow from source-node color to destination-node color; arrowheads with matching neon glow tips. | Render exactly **ONE** legend box (bottom-right). Do not duplicate. |
| **Bold Editorial** | Heavy straight lines with bold arrowheads matching source-node border color. | — |
| **Hand-Drawn Sketchnote** | Hand-drawn arrows, slightly wobbly curves, informal arrowheads. | — |
| **Claymation Studio** | Rope or ribbon connectors, soft curves. | — |
| **Lego Brick Builder** | Rigid brick-peg connector rods. | — |

---

## Cinematic Guidance Per Aesthetic

When rendering the Cinematic variant, apply these per-aesthetic directives on top of
the shared Cinematic rules above.

| Aesthetic | Cinematic guidance |
|---|---|
| **Clean Minimalist** | Use sweeping arcs and scale variation to create hierarchy; generous breathing room becomes deliberate whitespace composition rather than empty space. |
| **Dark Mode Tech** | Ambient bokeh glow behind hero node; holographic node quality with depth layers; glowing bezier edges carry source-to-destination color gradients. |
| **Bold Editorial** | Nodes become graphic elements with color-blocked panels and heavy typographic labels; dramatic directional lighting with strong shadows; hero node gets full-bleed color. |
| **Hand-Drawn Sketchnote** | Gestural organic spacing between nodes; wobbly arrows with varying weight; hero node gets hand-drawn callout or emphasis circle. |
| **Claymation Studio** | Full scene with sculpted characters/objects in clay environment; rope or ribbon connectors; hero node is physically larger or more prominent than surrounding nodes. |
| **Lego Brick Builder** | Nodes as brick constructions on full baseplate scene; brick-peg connector rods; hero node has the most elaborate brick construction. |

---

## Prompt Construction Rules

These rules govern how generation prompts are assembled for diagrams.
See Step 6 of the diagram-beautifier workflow for the full ordering spec.

### Quality bar directive (always first)

Always open the generation prompt with:

> "This should be dramatically more visually impressive than the source
> diagram — publication quality, not a recolored version of the input."

### Aesthetic before structural

VLMs respond better when the aesthetic directive appears before structural
preservation constraints. State the full aesthetic (background, nodes,
connectors, typography, lighting) first; state topology preservation last.

### Color-category mapping

When the source diagram has a semantic color legend, explicitly list every
category and the node names that belong to it. Do not rely on the reference
image — state the mapping in plain text.

Example:
```
Script Steps (cyan border): Check Environment, Discover Recipes,
  Validate Structure, Check Best Practices, Validate Semantics,
  Quick Approval, Compile Report
AI Agent Steps (purple border): Classify Quality, Check Diagram Freshness
Condition diamonds (green border): All clean?, Issues found?
Start/End terminals (gray border): Start, Done
```
