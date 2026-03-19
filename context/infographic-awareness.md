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

**How to pass flags when delegating:**

Before delegating, check the env var. Include the result in your instruction:

```
Check: echo $INFOGRAPHIC_CRITIC
If "true" → include "critic: true" in the delegation instruction
If unset/false → include "critic: false" or omit
```

The user can also explicitly request critic mode: "create an infographic about X
with critic review" -- in that case, pass `critic: true` regardless of the env var.

## Quick Direct Use

For simple one-off generation without design guidance, call `nano-banana` directly
with `operation: "generate"` and a descriptive prompt.

## Prerequisites

- `GOOGLE_API_KEY` environment variable (for Gemini image generation via nano-banana)
