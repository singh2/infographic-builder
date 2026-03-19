# Infographic Generation Style Guide

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

## Prompt Engineering for Infographics

When constructing the generation prompt, always specify:

1. **"infographic"** -- explicitly state the output type
2. **Orientation** -- "vertical layout" or "horizontal layout"
3. **Section count** -- "with 4 sections" or "showing 6 steps"
4. **Text content** -- include the actual text/labels/numbers to render
5. **Style modifier** -- "clean and modern", "bold and colorful", "minimal corporate"
6. **Aspect ratio hint** -- tall for vertical (9:16), wide for presentations (16:9)

## Quality Checklist

Before returning a result, verify the prompt addresses:

- [ ] Is the topic clearly stated?
- [ ] Are specific data points or text included in the prompt?
- [ ] Is the layout type appropriate for the content?
- [ ] Is the color direction specified?
- [ ] Is the target medium considered (social, slides, print)?

## Multi-Panel Composition

When generating multiple panels for a single infographic:

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
- Header chrome: [series title treatment, panel indicator position and style]
- Footer chrome: [visual treatment -- font, alignment, decorative elements;
  footer CONTENT may vary per panel but visual style must be identical]
- Aspect ratio: [same for all panels]
```

### Decomposition Heuristics

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

### Content Map (No Duplication)

Before writing any panel prompts, build a content map that assigns every concept
to exactly one panel:

```
CONTENT MAP:
Panel 1 -- [title]: [concepts/data ONLY in this panel]
Panel 2 -- [title]: [concepts/data ONLY in this panel]
...
Shared across panels: [series title, panel numbering, style brief only]
```

Rules:
- Each concept, statistic, or visual element appears in exactly ONE panel
- No panel recaps or summarizes another panel's content
- The only repeated elements: series title, panel number, and style brief
- Each panel prompt includes a scoping line: "This panel covers ONLY: [X].
  Do NOT include: [Y, Z]." where Y and Z are other panels' content

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
  path AND the **updated** style brief. The combination of visual reference +
  accurate text brief gives Gemini the best chance of style consistency.

Panel 1 MUST be generated first and alone. Panels 2-N may be generated in
parallel since they all reference Panel 1, not each other.

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

### Refinement rules

- Only refine if the analysis says `NEEDS_REFINEMENT`
- When refining, update the generation prompt to address ONLY the specific issues
  identified -- do not rewrite the entire prompt
- Max 1 refinement pass. If the second generation still has issues, return it
  with the critic notes and let the user decide
- Always report what the critic found, even if no refinement was needed
