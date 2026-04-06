# Extended Style Library Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add 17 extended library styles with content affinity tags to infographic-builder, surface them through the candidate pool and a conditional pre-generation style preview, and ship a style audition recipe for evaluating future candidates.

**Architecture:** A new `## Extended Library` section in `docs/style-guide.md` holds 17 paragraph-format style descriptions with affinity tags. Three small additions to `agents/infographic-builder.md` wire those styles into the existing multi-candidate pipeline (Step 2 outputs content types, Step 3 shows a conditional preview before generation, Step 5B expands the candidate pool). A new `recipes/style-audition.yaml` automates future style evaluation.

**Tech Stack:** Markdown (style guide + agent), YAML (recipe), pytest (tests assert markdown presence — same pattern as all existing tests in this project)

---

## File Map

| File | Action | What changes |
|------|--------|-------------|
| `tests/test_extended_library.py` | Create | All assertions for this feature (written first) |
| `docs/style-guide.md` | Modify | Append `## Extended Library` section after line 519 |
| `agents/infographic-builder.md` | Modify | Step 2: add `Content types:` output; Step 3: add conditional preview block; Step 5B: add extended library pool logic |
| `recipes/style-audition.yaml` | Create | Style audition recipe |

---

## Task 1: Extended Library in style-guide.md

**Files:**
- Create: `tests/test_extended_library.py`
- Modify: `docs/style-guide.md`

---

- [ ] **Step 1: Write the failing test file**

Create `tests/test_extended_library.py` with this exact content:

```python
import os
import pytest

STYLE_GUIDE_PATH = os.path.join(os.path.dirname(__file__), '..', 'docs', 'style-guide.md')
AGENT_PATH = os.path.join(os.path.dirname(__file__), '..', 'agents', 'infographic-builder.md')

EXTENDED_LIBRARY_STYLES = [
    "Minecraft Voxel",
    "Comic Book / Graphic Novel",
    "Gundam / Mobile Suit Mecha",
    "Warhammer 40K",
    "Pixel Art (8-bit)",
    "Cyberpunk / Neon",
    "Vintage Science Poster",
    "Blueprint / Schematic",
    "Knolling (Flat Lay)",
    "Da Vinci Notebook",
    "Storybook Watercolor",
    "Pop Art (Warhol / Lichtenstein)",
    "Neon Nightlife / Neon Sign",
    "Vintage Travel Poster (WPA / Art Deco)",
    "Paper Cutout",
    "Graffiti Wall",
    "Chalkboard Art",
]


# ── Style Guide: Extended Library Section ────────────────────────────────────

def test_extended_library_section_exists():
    with open(STYLE_GUIDE_PATH) as f:
        content = f.read()
    assert "## Extended Library" in content


@pytest.mark.parametrize("style_name", EXTENDED_LIBRARY_STYLES)
def test_style_has_heading(style_name):
    with open(STYLE_GUIDE_PATH) as f:
        content = f.read()
    assert f"### {style_name}" in content, f"Missing heading: ### {style_name}"


@pytest.mark.parametrize("style_name", EXTENDED_LIBRARY_STYLES)
def test_style_has_tagline(style_name):
    with open(STYLE_GUIDE_PATH) as f:
        content = f.read()
    heading_pos = content.find(f"### {style_name}")
    assert heading_pos != -1, f"Heading not found for {style_name}"
    section = content[heading_pos:heading_pos + 400]
    assert "\n> " in section, f"Missing blockquote tagline after ### {style_name}"


@pytest.mark.parametrize("style_name", EXTENDED_LIBRARY_STYLES)
def test_style_has_affinity_tags(style_name):
    with open(STYLE_GUIDE_PATH) as f:
        content = f.read()
    heading_pos = content.find(f"### {style_name}")
    assert heading_pos != -1, f"Heading not found for {style_name}"
    next_heading = content.find("\n###", heading_pos + 4)
    section = content[heading_pos:next_heading] if next_heading != -1 else content[heading_pos:]
    assert "**Content affinity:**" in section, \
        f"Missing **Content affinity:** in ### {style_name}"


# ── Agent: Step 2 content types (Task 2) ─────────────────────────────────────

def test_agent_step2_outputs_content_types():
    with open(AGENT_PATH) as f:
        content = f.read()
    assert "Content types:" in content


# ── Agent: Step 3 style preview (Task 3) ─────────────────────────────────────

def test_agent_step3_has_style_preview():
    with open(AGENT_PATH) as f:
        content = f.read()
    assert "swap a style by name" in content


# ── Agent: Step 5B extended library pool (Task 4) ────────────────────────────

def test_agent_step5b_has_extended_library_pool():
    with open(AGENT_PATH) as f:
        content = f.read()
    assert "extended library" in content.lower()
    assert "affinity" in content.lower()
```

---

- [ ] **Step 2: Run tests to confirm they all fail**

```bash
cd /Users/gurkaransingh/Desktop/Development/infographic-builder
python -m pytest tests/test_extended_library.py -v 2>&1 | head -60
```

Expected: All tests FAIL. `test_extended_library_section_exists` fails with `AssertionError`. The parametrized style tests fail with `AssertionError: Missing heading`. The agent tests fail because the text doesn't exist yet. If any test passes unexpectedly, stop and investigate before proceeding.

---

- [ ] **Step 3: Append the Extended Library section to docs/style-guide.md**

Open `docs/style-guide.md` and append the following block at the very end of the file (after the existing pre-generation checklist content, line 519+):

```markdown

---

## Extended Library

Seventeen additional styles available through the candidate pool and inline style shortcuts.
Each style carries a **content affinity** list — the content types it works best for.
The agent uses affinity to rank styles in the Tier 1 candidate pool (see Agent Behavior).

### Minecraft Voxel
> Constructive, blocky, instantly recognisable

Voxel block aesthetic. Every element built from chunky 3D pixel cubes with visible
block faces in isometric or front-facing arrangement. Palette: dirt brown, stone gray,
grass green, sky blue, obsidian black, diamond cyan, gold. Pixelated bitmap font in
white or gold. Soft ambient occlusion between blocks. Zero curves — hard block edges
throughout.

**Content affinity:** `narrative, educational, culture`

---

### Comic Book / Graphic Novel
> Vintage Marvel/DC — bold ink, halftone dots, panel energy

Bold black ink outlines (3–4px) on every element. Flat cel-shaded colors with halftone
Ben-Day dot shading in shadow areas. Dynamic panel grid with jagged borders. Palette:
vibrant CMYK primaries (hero red, captain blue, dynamic yellow) on cream newsprint.
Comic lettering ALL CAPS in speech bubbles and yellow caption boxes. Visible ink line
weight variation.

**Content affinity:** `process, narrative, educational`

---

### Gundam / Mobile Suit Mecha
> Japanese mecha engineering — panel lines, HUD overlays, military precision

Mechanical surface detail and panel lines on all illustrated elements. HUD/display UI
overlays with data readouts, status bars, and system diagnostics. Palette: military
gray, Federation white, accent blue/red, hazard stripes (yellow-black diagonal).
Technical stencil block lettering with katakana character accents. Measurement callouts
with leader lines. Reference grid overlay in background.

**Content affinity:** `technical, process`

---

### Warhammer 40K
> Grimdark miniature painting — weathered, gothic, parchment textures

Battle-weathered textures throughout: chipping paint, rust streaks, grime. Gothic
imperial architecture motifs as decorative framing. Palette: Abaddon black (#1C1C1C),
bone/skull cream (#E8D5B0), Mephiston red (#8B2020), Macragge blue, aged gold.
Parchment scroll backgrounds for text areas with ornate gothic borders. Visible
hand-painted brushstroke texture. Body text in gothic blackletter.

**Content affinity:** `culture, narrative`

---

### Pixel Art (8-bit)
> Retro NES/SNES console — sprite art, hard pixels, limited palette

Hard pixel edges with strictly limited 16-color palette — no gradients anywhere. Every
element drawn as sprite art at 16×16 or 32×32 pixel resolution. Background tiles create
repeating patterns. Health bar and score UI elements as decorative chrome. Monospace
pixel font throughout. The entire image reads as a screenshot from a 1988 game console.

**Content affinity:** `narrative, educational, culture`

---

### Cyberpunk / Neon
> Dark backgrounds, neon glow, CRT scan lines — developer-native

Near-black background (#0A0A0F). All elements outlined with electric neon glow: cyan
(#00FFFF), hot magenta (#FF00CC), UV purple (#9D00FF), acid green (#39FF14). Bloom glow
effect and light falloff around all neon elements. Horizontal CRT scan-line texture
overlay. Condensed monospace typography with glitch/corruption artifacts. Neon circuit
traces as connecting lines.

**Content affinity:** `technical, data`

---

### Vintage Science Poster
> 1960s natural history museum — aged paper, fine-line illustrations

Aged cream/ivory paper background with subtle foxing spots and paper grain. Fine-line
technical ink drawings with detailed labeled cross-sections and anatomical precision.
Authoritative serif typography (Garamond/Times Roman). Palette: rich browns, forest
greens, dusty orange, warm ivory, deep navy blue accents. The authority of a Smithsonian
exhibit.

**Content affinity:** `technical, educational`

---

### Blueprint / Schematic
> White lines on Prussian blue — engineering precision

Prussian blue background (#003366). All elements in crisp white linework only — no
color fills. Regular grid of thin white lines across entire background. Technical
schematic line drawings with measurement callouts, leader lines, labeled part
annotations. Technical stencil lettering. Title block in lower-right corner. Blueprint
fold-crease marks.

**Content affinity:** `technical, process`

---

### Knolling (Flat Lay)
> 90° organised objects — satisfying, premium, product-focused

Top-down bird's-eye view of physical objects arranged at perfect 90-degree angles with
precise, equal spacing. Objects cast crisp hard shadows from a single overhead light on
a white or marble surface. Clean sans-serif labels next to each object. All objects
perfectly parallel or perpendicular to the frame.

**Content affinity:** `showcase`

---

### Da Vinci Notebook
> Renaissance scientific manuscript — sepia ink, parchment, intellectual curiosity

Warm aged parchment/vellum background (#D4C4A0) with visible paper grain. Sepia brown
ink fine-line sketches with classical italic script annotations. Red chalk shading
accents on key features. Mirror-writing flourishes as decorative elements. Geometric
studies alongside the main content. Marginal notes. The intellectual curiosity of a
Renaissance scientific mind.

**Content affinity:** `technical, educational`

---

### Storybook Watercolor
> Soft painted textures, warm washes, picture-book warmth

Soft watercolor washes with visible paper texture and characteristic bleeding edges where
wet paint meets dry paper. Muted palette: warm terracotta, sage green, cream, coffee
brown, dusty rose. Rounded, friendly illustrations with a gentle personality. Loose brush
lettering for labels. No hard edges — everything organic and handmade.

**Content affinity:** `narrative`

---

### Pop Art (Warhol / Lichtenstein)
> Bold flat graphics, Ben-Day dots, consumer culture

Bold flat graphic forms with thick black outlines on everything. Ben-Day dot pattern as
the primary shading and texture technique. Palette strictly: canary yellow (#FFE600),
primary red (#E8311E), royal blue (#003EB2), black, white — zero gradients.
Warhol-style repetition and Lichtenstein-style speech bubbles. Very graphic and punchy.

**Content affinity:** `data, culture`

---

### Neon Nightlife / Neon Sign
> Physical glass neon tubes on dark brick wall — intimate, atmospheric

Physical neon glass tube sign installations on a dark textured brick wall. Glowing glass
neon tubes form shapes and letters with realistic bloom and light falloff on surrounding
brick. Atmospheric haze between signs. Neon tube colors: warm white, amber, red, blue.
Connecting arrows also in neon tubing. The intimacy of a vintage coffee bar or jazz club.

**Content affinity:** `culture, narrative`

---

### Vintage Travel Poster (WPA / Art Deco)
> Screen-print flat colors, Art Deco letterforms, 1930s optimism

WPA Works Progress Administration screen-print style — exactly 5 flat color zones per
poster, zero gradients. Art Deco geometric composition and condensed letterforms. Bold
silhouetted landscapes, large focal imagery, fan-shaped sun rays. The optimistic,
dignified aesthetic of 1930s New Deal American public art.

**Content affinity:** `narrative, process`

---

### Paper Cutout
> Construction paper collage — layered shapes, scissor edges, tactile depth

Every shape hand-cut from construction paper with visible slightly irregular scissor
edges. Layered paper shapes creating physical depth with drop shadows between layers.
Construction paper palette: red, yellow, orange, green, brown, tan, cream. Slight paper
grain texture on all surfaces. The tactile handmade warmth of a thoughtfully composed
elementary school art project.

**Content affinity:** `educational, narrative`

---

### Graffiti Wall
> Spray paint on concrete — wildstyle lettering, urban energy

Concrete wall texture clearly visible throughout. Aerosol spray paint characteristics:
drips running from letters, overspray halos, layered color builds. Wildstyle bubble
letter typography outlined in black. Vibrant street art palette: electric blue, lime
green, hot orange, magenta, yellow, white outline on gray concrete. The scale and energy
of a full building-side mural.

**Content affinity:** `culture`

---

### Chalkboard Art
> Chalk on dark green slate — artisanal, educational, coffee shop warmth

Dark green slate chalkboard texture. White chalk for main illustrations and headings —
slightly dusty, translucent, hand-drawn quality. Colored chalk accents: yellow,
red/coral, green, orange. Beautiful hand-lettered headers with decorative serif
flourishes. Decorative chalk borders and frames. The warm, artisanal atmosphere of a
specialty coffee shop menu board.

**Content affinity:** `educational`
```

---

- [ ] **Step 4: Run the style guide tests to confirm they pass**

```bash
python -m pytest tests/test_extended_library.py -k "style_guide or extended_library or heading or tagline or affinity" -v
```

Expected: `test_extended_library_section_exists` PASS, all 17 `test_style_has_heading` PASS, all 17 `test_style_has_tagline` PASS, all 17 `test_style_has_affinity_tags` PASS. The agent tests (Tasks 2–4) still fail — that is expected.

---

- [ ] **Step 5: Run the full existing test suite to confirm no regressions**

```bash
python -m pytest tests/ -v --ignore=tests/test_extended_library.py 2>&1 | tail -20
```

Expected: All pre-existing tests pass. If any fail, stop and investigate — the only change was appending to `style-guide.md`, so a failure here means a formatting issue in the appended content.

---

- [ ] **Step 6: Commit**

```bash
git add tests/test_extended_library.py docs/style-guide.md
git commit -m "feat: add extended library with 17 styles to style guide"
```

---

## Task 2: Agent Step 2 — Content Types Output

**Files:**
- Modify: `agents/infographic-builder.md` (Step 2 section, lines ~83–90)

---

- [ ] **Step 1: Confirm the failing test**

```bash
python -m pytest tests/test_extended_library.py::test_agent_step2_outputs_content_types -v
```

Expected: FAIL — `AssertionError` because `Content types:` is not yet in the agent file.

---

- [ ] **Step 2: Find the Step 2 output block in agents/infographic-builder.md**

Open `agents/infographic-builder.md`. Find the section for Step 2 (around line 83–90). It currently produces output like:

```
Panel count: N
Recommended layout: [layout type]
```

Add `Content types: [tag1, tag2]` as a third line in that output block. The tags are drawn from the vocabulary: `process`, `technical`, `narrative`, `data`, `showcase`, `educational`, `culture`. The agent detects these from the user's prompt content.

The updated Step 2 output instruction should read (adapt the existing wording, don't replace the whole step):

```
Output at end of Step 2:
- Panel count: [N]
- Recommended layout: [layout type]
- Content types: [comma-separated tags from: process, technical, narrative, data, showcase, educational, culture]
```

---

- [ ] **Step 3: Run the test to confirm it passes**

```bash
python -m pytest tests/test_extended_library.py::test_agent_step2_outputs_content_types -v
```

Expected: PASS.

---

- [ ] **Step 4: Run the full test suite**

```bash
python -m pytest tests/ -v 2>&1 | tail -20
```

Expected: All previous tests still pass. Only Task 3 and Task 4 agent tests still fail.

---

- [ ] **Step 5: Commit**

```bash
git add agents/infographic-builder.md
git commit -m "feat: add content type detection output to agent Step 2"
```

---

## Task 3: Agent Step 3 — Conditional Style Preview

**Files:**
- Modify: `agents/infographic-builder.md` (Step 3 section, lines ~92–119)

---

- [ ] **Step 1: Confirm the failing test**

```bash
python -m pytest tests/test_extended_library.py::test_agent_step3_has_style_preview -v
```

Expected: FAIL.

---

- [ ] **Step 2: Add the conditional style preview block to Step 3**

Open `agents/infographic-builder.md`. Find Step 3d — it currently reads something like:
```
3d. If no aesthetic specified, defer aesthetic selection to Step 5B multi-candidate presentation.
```

Replace Step 3d with this expanded version:

```markdown
**3d. If no aesthetic specified — show style preview before generating:**

Present the planned candidates and available styles to the user *before* running
Step 4 or generating anything. Use the content types from Step 2 to rank styles.

Say:

> I'll generate 3 variations. Based on your **[content types]** content, here's
> what I'm planning to try:
>
> → [Style A]
> → [Style B]
> → [Style C]
>
> Other styles that fit well: [list affinity-matched styles not in the 3 above]
>
> Also available (lower fit for this content): [list off-affinity styles with
> a "(better for [their affinity])" note for each]
>
> Say **go** to generate these 3, swap a style by name, or ask to see all styles.

**Stop and wait for user response before proceeding.**

If the user says "go" (or equivalent confirmation) → proceed to Step 4 with the
3 planned styles.

If the user swaps a style by name (e.g., "use Blueprint instead of Style A") →
update the planned 3 and proceed.

If the user asks to see all styles → list the full extended library grouped by
affinity fit, then wait again.

**Candidate pool for the 3 planned styles:**
- Flagship 6 are always eligible
- Extended library styles where ANY affinity tag matches ANY detected content
  type (boolean OR — one match is sufficient to include)
- Optional wildcard: one extended style outside affinity overlap, only when the
  eligible pool contains 6 or more styles; include at most 1 per round
- Pick 3 maximally contrasting styles from this pool
```

---

- [ ] **Step 3: Run the test**

```bash
python -m pytest tests/test_extended_library.py::test_agent_step3_has_style_preview -v
```

Expected: PASS (the phrase "swap a style by name" is now in the agent file).

---

- [ ] **Step 4: Run the full test suite**

```bash
python -m pytest tests/ -v 2>&1 | tail -20
```

Expected: `test_agent_step5b_has_extended_library_pool` still fails (Task 4), all others pass.

---

- [ ] **Step 5: Commit**

```bash
git add agents/infographic-builder.md
git commit -m "feat: add conditional style preview to agent Step 3"
```

---

## Task 4: Agent Step 5B — Extended Library Candidate Pool

**Files:**
- Modify: `agents/infographic-builder.md` (Step 5B section, lines ~154–172)

---

- [ ] **Step 1: Confirm the failing test**

```bash
python -m pytest tests/test_extended_library.py::test_agent_step5b_has_extended_library_pool -v
```

Expected: FAIL.

---

- [ ] **Step 2: Update Step 5B to reference the extended library**

Open `agents/infographic-builder.md`. Find Step 5b-i (around lines 154–172). It currently describes the Variation Cascade (Tier 1: vary aesthetic, Tier 2: vary axis, Tier 3: model freedom).

In the Tier 1 description, add the extended library pool logic. Find the sentence that describes where Tier 1 styles come from — it currently references the flagship curated aesthetics. Update it to:

```markdown
**Tier 1 — Vary aesthetic (highest diversity)**

**When:** User specified topic only, no aesthetic locked (Step 3c inline shortcut
and Step 3b reference shortcut did not fire, and user confirmed the planned styles
at Step 3d).

Candidate pool:
- Flagship 6 (always eligible)
- Extended library styles where ANY affinity tag matches ANY content type from
  Step 2 output (boolean OR)
- Optional wildcard: 1 extended style outside affinity overlap, only when eligible
  pool ≥ 6 styles

Pick 3 maximally contrasting styles from this pool. Generate each candidate
in parallel.

If the user says "show me more styles" after candidate presentation → pick 3
different styles from the remaining pool (styles not yet shown this session).
```

---

- [ ] **Step 3: Run the test**

```bash
python -m pytest tests/test_extended_library.py::test_agent_step5b_has_extended_library_pool -v
```

Expected: PASS.

---

- [ ] **Step 4: Run the full test suite — all tests should now pass**

```bash
python -m pytest tests/ -v 2>&1 | tail -30
```

Expected: All tests pass, including all 51 parametrized extended library tests (17 × 3 style guide checks) and 5 agent tests.

---

- [ ] **Step 5: Commit**

```bash
git add agents/infographic-builder.md
git commit -m "feat: expand Step 5B Tier 1 candidate pool with extended library styles"
```

---

## Task 5: Style Audition Recipe

**Files:**
- Create: `recipes/style-audition.yaml`

---

- [ ] **Step 1: Create the recipe file**

Create `recipes/style-audition.yaml` with this content:

```yaml
name: style-audition
description: |
  Audition candidate styles by generating a single-panel infographic for each
  style against a test prompt. Outputs sample images for visual review.

  Usage:
    context:
      styles: ["Blueprint / Schematic", "Cyberpunk / Neon", "Da Vinci Notebook"]
      test_prompt: "How Large Language Models Work"
      output_dir: "./style-audition"

context:
  styles:
    - "Minecraft Voxel"
    - "Comic Book / Graphic Novel"
    - "Blueprint / Schematic"
  test_prompt: "How Large Language Models Work"
  output_dir: "./style-audition"

steps:
  - name: generate-samples
    foreach: "{{styles}}"
    item_var: style
    parallel: true
    agent: infographic-builder
    instruction: |
      Generate a single-panel infographic about: "{{test_prompt}}"

      Use the {{style}} aesthetic. Apply it directly — do not present a style
      selection menu. The style is already chosen.

      Save the output image to: {{output_dir}}/{{style}}.png
      Replace any spaces or special characters in the filename with hyphens.

      Stop after generating the single panel. Do not stitch, do not ask about
      multi-panel, do not continue to quality review.

  - name: build-gallery
    agent: infographic-builder
    instruction: |
      Build an HTML comparison gallery for the style audition results.

      Look in {{output_dir}}/ for all .png files generated in the previous step.
      Create {{output_dir}}/gallery.html containing:

      - A CSS grid of cards, 3 columns
      - Each card shows the PNG image with the style name as a label
      - Hovering a card shows the style name in a tooltip
      - Clicking a card cycles through: unmarked → IN (green border) → CUT (red
        border) → unmarked
      - A sticky footer counts IN and CUT selections
      - Title at top: "Style Audition: {{test_prompt}}"

      Serve the gallery by opening {{output_dir}}/gallery.html in the browser.
      Tell the user: "Open {{output_dir}}/gallery.html to review. Click once to
      mark IN, twice to mark CUT."
```

---

- [ ] **Step 2: Validate the recipe**

```bash
amplifier tool invoke recipes operation=validate recipe_path=recipes/style-audition.yaml
```

Expected: `{"valid": true}` or equivalent success output. If validation fails, fix the YAML structure — check indentation and that `foreach` + `parallel` are valid together (they are, per the recipe schema).

---

- [ ] **Step 3: Commit**

```bash
git add recipes/style-audition.yaml
git commit -m "feat: add style-audition recipe for evaluating new candidate styles"
```

---

## Final Verification

- [ ] **Run the complete test suite one last time**

```bash
python -m pytest tests/ -v 2>&1 | tail -40
```

Expected: All tests pass. Count: 51 new parametrized tests (17 styles × 3 assertions each) + 5 new agent tests + all existing tests.

- [ ] **Confirm git log looks clean**

```bash
git log --oneline -6
```

Expected output (roughly):
```
[hash] feat: add style-audition recipe for evaluating new candidate styles
[hash] feat: expand Step 5B Tier 1 candidate pool with extended library styles
[hash] feat: add conditional style preview to agent Step 3
[hash] feat: add content type detection output to agent Step 2
[hash] feat: add extended library with 17 styles to style guide
[hash] docs: add extended style library design spec
```
