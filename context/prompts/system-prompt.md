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
