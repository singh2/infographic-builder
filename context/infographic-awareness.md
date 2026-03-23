# Infographic Builder

This bundle provides infographic design and generation. The
`infographic-builder` agent handles everything automatically -- layout selection,
interactive aesthetic selection (6 curated styles + freeform), panel decomposition
for complex topics, quality review, and image generation.

## Delegation

Agent name: `infographic-builder:infographic-builder`

Delegate with a direct instruction. Pass the user's request as-is — no need to
relay conversation history or parent context. The agent is self-contained.

> Example: `delegate(agent="infographic-builder:infographic-builder", instruction="Create an infographic about [topic]")`

The agent automatically:
- Picks the best layout for the content (timeline, comparison, hierarchy, etc.)
- Proposes a visual aesthetic before generating (6 curated styles + freeform)
- Splits complex topics into multiple panels when the content is dense enough
- Reviews its own output and refines if it spots issues
- Maintains visual consistency across multi-panel sets

No flags or configuration needed. The user steers with natural language:
- "make it a 3-panel infographic" -- sets an explicit panel count
- "single panel only" -- forces one image even for complex topics
- "skip the review" -- faster generation, skips the quality check
- "use a timeline layout" -- overrides automatic layout selection
- "bold and colorful" / "minimal and corporate" -- sets the style direction
- "make it claymation" / "dark mode tech style" -- picks a curated aesthetic
- "3" (as a reply to aesthetic options) -- selects an aesthetic by number

**Delegate when the user says:**
- "create an infographic about..."
- "make an infographic...", "visualize this data", "create a visual for..."
- Any request for presentation graphics, explainer visuals, or data visualizations

## Prerequisites

- `GOOGLE_API_KEY` environment variable (for Gemini image generation via nano-banana)
