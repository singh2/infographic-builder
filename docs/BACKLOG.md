# Backlog

Ideas and planned work for the infographic builder.

## Planned

### Pre-rendered data visualization compositing

**Problem:** Gemini (and all current image-gen models) cannot produce numerically
accurate charts. Bar heights, pie slice proportions, and line graph trajectories
are approximate at best. For knowledge workers presenting data, this is a
significant gap -- they will notice when a "42% vs 58%" bar chart looks like
50/50.

**Idea:** Use a real charting library (matplotlib, plotly, or a lightweight SVG
renderer) to pre-render accurate chart images, then pass them to Gemini as a
`reference_image_path` with a prompt that wraps the chart in infographic context
(title, annotations, surrounding narrative sections, consistent style).

This splits the problem: precision math goes to a deterministic tool, aesthetic
wrapping goes to the model.

**Trade-off:** This would add a Python dependency to what is currently a
zero-code declarative bundle. Could be implemented as an optional tool module
that the agent calls when it detects data-heavy requests, falling back to
pure prompt-based generation when the tool isn't available.

**Status:** Idea stage. Needs design work on the tool interface and how the
agent decides when to use pre-rendered charts vs pure generation.

Note: The bundle now has a Python tool module precedent (`tool-stitch-panels`
in `modules/`), so adding another module for chart pre-rendering follows the
same pattern.

## Done

### Multi-panel stitching tool

**Problem:** Multi-panel infographics were delivered as separate PNG files.
Users had to manually combine them to get a single shareable image.

**Solution:** Added `tool-stitch-panels` -- a Pillow-based tool module at
`modules/tool-stitch-panels/` that vertically stacks panel PNGs into a single
combined image. The agent calls it automatically after multi-panel generation.
Both individual panels and the combined image are delivered.

**Files:**
- `modules/tool-stitch-panels/` -- the tool module (pyproject.toml + __init__.py)
- `behaviors/infographic.yaml` -- wired via `source: ./modules/tool-stitch-panels`
- `agents/infographic-builder.md` -- step 6 added (assemble), tool docs added,
  output contract updated to include combined image path