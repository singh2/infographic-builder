# infographic-designer

Amplifier bundle for AI-powered infographic design and generation.

## What it does

Say "create an infographic about X" in any Amplifier session. The `infographic-designer` agent constructs a detailed visual prompt and calls nano-banana's `generate` operation to produce an image.

## Quick start

```bash
amplifier bundle add git+https://github.com/singh2/infographic-designer@main --app
```

Or compose into your own bundle:

```yaml
includes:
  - bundle: foundation
  - bundle: git+https://github.com/singh2/infographic-designer@main
```

## How it works

```
1. User provides data or topic
2. Root session delegates to infographic-designer agent
3. Agent constructs a detailed visual prompt (layout, palette, hierarchy)
4. Agent calls nano-banana tool with operation: "generate"
5. Image saved to disk, path returned to user
```

## Prerequisites

- `GOOGLE_API_KEY` environment variable (for Gemini image generation via nano-banana)

## Structure

```
infographic-designer/
|-- bundle.md                        # thin root: foundation + nano-banana + behavior
|-- behaviors/
|   +-- infographic.yaml             # wires tool + agent + context
|-- agents/
|   +-- infographic-designer.md      # the expert agent (context sink)
+-- context/
    |-- infographic-awareness.md     # thin pointer loaded every session
    +-- prompts/
        +-- system-prompt.md         # infographic generation style guide
```

## Feature flags

Optional capabilities you can toggle per-session via environment variables:

| Flag | Env Var | Default | What it does |
|------|---------|---------|--------------|
| Critic loop | `INFOGRAPHIC_CRITIC` | off | Self-evaluates the generated image and refines if issues found |
| Multi-panel | `INFOGRAPHIC_MULTI_PANEL` | off | Decomposes complex infographics into 2-4 focused panels |

```bash
# Basic (single pass, no critique)
amplifier run

# With critic loop (measure latency delta)
INFOGRAPHIC_CRITIC=true amplifier run

# Multi-panel
INFOGRAPHIC_MULTI_PANEL=true amplifier run

# Both
INFOGRAPHIC_CRITIC=true INFOGRAPHIC_MULTI_PANEL=true amplifier run
```

Users can also request these inline: "create a multi-panel infographic about X with critic review".

## Testing

### 1. Local development setup

Point your Amplifier settings at the local checkout instead of the git URL:

```yaml
# .amplifier/settings.yaml  (in this repo, already gitignored)
default_bundle: file:///Users/YOU/path/to/infographic-builder
```

Or use the source override pattern if you already have a default bundle:

```yaml
# ~/.amplifier/settings.yaml
sources:
  infographic-builder: file:///Users/YOU/path/to/infographic-builder
```

### 2. Prerequisites check

```bash
# Confirm you have a Google API key for Gemini image generation
echo $GOOGLE_API_KEY   # should print your key

# Confirm Amplifier is installed
amplifier --version
```

### 3. Smoke tests

Run from the repo directory (so the local bundle resolves):

```bash
cd /path/to/infographic-builder

# Test 1: Basic generation (single pass)
amplifier run
# Then say: "Create an infographic about the water cycle"
# Expected: agent delegates, generates image, returns path + rationale

# Test 2: Critic loop
INFOGRAPHIC_CRITIC=true amplifier run
# Then say: "Create an infographic about the water cycle"
# Expected: generates image, analyzes it, optionally refines, returns critic summary

# Test 3: Multi-panel
INFOGRAPHIC_MULTI_PANEL=true amplifier run
# Then say: "Create an infographic about the history of the internet"
# Expected: decomposes into panels, generates each, returns all paths with assembly order

# Test 4: Both flags
INFOGRAPHIC_CRITIC=true INFOGRAPHIC_MULTI_PANEL=true amplifier run
# Then say: "Create a multi-panel infographic about climate change impacts"
# Expected: decomposes, generates each panel with critic loop, returns all paths
```

### 4. What to check

| Check | What to look for |
|-------|------------------|
| Delegation | Root session delegates to `infographic-designer` (not handling it directly) |
| Image output | `.png` file saved to disk at the reported path |
| Design rationale | Agent explains layout choice, palette, and reasoning |
| Critic summary | (when flag on) Reports what the critic found and whether it refined |
| Multi-panel output | (when flag on) Multiple numbered panel files with assembly instructions |
| Style consistency | (multi-panel) All panels share the same color palette and typography |

### 5. Latency benchmarking

To measure the critic loop's latency impact:

```bash
# Run N basic generations, note wallclock time per generation
amplifier run    # "create an infographic about X" — repeat with different topics

# Run N critic generations, note wallclock time per generation
INFOGRAPHIC_CRITIC=true amplifier run    # same topics

# Compare: critic adds ~1 analyze + up to 1 extra generate
```

## License

MIT
