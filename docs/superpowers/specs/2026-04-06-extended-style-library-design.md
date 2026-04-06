# Extended Style Library Design

**Date:** 2026-04-06
**Status:** Draft
**Scope:** infographic-builder agent + style guide

---

## Problem

The tool currently offers 6 curated flagship aesthetics. Users and community members
have requested a wider variety — Minecraft voxel, Comic Book, Blueprint/Schematic,
Cyberpunk, and others. Simply expanding the flagship list to 20+ styles creates two
problems:

1. **Overwhelming choice** — a 20-item text menu at Step 3D is worse UX than a 6-item one
2. **High engineering cost** — each flagship style requires a full 7-dimension spec and
   machine-tested coverage

Additionally, the existing multi-candidate-selection feature (merged in `17e75a0`)
removed Step 3D entirely — aesthetic selection is now deferred to Step 5B where the
user picks from 3 real generated images. This changes where and how styles surface.

---

## Solution

Two-tier style architecture:

- **Flagship (6 styles):** Full 7-dimension specs, machine-tested, always-on quality
  guarantee. Unchanged.
- **Extended Library (17 styles):** Concise paragraph descriptions + content affinity
  tags. Lower specification cost. Surfaces through the Tier 1 candidate pool and
  on-demand browsing.

---

## Content Affinity System

Each extended library style carries a list of content-type tags. These drive
ranking and candidate pool selection.

### Tag Vocabulary

| Tag | Means |
|-----|-------|
| `process` | Step-by-step flows, pipelines, how-things-work |
| `technical` | Architecture diagrams, engineering concepts, code |
| `narrative` | Journeys, timelines, stories, before/after |
| `data` | Stats, metrics, rankings, dashboards |
| `showcase` | Product displays, gear lists, object inventories |
| `educational` | Explainers, tutorials, conceptual topics |
| `culture` | Pop culture, social topics, lifestyle, community |

Most styles carry 2–3 tags. The agent detects content types from the user prompt in
Step 2 and uses overlap between detected types and style affinity to rank candidates.

---

## The Extended Library — 17 Styles

### 1. Minecraft Voxel
> Constructive, blocky, instantly recognisable

Voxel block aesthetic. Every element built from chunky 3D pixel cubes with visible
block faces in isometric or front-facing arrangement. Palette: dirt brown, stone gray,
grass green, sky blue, obsidian black, diamond cyan, gold. Pixelated bitmap font in
white or gold. Soft ambient occlusion between blocks. Zero curves — hard block edges
throughout.

**Content affinity:** `narrative, educational, culture`

---

### 2. Comic Book / Graphic Novel
> Vintage Marvel/DC — bold ink, halftone dots, panel energy

Bold black ink outlines (3–4px) on every element. Flat cel-shaded colors with
halftone Ben-Day dot shading in shadow areas. Dynamic panel grid with jagged borders.
Palette: vibrant CMYK primaries (hero red, captain blue, dynamic yellow) on cream
newsprint. Comic lettering ALL CAPS in speech bubbles and yellow caption boxes.
Visible ink line weight variation.

**Content affinity:** `process, narrative, educational`

---

### 3. Gundam / Mobile Suit Mecha
> Japanese mecha engineering — panel lines, HUD overlays, military precision

Mechanical surface detail and panel lines on all illustrated elements. HUD/display UI
overlays with data readouts, status bars, and system diagnostics. Palette: military
gray, Federation white, accent blue/red, hazard stripes (yellow-black diagonal).
Technical stencil block lettering with katakana character accents. Measurement
callouts with leader lines. Reference grid overlay in background.

**Content affinity:** `technical, process`

---

### 4. Warhammer 40K
> Grimdark miniature painting — weathered, gothic, parchment textures

Battle-weathered textures throughout: chipping paint, rust streaks, grime. Gothic
imperial architecture motifs as decorative framing. Palette: Abaddon black (#1C1C1C),
bone/skull cream (#E8D5B0), Mephiston red (#8B2020), Macragge blue, aged gold.
Parchment scroll backgrounds for text areas with ornate gothic borders. Visible
hand-painted brushstroke texture. Body text in gothic blackletter.

**Content affinity:** `culture, narrative`

---

### 5. Pixel Art (8-bit)
> Retro NES/SNES console — sprite art, hard pixels, limited palette

Hard pixel edges with strictly limited 16-color palette — no gradients anywhere.
Every element drawn as sprite art at 16×16 or 32×32 pixel resolution. Background
tiles create repeating patterns. Health bar and score UI elements as decorative
chrome. Monospace pixel font throughout. The entire image reads as a screenshot from
a 1988 game console.

**Content affinity:** `narrative, educational, culture`

---

### 6. Cyberpunk / Neon
> Dark backgrounds, neon glow, CRT scan lines — developer-native

Near-black background (#0A0A0F). All elements outlined with electric neon glow:
cyan (#00FFFF), hot magenta (#FF00CC), UV purple (#9D00FF), acid green (#39FF14).
Bloom glow effect and light falloff around all neon elements. Horizontal CRT
scan-line texture overlay. Condensed monospace typography with glitch/corruption
artifacts. Neon circuit traces as connecting lines.

**Content affinity:** `technical, data`

---

### 7. Vintage Science Poster
> 1960s natural history museum — aged paper, fine-line illustrations

Aged cream/ivory paper background with subtle foxing spots and paper grain. Fine-line
technical ink drawings with detailed labeled cross-sections and anatomical precision.
Authoritative serif typography (Garamond/Times Roman). Palette: rich browns, forest
greens, dusty orange, warm ivory, deep navy blue accents. The authority of a
Smithsonian exhibit.

**Content affinity:** `technical, educational`

---

### 8. Blueprint / Schematic
> White lines on Prussian blue — engineering precision

Prussian blue background (#003366). All elements in crisp white linework only — no
color fills. Regular grid of thin white lines across entire background. Technical
schematic line drawings with measurement callouts, leader lines, labeled part
annotations. Technical stencil lettering. Title block in lower-right corner.
Blueprint fold-crease marks.

**Content affinity:** `technical, process`

---

### 9. Knolling (Flat Lay)
> 90° organised objects — satisfying, premium, product-focused

Top-down bird's-eye view of physical objects arranged at perfect 90-degree angles
with precise, equal spacing. Objects cast crisp hard shadows from a single overhead
light on a white or marble surface. Clean sans-serif labels next to each object. All
objects perfectly parallel or perpendicular to the frame.

**Content affinity:** `showcase`

---

### 10. Da Vinci Notebook
> Renaissance scientific manuscript — sepia ink, parchment, intellectual curiosity

Warm aged parchment/vellum background (#D4C4A0) with visible paper grain. Sepia
brown ink fine-line sketches with classical italic script annotations. Red chalk
shading accents on key features. Mirror-writing flourishes as decorative elements.
Geometric studies alongside the main content. Marginal notes. The intellectual
curiosity of a Renaissance scientific mind.

**Content affinity:** `technical, educational`

---

### 11. Storybook Watercolor
> Soft painted textures, warm washes, picture-book warmth

Soft watercolor washes with visible paper texture and characteristic bleeding edges
where wet paint meets dry paper. Muted palette: warm terracotta, sage green, cream,
coffee brown, dusty rose. Rounded, friendly illustrations with a gentle personality.
Loose brush lettering for labels. No hard edges — everything organic and handmade.

**Content affinity:** `narrative`

---

### 12. Pop Art (Warhol / Lichtenstein)
> Bold flat graphics, Ben-Day dots, consumer culture

Bold flat graphic forms with thick black outlines on everything. Ben-Day dot pattern
as the primary shading and texture technique. Palette strictly: canary yellow
(#FFE600), primary red (#E8311E), royal blue (#003EB2), black, white — zero
gradients. Warhol-style repetition and Lichtenstein-style speech bubbles. Very
graphic and punchy.

**Content affinity:** `data, culture`

---

### 13. Neon Nightlife / Neon Sign
> Physical glass neon tubes on dark brick wall — intimate, atmospheric

Physical neon glass tube sign installations on a dark textured brick wall. Glowing
glass neon tubes form shapes and letters with realistic bloom and light falloff on
surrounding brick. Atmospheric haze between signs. Neon tube colors: warm white,
amber, red, blue. Connecting arrows also in neon tubing. The intimacy of a vintage
coffee bar or jazz club.

**Content affinity:** `culture, narrative`

---

### 14. Vintage Travel Poster (WPA / Art Deco)
> Screen-print flat colors, Art Deco letterforms, 1930s optimism

WPA Works Progress Administration screen-print style — exactly 5 flat color zones
per poster, zero gradients. Art Deco geometric composition and condensed letterforms.
Bold silhouetted landscapes, large focal imagery, fan-shaped sun rays. The optimistic,
dignified aesthetic of 1930s New Deal American public art.

**Content affinity:** `narrative, process`

---

### 15. Paper Cutout
> Construction paper collage — layered shapes, scissor edges, tactile depth

Every shape hand-cut from construction paper with visible slightly irregular scissor
edges. Layered paper shapes creating physical depth with drop shadows between layers.
Construction paper palette: red, yellow, orange, green, brown, tan, cream. Slight
paper grain texture on all surfaces. The tactile handmade warmth of a thoughtfully
composed elementary school art project.

**Content affinity:** `educational, narrative`

---

### 16. Graffiti Wall
> Spray paint on concrete — wildstyle lettering, urban energy

Concrete wall texture clearly visible throughout. Aerosol spray paint characteristics:
drips running from letters, overspray halos, layered color builds. Wildstyle bubble
letter typography outlined in black. Vibrant street art palette: electric blue, lime
green, hot orange, magenta, yellow, white outline on gray concrete. The scale and
energy of a full building-side mural.

**Content affinity:** `culture`

---

### 17. Chalkboard Art
> Chalk on dark green slate — artisanal, educational, coffee shop warmth

Dark green slate chalkboard texture. White chalk for main illustrations and headings —
slightly dusty, translucent, hand-drawn quality. Colored chalk accents: yellow,
red/coral, green, orange. Beautiful hand-lettered headers with decorative serif
flourishes. Decorative chalk borders and frames. The warm, artisanal atmosphere of a
specialty coffee shop menu board.

**Content affinity:** `educational`

---

## Agent Behavior Changes

### Step 2 — Small Addition

Step 2 already outputs:
```
Panel count: N
Recommended layout: [layout type]
```

Add one line:
```
Content types: [tag1, tag2]
```

This feeds both Step 3 style preview and Step 5B candidate pool selection.

---

### Step 3 — Style Preview (conditional)

**Trigger:** Only when the user has not specified an aesthetic (no inline style name, no reference image passed).

**When NOT triggered (no change to existing flow):**
- User specifies aesthetic inline → inline shortcut fires, skip to Step 4
- User passes a reference image → Style Reference shortcut fires, skip to Step 4

**When triggered (new):**

The agent presents the 3 planned candidates by name before generating anything:

```
I'll generate 3 variations. Based on your [content types] content, here's
what I'm planning:

  → Cyberpunk / Neon
  → Blueprint / Schematic
  → Gundam / Mecha

Other styles that fit well:
  Dark Mode Tech · Vintage Science Poster · Comic Book · Da Vinci Notebook

Also available (lower fit for this content):
  Knolling (better for product showcases) · Pop Art (better for bold data) · …

Say "go" to generate these 3, swap a style by name, or ask to see all styles.
```

This runs before any generation cost is incurred. The primary action ("go") keeps
the fast path intact. Users who want to explore can engage; users who don't can
ignore it.

---

### Step 5B — Expanded Candidate Pool

The Tier 1 candidate pool (when no aesthetic is locked) now includes extended
library styles in addition to the flagship 6.

**Pool construction:**
```
Pool = flagship 6
     + extended library styles where ANY affinity tag matches ANY detected
       content type (boolean OR — one match is sufficient)
     + (optional) 1 wildcard: one extended style with no affinity overlap,
       for serendipity — only when the eligible pool contains 6+ styles

Agent picks 3 maximally contrasting styles from this pool.
```

If the user says "show me more styles" after seeing 3 candidates, the agent picks 3
different styles from the remaining pool (styles not yet shown in this session).

---

### Single-Panel Flow Note

For single-panel infographics with multi-candidate selection, the flow ends at Step
5B — the user picks one of the 3 candidates and that image is the final output. The
cross-panel quality review (Step 6) only applies when Panels 2-N exist. The
dealbreaker pre-screen (already implemented) is the automated quality gate before
the candidates are presented.

---

## Style Audition Recipe

**File:** `recipes/style-audition.yaml`

A recipe for evaluating new candidate styles before adding them to the library.
Automates the "batch generation → visual review → decision" workflow.

**Inputs:**
- `styles`: list of style names to audition
- `test_prompts`: 1–2 infographic topics (recommend one organic/process topic +
  one technical topic for range assessment)

**What it does:**
1. For each `style × test_prompt` combination, generates a single-panel infographic
   in parallel
2. Stitches all outputs into a comparison gallery HTML
3. Optionally scores each output through the eval rubric for objective dimension
   scores alongside visual review

**Why it exists:**
New style requests will continue to come in from users and community members. This
recipe makes the evaluation process repeatable and fast — run it, review the gallery,
make the call — rather than requiring a manual brainstorm session for each new
candidate.

---

## What Doesn't Change

- Flagship 6 style specs — no edits
- Multi-panel consistency pipeline (style brief → reconciliation → chain)
- Style brief format — extended library styles produce the same 7-dimension brief at
  generation time, assembled from the paragraph description at runtime
- Cross-panel critic
- Existing tests

---

## Files to Change

| File | What changes |
|------|-------------|
| `docs/style-guide.md` | New `## Extended Library` section with 17 style entries |
| `agents/infographic-builder.md` Step 2 | Add `Content types:` to output |
| `agents/infographic-builder.md` Step 3 | New conditional style preview block |
| `agents/infographic-builder.md` Step 5B | Extended library in Tier 1 candidate pool |
| `recipes/style-audition.yaml` | New recipe (create) |
| `tests/test_extended_library.py` | New test file asserting library structure |

---

## Open Questions

None — all design decisions resolved.
