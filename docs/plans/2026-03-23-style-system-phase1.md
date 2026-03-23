# Style System (Phase 1) Implementation Plan

> **Execution:** Use the subagent-driven-development workflow to implement this plan.

**Goal:** Add a composable aesthetic system to infographic-builder so users choose from 6 curated visual styles (or describe their own) before generation, producing dramatically different visual results from the same content.

**Architecture:** A new Aesthetics section in the style guide defines 6 self-contained prompt templates that override the existing "style modifier" slot (Prompt Engineering item 5). The agent gains a new step 3 (aesthetic selection UX) that presents options and waits for user choice before proceeding. All changes are declarative Markdown edits to 4 existing files — no code, no tests, no build step.

**Tech Stack:** Markdown, YAML frontmatter (existing), git

**Design document:** `docs/plans/2026-03-20-style-system-design.md`

**Scope:** Phase 1 only — core style system. Phase 2 (browsable catalog website, sample generation) is a separate plan.

---

## Setup

```bash
cd /Users/gurkaransingh/Desktop/Development/infographic-builder
git checkout master
git pull origin master
git checkout -b feat/style-system-phase1
```

Verify the four files you'll modify all exist:

```bash
ls docs/style-guide.md agents/infographic-builder.md context/infographic-awareness.md README.md
```

All four must exist. You will **not** create any new files in this plan.

---

## Tasks 1–5: Style Guide (`docs/style-guide.md`)

All five tasks modify the same file. Work from the **top of the file downward**. Line numbers reference the file's original state; after each edit they shift — always locate content by the **Find** text, never by line number alone.

---

### Task 1: Add Aesthetics Section with 6 Curated Prompt Templates

This is the creative core of the style system. Each aesthetic is a self-contained prompt template whose properties get injected into the generation prompt's "style modifier" slot. The six span professional → playful, and freeform input covers everything else.

**Files:**
- Modify: `docs/style-guide.md` — insert between `## Default Style` (ends line 17) and `## Layout Types` (starts line 19)

**Step 1: Insert the Aesthetics section**

**Find** this exact text in `docs/style-guide.md`:

```
- **Whitespace**: Generous -- let the content breathe

## Layout Types
```

**Replace** with (note: the first and last lines are the existing anchors — everything between them is new):

```
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
- **Icons:** Monochrome flat icons, single accent color, no outlines
- **Color palette:** 1 primary accent + neutral grays — one blue or one teal against white
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

- **Background:** Cardboard or craft paper set, visible texture and slight wrinkles
- **Typography:** Rounded playful sans-serif; letters may appear sculpted from clay or extruded
- **Icons:** 3D sculpted plasticine/clay figures, fingerprint texture visible, rounded organic shapes
- **Color palette:** Warm saturated primaries — clay red, cobalt blue, sunshine yellow, grass green — like real plasticine
- **Lighting:** Soft diffused studio lighting with realistic cast shadows, shallow depth of field
- **Texture:** Visible clay fingerprints, slightly lumpy sculpted surfaces
- **Mood:** Whimsical, tactile, handmade, warm

### 6. Lego Brick Builder

> Playful, structural, plastic bricks

- **Background:** Plastic Lego baseplate — gray or green studded surface
- **Typography:** Blocky geometric letterforms; may appear embossed on Lego tiles or printed on brick faces
- **Icons:** Built from Lego bricks — recognizable objects constructed from studs and plates
- **Color palette:** Classic Lego primaries — red (#D01012), blue (#0057A6), yellow (#FFD700), green (#00852B), black, white
- **Lighting:** Macro photography lighting with shallow depth of field, plastic specular highlights
- **Texture:** Smooth injection-molded plastic, visible stud geometry
- **Mood:** Playful, structural, childhood delight, tilt-shift perspective

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

## Layout Types
```

**Step 2: Verify the edit**

Read `docs/style-guide.md` from the top and confirm:
- The `> **Note:**` callout appears directly after the Default Style bullet list
- `## Aesthetics` is a new H2 section before `## Layout Types`
- All 6 aesthetics have `###` subheadings, a blockquote tagline, and 7 bullet-point properties
- The `### Freeform Aesthetics` subsection is last, with 3 numbered rules
- `## Layout Types` still appears after the Aesthetics section

**Step 3: Commit**

```bash
git add docs/style-guide.md
git commit -m "feat: add Aesthetics section with 6 curated prompt templates to style guide"
```

---

### Task 2: Add New Layout Rows to Style Guide

Add 2 new layout types (Storyboard Journey, Long-Form Explainer Panel) and enrich the existing Flowchart entry to match the "Process Flow Diagram" spec from the design doc. Mind Map already exists on line 36 — do **not** duplicate it.

**Files:**
- Modify: `docs/style-guide.md` — Layout Types table (originally lines 23–36, now shifted down by Task 1's insertion)

**Step 1: Enrich the Flowchart row**

**Find:**

```
| Decision tree / branching logic | Flowchart with decision nodes | If/then scenarios, troubleshooting guides, approval workflows |
```

**Replace with:**

```
| Decision tree / process logic | Flowchart / process flow diagram | If/then scenarios, algorithms, logic flows, troubleshooting, approval workflows |
```

**Step 2: Add the 2 new layout rows**

**Find:**

```
| Concept relationships / brainstorms | Mind map / radial | Ecosystem maps, topic exploration, feature relationships |
```

**Replace with:**

```
| Concept relationships / brainstorms | Mind map / radial | Ecosystem maps, topic exploration, feature relationships |
| Narrative sequence / user journey | Storyboard journey (sequential scenes) | Step-by-step stories, user journey maps, customer experience flows |
| Deep dive / multi-section explanation | Long-form explainer panel (horizontal bands) | In-depth topics with per-section illustrations, comprehensive guides |
```

**Step 3: Verify the edit**

Read the Layout Types table and confirm:
- The Flowchart row now says "Flowchart / process flow diagram"
- Two new rows appear after Mind map: Storyboard journey and Long-form explainer panel
- The table now has 14 rows (12 original + 2 new), counting the header and separator
- Mind Map is NOT duplicated

**Step 4: Commit**

```bash
git add docs/style-guide.md
git commit -m "feat: add Storyboard Journey and Long-Form Explainer layouts, enrich Flowchart entry"
```

---

### Task 3: Add Aesthetic Fidelity as 5th Quality Review Dimension

The quality review evaluation prompt currently has 4 dimensions. Add a 5th — AESTHETIC FIDELITY — that checks whether the output visually matches the requested aesthetic.

**Files:**
- Modify: `docs/style-guide.md` — Quality Review Criteria section (originally lines 180–203)

**Step 1: Add the 5th dimension**

**Find:**

```
4. PROMPT FIDELITY: Does the output match the style, layout type, and color
   direction specified in the generation prompt?

Summary: Overall PASS or NEEDS_REFINEMENT. If NEEDS_REFINEMENT, list the
specific changes that would fix the issues (be concrete -- these will be
used to refine the generation prompt).
```

**Replace with:**

```
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

**Step 2: Verify the edit**

Read the Quality Review Criteria section and confirm:
- Dimension 5 (AESTHETIC FIDELITY) appears after dimension 4
- The Summary line says "all 5 dimensions" (not "all 4")
- The rest of the evaluation template is unchanged

**Step 3: Commit**

```bash
git add docs/style-guide.md
git commit -m "feat: add AESTHETIC FIDELITY as 5th quality review dimension"
```

---

### Task 4: Add Aesthetic Checkbox to Pre-Generation Checklist

The Pre-Generation Checklist currently has 5 items. Add a 6th: confirm that an aesthetic has been selected.

**Files:**
- Modify: `docs/style-guide.md` — Pre-Generation Checklist section (originally lines 215–223)

**Step 1: Add the 6th checkbox**

**Find:**

```
- [ ] Is the target medium considered (social, slides, print)?
```

**Replace with:**

```
- [ ] Is the target medium considered (social, slides, print)?
- [ ] Has an aesthetic been selected or confirmed (curated, freeform, or default)?
```

**Step 2: Verify the edit**

Read the Pre-Generation Checklist and confirm 6 checkboxes total.

**Step 3: Commit**

```bash
git add docs/style-guide.md
git commit -m "feat: add aesthetic selection checkbox to pre-generation checklist"
```

---

### Task 5: Add Aesthetic Field to Style Consistency Brief

The Style Consistency Brief template drives multi-panel visual consistency. Add an "Aesthetic" field as the first entry so all panels share the same aesthetic.

**Files:**
- Modify: `docs/style-guide.md` — Style Consistency Brief template (originally lines 94–104)

**Step 1: Add the Aesthetic field**

**Find:**

```
STYLE BRIEF (apply to all panels):
- Background: [exact description, e.g. "white background, #F5F5F5"]
```

**Replace with:**

```
STYLE BRIEF (apply to all panels):
- Aesthetic: [curated name (e.g. "Claymation Studio") or freeform description (e.g. "vintage travel poster")]
- Background: [from the aesthetic template -- e.g. "white background, #F5F5F5"]
```

**Step 2: Verify the edit**

Read the Style Consistency Brief template and confirm:
- "Aesthetic" is the first field (before Background)
- The rest of the brief fields are unchanged
- The bracket hint shows both curated and freeform examples

**Step 3: Commit**

```bash
git add docs/style-guide.md
git commit -m "feat: add Aesthetic field to Style Consistency Brief template"
```

---

## Tasks 6–8: Agent Definition (`agents/infographic-builder.md`)

Three tasks modify the agent workflow. Task 6 inserts a new step and renumbers all subsequent steps. Tasks 7 and 8 update content within steps.

**Important context for the agent file:** The current workflow has 7 numbered steps (1–7). After Task 6, it will have 8 steps (1–8). Here is the renumbering map:

| Current | After Task 6 | Step name |
|---------|-------------|-----------|
| 1 | 1 | Parse the request |
| 2 | 2 | Analyze content density |
| _(new)_ | **3** | **Aesthetic selection** |
| 3 | 4 | Plan the design |
| 4 | 5 | Generate the image(s) |
| 5 | 6 | Quality review |
| 6 | 7 | Assemble multi-panel output |
| 7 | 8 | Return results |

---

### Task 6: Add Step 3 — Aesthetic Selection UX

Insert the new aesthetic selection step between current steps 2 and 3, then renumber all subsequent steps.

**Files:**
- Modify: `agents/infographic-builder.md`

**Step 1: Insert the new step 3**

**Find:**

```
   - "skip the review" or "no critic" -- skip the quality review in step 5

3. **Plan the design**: layout type (vertical flow, comparison, timeline, process,
```

**Replace with:**

````
   - "skip the review" or "no critic" -- skip the quality review in step 6

3. **Aesthetic selection**: Before designing, guide the user to a visual style.

   **a. Recommend a layout** based on content analysis from step 2 — reference
   the Layout Types table in the Style Guide.

   **b. Check for inline style specification.** If the user already described
   an aesthetic in their original request (e.g., "make a claymation infographic
   about DNS", "dark mode tech style"), skip to step 4 using that aesthetic.
   This is the **two-turn shortcut** — no proposal needed.

   **c. If no style was specified**, present the aesthetic options and halt:

   ```
   For "[topic]," I'd recommend [Layout Name].

   Choose a style, or describe your own:

     1. Clean Minimalist       4. Hand-Drawn Sketchnote
     2. Dark Mode Tech         5. Claymation Studio
     3. Bold Editorial         6. Lego Brick Builder

     Or describe any style — "professional report",
     "watercolor", "comic book", "retro pixel art",
     "vintage travel poster" — get creative.
   ```

   **Then stop and wait for the user's selection.** Do not proceed to design
   or generation until the user has chosen.

   **d. Load the aesthetic template.** If the user picks a numbered option,
   load the corresponding template from the Aesthetics section of the Style
   Guide. If they describe a freeform style, translate their description into
   reasonable defaults for background, typography, icon style, color palette,
   lighting, texture, and mood.

4. **Plan the design**: layout type (vertical flow, comparison, timeline, process,
````

**Step 2: Renumber old step 4 → 5**

**Find:**

```
4. **Generate the image(s)**:
```

**Replace with:**

```
5. **Generate the image(s)**:
```

**Step 3: Renumber old step 5 → 6**

**Find:**

```
5. **Quality review**:
```

**Replace with:**

```
6. **Quality review**:
```

**Step 4: Renumber old step 6 → 7**

**Find:**

```
6. **Assemble multi-panel output**
```

**Replace with:**

```
7. **Assemble multi-panel output**
```

**Step 5: Renumber old step 7 → 8**

**Find:**

```
7. **Return results**:
```

**Replace with:**

```
8. **Return results**:
```

**Step 6: Verify the edit**

Read `agents/infographic-builder.md` and confirm:
- Steps are now numbered 1 through 8 with no gaps or duplicates
- Step 3 is the new "Aesthetic selection" step with sub-parts a–d
- Step 3c contains the aesthetic menu code block (6 numbered options + freeform)
- The cross-reference on step 2 says "step 6" (not "step 5")
- All other step content is unchanged (just renumbered)

**Step 7: Commit**

```bash
git add agents/infographic-builder.md
git commit -m "feat: add Step 3 aesthetic selection UX to agent workflow"
```

---

### Task 7: Update Step 4 (Plan the Design) and Step 6 (Quality Review)

Update step 4 to reference aesthetic templates, and update step 6 to reference 5 quality dimensions (matching the style guide change from Task 3).

**Files:**
- Modify: `agents/infographic-builder.md`

**Step 1: Update step 4 to use aesthetic templates**

**Find:**

```
4. **Plan the design**: layout type (vertical flow, comparison, timeline, process,
   stats), color palette, typography direction, visual metaphors. Consult the
   Layout Types table in the Style Guide.
```

**Replace with:**

```
4. **Plan the design**: Apply the selected aesthetic template from the Aesthetics
   section of the Style Guide to set color palette, typography, and icon style.
   The aesthetic drives these decisions — not ad-hoc choices. Choose layout type
   from the Layout Types table. Plan visual metaphors appropriate to the content.
```

**Step 2: Update step 6 from four dimensions to five**

**Find:**

```
   Score against four dimensions: content accuracy, layout quality, visual
   clarity, and prompt fidelity.
```

**Replace with:**

```
   Score against five dimensions: content accuracy, layout quality, visual
   clarity, prompt fidelity, and aesthetic fidelity.
```

**Step 3: Verify the edit**

Read steps 4 and 6 and confirm:
- Step 4 mentions "selected aesthetic template" and "Aesthetics section of the Style Guide"
- Step 6 says "five dimensions" and lists "aesthetic fidelity" at the end

**Step 4: Commit**

```bash
git add agents/infographic-builder.md
git commit -m "feat: update design step to use aesthetic templates, add 5th quality dimension"
```

---

### Task 8: Update Output Contract — Suggest Different Aesthetic

Add "try a different aesthetic" to the suggested next steps in the Output Contract.

**Files:**
- Modify: `agents/infographic-builder.md`

**Step 1: Update the suggestions line**

**Find:**

```
- Suggested next steps (different layout, style variation, panel count adjustment)
```

**Replace with:**

```
- Suggested next steps (try a different aesthetic, different layout, panel count adjustment)
```

**Step 2: Also update the Return results step**

**Find:**

```
8. **Return results**: image path(s) + design rationale + quality review summary +
   suggestions for what the user could try next (different layout, more/fewer panels,
   style variation)
```

**Replace with:**

```
8. **Return results**: image path(s) + design rationale + quality review summary +
   suggestions for what the user could try next (different aesthetic, different layout,
   more/fewer panels)
```

**Step 3: Verify the edit**

Read the Output Contract section and the step 8 description. Both should mention "different aesthetic" as the first suggestion.

**Step 4: Commit**

```bash
git add agents/infographic-builder.md
git commit -m "feat: add 'try a different aesthetic' to output contract suggestions"
```

---

## Task 9: Update Awareness Context (`context/infographic-awareness.md`)

The awareness context is a thin file loaded every session that tells the root agent when and how to delegate to infographic-builder. Update it to mention aesthetic selection.

**Files:**
- Modify: `context/infographic-awareness.md`

**Step 1: Update the description to mention aesthetic selection**

**Find:**

```
This bundle provides infographic design and generation. The
`infographic-builder` agent handles everything automatically -- layout selection,
style decisions, panel decomposition for complex topics, quality review, and
image generation.
```

**Replace with:**

```
This bundle provides infographic design and generation. The
`infographic-builder` agent handles everything automatically -- layout selection,
interactive aesthetic selection (6 curated styles + freeform), panel decomposition
for complex topics, quality review, and image generation.
```

**Step 2: Add aesthetic proposal to the auto-behaviors list**

**Find:**

```
Just pass the user's request as-is. The agent automatically:
- Picks the best layout for the content (timeline, comparison, hierarchy, etc.)
- Splits complex topics into multiple panels when the content is dense enough
- Reviews its own output and refines if it spots issues
- Maintains visual consistency across multi-panel sets
```

**Replace with:**

```
Just pass the user's request as-is. The agent automatically:
- Picks the best layout for the content (timeline, comparison, hierarchy, etc.)
- Proposes a visual aesthetic before generating (6 curated styles + freeform)
- Splits complex topics into multiple panels when the content is dense enough
- Reviews its own output and refines if it spots issues
- Maintains visual consistency across multi-panel sets
```

**Step 3: Add aesthetic steering examples**

**Find:**

```
- "bold and colorful" / "minimal and corporate" -- sets the style direction

**Delegate when the user says:**
```

**Replace with:**

```
- "bold and colorful" / "minimal and corporate" -- sets the style direction
- "make it claymation" / "dark mode tech style" -- picks a curated aesthetic
- "3" (as a reply to aesthetic options) -- selects an aesthetic by number

**Delegate when the user says:**
```

**Step 4: Verify the edit**

Read `context/infographic-awareness.md` and confirm:
- Description mentions "interactive aesthetic selection"
- Auto-behaviors list includes the aesthetic proposal bullet (2nd item)
- Two new steering examples appear after "bold and colorful" line

**Step 5: Commit**

```bash
git add context/infographic-awareness.md
git commit -m "feat: update awareness context with aesthetic selection capabilities"
```

---

## Task 10: Update README

Multiple updates to the README: fix stale path references, add aesthetic examples, update the workflow description, and add smoke tests for the aesthetic flow.

**Files:**
- Modify: `README.md`

**Step 1: Add aesthetic-steered examples to "What you can create" table**

**Find:**

```
| "Create a timeline of the space race" | Horizontal/vertical timeline layout |
```

**Replace with:**

```
| "Create a timeline of the space race" | Horizontal/vertical timeline layout |
| "Create a claymation infographic about how DNS works" | Claymation-styled infographic (detects style inline, skips selection) |
| "Make a dark mode tech infographic about CI/CD pipelines" | Dark Mode Tech aesthetic with auto-selected layout |
| "Create an infographic about quarterly metrics" → pick "Bold Editorial" | Bold editorial magazine-style infographic |
```

**Step 2: Add aesthetic steering examples to the "You steer" list**

**Find:**

```
- "skip the review" -- faster generation, skip the quality check
```

**Replace with:**

```
- "make it claymation" / "dark mode tech" -- choose a curated aesthetic
- "2" (when prompted) -- pick an aesthetic by number
- "skip the review" -- faster generation, skip the quality check
```

**Step 3: Add "aesthetic selection" to the auto-behavior list**

**Find:**

```
The agent automatically:
- **Picks the best layout** for your content -- process flow, comparison, timeline, hierarchy, cycle, or statistics
- **Splits complex topics** into multiple panels when there's too much for one image
```

**Replace with:**

```
The agent automatically:
- **Picks the best layout** for your content -- process flow, comparison, timeline, hierarchy, cycle, or statistics
- **Presents aesthetic options** -- 6 curated styles from Clean Minimalist to Lego Brick Builder, plus freeform
- **Splits complex topics** into multiple panels when there's too much for one image
```

**Step 4: Add aesthetic fidelity row to Pitfalls table**

**Find:**

```
| Image text is garbled or unreadable | Limitation of current image generation models | Simplify: fewer data points, shorter labels, larger text emphasis in your prompt |
```

**Replace with:**

```
| Image text is garbled or unreadable | Limitation of current image generation models | Simplify: fewer data points, shorter labels, larger text emphasis in your prompt |
| Output doesn't match requested aesthetic | Aesthetic fidelity varies by complexity | The critic loop checks aesthetic fidelity -- try regenerating or simplify the content |
```

**Step 5: Update "How it works" flow with aesthetic selection step**

**Find:**

```
1. You describe what you want
2. Agent analyzes content density --> picks single or multi-panel
3. Agent designs layout, palette, typography, and visual hierarchy
4. Agent generates image(s) via Gemini (nano-banana tool)
5. Agent reviews output and refines if needed
6. You get the .png file(s) + design rationale + suggestions
```

**Replace with:**

```
1. You describe what you want
2. Agent analyzes content density --> picks single or multi-panel
3. Agent recommends a layout and presents 6 aesthetic options (or detects your inline style)
4. Agent designs layout, palette, typography using your chosen aesthetic template
5. Agent generates image(s) via Gemini (nano-banana tool)
6. Agent reviews output (including aesthetic fidelity) and refines if needed
7. You get the .png file(s) + design rationale + suggestions
```

**Step 6: Fix stale path in Mermaid diagram**

**Find:**

```
        SP["context/prompts/system-prompt.md<br/><i>style guide</i>"]
```

**Replace with:**

```
        SP["docs/style-guide.md<br/><i>style guide</i>"]
```

**Step 7: Fix stale path in structure tree**

**Find:**

```
+-- context/
    |-- infographic-awareness.md     # thin pointer loaded every session
    +-- prompts/
        +-- system-prompt.md         # infographic generation style guide
```

**Replace with:**

```
|-- context/
|   +-- infographic-awareness.md     # thin pointer loaded every session
+-- docs/
    +-- style-guide.md              # design knowledge: aesthetics, layouts, quality criteria
```

**Step 8: Add aesthetic smoke tests**

**Find:**

```
# Test 4: User override -- force single panel
amplifier run
# Say: "Create a single-panel infographic about climate change impacts"
# Expected: one image even though topic is dense
```

**Replace with:**

```
# Test 4: User override -- force single panel
amplifier run
# Say: "Create a single-panel infographic about climate change impacts"
# Expected: one image even though topic is dense

# Test 5: Aesthetic selection flow
amplifier run
# Say: "Create an infographic about how DNS works"
# Expected: Agent recommends layout, presents 6 aesthetic options + freeform
# Pick: "2" or "Dark Mode Tech"
# Expected: Infographic generated in Dark Mode Tech style

# Test 6: Inline aesthetic shortcut (two-turn)
amplifier run
# Say: "Make a claymation infographic about the water cycle"
# Expected: Skips aesthetic proposal, generates directly in Claymation style
```

**Step 9: Add aesthetic rows to "What to check" table**

**Find:**

```
| Style consistency | Multi-panel sets share the same color palette and typography |
```

**Replace with:**

```
| Style consistency | Multi-panel sets share the same color palette and typography |
| Aesthetic selection | Agent presents 6 options + freeform and waits for user choice |
| Inline style shortcut | Specifying aesthetic in the request skips the proposal turn |
| Aesthetic fidelity | Quality review includes aesthetic match as a review dimension |
```

**Step 10: Verify the edit**

Read `README.md` and confirm:
- "What you can create" table has 3 new aesthetic-steered rows
- "You steer" list includes aesthetic picking examples
- Auto-behavior list includes "Presents aesthetic options"
- Pitfalls table has the aesthetic fidelity row
- "How it works" has 7 steps (not 6), including aesthetic selection
- Mermaid diagram references `docs/style-guide.md` (not `context/prompts/system-prompt.md`)
- Structure tree shows `docs/style-guide.md` (not `context/prompts/system-prompt.md`)
- Smoke tests include Test 5 (aesthetic flow) and Test 6 (inline shortcut)
- "What to check" table has 3 new aesthetic rows

**Step 11: Commit**

```bash
git add README.md
git commit -m "docs: update README with aesthetic system, fix stale paths, add smoke tests"
```

---

## Final Verification

After all 10 tasks, run a full check:

```bash
cd /Users/gurkaransingh/Desktop/Development/infographic-builder

# Check git log shows 10 commits on this branch
git log --oneline master..HEAD

# Verify all 4 files are modified
git diff --stat master..HEAD

# Scan for any remaining stale references
grep -r "system-prompt.md" . --include="*.md" | grep -v node_modules | grep -v ".git"
# Expected: no results (all stale references fixed)

# Verify the aesthetic section exists
grep -c "### [0-9]. " docs/style-guide.md
# Expected: 6 (one for each curated aesthetic)

# Verify step numbering in agent
grep -c "^[0-9]\. \*\*" agents/infographic-builder.md
# Expected: 8 (steps 1-8)
```

**Expected commit history (oldest first):**

1. `feat: add Aesthetics section with 6 curated prompt templates to style guide`
2. `feat: add Storyboard Journey and Long-Form Explainer layouts, enrich Flowchart entry`
3. `feat: add AESTHETIC FIDELITY as 5th quality review dimension`
4. `feat: add aesthetic selection checkbox to pre-generation checklist`
5. `feat: add Aesthetic field to Style Consistency Brief template`
6. `feat: add Step 3 aesthetic selection UX to agent workflow`
7. `feat: update design step to use aesthetic templates, add 5th quality dimension`
8. `feat: add 'try a different aesthetic' to output contract suggestions`
9. `feat: update awareness context with aesthetic selection capabilities`
10. `docs: update README with aesthetic system, fix stale paths, add smoke tests`

When all checks pass, push and open a PR:

```bash
git push -u origin feat/style-system-phase1
```
