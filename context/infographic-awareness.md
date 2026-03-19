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

## Feature Flags

Optional capabilities controlled by environment variables. Pass the flag value
in the delegation instruction so the agent knows which mode to use.

| Flag | Env Var | Default | Effect |
|------|---------|---------|--------|
| Critic loop | `INFOGRAPHIC_CRITIC` | `false` | After generation, analyzes the image and refines if issues found. Adds 1 analyze + up to 1 extra generate call. |
| Multi-panel | `INFOGRAPHIC_MULTI_PANEL` | `false` | Decomposes complex infographics into 2-4 focused panels with consistent style. Each panel is a separate image. |

**How to pass flags when delegating:**

Before delegating, check the env var. Include the result in your instruction:

```
Check: echo $INFOGRAPHIC_CRITIC $INFOGRAPHIC_MULTI_PANEL
Pass results in delegation instruction:
  INFOGRAPHIC_CRITIC=true   → "critic: true"
  INFOGRAPHIC_MULTI_PANEL=true → "multi_panel: true"
  unset/false → omit or "false"
```

The user can also explicitly request these modes:
- "create an infographic about X with critic review" → pass `critic: true`
- "create a multi-panel infographic about X" → pass `multi_panel: true`
- Both can be combined: "multi-panel infographic with critic review"

## Quick Direct Use

For simple one-off generation without design guidance, call `nano-banana` directly
with `operation: "generate"` and a descriptive prompt.

## Prerequisites

- `GOOGLE_API_KEY` environment variable (for Gemini image generation via nano-banana)
