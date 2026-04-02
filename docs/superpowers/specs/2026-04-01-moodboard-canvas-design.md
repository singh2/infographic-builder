# Moodboard Canvas — Design Spec

**Date:** 2026-04-01  
**Status:** Approved  
**Scope:** Page 1 of 2 (Moodboard). Page 2 (Style Explorer) is a separate future spec.

---

## Overview

A standalone HTML page (`canvas/index.html`) that showcases the full range of Infographic Builder and Diagram Beautifier outputs. Primary goals:

1. **Show range** — same prompt can produce radically different outputs depending on aesthetic choice
2. **Show depth** — each aesthetic has multiple use cases, layout variants, and sub-modes (diorama)
3. **Show possibility** — freeform outputs prove the system isn't limited to six presets
4. **Enable action** — any style card can open a live generation modal (the hybrid CTA)

**Audience:** Anyone evaluating or exploring what Infographic Builder can produce — potential users, demos, internal showcases.

**Format:** Single HTML file with embedded CSS and a thin Python backend for live generation. No framework dependencies. Works as a static file with CTAs disabled if no backend is running.

---

## Visual Language

| Token | Value | Usage |
|-------|-------|-------|
| Background | `#080810` | Page base |
| Surface | `#0c0c18` | Card footers, section surfaces |
| Elevated | `#131328` | Active nav items, modal background |
| Border | `#141420` | Card and section borders |
| Border subtle | `#0f0f1e` | Section dividers |
| Text primary | `#e0e0f0` | Headings, card names |
| Text secondary | `#888` | Descriptions, metadata |
| Text muted | `#444–#555` | Tags, captions, diagram card copy |
| Accent | `#5b6af0` | Try button, nav active state, modal CTA — used nowhere else |
| Scroll gradient | `radial-gradient(ellipse at 50% -10%, #0e0e30, #080810)` | Hero only |

**Typography:** System sans-serif (`-apple-system, 'Inter', sans-serif`)

| Role | Size | Weight | Notes |
|------|------|--------|-------|
| Hero headline | 54px | 800 | Letter-spacing: −2px |
| Section name | 26px | 800 | Letter-spacing: −0.5px |
| Card name | 11px | 600 | — |
| Use case tag | 10px | 600 | Pill shape, per-style color |
| Body / desc | 13px | 400 | Line-height 1.55 |
| Eyebrow / label | 10px | 400 | Letter-spacing 3px, uppercase |

**Spacing:** 8pt grid. Section padding: `48px 40px`. Card gap: `10–12px`. Section dividers: `border-top: 1px solid #0f0f1e`.

**Corner radius:** Cards `10px`, buttons `20px` (pill), variant badges `6px`.

---

## Page Structure

Eleven sections (including nav and footer):

| # | Section | Purpose |
|---|---------|---------|
| 0 | Sticky Nav | Section anchors + wordmark |
| 1 | Hero | Same topic × 4 styles — establishes range upfront |
| 2 | Clean Minimalist | First style section |
| 3 | Claymation Studio | Second — with diorama callout |
| 4 | Hand-Drawn Sketchnote | Third |
| 5 | Bold Editorial | Fourth |
| 6 | Dark Mode Tech | Fifth |
| 7 | Lego Brick Builder | Sixth — with diorama callout |
| 8 | Freeform ✦ | Open-ended, any-style examples + live CTA |
| 9 | Layout Types Strip | 14 layout types, horizontal filmstrip |
| 10 | Diagram Beautifier | Transformation strip: source → polished → cinematic |
| — | Footer | Two CTAs: generate infographic / beautify diagram |

---

## Section 0 — Sticky Nav

- **Left:** `InfographicBuilder` wordmark, `Builder` portion in accent color
- **Right:** Anchor links — `Gallery`, `Clean`, `Claymation`, `Sketchnote`, `Editorial`, `Freeform`, `Diagrams`
- **Behavior:** `position: sticky; top: 0`. Active anchor highlighted with elevated background + accent border. `backdrop-filter: blur(12px)` on `rgba(8,8,16,0.94)` background.
- **Height:** 52px

---

## Section 1 — Hero

**Headline:** "Your topic. Your style."  
**Sub:** "From boardroom-clean to tactile clay, hand-drawn sketches to neon-lit tech — the same idea, expressed in any aesthetic."  
**Eyebrow:** "Infographic Builder · Canvas"

**Comparison strip:** Four cards side by side, same topic rendered in:
1. Clean Minimalist
2. Claymation Studio
3. Hand-Drawn Sketchnote
4. Bold Editorial

Each card:
- `aspect-ratio: 2/3` — portrait proportion
- Image area: actual generated output (curated from existing `infographics/`)
- Footer: style name + use case tag (e.g. "Boardroom · Professional")
- Hover: lifts 4px, border lightens
- The four aesthetics above are chosen because they cover the full stylistic range from flat/minimal to 3D/tactile to illustrated — all visible in one glance

**Below strip:** Caption — `← same prompt — four aesthetics →`  
**Scroll cue:** Vertical line + "explore all styles" label, 48px below strip

**Content decision:** Use the `octo-meeting` series as the canonical comparison topic — outputs already exist for claymation, editorial, sketchnote. A clean minimalist version needs to be generated or substituted with another existing output in the same style.

---

## Sections 2–7 — Style Sections

Each style section follows an identical component structure:

### Section Header
```
[Style Name]            [Variant badges — right-aligned]
[Description, 1–2 sentences]
[Use case tags — pill row]
```

- **Style name:** 26px, 800 weight, in the aesthetic's accent color
- **Description:** 13px, secondary text, max-width 440px
- **Use case tags:** Pill-shaped tags, per-style color at ~30% opacity border, 10% opacity background fill
- **Variant badges** (where applicable): small `6px` radius chips — "Standard", "Diorama", "Multi-panel". Shown only on sections where variants exist (Claymation, Lego).

### Gallery Grid

12-column grid with editorial card sizing — not uniform. The primary (hero) card for each section is larger. Typical layouts:

| Section | Grid config |
|---------|-------------|
| Clean Minimalist | 3-col equal (light-themed cards, white backgrounds) |
| Claymation | 4 cols: 1.8fr / 1fr / 1fr / 1fr — hero card dominant |
| Sketchnote | 3 cols: 1.5fr / 1fr / 1fr |
| Bold Editorial | 3 equal cols |
| Dark Mode Tech | 3 equal cols |
| Lego | 2 equal cols (standard + diorama paired) |

### Style Card

```
┌─────────────────────────────┐
│                             │
│        [image area]         │  ← fills card, no internal padding
│                             │
├─────────────────────────────┤
│ [Style name]   [sub-label]  │  ← footer, surface color background
└─────────────────────────────┘
```

- `border-radius: 10px`, `overflow: hidden`, `border: 1px solid #141420`
- Image height varies by card weight (140px–280px)
- Footer: `padding: 8px 12px`, `background: #0c0c18` (or style-appropriate override)
- Card name: 11px, 600 weight, style accent color
- Sub-label: 9px, `#444`

**Hover state:**
- Overlay fades in: `rgba(0,0,0,0.72)` covering full card
- Centered "Try this style →" button (accent color, pill shape, 11px 600)
- Transition: `opacity 0.18s`

### Style-specific accent colors

| Style | Accent color |
|-------|-------------|
| Clean Minimalist | `#c8c8c8` (neutral — uses `#0D7377` teal in actual outputs) |
| Claymation | `#e07060` |
| Sketchnote | `#c8a86a` |
| Bold Editorial | `#e06050` |
| Dark Mode Tech | `#40c8d8` |
| Lego | `#FFD700` |
| Freeform | `#d0a040` |
| Diagram Beautifier | `#9060d0` |

### Diorama Callout

Appears at the bottom of the Claymation and Lego sections only:

```
┌─────────────────────────────────────────────────────────────┐
│  [DIORAMA MODE badge]   [description text]                  │
└─────────────────────────────────────────────────────────────┘
```

- Background: `#080f08`, border: `1px solid #1e2e1e`
- Badge: green pill — `#60d060`
- Text: *"Available for Claymation and Lego. Instead of a flat infographic layout, characters and objects act out your workflow in a physical scene — ideal for linear processes up to 6 steps."*

### Clean Minimalist section note

Cards in this section have light backgrounds (`#f8f8f5`) — the card footer and name styling inverts to dark-on-light to match the aesthetic. This is the only section that breaks the dark card pattern.

---

## Section 8 — Freeform ✦

**Header:**
- Name: "Freeform ✦" in `#d0a040`
- Description: "Beyond the six. Describe any aesthetic and the system interprets it into a full style brief. These examples were all generated with plain-language descriptions."

**Grid:** 12-column, cards sized editorially. Showcased styles (from existing `infographics/style-showcase/`):
- Comic Book (col-4)
- Disney Storybook (col-4)
- Pixel Art (col-4)
- Tron / Neon Grid (col-3)
- Watercolor (col-3)
- Super Mario (col-3)
- Vintage Poster (col-3)

Each card shows the actual generated image + the plain-language prompt the user typed, shown as the sub-label (e.g. `"8-bit pixel art, retro game palette"`). This reinforces that freeform is just natural language.

**CTA card** (last position, col-3):
- Dashed border: `2px dashed #201e3a`
- Content: `+` icon, "Describe any style and generate your own"
- On hover: border transitions to accent color
- On click: opens the generation modal (same as "Try this style →") with style field empty and focused

---

## Section 9 — Layout Types Strip

**Label:** "Layout types · 14 structures · any style" (10px, uppercase, muted)

**Filmstrip:** Horizontal scroll container, no scrollbar on modern browsers (`scrollbar-width: none`). Scroll affordance implied by cards clipping at edge.

Each layout thumbnail:
- `min-width: 90px`, `border-radius: 8px`, `border: 1px solid #141422`
- Icon area: 60px tall, `background: #0c0c18`, centered icon (emoji placeholder in v1, replaced with generated thumbnail in v2)
- Name: 9px, `#555`, `background: #090912`
- Hover: border transitions to accent

14 layouts in order: Timeline, Comparison, Hierarchy, Flow / Process, Hero + Details, Grid Breakdown, Hub & Spoke, Side by Side, Stats Dashboard, Journey Map, Before / After, Narrative Strip, Anatomy, Cycle / Loop.

---

## Section 10 — Diagram Beautifier

**Header:**
- Name: "Diagram Beautifier" in `#9060d0`
- Description: "Drop in any .dot or Mermaid file. Get back two simultaneous variants — one document-ready, one presentation-ready."

**Transformation strip:** Three cards linked by `→` and `+` arrows, `max-width: 880px`.

| Card | Border | Background | Content |
|------|--------|-----------|---------|
| Source | `#202028` | `#080808` | Raw `.dot` source code in monospace, `#333`, 9px |
| Polished | `#0D737740` | `linear-gradient(135deg,#050e14,#091e2e)` | Generated output image |
| Cinematic | `#B026FF40` | `linear-gradient(135deg,#07040e,#120820)` | Generated output image |

Footer for each:
- **Source:** "Your .dot or Mermaid file, untouched"
- **Polished** (`#0D8080`): "Document-ready. Aesthetic applied faithfully. All labels intact. Every node placed."
- **Cinematic** (`#9020d0`): "Presentation-ready. Hero focal point. Full spatial freedom. Mood over fidelity."

Card image `aspect-ratio: 3/2`.

---

## Footer

Centered, `padding: 56px 40px 72px`.

- **Headline:** "Start creating"
- **Sub:** "Describe your topic or drop in a diagram — pick your style, or invent your own"
- **Two buttons:**
  - "Generate an infographic" — filled accent
  - "Beautify a diagram" — ghost (transparent, `border: 1px solid #222`)
- Both buttons open the generation modal with the appropriate mode pre-selected.

---

## "Try This Style" Modal

Triggered by:
- Hovering any style card and clicking "Try this style →"
- Clicking the Freeform CTA card
- Clicking footer buttons

### Layout

```
┌─────────────────────────────────────────────────┐
│  [Style name] · [Use case summary]          [×] │
├─────────────────────────────────────────────────┤
│                                                 │
│  What do you want to visualise?                 │
│  ┌─────────────────────────────────────────┐   │
│  │  e.g. "How the agent loop works"        │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  Style  [Clean Minimalist ▾]  (pre-selected,   │
│          user can change)                       │
│                                                 │
│  [Generate ─────────────────────────────────]  │
│                                                 │
│  ─── or ──────────────────────────────────────  │
│  Have a diagram? Drop a .dot or Mermaid file    │
│                                                 │
└─────────────────────────────────────────────────┘
```

- Background: `rgba(0,0,0,0.85)` overlay behind modal
- Modal: `background: #131328`, `border-radius: 14px`, `border: 1px solid #2a2a4a`, `max-width: 520px`, centered
- Header: style name + eyebrow (use case), close button top-right
- Prompt textarea: multiline, `min-height: 80px`, `background: #0a0a1a`, `border: 1px solid #222`, focused border accent color
- Style selector: dropdown pre-populated with the 6 aesthetics + Freeform, pre-selected to whatever card triggered the modal
- Generate button: full-width, accent color, `border-radius: 8px`
- "Have a diagram?" section: file drop zone, secondary visual treatment

### Backend contract

`POST /generate`

```json
{
  "prompt": "How the agent loop works",
  "style": "claymation",
  "mode": "infographic"   // or "diagram"
}
```

Response: streamed status updates while the agent runs, then a final image URL. The modal shows a loading state during generation and renders the output inline when complete.

**Graceful degradation:** If no backend is running (pure static file), the Generate button is replaced with copy text: "Open Amplifier and use the prompt above." The textarea and style selector still render so the user can copy their inputs.

---

## Asset Inventory

Curated outputs to use per section (from existing `infographics/` directory):

| Section | Suggested outputs |
|---------|------------------|
| Hero strip | `octo-meeting-editorial_combined.png`, `octo-meeting-claymation_combined.png`, `octo-meeting-sketchnote_combined.png` + generate one clean minimalist |
| Clean Minimalist | `docs/examples/dtu_infographic.png`, `docs/examples/infobuilder_combined.png` |
| Claymation | `nation-and-state-claymation.png`, `network-state-claymation.png`, `recipe-pipeline-claymation.png`, `recipe-doc-gen_claymation-diorama.png` |
| Sketchnote | `8-rules-sketch.png`, `network-state-sketch_combined.png`, `octo-meeting-sketchnote_combined.png` |
| Bold Editorial | `octo-meeting-editorial_combined.png`, `flirt-guide-70s-editorial_combined.png`, `octo-meeting-mission-control_combined.png` |
| Dark Mode Tech | `multi-level-code-analysis_combined.png`, `code-analysis-dark-tech.png`, `recipe-pipeline-dark-tech.png` |
| Lego | `build-network-state-lego_combined.png`, `conditional-workflow_lego-diorama.png` |
| Freeform | `infographics/style-showcase/` directory (comic-book, disney-storybook, mario, pixel-art, tron, vintage-poster, watercolor) |

---

## File Structure

```
canvas/
├── index.html          ← Single-page moodboard (this spec)
├── styles.css          ← Extracted CSS (if HTML gets large)
├── modal.js            ← Modal open/close + backend fetch
└── server.py           ← Thin FastAPI server: POST /generate
```

`canvas/` lives at the project root alongside `agents/`, `docs/`, `infographics/`.

---

## Out of Scope (Page 2 — Style Explorer)

The second canvas page — where a user enters a single prompt and sees it rendered across all styles simultaneously — is a separate design. That spec will cover the comparison grid layout, style selection controls, and side-by-side output rendering.
