# Infographic Design Style Guide

The single source of truth for all design knowledge used by the infographic-builder
agent. Workflow and procedural logic live in the agent definition -- this file covers
what to design, not when to do it.

## Default Style

Unless the user specifies otherwise, generate infographics with:

- **Layout**: Vertical flow (top to bottom), clear sections with visual separators
- **Background**: Clean, solid or subtle gradient -- never busy or textured
- **Typography**: Bold headers, readable body text, consistent hierarchy
- **Icons**: Simple, flat icons to represent concepts -- avoid photorealistic clipart
- **Color**: 2-3 primary colors plus neutrals. High contrast for readability.
- **Data viz**: Use charts, graphs, or visual metaphors appropriate to the data type
- **Whitespace**: Generous -- let the content breathe

> **Note:** The Default Style above _is_ Clean Minimalist. When a user selects
> "Clean Minimalist" from the aesthetic options, apply these defaults as-is.

## Aesthetics

Six curated prompt templates spanning the professional-to-playful spectrum, plus
open-ended freeform input. Each template overrides three prompt dimensions
(typography, palette, icon style) and bakes in additional modifiers (texture,
lighting, mood) that stay invisible to the user.

When constructing a generation prompt, load the selected aesthetic's template and
use its properties to fill the **Style modifier** slot (item 5 under Prompt
Engineering below).

### 1. Clean Minimalist

> Professional, Swiss design, boardroom-ready

- **Background:** Solid white (#FFFFFF) or subtle light gradient (#F5F5F5 → #FFFFFF)
- **Typography:** Helvetica/sans-serif; bold weight headers, light weight body; dark gray (#333333) text
- **Icons:** Flat icons in the primary accent color, no outlines
- **Color palette:** 1 primary accent + 1 secondary accent + neutral grays.
  Recommended pairings (pick one row):

  | Primary | Secondary | Vibe |
  |---------|-----------|------|
  | Deep teal (#0D7377) | Warm coral (#E8634A) | Balanced, modern |
  | Navy blue (#1B3A5C) | Gold (#D4A843) | Authoritative, premium |
  | Slate blue (#4A6FA5) | Soft amber (#E8A838) | Approachable, warm |

  The primary accent drives headers, icons, and dividers. The secondary accent
  is used sparingly — data highlights, callout boxes, one or two key emphasis
  elements per panel. This prevents monochrome flatness while keeping the
  palette controlled.
- **Lighting:** Flat, even — no shadows, no directional light
- **Texture:** None — pure clean surfaces
- **Mood:** Calm, authoritative, boardroom-safe

### 2. Dark Mode Tech

> Developer-native, neon on dark, glassmorphism

- **Background:** Dark slate (#1A1A2E to #16213E), subtle grid or circuit-trace pattern
- **Typography:** Monospace or tech sans-serif; neon-colored headers, light gray (#E0E0E0) body text
- **Icons:** Glassmorphism — frosted glass containers with neon glow outlines
- **Color palette:** Neon cyan (#00F5FF), electric purple (#B026FF), neon green (#39FF14) on dark
- **Lighting:** Neon glow, subtle ambient light bloom, no natural light sources
- **Texture:** Faint digital grid or noise overlay
- **Mood:** Futuristic, technical, developer-native

### 3. Bold Editorial

> Wired/Vox magazine style, high contrast, commanding

- **Background:** High-contrast color blocks — bold red, deep navy, bright yellow as section fills
- **Typography:** Massive serif headlines (72pt+ feel), tight tracking, bold weight; clean sans-serif body
- **Icons:** Collage-style mixed elements — cutout photos, bold graphic shapes, editorial illustrations
- **Color palette:** 2-3 bold primaries (red + navy + yellow, or orange + black + white), no pastels
- **Lighting:** Dramatic directional lighting, strong highlights and deep shadows
- **Texture:** Slight paper grain or halftone dot overlay
- **Mood:** High energy, commanding, magazine-cover striking

### 4. Hand-Drawn Sketchnote

> Casual, marker-on-notebook, creative

- **Background:** Off-white paper (#F5F0E8), lightly textured graph paper or dot grid, visible grain
- **Typography:** Hand-drawn marker lettering, slightly irregular baselines, doodle emphasis (underlines, circles, arrows)
- **Icons:** Hand-drawn sketch icons, wobbly outlines, filled with hatching or loose color wash
- **Color palette:** 3-4 marker colors — warm gray, teal, orange, red — like a real Copic/Sharpie palette on paper
- **Lighting:** Flat even — like scanning a notebook page
- **Texture:** Paper grain, visible notebook ruling or dot grid
- **Mood:** Casual, handmade, charming, deliberately imperfect

### 5. Claymation Studio

> Whimsical, tactile, plasticine textures

- **Background:** Choose based on content — for narrative, story-driven, or physical topics (daily routines, journeys, recipes, environments), build a **full 3D claymation environment** with sculpted clay scenery, props, and depth (rooms, forests, kitchens, landscapes). For abstract or conceptual topics (definitions, comparisons, data), use a **simple studio backdrop** — a cardboard-box diorama stage or craft-paper set with visible texture. The richer the subject's real-world setting, the richer the environment should be
- **Typography:** Rounded playful sans-serif; letters may appear sculpted from clay or extruded
- **Icons:** 3D sculpted plasticine/clay figures, fingerprint texture visible, rounded organic shapes
- **Color palette:** Warm saturated primaries — clay red, cobalt blue, sunshine yellow, grass green — like real plasticine
- **Lighting:** Soft diffused studio lighting with realistic cast shadows, shallow depth of field
- **Texture:** Visible clay fingerprints, slightly lumpy sculpted surfaces
- **Mood:** Whimsical, tactile, handmade, warm
- **Diorama compatible:** Yes — see Representation Mode above

### 6. Lego Brick Builder

> Playful, structural, plastic bricks

- **Background:** Plastic Lego baseplate — gray or green studded surface
- **Typography:** Blocky geometric letterforms; may appear embossed on Lego tiles or printed on brick faces
- **Icons:** Built from Lego bricks — recognizable objects constructed from studs and plates
- **Color palette:** Classic Lego primaries — red (#D01012), blue (#0057A6), yellow (#FFD700), green (#00852B), black, white
- **Lighting:** Macro photography lighting with shallow depth of field, plastic specular highlights
- **Texture:** Smooth injection-molded plastic, visible stud geometry
- **Mood:** Playful, structural, childhood delight, tilt-shift perspective
- **Diorama compatible:** Yes — see Representation Mode above

### Style Reference Mode

When the root session provides an `aesthetic_description` (extracted from a
user-provided reference image), the 6-option menu is skipped entirely. The
agent translates the aesthetic description into the same 7 style dimensions
used by the curated templates above: palette, typography, icons, background,
lighting, texture, and mood.

This produces the same shape of input that downstream steps (4–8) always
expect — no special casing required. The reference image's visual character
drives the aesthetic instead of a curated template or freeform description.

### Freeform Aesthetics

Users can describe any aesthetic beyond the featured six — "vintage travel poster",
"watercolor", "comic book", "pixel art", "corporate annual report". When a user
provides a freeform description:

1. Translate it into reasonable defaults for background, typography, icon style,
   color palette, lighting, texture, and mood
2. All structural prompt engineering still applies (output type, orientation,
   sections, text, aspect ratio) — only the visual treatment is freeform
3. Use your best design judgment — there is no failure mode, only best-effort
   interpretation

## Diorama Mode

3D-capable aesthetics (Lego, Claymation, freeform 3D) naturally bring
content to life in the medium. This is the default and needs no special prompting.

If the user asks for a **"diorama"**, frame the prompt as characters acting
out a scene. Dioramas work best for linear sequential workflows.

## Variation Cascade

When generating 3 candidates for Panel 1 selection, what to vary depends on what
the user has already specified. Three tiers, applied in priority order:

### Tier 1: Vary aesthetic (highest diversity)

**When:** User specified a topic but no aesthetic.

Generate 3 candidates each in a **different curated aesthetic**, selected to
maximize visual diversity across the professional-to-playful spectrum. Choose 3
aesthetics that contrast strongly — e.g., Clean Minimalist, Claymation Studio,
and Dark Mode Tech rather than three adjacent styles.

### Tier 2: Vary based on aesthetic type (medium diversity)

**When:** User specified an aesthetic (curated or freeform).

The variation axis depends on the aesthetic type:

| Aesthetic | Variation axis |
|-----------|----------------|
| Claymation Studio | Environment/setting |
| Lego Brick Builder | Environment/setting |
| Clean Minimalist | Composition |
| Dark Mode Tech | Composition |
| Bold Editorial | Composition |
| Hand-Drawn Sketchnote | Composition |
| Freeform | Composition |

**Composition directions** (flat/2D aesthetics — use all 3 across the candidates):

- Central focal point — hero visual dominates, supporting text arranged around it
- Scene-based — characters or objects act out the topic in a spatial arrangement
- Structured/diagrammatic — grid, flow, or table layout emphasizes relationships and data

**Environment directions** (3D aesthetics — Claymation Studio, Lego Brick Builder):

Agent picks 3 contrasting settings appropriate to the topic. Settings should be
visually distinct and reinforce the content theme — for example, for a productivity
topic: a cozy home office, a busy open-plan workspace, and an outdoor café.

### Tier 3: Model freedom (lowest diversity)

**When:** User specified both an aesthetic and a layout type.

Generate 3 candidates with **identical constraints** (same aesthetic, same layout).
Add the nudge: "Explore a distinct visual interpretation." The model finds variation
within fixed parameters — different color emphasis, icon choices, spatial
arrangements, or mood — all within the locked aesthetic and structure.

## Layout Types

Match layout to content:

| Content Type | Layout | When to Use |
|--------------|--------|-------------|
| Step-by-step process | Numbered vertical flow | How-to, workflows, timelines |
| Comparison | Side-by-side columns | vs. content, pros/cons, before/after |
| Statistics | Large numbers with icons | Key metrics, survey results, KPIs |
| Timeline | Horizontal or vertical line | History, roadmaps, project phases |
| Hierarchy | Tree or pyramid | Org charts, taxonomies, priorities |
| Cycle | Circular arrows | Recurring processes, feedback loops |
| Decision tree / process logic | Flowchart / process flow diagram | If/then scenarios, algorithms, logic flows, troubleshooting, approval workflows |
| Conversion / narrowing stages | Funnel (wide to narrow) | Sales pipeline, user journey drop-off, filtering processes |
| Multi-option evaluation | Comparison grid / matrix | Feature comparison, vendor evaluation, option scoring |
| Strategic positioning (2 axes) | Quadrant chart (2x2) | Priority matrices, risk/impact, build vs buy |
| Overlapping concepts | Venn diagram | Skill intersections, market overlap, shared responsibilities |
| Concept relationships / brainstorms | Mind map / radial | Ecosystem maps, topic exploration, feature relationships |
| Narrative sequence / user journey | Storyboard journey (sequential scenes) | Step-by-step stories, user journey maps, customer experience flows |
| Deep dive / multi-section explanation | Long-form explainer panel (horizontal bands) | In-depth topics with per-section illustrations, comprehensive guides |

## Prompt Engineering

When constructing the generation prompt, always specify:

1. **"infographic"** -- explicitly state the output type
2. **Orientation** -- "vertical layout" or "horizontal layout"
3. **Section count** -- "with 4 sections" or "showing 6 steps"
4. **Text content** -- include the actual text/labels/numbers to render
5. **Style modifier** -- "clean and modern", "bold and colorful", "minimal corporate"
6. **Aspect ratio hint** -- tall for vertical (9:16), wide for presentations (16:9)

## Decomposition Heuristics

**If the user specifies a panel count** (e.g., "make a 3-panel infographic",
"split this into 5 panels"), use that count directly. Skip the heuristic table.
The user's explicit count overrides the density-based default, up to the maximum
of 6 panels.

**If the user does not specify**, decide how many panels based on content density:

| Data points / concepts | Panels | Rationale |
|------------------------|--------|-----------|
| 1-3 items | 1 (no decomposition) | Single panel handles this well |
| 4-6 items | 2 | Split into logical groups |
| 7-10 items | 3 | Group by theme or phase |
| 10-15 items | 4 | Group by theme or phase |
| 15-20 items | 5 | Dense topics with distinct sections |
| 20+ items | 6 (max) | More than 6 panels loses coherence |

## Multi-Panel Composition

### Content Map (No Duplication)

Before writing any panel prompts, build a content map that assigns every concept
to exactly one panel:

```
CONTENT MAP:
Panel 1 -- [title]: [concepts/data ONLY in this panel]
Panel 2 -- [title]: [concepts/data ONLY in this panel]
...
Shared across panels: [series title, style brief only]
```

Rules:
- Each concept, statistic, or visual element appears in exactly ONE panel
- No panel recaps or summarizes another panel's content
- The only repeated elements: series title and style brief
- Each panel prompt includes a scoping line: "This panel covers ONLY: [X].
  Do NOT include: [Y, Z]." where Y and Z are other panels' content

### Style Consistency Brief

Before generating any panels, write a style brief that will be copied verbatim
into every panel's generation prompt. The brief MUST specify:

```
STYLE BRIEF (apply to all panels):
- Aesthetic: [curated name (e.g. "Claymation Studio") or freeform description (e.g. "vintage travel poster")]
- Background: [from the aesthetic template -- e.g. "white background, #F5F5F5"]
- Primary colors: [2-3 hex codes or color names]
- Accent color: [1 hex code or color name]
- Typography: [font style direction, e.g. "bold sans-serif headers, light body"]
- Icons: [style, e.g. "flat two-tone icons, matching primary palette"]
- Border/separator: [e.g. "thin #E0E0E0 line at bottom of each panel"]
- Header chrome: [series title treatment]
- Aspect ratio: [same for all panels]
```

**Header chrome is style, not content.** The style brief governs the visual
treatment of headers (font, alignment, decorative elements). The *rendering*
must be identical across all panels -- same font size, weight, position, and
decorative elements (arrows, dividers, etc.).

**Do not include panel numbering or footer text** ("Panel 1 of 4", etc.).
Position already implies order. If a user explicitly requests numbered panels
(e.g., for individual use in a slide deck), add them at that point.

### Reference Image Chaining (Visual Consistency)

Panel 1 is the style anchor. All subsequent panels reference it:

- **Panel 1**: Generate without `reference_image_path` -- establishes the exact
  typography, spacing, icon rendering, and color treatment
- **Post-Panel 1 style reconciliation** (REQUIRED): After generating Panel 1,
  analyze it to capture what Gemini *actually rendered*. Update the style brief
  to match the real output before writing Panels 2-N prompts. Where the original
  brief and the actual render disagree, **the render wins** -- Panels 2-N must
  match what Panel 1 *looks like*, not what you originally *asked for*.
- **Panels 2-N**: Generate with `reference_image_path` set to Panel 1's output
  path AND the **replaced** style brief (from reconciliation). Every Panel 2-N
  prompt MUST open with this directive:

  > "This panel MUST match the exact visual style of the reference image provided."

  This directive + the reference image + the reconciled style brief create three
  reinforcing consistency signals. All three are required -- dropping any one
  weakens cross-panel coherence.

Panel 1 MUST be generated first and alone. Panels 2-N may be generated in
parallel since they all reference Panel 1, not each other.

**Style reference mode (multi-panel):** When the root session provides an
`image_path` for style reference, the reference image chaining uses a
two-anchor pattern:

- **Panel 1**: `reference_image_path = image_path` (user's reference image
  anchors the aesthetic)
- **Panels 2-N**: `reference_image_paths = [panel_1_path, image_path]` — two
  anchors: Panel 1 for cross-panel consistency, and the original `image_path`
  for aesthetic fidelity

This is the first use of `reference_image_paths` (plural) in the project.
The two-anchor approach ensures Panels 2-N stay consistent with both Panel 1
and the original style reference.

### Post-Panel 1 Style Reconciliation

After Panel 1 is generated, analyze it with nano-banana `analyze` using this
prompt:

```
Describe the exact visual style of this infographic panel:
- Background: solid color, gradient, alternating bands, or textured? Describe the progression.
- Section backgrounds: how do they differ from top to bottom?
- Step number circles: color, size, border style
- Icon rendering: flat, outlined, two-tone, detailed? Color treatment?
- Typography: header weight/size relative to body, color
- Separators: lines, arrows, spacing? Style and color
- Header area: layout, font treatment, any decorative elements
- Footer area: layout, font treatment, any decorative elements
Be specific -- these descriptions will be used to prompt-match subsequent panels.
```

**Replace your original style brief entirely with the reconciliation output.
Do not merge -- overwrite.** The analysis describes what Gemini *actually
rendered*, which is what Panels 2-N must match. Carrying forward any original
brief language that contradicts the render causes style drift. The render wins,
completely.

### Panel Naming Convention

**If the user specified an output path, always use it exactly.** User-specified
paths take absolute priority over the defaults below.

For example, if the user says "Save as `./samples/dns_panel_1.png`", save to
exactly that path. If they say "Save as `./samples/mechanical-keyboard.png`"
for a single-panel infographic, save to exactly `./samples/mechanical-keyboard.png`.

**Default convention** (only when no output path is specified):

Derive a short filename from the topic -- lowercase, hyphens for spaces,
no special characters. For example:
- "How DNS Works" -> `dns`
- "The History of the Internet" -> `history-of-internet`
- "Agile vs Waterfall" -> `agile-vs-waterfall`

Save into an `./infographics/` subdirectory of the current working directory.

- Single panel: `./infographics/{topic}.png`
- Multi-panel: `./infographics/{topic}_panel_1.png`, `./infographics/{topic}_panel_2.png`, etc.
- Combined: `./infographics/{topic}_combined.png`

If the user specified a custom stem like `./sales.png` without panel suffixes, adapt:
- `./sales_panel_1.png`
- `./sales_panel_2.png`
- etc.

## Quality Review Criteria

After generating each image, analyze it with nano-banana `analyze` using this
evaluation prompt template:

```
Evaluate this infographic against the following criteria. For each dimension,
give a rating (PASS / NEEDS_WORK) and a brief explanation.

ORIGINAL REQUEST: {original_user_request}
GENERATION PROMPT: {the_prompt_you_sent_to_generate}

Dimensions:

1. CONTENT ACCURACY: Are the requested data points, labels, text, or concepts
   visibly present in the image? Is anything missing or incorrect?

2. LAYOUT QUALITY: Is the structure clear and well-organized? Can a viewer
   follow the information flow? Are sections visually distinct?

3. VISUAL CLARITY: Is the text readable? Is there sufficient contrast between
   foreground and background? Is whitespace used effectively?

4. PROMPT FIDELITY: Does the output match the style, layout type, and color
   direction specified in the generation prompt?

5. AESTHETIC FIDELITY: If a specific aesthetic was requested (e.g., "Claymation
   Studio", "Dark Mode Tech", or a freeform description), does the output
   visually match that aesthetic? Check background treatment, icon style,
   typography feel, lighting, and overall mood against the aesthetic template.

Summary: Overall PASS or NEEDS_REFINEMENT across all 5 dimensions. If
NEEDS_REFINEMENT, list the specific changes that would fix the issues (be
concrete -- these will be used to refine the generation prompt).
```

### Dealbreaker Check (Multi-Candidate Pre-Screen)

Before presenting candidates to the user, run a lightweight binary pre-screen on
each generated image. This is **not** the full 5-dimension quality review — it
only catches broken outputs that should never reach the user (garbled text,
missing content, completely wrong aesthetic).

Use nano-banana `analyze` with this prompt:

```
Quick dealbreaker check — answer YES or NO for each question only.

1. TEXT LEGIBILITY: Is the text in the image legible and readable (not garbled,
   corrupted, or illegibly small)?

2. CORE CONTENT PRESENT: Is the core content present in the image (main topic,
   key data points, or central concept visibly represented)?

3. AESTHETIC MATCH: Does the overall aesthetic of the image roughly match the
   requested style (not a completely different visual genre)?

Return exactly three lines:
TEXT_LEGIBLE: YES|NO
CONTENT_PRESENT: YES|NO
AESTHETIC_MATCH: YES|NO
```

**Failure handling:**

- If any check returns NO, silently regenerate the image once (do not inform the
  user).
- If the regenerated image still fails any dealbreaker check, drop (discard) that
  candidate entirely — do not show it to the user.
- Always present a minimum of 2 candidates. If too many are dropped, regenerate
  additional candidates until at least 2 pass all dealbreaker checks.

### Cross-Panel Visual Comparison (Multi-Panel Only)

For Panels 2-N, add a visual comparison step using nano-banana `compare` with
Panel 1 as image1 and the panel under review as image2. Use this prompt:

```
Compare these two infographic panels that must share identical visual style.
Image 1 is the style anchor (Panel 1). Image 2 is a subsequent panel.

Check each dimension for consistency:
1. BORDER TREATMENT — same frame/border presence and style?
2. BACKGROUND — same color, shade, texture?
3. TYPOGRAPHY — same fonts, weights, sizes for comparable hierarchy levels?
4. COLOR PALETTE — same accent colors? Any new colors introduced?
5. ICON STYLE — same rendering (flat/outlined/detailed)? Same color treatment?
6. DIVIDER LINES — same thickness, color, style?
7. SPACING/MARGINS — consistent outer margins and padding?
8. RENDERING STYLE — both same approach (flat/illustrated/3D)?

For each dimension: MATCH or DRIFT.
If ANY dimension shows DRIFT, the overall verdict is NEEDS_REFINEMENT.
List the specific drifts so the generation prompt can be corrected.
```

This comparison catches visual inconsistencies that text-only review misses --
the critic is comparing actual rendered pixels, not just checking against a
text brief.

### Refinement Rules

- Only refine if the analysis says `NEEDS_REFINEMENT`
- When refining, update the generation prompt to address ONLY the specific issues
  identified -- do not rewrite the entire prompt
- Max 1 refinement pass. If the second generation still has issues, return it
  with the critic notes and let the user decide
- Always report what the critic found, even if no refinement was needed

## Pre-Generation Checklist

Before calling nano-banana generate, verify the prompt addresses:

- [ ] Is the topic clearly stated?
- [ ] Are specific data points or text included in the prompt?
- [ ] Is the layout type appropriate for the content?
- [ ] Is the color direction specified?
- [ ] Is the target medium considered (social, slides, print)?
- [ ] Has an aesthetic been selected or confirmed (curated, freeform, or default)?

**Additional items for multi-panel (Panels 2-N only):**

- [ ] Has Panel 1 been generated and reviewed?
- [ ] Has the style reconciliation `analyze` call been run on Panel 1?
- [ ] Has the original style brief been OVERWRITTEN (not merged) with the reconciliation output?
- [ ] Does this panel's prompt include the opening directive ("This panel MUST match...")?
- [ ] Is `reference_image_path` set to Panel 1's output path?
- [ ] Is the reconciled style brief included verbatim in the prompt?

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
