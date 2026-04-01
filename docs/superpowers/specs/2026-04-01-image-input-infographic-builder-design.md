# Design: Image Input for the Infographic Builder

**Date:** 2026-04-01
**Status:** Approved

---

## Problem

The infographic builder currently accepts only text as input. The diagram-beautifier, by contrast, now accepts image input (PNG) as part of the analyze-first routing introduced in PR #27. There is a natural extension: users should be able to provide a reference image to the infographic builder too — either as a **style reference** ("make it feel like this") or as a **content source** ("make me an infographic about this").

This design extends the analyze-first routing primitive to serve both agents, without adding new analyze calls or routing complexity.

---

## Design

### Core principle: single analysis, dual output

When a user provides a PNG alongside a text prompt, the root session runs one `nano-banana analyze` call that extracts three things simultaneously:

1. **Diagram classification** — YES/NO: is this a structured diagram?
2. **Content summary** — what is this image about? (subject matter, key elements, data, concepts)
3. **Aesthetic description** — what does this look like visually? (palette, typography character, mood, style)

This is the same analyze call that already drives diagram-vs-infographic routing. It now does more work in the same call.

### Aesthetic characteristics are opt-in, not opt-out

The aesthetic description is extracted in every analyze call, but is **only passed to the infographic-builder if the user's text prompt explicitly signals style intent**.

Style intent signals: phrases like "feels like this", "in the style of", "make it look like", "matching this aesthetic".

If no style signal is present → aesthetic description is silently discarded. The normal 6-option aesthetic menu runs.

This is deliberate. The user should not have to think about suppressing style inference when they just want to extract content from a whiteboard photo.

---

## Routing flow

```
User provides: text prompt + PNG image
                    │
                    ▼
         nano-banana analyze (single call)
         extracts: diagram? / content_summary / aesthetic_description
                    │
          ┌─────────┴──────────┐
        YES                   NO
    (diagram)            (not diagram)
          │                    │
          ▼                    ▼
   diagram-beautifier    check user prompt
   (existing, unchanged)  for style intent
                               │
                    ┌──────────┴──────────┐
               style signal          no style signal
               detected               (default)
                    │                    │
                    ▼                    ▼
            infographic-builder   infographic-builder
            + content_summary     + content_summary only
            + aesthetic_description  (aesthetic discarded)
            + image_path          + image_path NOT passed
                                    to nano-banana
```

---

## Infographic-builder agent changes

### Step 1 — Parse
If `content_summary` is provided, it becomes the subject matter. The text prompt supplies intent and modifiers (tone, format, constraints); `content_summary` supplies the topic. For example: "make me a dark infographic about this" — "dark" comes from the text prompt, the subject comes from `content_summary`. If the text prompt already fully specifies the topic, `content_summary` is treated as supplementary detail.

### Step 2 — Content density analysis
Unchanged. `content_summary` is text; the same panel-count heuristics apply.

### Step 3 — Aesthetic selection
- If `aesthetic_description` is present: skip the 6-option menu entirely. Translate the aesthetic description into the same 7 style dimensions used by existing templates (palette, typography, icons, background, lighting, texture, mood). Downstream steps see the same shape of input they always have.
- If absent: normal menu flow, unchanged.

### Step 4 — Design planning
Unchanged. By this step, the aesthetic (however it arrived) has already been translated into the 7 style dimensions. No special casing required.

### Step 5 — Generation

| Mode | Panel 1 | Panels 2-N |
|---|---|---|
| Style reference, single panel | `reference_image_path = image_path` | — |
| Style reference, multi-panel | `reference_image_path = image_path` | `reference_image_paths = [panel_1_path, image_path]` |
| Content source | No reference image passed | Panel 1 used for chaining only (existing) |

The multi-panel style reference case is the first use of `reference_image_paths` (plural) in the project. Two anchors: Panel 1 for cross-panel consistency, original style reference for aesthetic fidelity.

In content source mode, `image_path` is intentionally NOT passed to nano-banana. The content summary (text) is sufficient, and passing a raw whiteboard photo or screenshot would pollute the generated aesthetic.

### Steps 6–8 — Quality review, assembly, return
Unchanged.

---

## What does NOT change

- The diagram-beautifier flow is entirely unchanged.
- Text-only prompts (no image) are entirely unchanged — all existing behavior is preserved.
- The 6-option aesthetic menu continues to appear whenever no style reference is provided.
- The inline style shortcut ("claymation infographic about DNS") continues to bypass the menu as before.

---

## Files to change

| File | Change |
|---|---|
| `context/infographic-awareness.md` | Upgrade analyze prompt to extract content_summary + aesthetic_description in addition to diagram classification; add style intent detection logic; pass enriched context to infographic-builder |
| `agents/infographic-builder.md` | Step 1: accept content_summary; Step 3: accept + translate aesthetic_description, skip menu; Step 5: pass image_path as reference in style mode; document reference_image_paths for multi-panel style reference |
| `docs/style-guide.md` | Document `reference_image_paths` (plural) in the multi-panel generation section; add style reference mode to aesthetic selection section |
| `tests/test_diagram_routing.py` | Add tests for enriched analyze prompt; add tests for style intent detection |
| `tests/test_infographic_builder_agent.py` | Add tests for content_summary acceptance in Step 1; aesthetic_description → menu skip in Step 3; reference_image_path in Step 5 generation |
