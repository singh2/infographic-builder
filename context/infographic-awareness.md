# Infographic Builder

This bundle provides infographic design and generation. The
`infographic-designer` agent handles prompt construction, style decisions,
and image generation end-to-end -- delegate to it directly, no exploration needed.

## Delegation

Agent name: `infographic-builder:infographic-designer`

```
delegate(
  agent="infographic-builder:infographic-designer",
  instruction="Create an infographic about [topic]. critic: false, multi_panel: false",
  context_depth="none"
)
```

Note: the agent name is `infographic-designer`, not `agents/infographic-designer`.

**Delegate when the user says:**
- "create an infographic about..."
- "make an infographic...", "visualize this data", "create a visual for..."
- Any request for presentation graphics, explainer visuals, or data visualizations

## Feature Flags

Check env vars before delegating and pass them in the instruction:

```bash
echo $INFOGRAPHIC_CRITIC $INFOGRAPHIC_MULTI_PANEL
```

| Flag | Env Var | Default | Effect |
|------|---------|---------|--------|
| Critic loop | `INFOGRAPHIC_CRITIC` | `false` | Self-evaluates and refines the generated image |
| Multi-panel | `INFOGRAPHIC_MULTI_PANEL` | `false` | Decomposes into 2-4 focused panels |

The user can also request these inline:
- "with critic review" --> `critic: true`
- "multi-panel infographic" --> `multi_panel: true`

## Prerequisites

- `GOOGLE_API_KEY` environment variable (for Gemini image generation via nano-banana)
