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

## Critic Evaluation Criteria

Used by the critic loop when `critic: true`. After generating an image, analyze it
with nano-banana `analyze` using this evaluation prompt template:

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
