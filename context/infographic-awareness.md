# Infographic Builder

You have access to infographic design and generation capabilities via the
`infographic-builder:infographic-designer` agent and the `nano-banana` tool.

## When to Delegate

**Delegate to `infographic-builder:infographic-designer` when the user:**
- Asks to create, design, or generate an infographic
- Wants a visual representation of data, concepts, or processes
- Says "make an infographic about...", "visualize this data", "create a visual for..."
- Needs presentation graphics, explainer visuals, or data visualizations

The agent handles prompt construction, style decisions, and image generation
end-to-end. Provide it with the user's topic/data and any style preferences.

## Quick Direct Use

For simple one-off generation without design guidance, call `nano-banana` directly
with `operation: "generate"` and a descriptive prompt.

Requires `GOOGLE_API_KEY` environment variable for image generation.
