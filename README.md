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

## License

MIT
