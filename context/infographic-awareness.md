# Infographic Builder

**IMMEDIATE DELEGATION -- DO NOT EXPLORE THIS PROJECT.**

When the user asks to create, design, or generate an infographic (or any visual
representation of data/concepts), delegate IMMEDIATELY to the infographic-designer
agent. Do NOT explore the codebase, read files, or investigate the project first.
The agent handles everything end-to-end.

## Exact Delegation Syntax

Use this exact agent name -- do NOT add path components like `agents/`:

```
delegate(
  agent="infographic-builder:infographic-designer",
  instruction="Create an infographic about [topic]. critic: false, multi_panel: false",
  context_depth="none"
)
```

**Common mistake:** Using `infographic-builder:agents/infographic-designer` (WRONG).
The agent name is `infographic-designer`, not `agents/infographic-designer`.

## Trigger Phrases

Delegate immediately when the user says anything like:
- "create an infographic about..."
- "make an infographic..."
- "visualize this data"
- "create a visual for..."
- "infographic showing..."
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

Include flag values in the delegation instruction:

```
delegate(
  agent="infographic-builder:infographic-designer",
  instruction="Create an infographic about [topic]. critic: true, multi_panel: false",
  context_depth="none"
)
```

The user can also request modes explicitly:
- "with critic review" --> pass `critic: true`
- "multi-panel infographic" --> pass `multi_panel: true`

## Prerequisites

- `GOOGLE_API_KEY` environment variable (for Gemini image generation via nano-banana)
