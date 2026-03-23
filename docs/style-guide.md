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
| Decision tree / branching logic | Flowchart with decision nodes | If/then scenarios, troubleshooting guides, approval workflows |
| Conversion / narrowing stages | Funnel (wide to narrow) | Sales pipeline, user journey drop-off, filtering processes |
| Multi-option evaluation | Comparison grid / matrix | Feature comparison, vendor evaluation, option scoring |
| Strategic positioning (2 axes) | Quadrant chart (2x2) | Priority matrices, risk/impact, build vs buy |
| Overlapping concepts | Venn diagram | Skill intersections, market overlap, shared responsibilities |
| Concept relationships / brainstorms | Mind map / radial | Ecosystem maps, topic exploration, feature relationships |

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
- Background: [exact description, e.g. "white background, #F5F5F5"]
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

Output files follow this pattern:
- `./infographic_panel_1.png`
- `./infographic_panel_2.png`
- etc.

If the user specified a custom output path like `./sales.png`, adapt:
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

Summary: Overall PASS or NEEDS_REFINEMENT. If NEEDS_REFINEMENT, list the
specific changes that would fix the issues (be concrete -- these will be
used to refine the generation prompt).
```

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
