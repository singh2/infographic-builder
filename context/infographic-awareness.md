# Infographic Builder

This bundle provides infographic design and generation. The
`infographic-builder` agent handles everything automatically -- layout selection,
style decisions, panel decomposition for complex topics, quality review, and
image generation.

## Delegation

Agent name: `infographic-builder:infographic-builder`

```
delegate(
  agent="infographic-builder:infographic-builder",
  instruction="Create an infographic about [topic]",
  context_depth="none"
)
```

Just pass the user's request as-is. The agent automatically:
- Picks the best layout for the content (timeline, comparison, hierarchy, etc.)
- Splits complex topics into multiple panels when the content is dense enough
- Reviews its own output and refines if it spots issues
- Maintains visual consistency across multi-panel sets

No flags or configuration needed. The user steers with natural language:
- "make it a 3-panel infographic" -- sets an explicit panel count
- "single panel only" -- forces one image even for complex topics
- "skip the review" -- faster generation, skips the quality check
- "use a timeline layout" -- overrides automatic layout selection
- "bold and colorful" / "minimal and corporate" -- sets the style direction

**Delegate when the user says:**
- "create an infographic about..."
- "make an infographic...", "visualize this data", "create a visual for..."
- Any request for presentation graphics, explainer visuals, or data visualizations

## Prerequisites

- `GOOGLE_API_KEY` environment variable (for Gemini image generation via nano-banana)
