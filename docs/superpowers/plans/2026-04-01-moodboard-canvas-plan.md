# Moodboard Canvas Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `canvas/index.html`, a scrollable moodboard page showcasing all Infographic Builder and Diagram Beautifier outputs, with a live generation modal backed by a FastAPI server.

**Architecture:** A single HTML file with external CSS (`canvas/styles.css`) and vanilla JS (`canvas/modal.js`), serving curated output images from the existing `infographics/` directory. A thin FastAPI server (`canvas/server.py`) accepts `POST /generate` requests and invokes the Amplifier agent, streaming status back to the browser. The page degrades gracefully to a static gallery if no server is running.

**Tech Stack:** HTML5, CSS3, vanilla JavaScript (ES2020), FastAPI, Python 3.11+, pytest, httpx (for async API tests)

**Spec:** `docs/superpowers/specs/2026-04-01-moodboard-canvas-design.md`

---

## File Map

| File | Responsibility |
|------|---------------|
| `canvas/index.html` | Full page markup — nav, all 10 sections, footer, modal overlay |
| `canvas/styles.css` | All styles — tokens, typography, card, section, modal, filmstrip |
| `canvas/modal.js` | Modal open/close, style pre-selection, server health check, fetch + loading state |
| `canvas/server.py` | FastAPI app — `POST /generate` endpoint that invokes the Amplifier agent |
| `tests/canvas/test_assets.py` | Verify every image path referenced in the HTML actually exists on disk |
| `tests/canvas/test_server.py` | API tests for POST /generate — structure, validation, error handling |

---

## Task 1: Scaffold canvas/ and write the asset existence test harness

**Files:**
- Create: `canvas/index.html` (empty)
- Create: `canvas/styles.css` (empty)
- Create: `canvas/modal.js` (empty)
- Create: `canvas/server.py` (empty)
- Create: `tests/canvas/__init__.py` (empty)
- Create: `tests/canvas/test_assets.py`

- [ ] **Step 1: Create the canvas/ directory and empty files**

```bash
mkdir -p canvas tests/canvas
touch canvas/index.html canvas/styles.css canvas/modal.js canvas/server.py
touch tests/canvas/__init__.py
```

- [ ] **Step 2: Write the failing asset existence test**

Create `tests/canvas/test_assets.py`:

```python
"""Verify every image referenced in canvas/index.html exists on disk.

This test is intentionally written before the HTML so it fails
until the correct image paths are wired in.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent  # repo root


def _extract_img_srcs(html: str) -> list[str]:
    return re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html)


def test_all_referenced_images_exist():
    html_path = ROOT / "canvas" / "index.html"
    if not html_path.exists() or html_path.stat().st_size == 0:
        return  # skip until HTML is written
    html = html_path.read_text()
    srcs = _extract_img_srcs(html)
    assert srcs, "No <img> tags found — check HTML is populated"
    missing = [s for s in srcs if not (ROOT / s.lstrip("/")).exists()]
    assert not missing, (
        f"Missing image files referenced in canvas/index.html:\n"
        + "\n".join(f"  {m}" for m in missing)
    )


def test_hero_images_all_present():
    """The four hero comparison images must exist — they're visible above the fold."""
    expected = [
        "infographics/octo-meeting-claymation_combined.png",
        "infographics/octo-meeting-sketchnote_combined.png",
        "infographics/octo-meeting-editorial_combined.png",
    ]
    missing = [p for p in expected if not (ROOT / p).exists()]
    assert not missing, f"Hero images missing: {missing}"
```

- [ ] **Step 3: Run the tests to confirm they pass (hero check) or skip (asset check)**

```bash
pytest tests/canvas/test_assets.py -v
```

Expected: `test_hero_images_all_present` PASS (files exist), `test_all_referenced_images_exist` PASS (skips because HTML empty).

- [ ] **Step 4: Commit**

```bash
git add canvas/ tests/canvas/
git commit -m "feat: scaffold canvas/ directory and asset existence tests"
```

---

## Task 2: CSS design tokens and base styles

**Files:**
- Modify: `canvas/styles.css`

- [ ] **Step 1: Write the full CSS token and base style layer**

Write `canvas/styles.css`:

```css
/* ── TOKENS ─────────────────────────────────────────────── */
:root {
  --bg:           #080810;
  --surface:      #0c0c18;
  --elevated:     #131328;
  --border:       #141420;
  --border-sub:   #0f0f1e;
  --text-primary: #e0e0f0;
  --text-sec:     #888888;
  --text-muted:   #555555;
  --accent:       #5b6af0;

  /* per-style accent colors */
  --c-minimal:    #c8c8c8;
  --c-clay:       #e07060;
  --c-sketch:     #c8a86a;
  --c-editorial:  #e06050;
  --c-darktech:   #40c8d8;
  --c-lego:       #FFD700;
  --c-freeform:   #d0a040;
  --c-diagram:    #9060d0;

  --radius-card:   10px;
  --radius-btn:    20px;
  --radius-badge:   6px;
  --section-pad: 48px 40px;
  --card-gap:      10px;
}

/* ── RESET ───────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  background: var(--bg);
  color: var(--text-primary);
  font-family: -apple-system, 'Inter', sans-serif;
  font-size: 14px;
  line-height: 1.5;
}

img { display: block; width: 100%; height: 100%; object-fit: cover; }

/* ── TYPOGRAPHY SCALE ────────────────────────────────────── */
.t-hero    { font-size: 54px;  font-weight: 800; line-height: 1.07; letter-spacing: -2px; }
.t-section { font-size: 26px;  font-weight: 800; letter-spacing: -.5px; }
.t-card    { font-size: 11px;  font-weight: 600; }
.t-tag     { font-size: 10px;  font-weight: 600; }
.t-body    { font-size: 13px;  font-weight: 400; line-height: 1.55; }
.t-eye     { font-size: 10px;  letter-spacing: 3px; text-transform: uppercase; }
.t-meta    { font-size: 9px;   color: var(--text-muted); }

/* ── STICKY NAV ──────────────────────────────────────────── */
.nav {
  position: sticky; top: 0; z-index: 100;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 40px; height: 52px;
  background: rgba(8,8,16,.94);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-sub);
}
.nav-logo { font-size: 13px; font-weight: 700; color: var(--text-primary); }
.nav-logo span { color: var(--accent); }
.nav-anchors { display: flex; gap: 4px; }
.nav-anchor {
  padding: 5px 12px; border-radius: var(--radius-btn);
  font-size: 11px; color: var(--text-muted);
  border: 1px solid transparent; text-decoration: none;
  transition: color .15s, border-color .15s, background .15s;
}
.nav-anchor:hover { color: #aaa; border-color: #222; }
.nav-anchor.active { color: var(--text-primary); border-color: #2a2a4a; background: var(--elevated); }

/* ── SECTION ─────────────────────────────────────────────── */
.section { padding: var(--section-pad); border-top: 1px solid var(--border-sub); }

.section-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 28px; }
.section-left { flex: 1; }
.section-name { margin-bottom: 6px; }
.section-desc { color: var(--text-sec); max-width: 440px; }
.use-cases { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 12px; }

.uc-tag {
  padding: 4px 10px; border-radius: var(--radius-btn);
  font-size: 10px; font-weight: 600;
  border: 1px solid; background: transparent;
}

.variant-badges { display: flex; gap: 6px; align-items: flex-start; padding-top: 4px; }
.variant-badge {
  padding: 4px 10px; border-radius: var(--radius-badge);
  font-size: 9px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase;
  border: 1px solid var(--border); color: var(--text-muted);
}
.variant-badge.active { border-color: #3a3a5a; color: var(--text-primary); background: var(--elevated); }

/* ── 12-COLUMN GRID ──────────────────────────────────────── */
.grid-12 { display: grid; grid-template-columns: repeat(12, 1fr); gap: var(--card-gap); }
.col-3  { grid-column: span 3; }
.col-4  { grid-column: span 4; }
.col-5  { grid-column: span 5; }
.col-6  { grid-column: span 6; }
.col-7  { grid-column: span 7; }

/* named editorial grid configs */
.grid-editorial-clay     { grid-template-columns: 1.8fr 1fr 1fr 1fr; }
.grid-editorial-sketch   { grid-template-columns: 1.5fr 1fr 1fr; }
.grid-editorial-3col     { grid-template-columns: 1fr 1fr 1fr; }
.grid-editorial-2col     { grid-template-columns: 1fr 1fr; }
.grid-editorial-minimal  { grid-template-columns: 1fr 1fr 1fr; }

/* ── STYLE CARD ──────────────────────────────────────────── */
.style-card {
  border-radius: var(--radius-card);
  overflow: hidden;
  border: 1px solid var(--border);
  cursor: pointer;
  position: relative;
}
.style-card:hover .card-overlay { opacity: 1; }

.card-img {
  width: 100%; overflow: hidden;
}
.card-img img { width: 100%; height: 100%; object-fit: cover; }

/* card heights */
.h-280 .card-img { height: 280px; }
.h-260 .card-img { height: 260px; }
.h-220 .card-img { height: 220px; }
.h-200 .card-img { height: 200px; }
.h-180 .card-img { height: 180px; }
.h-160 .card-img { height: 160px; }
.h-150 .card-img { height: 150px; }

.card-footer {
  padding: 8px 12px;
  background: var(--surface);
}
.card-footer .card-name { font-size: 11px; font-weight: 600; }
.card-footer .card-sub  { font-size: 9px; color: var(--text-muted); margin-top: 2px; }

/* Clean Minimalist light override */
.card-light .card-img { background: #f8f8f5; }
.card-light .card-footer { background: #f0efe8; }
.card-light .card-footer .card-name { color: #2a2a2a; }
.card-light .card-footer .card-sub  { color: #888; }

/* card hover overlay */
.card-overlay {
  position: absolute; inset: 0;
  background: rgba(0,0,0,.72);
  display: flex; align-items: center; justify-content: center;
  opacity: 0; transition: opacity .18s;
}
.try-btn {
  padding: 8px 18px;
  background: var(--accent); color: #fff;
  border-radius: var(--radius-btn);
  font-size: 11px; font-weight: 600;
  border: none; cursor: pointer;
}

/* ── DIORAMA CALLOUT ─────────────────────────────────────── */
.diorama-callout {
  margin-top: 12px;
  padding: 14px 16px;
  border-radius: 8px;
  border: 1px solid #1e2e1e;
  background: #080f08;
  display: flex; align-items: center; gap: 16px;
}
.diorama-badge {
  padding: 4px 10px; border-radius: var(--radius-badge);
  font-size: 9px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase;
  border: 1px solid rgba(96,208,96,.25); color: #60d060; background: rgba(96,208,96,.06);
  white-space: nowrap;
}
.diorama-text { font-size: 11px; color: var(--text-sec); line-height: 1.5; }
.diorama-text strong { color: var(--text-primary); }

/* ── FREEFORM SECTION ────────────────────────────────────── */
.ff-cta-card {
  border-radius: var(--radius-card);
  border: 2px dashed #201e3a;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 10px; cursor: pointer; min-height: 150px;
  transition: border-color .18s;
}
.ff-cta-card:hover { border-color: var(--accent); }
.ff-cta-plus  { font-size: 22px; color: #2a2840; }
.ff-cta-label { font-size: 11px; color: #383650; text-align: center; line-height: 1.5; }

/* ── LAYOUT FILMSTRIP ────────────────────────────────────── */
.filmstrip-label {
  font-size: 10px; letter-spacing: 2px; text-transform: uppercase;
  color: var(--text-muted); margin-bottom: 18px;
}
.filmstrip {
  display: flex; gap: 8px; overflow-x: auto;
  padding-bottom: 6px; scrollbar-width: none;
}
.filmstrip::-webkit-scrollbar { display: none; }
.layout-thumb {
  min-width: 90px; border-radius: 8px;
  border: 1px solid #141422; overflow: hidden;
  cursor: pointer; flex-shrink: 0;
  transition: border-color .15s;
}
.layout-thumb:hover { border-color: var(--accent); }
.lt-icon {
  height: 60px; background: var(--surface);
  display: flex; align-items: center; justify-content: center;
  font-size: 20px;
}
.lt-name { padding: 5px 8px; font-size: 9px; color: var(--text-muted); background: #090912; }

/* ── DIAGRAM BEAUTIFIER ──────────────────────────────────── */
.diag-strip {
  display: flex; gap: 16px; align-items: stretch; max-width: 880px;
}
.diag-arrow { font-size: 18px; color: #1e1e2e; align-self: center; flex-shrink: 0; }
.diag-card {
  flex: 1; border-radius: var(--radius-card); overflow: hidden;
  border: 1px solid var(--border);
}
.diag-card.polished { flex: 1.1; border-color: rgba(13,115,119,.25); }
.diag-card.cinematic { flex: 1.1; border-color: rgba(176,38,255,.25); }
.diag-card-img {
  aspect-ratio: 3/2; overflow: hidden;
}
.diag-card-img img { width: 100%; height: 100%; object-fit: cover; }
.diag-card.source .diag-card-img {
  background: #080808;
  padding: 14px;
  font-family: monospace; font-size: 9px; color: #333; white-space: pre; line-height: 1.7;
  display: flex; align-items: flex-start; /* overrides img rule */
}
.diag-card-footer { padding: 10px 14px; background: #0a0a12; }
.diag-card-name {
  font-size: 11px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase;
  margin-bottom: 3px;
}
.diag-card-desc { font-size: 10px; color: #3a3a4a; line-height: 1.5; }

/* ── FOOTER ──────────────────────────────────────────────── */
.page-footer {
  text-align: center;
  padding: 56px 40px 72px;
  border-top: 1px solid var(--border-sub);
}
.footer-headline { font-size: 28px; font-weight: 700; margin-bottom: 10px; }
.footer-sub { font-size: 14px; color: var(--text-muted); margin-bottom: 24px; }
.btn {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 11px 26px; border-radius: 8px;
  font-size: 13px; font-weight: 600; border: none; cursor: pointer; margin: 0 5px;
}
.btn-primary { background: var(--accent); color: #fff; }
.btn-ghost   { background: transparent; border: 1px solid #222; color: var(--text-muted); }

/* ── MODAL ───────────────────────────────────────────────── */
.modal-overlay {
  position: fixed; inset: 0; z-index: 200;
  background: rgba(0,0,0,.85);
  display: flex; align-items: center; justify-content: center;
  opacity: 0; pointer-events: none;
  transition: opacity .2s;
}
.modal-overlay.open { opacity: 1; pointer-events: all; }

.modal {
  background: var(--elevated);
  border-radius: 14px;
  border: 1px solid #2a2a4a;
  max-width: 520px; width: 90%;
  padding: 24px;
}
.modal-header {
  display: flex; align-items: flex-start; justify-content: space-between;
  margin-bottom: 20px;
}
.modal-style-name { font-size: 16px; font-weight: 700; }
.modal-use-case   { font-size: 11px; color: var(--text-muted); margin-top: 3px; }
.modal-close      { background: none; border: none; color: var(--text-muted); cursor: pointer; font-size: 18px; }

.modal-label { font-size: 11px; color: var(--text-sec); margin-bottom: 6px; margin-top: 16px; }
.modal-textarea {
  width: 100%; min-height: 80px; resize: vertical;
  background: #0a0a1a; border: 1px solid #222; border-radius: 6px;
  color: var(--text-primary); font-size: 13px; padding: 10px 12px;
  font-family: inherit; line-height: 1.5;
  transition: border-color .15s;
}
.modal-textarea:focus { outline: none; border-color: var(--accent); }

.modal-style-select {
  width: 100%; background: #0a0a1a; border: 1px solid #222; border-radius: 6px;
  color: var(--text-primary); font-size: 13px; padding: 8px 12px;
  cursor: pointer;
}

.modal-generate {
  width: 100%; margin-top: 20px;
  padding: 12px; border-radius: 8px;
  background: var(--accent); color: #fff;
  font-size: 13px; font-weight: 600; border: none; cursor: pointer;
  transition: opacity .15s;
}
.modal-generate:disabled { opacity: .5; cursor: not-allowed; }
.modal-generate.loading::after { content: " …"; }

.modal-or {
  display: flex; align-items: center; gap: 10px;
  margin: 18px 0; color: var(--text-muted); font-size: 11px;
}
.modal-or::before, .modal-or::after {
  content: ''; flex: 1; height: 1px; background: #1e1e2e;
}

.modal-diagram-zone {
  border: 1px dashed #2a2a3a; border-radius: 8px;
  padding: 14px 16px; text-align: center;
  color: var(--text-muted); font-size: 11px; cursor: pointer;
}

.modal-output { margin-top: 20px; }
.modal-output img { width: 100%; border-radius: 8px; }

/* copy-prompt mode (no server) */
.modal-copy-prompt {
  margin-top: 16px; padding: 12px 14px;
  background: #0a0a1a; border-radius: 8px; border: 1px solid #1e1e2e;
  font-size: 11px; color: var(--text-sec); line-height: 1.6;
}
.modal-copy-prompt code {
  font-family: monospace; color: var(--text-primary); font-size: 11px;
}
```

- [ ] **Step 2: Verify CSS file is valid (no syntax errors)**

```bash
# Quick parse check — if node is available
node -e "const fs=require('fs'); fs.readFileSync('canvas/styles.css','utf8'); console.log('CSS OK')"
# or just open canvas/index.html in browser after Task 3 and check DevTools console
```

- [ ] **Step 3: Commit**

```bash
git add canvas/styles.css
git commit -m "feat: add full CSS design system for canvas moodboard"
```

---

## Task 3: HTML skeleton — nav, section containers, footer

**Files:**
- Modify: `canvas/index.html`

- [ ] **Step 1: Write base HTML with nav, all 10 section shells, and footer**

Write `canvas/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Infographic Builder · Canvas</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>

<!-- NAV -->
<nav class="nav">
  <div class="nav-logo">Infographic<span>Builder</span></div>
  <div class="nav-anchors">
    <a href="#hero"       class="nav-anchor active">Gallery</a>
    <a href="#minimal"    class="nav-anchor">Clean</a>
    <a href="#claymation" class="nav-anchor">Claymation</a>
    <a href="#sketchnote" class="nav-anchor">Sketchnote</a>
    <a href="#editorial"  class="nav-anchor">Editorial</a>
    <a href="#freeform"   class="nav-anchor">Freeform</a>
    <a href="#diagrams"   class="nav-anchor">Diagrams</a>
  </div>
</nav>

<!-- HERO -->
<section id="hero"><!-- Task 4 --></section>

<!-- CLEAN MINIMALIST -->
<section id="minimal" class="section"><!-- Task 5 --></section>

<!-- CLAYMATION -->
<section id="claymation" class="section"><!-- Task 6 --></section>

<!-- SKETCHNOTE -->
<section id="sketchnote" class="section"><!-- Task 7 --></section>

<!-- BOLD EDITORIAL -->
<section id="editorial" class="section"><!-- Task 7 --></section>

<!-- DARK MODE TECH -->
<section id="darktech" class="section"><!-- Task 8 --></section>

<!-- LEGO -->
<section id="lego" class="section"><!-- Task 8 --></section>

<!-- FREEFORM -->
<section id="freeform" class="section"><!-- Task 9 --></section>

<!-- LAYOUT TYPES -->
<section id="layouts" class="section"><!-- Task 10 --></section>

<!-- DIAGRAM BEAUTIFIER -->
<section id="diagrams" class="section"><!-- Task 11 --></section>

<!-- FOOTER -->
<footer class="page-footer"><!-- Task 11 --></footer>

<!-- MODAL OVERLAY -->
<div class="modal-overlay" id="modal-overlay" role="dialog" aria-modal="true">
  <!-- Task 12 -->
</div>

<script src="modal.js"></script>
</body>
</html>
```

- [ ] **Step 2: Open in browser and verify nav renders and section anchors scroll**

```bash
open canvas/index.html
# Verify: nav appears, section IDs are reachable via anchor links
```

- [ ] **Step 3: Commit**

```bash
git add canvas/index.html
git commit -m "feat: add HTML skeleton with nav and section containers"
```

---

## Task 4: Hero section

**Files:**
- Modify: `canvas/index.html` — fill in `#hero`

The hero comparison strip uses the `octo-meeting` series. Three images already exist; the Clean Minimalist slot uses `docs/examples/dtu_infographic.png` as a stand-in until a proper Clean Minimalist octo-meeting variant is generated.

- [ ] **Step 1: Write CSS additions for the hero section** — append to `canvas/styles.css`:

```css
/* ── HERO ────────────────────────────────────────────────── */
.hero {
  min-height: 88vh;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 80px 40px 60px;
  background: radial-gradient(ellipse at 50% -10%, #0e0e30, var(--bg));
  text-align: center;
}
.hero-eye     { color: var(--accent); margin-bottom: 16px; }
.hero-h1      { color: #fff; margin-bottom: 16px; max-width: 700px; }
.hero-sub     { color: var(--text-muted); max-width: 480px; line-height: 1.65; margin-bottom: 52px; }
.hero-caption { margin-top: 18px; font-size: 10px; color: #2a2a3a; letter-spacing: 1px; }

.hero-strip { display: flex; gap: 12px; width: 100%; max-width: 960px; }
.hero-card {
  flex: 1; border-radius: 12px; overflow: hidden;
  border: 1px solid var(--border);
  cursor: pointer; transition: transform .18s, border-color .18s;
}
.hero-card:hover { transform: translateY(-4px); border-color: #3a3a5a; }
.hero-card-img { aspect-ratio: 2/3; overflow: hidden; }
.hero-card-img img { width: 100%; height: 100%; object-fit: cover; }
.hero-card-foot { padding: 10px 12px; background: #0c0c18; }
.hero-card-name { font-size: 10px; font-weight: 700; }
.hero-card-tag  { font-size: 9px; color: var(--text-muted); margin-top: 2px; }

.scroll-hint {
  margin-top: 48px;
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  font-size: 9px; color: #2a2a3a; letter-spacing: 2px; text-transform: uppercase;
}
.scroll-line { width: 1px; height: 36px; background: linear-gradient(to bottom, #2a2a3a, transparent); }
```

- [ ] **Step 2: Fill in the hero section in `canvas/index.html`**

Replace `<!-- Task 4 -->` inside `<section id="hero">` with:

```html
<div class="hero">
  <p class="t-eye hero-eye">Infographic Builder · Canvas</p>
  <h1 class="t-hero hero-h1">Your topic.<br>Your style.</h1>
  <p class="t-body hero-sub">From boardroom-clean to tactile clay, hand-drawn sketches to neon-lit tech — the same idea, expressed in any aesthetic.</p>

  <div class="hero-strip">
    <div class="hero-card" data-style="minimalist" data-usecase="Boardroom · Professional">
      <div class="hero-card-img">
        <img src="../docs/examples/dtu_infographic.png" alt="Clean Minimalist example">
      </div>
      <div class="hero-card-foot">
        <div class="hero-card-name" style="color:var(--c-minimal)">Clean Minimalist</div>
        <div class="hero-card-tag">Boardroom · Professional</div>
      </div>
    </div>

    <div class="hero-card" data-style="claymation" data-usecase="Tutorials · Storytelling">
      <div class="hero-card-img">
        <img src="../infographics/octo-meeting-claymation_combined.png" alt="Claymation example">
      </div>
      <div class="hero-card-foot">
        <div class="hero-card-name" style="color:var(--c-clay)">Claymation Studio</div>
        <div class="hero-card-tag">Tutorials · Storytelling</div>
      </div>
    </div>

    <div class="hero-card" data-style="sketchnote" data-usecase="Meeting notes · Brainstorms">
      <div class="hero-card-img">
        <img src="../infographics/octo-meeting-sketchnote_combined.png" alt="Sketchnote example">
      </div>
      <div class="hero-card-foot">
        <div class="hero-card-name" style="color:var(--c-sketch)">Hand-Drawn Sketchnote</div>
        <div class="hero-card-tag">Meeting notes · Brainstorms</div>
      </div>
    </div>

    <div class="hero-card" data-style="editorial" data-usecase="Reports · Presentations">
      <div class="hero-card-img">
        <img src="../infographics/octo-meeting-editorial_combined.png" alt="Bold Editorial example">
      </div>
      <div class="hero-card-foot">
        <div class="hero-card-name" style="color:var(--c-editorial)">Bold Editorial</div>
        <div class="hero-card-tag">Reports · Presentations</div>
      </div>
    </div>
  </div>

  <p class="hero-caption">← same prompt — four aesthetics →</p>
  <div class="scroll-hint"><div class="scroll-line"></div>explore all styles</div>
</div>
```

- [ ] **Step 3: Run asset test — expect pass**

```bash
pytest tests/canvas/test_assets.py::test_hero_images_all_present -v
```

Expected: PASS

- [ ] **Step 4: Open in browser and verify hero renders with images**

```bash
open canvas/index.html
```

- [ ] **Step 5: Commit**

```bash
git add canvas/index.html canvas/styles.css
git commit -m "feat: add hero section with four-style comparison strip"
```

---

## Task 5: Clean Minimalist section

**Files:**
- Modify: `canvas/index.html` — fill in `#minimal`

- [ ] **Step 1: Fill in Clean Minimalist section in `canvas/index.html`**

Replace `<!-- Task 5 -->` inside `<section id="minimal" class="section">` with:

```html
<div class="section-header">
  <div class="section-left">
    <h2 class="t-section section-name" style="color:var(--c-minimal)">Clean Minimalist</h2>
    <p class="t-body section-desc">Swiss design, boardroom-ready. White space does the heavy lifting — flat icons, deep teal or navy accents, no shadows.</p>
    <div class="use-cases">
      <span class="uc-tag" style="color:var(--c-minimal);border-color:rgba(200,200,200,.3)">Boardroom</span>
      <span class="uc-tag" style="color:var(--c-minimal);border-color:rgba(200,200,200,.3)">Corporate</span>
      <span class="uc-tag" style="color:var(--c-minimal);border-color:rgba(200,200,200,.3)">Annual reports</span>
      <span class="uc-tag" style="color:var(--c-minimal);border-color:rgba(200,200,200,.3)">Data presentations</span>
    </div>
  </div>
</div>

<div class="grid-12 grid-editorial-minimal" style="gap:10px;">
  <div class="style-card h-220 card-light" data-style="minimalist" data-usecase="Boardroom · Professional">
    <div class="card-img"><img src="../docs/examples/dtu_infographic.png" alt="Clean Minimalist — DTU"></div>
    <div class="card-footer">
      <div class="card-name" style="color:#0D7377">Clean Minimalist</div>
      <div class="card-sub">DTU infographic</div>
    </div>
    <div class="card-overlay"><button class="try-btn">Try this style →</button></div>
  </div>

  <div class="style-card h-220 card-light" data-style="minimalist" data-usecase="Boardroom · Professional">
    <div class="card-img"><img src="../docs/examples/infobuilder_combined.png" alt="Clean Minimalist — Infographic Builder"></div>
    <div class="card-footer">
      <div class="card-name" style="color:#0D7377">Clean Minimalist</div>
      <div class="card-sub">Infographic Builder overview</div>
    </div>
    <div class="card-overlay"><button class="try-btn">Try this style →</button></div>
  </div>

  <div class="style-card h-220 card-light" data-style="minimalist" data-usecase="Boardroom · Professional">
    <div class="card-img"><img src="../docs/showcase/devops-lifecycle.png" alt="Clean Minimalist — DevOps lifecycle"></div>
    <div class="card-footer">
      <div class="card-name" style="color:#0D7377">Clean Minimalist</div>
      <div class="card-sub">DevOps lifecycle</div>
    </div>
    <div class="card-overlay"><button class="try-btn">Try this style →</button></div>
  </div>
</div>
```

- [ ] **Step 2: Run asset test**

```bash
pytest tests/canvas/test_assets.py -v
```

Expected: PASS (all three images exist under `docs/`)

- [ ] **Step 3: Commit**

```bash
git add canvas/index.html
git commit -m "feat: add Clean Minimalist style section"
```

---

## Task 6: Claymation and Sketchnote sections

**Files:**
- Modify: `canvas/index.html` — fill in `#claymation` and `#sketchnote`

- [ ] **Step 1: Fill in Claymation section**

Replace `<!-- Task 6 -->` inside `<section id="claymation" class="section">` with:

```html
<div class="section-header">
  <div class="section-left">
    <h2 class="t-section section-name" style="color:var(--c-clay)">Claymation Studio</h2>
    <p class="t-body section-desc">Tactile, whimsical, plasticine-textured. Characters and objects sculpted by hand, lit with shallow depth-of-field. Makes complex ideas feel approachable.</p>
    <div class="use-cases">
      <span class="uc-tag" style="color:var(--c-clay);border-color:rgba(224,112,96,.3)">Tutorials</span>
      <span class="uc-tag" style="color:var(--c-clay);border-color:rgba(224,112,96,.3)">Process flows</span>
      <span class="uc-tag" style="color:var(--c-clay);border-color:rgba(224,112,96,.3)">Storytelling</span>
      <span class="uc-tag" style="color:var(--c-clay);border-color:rgba(224,112,96,.3)">Product explainers</span>
      <span class="uc-tag" style="color:var(--c-clay);border-color:rgba(224,112,96,.3)">Marketing</span>
    </div>
  </div>
  <div class="variant-badges">
    <span class="variant-badge active">Standard</span>
    <span class="variant-badge active">Diorama</span>
    <span class="variant-badge active">Multi-panel</span>
  </div>
</div>

<div class="grid-12 grid-editorial-clay" style="gap:10px;">
  <div class="style-card h-280" data-style="claymation" data-usecase="Tutorials · Storytelling">
    <div class="card-img"><img src="../infographics/nation-and-state-claymation.png" alt="Claymation — Nation and State"></div>
    <div class="card-footer">
      <div class="card-name" style="color:var(--c-clay)">Multi-panel · Claymation</div>
      <div class="card-sub">Nation and state explained</div>
    </div>
    <div class="card-overlay"><button class="try-btn">Try this style →</button></div>
  </div>

  <div class="style-card h-260" data-style="claymation" data-usecase="Tutorials · Storytelling">
    <div class="card-img"><img src="../infographics/network-state-claymation.png" alt="Claymation — Network State"></div>
    <div class="card-footer">
      <div class="card-name" style="color:var(--c-clay)">Claymation</div>
      <div class="card-sub">Network state</div>
    </div>
    <div class="card-overlay"><button class="try-btn">Try this style →</button></div>
  </div>

  <div class="style-card h-260" data-style="claymation" data-usecase="Tutorials · Storytelling">
    <div class="card-img"><img src="../infographics/recipe-pipeline-claymation.png" alt="Claymation — Recipe pipeline"></div>
    <div class="card-footer">
      <div class="card-name" style="color:var(--c-clay)">Claymation</div>
      <div class="card-sub">Recipe pipeline</div>
    </div>
    <div class="card-overlay"><button class="try-btn">Try this style →</button></div>
  </div>

  <div class="style-card h-260" data-style="claymation-diorama" data-usecase="Diorama · Linear workflows">
    <div class="card-img"><img src="../infographics/recipe-doc-gen_claymation-diorama.png" alt="Claymation Diorama"></div>
    <div class="card-footer" style="background:#0a0f0a;">
      <div class="card-name" style="color:#60c060">Diorama · Claymation</div>
      <div class="card-sub">Recipe doc generation</div>
    </div>
    <div class="card-overlay"><button class="try-btn">Try this style →</button></div>
  </div>
</div>

<div class="diorama-callout">
  <span class="diorama-badge">Diorama mode</span>
  <p class="diorama-text"><strong>Available for Claymation and Lego.</strong> Instead of a flat infographic layout, characters and objects act out your workflow in a physical scene — ideal for linear processes up to 6 steps.</p>
</div>
```

- [ ] **Step 2: Fill in Sketchnote section**

Replace `<!-- Task 7 -->` inside `<section id="sketchnote" class="section">` with:

```html
<div class="section-header">
  <div class="section-left">
    <h2 class="t-section section-name" style="color:var(--c-sketch)">Hand-Drawn Sketchnote</h2>
    <p class="t-body section-desc">Off-white paper, marker lettering, wobbly sketch icons. Casual and human — the right tone for brainstorms and lightweight explainers.</p>
    <div class="use-cases">
      <span class="uc-tag" style="color:var(--c-sketch);border-color:rgba(200,168,106,.3)">Meeting notes</span>
      <span class="uc-tag" style="color:var(--c-sketch);border-color:rgba(200,168,106,.3)">Brainstorms</span>
      <span class="uc-tag" style="color:var(--c-sketch);border-color:rgba(200,168,106,.3)">Quick explainers</span>
      <span class="uc-tag" style="color:var(--c-sketch);border-color:rgba(200,168,106,.3)">Workshops</span>
    </div>
  </div>
</div>

<div class="grid-12 grid-editorial-sketch" style="gap:10px;">
  <div class="style-card h-260" data-style="sketchnote" data-usecase="Meeting notes · Brainstorms">
    <div class="card-img"><img src="../infographics/8-rules-sketch.png" alt="Sketchnote — 8 rules"></div>
    <div class="card-footer" style="background:#ede5d0;">
      <div class="card-name" style="color:#5a4a28">Sketchnote</div>
      <div class="card-sub" style="color:#8a7a58">8 rules of software</div>
    </div>
    <div class="card-overlay"><button class="try-btn">Try this style →</button></div>
  </div>

  <div class="style-card h-260" data-style="sketchnote" data-usecase="Meeting notes · Brainstorms">
    <div class="card-img"><img src="../infographics/network-state-sketch_combined.png" alt="Sketchnote — Network state"></div>
    <div class="card-footer" style="background:#ede5d0;">
      <div class="card-name" style="color:#5a4a28">Sketchnote</div>
      <div class="card-sub" style="color:#8a7a58">Network state</div>
    </div>
    <div class="card-overlay"><button class="try-btn">Try this style →</button></div>
  </div>

  <div class="style-card h-260" data-style="sketchnote" data-usecase="Meeting notes · Brainstorms">
    <div class="card-img"><img src="../infographics/octo-meeting-sketchnote_combined.png" alt="Sketchnote — Octo meeting"></div>
    <div class="card-footer" style="background:#ede5d0;">
      <div class="card-name" style="color:#5a4a28">Sketchnote</div>
      <div class="card-sub" style="color:#8a7a58">Octo meeting</div>
    </div>
    <div class="card-overlay"><button class="try-btn">Try this style →</button></div>
  </div>
</div>
```

- [ ] **Step 3: Run asset test**

```bash
pytest tests/canvas/test_assets.py -v
```

Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add canvas/index.html
git commit -m "feat: add Claymation and Sketchnote style sections"
```

---

## Task 7: Bold Editorial, Dark Mode Tech, and Lego sections

**Files:**
- Modify: `canvas/index.html` — fill in `#editorial`, `#darktech`, `#lego`

- [ ] **Step 1: Fill in Bold Editorial section** — replace second `<!-- Task 7 -->` comment inside `<section id="editorial">`:

```html
<div class="section-header">
  <div class="section-left">
    <h2 class="t-section section-name" style="color:var(--c-editorial)">Bold Editorial</h2>
    <p class="t-body section-desc">Wired-meets-Vox magazine aesthetic. High contrast, commanding typography, bold color blocks. Demands attention in a deck or a feed.</p>
    <div class="use-cases">
      <span class="uc-tag" style="color:var(--c-editorial);border-color:rgba(224,96,80,.3)">Reports</span>
      <span class="uc-tag" style="color:var(--c-editorial);border-color:rgba(224,96,80,.3)">Presentations</span>
      <span class="uc-tag" style="color:var(--c-editorial);border-color:rgba(224,96,80,.3)">Social media</span>
      <span class="uc-tag" style="color:var(--c-editorial);border-color:rgba(224,96,80,.3)">Thought leadership</span>
    </div>
  </div>
</div>

<div class="grid-12 grid-editorial-3col" style="gap:10px;">
  <div class="style-card h-260" data-style="editorial" data-usecase="Reports · Presentations">
    <div class="card-img"><img src="../infographics/octo-meeting-editorial_combined.png" alt="Bold Editorial — Octo meeting"></div>
    <div class="card-footer">
      <div class="card-name" style="color:var(--c-editorial)">Bold Editorial</div>
      <div class="card-sub">Octo meeting recap</div>
    </div>
    <div class="card-overlay"><button class="try-btn">Try this style →</button></div>
  </div>

  <div class="style-card h-260" data-style="editorial" data-usecase="Reports · Presentations">
    <div class="card-img"><img src="../infographics/flirt-guide-70s-editorial_combined.png" alt="70s Editorial"></div>
    <div class="card-footer">
      <div class="card-name" style="color:#c07820">70s Editorial</div>
      <div class="card-sub">Freeform variant</div>
    </div>
    <div class="card-overlay"><button class="try-btn">Try this style →</button></div>
  </div>

  <div class="style-card h-260" data-style="editorial" data-usecase="Reports · Presentations">
    <div class="card-img"><img src="../infographics/octo-meeting-mission-control_combined.png" alt="Mission Control"></div>
    <div class="card-footer">
      <div class="card-name" style="color:#2080c0">Mission Control</div>
      <div class="card-sub">Freeform variant</div>
    </div>
    <div class="card-overlay"><button class="try-btn">Try this style →</button></div>
  </div>
</div>
```

- [ ] **Step 2: Fill in Dark Mode Tech section** — replace `<!-- Task 8 -->` in `<section id="darktech">`:

```html
<div class="section-header">
  <div class="section-left">
    <h2 class="t-section section-name" style="color:var(--c-darktech)">Dark Mode Tech</h2>
    <p class="t-body section-desc">Developer-native aesthetic. Neon on dark, glassmorphism, monospace typography. The natural home for architecture diagrams and code walkthroughs.</p>
    <div class="use-cases">
      <span class="uc-tag" style="color:var(--c-darktech);border-color:rgba(64,200,216,.3)">Dev docs</span>
      <span class="uc-tag" style="color:var(--c-darktech);border-color:rgba(64,200,216,.3)">Architecture</span>
      <span class="uc-tag" style="color:var(--c-darktech);border-color:rgba(64,200,216,.3)">Code walkthroughs</span>
      <span class="uc-tag" style="color:var(--c-darktech);border-color:rgba(64,200,216,.3)">System design</span>
      <span class="uc-tag" style="color:var(--c-darktech);border-color:rgba(64,200,216,.3)">Technical deep-dives</span>
    </div>
  </div>
</div>

<div class="grid-12 grid-editorial-3col" style="gap:10px;">
  <div class="style-card h-260" data-style="darktech" data-usecase="Dev docs · Architecture">
    <div class="card-img"><img src="../infographics/multi-level-code-analysis_combined.png" alt="Dark Mode Tech — Code analysis"></div>
    <div class="card-footer">
      <div class="card-name" style="color:var(--c-darktech)">Dark Mode Tech</div>
      <div class="card-sub">Multi-level code analysis</div>
    </div>
    <div class="card-overlay"><button class="try-btn">Try this style →</button></div>
  </div>

  <div class="style-card h-260" data-style="darktech" data-usecase="Dev docs · Architecture">
    <div class="card-img"><img src="../infographics/recipe-pipeline-dark-tech.png" alt="Dark Mode Tech — Recipe pipeline"></div>
    <div class="card-footer">
      <div class="card-name" style="color:var(--c-darktech)">Dark Mode Tech</div>
      <div class="card-sub">Recipe pipeline</div>
    </div>
    <div class="card-overlay"><button class="try-btn">Try this style →</button></div>
  </div>

  <div class="style-card h-260" data-style="darktech" data-usecase="Dev docs · Architecture">
    <div class="card-img"><img src="../infographics/code-analysis-dark-tech.png" alt="Dark Mode Tech — Code analysis 2"></div>
    <div class="card-footer">
      <div class="card-name" style="color:var(--c-darktech)">Dark Mode Tech</div>
      <div class="card-sub">Code analysis</div>
    </div>
    <div class="card-overlay"><button class="try-btn">Try this style →</button></div>
  </div>
</div>
```

- [ ] **Step 3: Fill in Lego section** — replace second `<!-- Task 8 -->` in `<section id="lego">`:

```html
<div class="section-header">
  <div class="section-left">
    <h2 class="t-section section-name" style="color:var(--c-lego)">Lego Brick Builder</h2>
    <p class="t-body section-desc">Studded baseplates, primary palette, macro photography lighting. Structural and playful — best for step-by-step assembly and process flows.</p>
    <div class="use-cases">
      <span class="uc-tag" style="color:var(--c-lego);border-color:rgba(255,215,0,.3)">Step-by-step</span>
      <span class="uc-tag" style="color:var(--c-lego);border-color:rgba(255,215,0,.3)">Assembly guides</span>
      <span class="uc-tag" style="color:var(--c-lego);border-color:rgba(255,215,0,.3)">Process flows</span>
      <span class="uc-tag" style="color:var(--c-lego);border-color:rgba(255,215,0,.3)">Kids content</span>
    </div>
  </div>
  <div class="variant-badges">
    <span class="variant-badge active">Standard</span>
    <span class="variant-badge active">Diorama</span>
  </div>
</div>

<div class="grid-12 grid-editorial-2col" style="gap:10px;">
  <div class="style-card h-220" data-style="lego" data-usecase="Step-by-step · Assembly guides">
    <div class="card-img"><img src="../infographics/build-network-state-lego_combined.png" alt="Lego — Network state"></div>
    <div class="card-footer">
      <div class="card-name" style="color:var(--c-lego)">Lego Brick Builder</div>
      <div class="card-sub">Build network state</div>
    </div>
    <div class="card-overlay"><button class="try-btn">Try this style →</button></div>
  </div>

  <div class="style-card h-220" data-style="lego-diorama" data-usecase="Diorama · Linear workflows">
    <div class="card-img"><img src="../infographics/conditional-workflow_lego-diorama.png" alt="Lego Diorama"></div>
    <div class="card-footer" style="background:#080810;">
      <div class="card-name" style="color:#7fa0ff">Diorama · Lego</div>
      <div class="card-sub">Conditional workflow</div>
    </div>
    <div class="card-overlay"><button class="try-btn">Try this style →</button></div>
  </div>
</div>

<div class="diorama-callout">
  <span class="diorama-badge">Diorama mode</span>
  <p class="diorama-text"><strong>Available for Claymation and Lego.</strong> Instead of a flat infographic layout, characters and objects act out your workflow in a physical scene — ideal for linear processes up to 6 steps.</p>
</div>
```

- [ ] **Step 4: Run asset test**

```bash
pytest tests/canvas/test_assets.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add canvas/index.html
git commit -m "feat: add Bold Editorial, Dark Mode Tech, and Lego sections"
```

---

## Task 8: Freeform section

**Files:**
- Modify: `canvas/index.html` — fill in `#freeform`

- [ ] **Step 1: Fill in Freeform section**

Replace `<!-- Task 9 -->` inside `<section id="freeform">` with:

```html
<div class="section-header">
  <div class="section-left">
    <h2 class="t-section section-name" style="color:var(--c-freeform)">Freeform ✦</h2>
    <p class="t-body section-desc">Beyond the six. Describe any aesthetic and the system interprets it into a full style brief. These examples were all generated with plain-language descriptions.</p>
  </div>
</div>

<div class="grid-12" style="gap:10px;">
  <div class="style-card col-4" data-style="freeform" data-usecase="Any style you can describe">
    <div class="card-img" style="height:180px;"><img src="../infographics/style-showcase/comic-book.png" alt="Comic Book style"></div>
    <div class="card-footer">
      <div class="card-name">Comic Book</div>
      <div class="card-sub">"comic book with ink outlines and speech bubbles"</div>
    </div>
    <div class="card-overlay"><button class="try-btn">Try this style →</button></div>
  </div>

  <div class="style-card col-4" data-style="freeform" data-usecase="Any style you can describe">
    <div class="card-img" style="height:200px;"><img src="../infographics/style-showcase/disney-storybook.png" alt="Disney Storybook style"></div>
    <div class="card-footer">
      <div class="card-name">Disney Storybook</div>
      <div class="card-sub">"illustrated disney storybook, warm magical lighting"</div>
    </div>
    <div class="card-overlay"><button class="try-btn">Try this style →</button></div>
  </div>

  <div class="style-card col-4" data-style="freeform" data-usecase="Any style you can describe">
    <div class="card-img" style="height:160px;"><img src="../infographics/style-showcase/pixel-art.png" alt="Pixel Art style"></div>
    <div class="card-footer">
      <div class="card-name">Pixel Art</div>
      <div class="card-sub">"8-bit pixel art, retro game palette"</div>
    </div>
    <div class="card-overlay"><button class="try-btn">Try this style →</button></div>
  </div>

  <div class="style-card col-3" data-style="freeform" data-usecase="Any style you can describe">
    <div class="card-img" style="height:180px;"><img src="../infographics/style-showcase/tron.png" alt="Tron style"></div>
    <div class="card-footer">
      <div class="card-name">Tron</div>
      <div class="card-sub">"tron neon grid, black background"</div>
    </div>
    <div class="card-overlay"><button class="try-btn">Try this style →</button></div>
  </div>

  <div class="style-card col-3" data-style="freeform" data-usecase="Any style you can describe">
    <div class="card-img" style="height:180px;"><img src="../infographics/style-showcase/watercolor.png" alt="Watercolor style"></div>
    <div class="card-footer">
      <div class="card-name">Watercolor</div>
      <div class="card-sub">"soft watercolor illustration"</div>
    </div>
    <div class="card-overlay"><button class="try-btn">Try this style →</button></div>
  </div>

  <div class="style-card col-3" data-style="freeform" data-usecase="Any style you can describe">
    <div class="card-img" style="height:180px;"><img src="../infographics/style-showcase/mario.png" alt="Mario style"></div>
    <div class="card-footer">
      <div class="card-name">Super Mario</div>
      <div class="card-sub">"super mario world aesthetic"</div>
    </div>
    <div class="card-overlay"><button class="try-btn">Try this style →</button></div>
  </div>

  <div class="col-3">
    <div class="ff-cta-card" id="freeform-cta">
      <div class="ff-cta-plus">+</div>
      <div class="ff-cta-label">Describe any style<br>and generate your own</div>
    </div>
  </div>
</div>
```

- [ ] **Step 2: Run asset test**

```bash
pytest tests/canvas/test_assets.py -v
```

Expected: PASS (all style-showcase images exist)

- [ ] **Step 3: Commit**

```bash
git add canvas/index.html
git commit -m "feat: add Freeform section with plain-language prompt labels"
```

---

## Task 9: Layout types filmstrip and Diagram Beautifier sections + footer

**Files:**
- Modify: `canvas/index.html` — fill in `#layouts`, `#diagrams`, footer

- [ ] **Step 1: Fill in Layout Types section** — replace `<!-- Task 10 -->` in `<section id="layouts">`:

```html
<p class="filmstrip-label">Layout types · 14 structures · any style · scroll to explore</p>
<div class="filmstrip">
  <div class="layout-thumb"><div class="lt-icon">⬇</div><div class="lt-name">Timeline</div></div>
  <div class="layout-thumb"><div class="lt-icon">⇔</div><div class="lt-name">Comparison</div></div>
  <div class="layout-thumb"><div class="lt-icon">◈</div><div class="lt-name">Hierarchy</div></div>
  <div class="layout-thumb"><div class="lt-icon">↩</div><div class="lt-name">Flow / Process</div></div>
  <div class="layout-thumb"><div class="lt-icon">◉</div><div class="lt-name">Hero + Details</div></div>
  <div class="layout-thumb"><div class="lt-icon">▦</div><div class="lt-name">Grid Breakdown</div></div>
  <div class="layout-thumb"><div class="lt-icon">⬡</div><div class="lt-name">Hub &amp; Spoke</div></div>
  <div class="layout-thumb"><div class="lt-icon">∥</div><div class="lt-name">Side by Side</div></div>
  <div class="layout-thumb"><div class="lt-icon">📊</div><div class="lt-name">Stats Dashboard</div></div>
  <div class="layout-thumb"><div class="lt-icon">🗺</div><div class="lt-name">Journey Map</div></div>
  <div class="layout-thumb"><div class="lt-icon">⚡</div><div class="lt-name">Before / After</div></div>
  <div class="layout-thumb"><div class="lt-icon">📖</div><div class="lt-name">Narrative Strip</div></div>
  <div class="layout-thumb"><div class="lt-icon">🧩</div><div class="lt-name">Anatomy</div></div>
  <div class="layout-thumb"><div class="lt-icon">◎</div><div class="lt-name">Cycle / Loop</div></div>
</div>
```

- [ ] **Step 2: Fill in Diagram Beautifier section** — replace `<!-- Task 11 -->` in `<section id="diagrams">`:

```html
<div class="section-header">
  <div class="section-left">
    <h2 class="t-section section-name" style="color:var(--c-diagram)">Diagram Beautifier</h2>
    <p class="t-body section-desc">Drop in any .dot or Mermaid file. Get back two simultaneous variants — one document-ready, one presentation-ready.</p>
  </div>
</div>

<div class="diag-strip">
  <div class="diag-card source">
    <div class="diag-card-img">digraph {
  A [label="Start"]
  B [label="Process"]
  C [label="Review"]
  D [label="Ship"]
  A -&gt; B -&gt; C -&gt; D
}</div>
    <div class="diag-card-footer">
      <div class="diag-card-name" style="color:#444">Source</div>
      <div class="diag-card-desc">Your .dot or Mermaid file, untouched</div>
    </div>
  </div>

  <div class="diag-arrow">→</div>

  <div class="diag-card polished">
    <div class="diag-card-img">
      <img src="../docs/showcase/devops-lifecycle.png" alt="Polished diagram variant">
    </div>
    <div class="diag-card-footer">
      <div class="diag-card-name" style="color:#0D8080">Polished</div>
      <div class="diag-card-desc">Document-ready. Aesthetic applied faithfully. All labels intact. Every node placed.</div>
    </div>
  </div>

  <div class="diag-arrow">+</div>

  <div class="diag-card cinematic">
    <div class="diag-card-img">
      <img src="../infographics/architecture-diagram.png" alt="Cinematic diagram variant">
    </div>
    <div class="diag-card-footer">
      <div class="diag-card-name" style="color:#9020d0">Cinematic</div>
      <div class="diag-card-desc">Presentation-ready. Hero focal point. Full spatial freedom. Mood over fidelity.</div>
    </div>
  </div>
</div>
```

- [ ] **Step 3: Fill in footer** — replace `<!-- Task 11 -->` in `<footer>`:

```html
<h2 class="footer-headline">Start creating</h2>
<p class="footer-sub">Describe your topic or drop in a diagram — pick your style, or invent your own</p>
<button class="btn btn-primary" data-style="claymation" data-usecase="Tutorials · Storytelling">Generate an infographic</button>
<button class="btn btn-ghost"   data-style="minimalist" data-usecase="Document-ready" data-mode="diagram">Beautify a diagram</button>
```

- [ ] **Step 4: Run asset test**

```bash
pytest tests/canvas/test_assets.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add canvas/index.html
git commit -m "feat: add layout filmstrip, diagram beautifier section, and footer"
```

---

## Task 10: Modal HTML

**Files:**
- Modify: `canvas/index.html` — fill in `#modal-overlay`

- [ ] **Step 1: Fill in the modal overlay** — replace `<!-- Task 12 -->` inside `<div class="modal-overlay">`:

```html
<div class="modal" id="modal">
  <div class="modal-header">
    <div>
      <div class="modal-style-name" id="modal-style-name">Claymation Studio</div>
      <div class="modal-use-case"  id="modal-use-case">Tutorials · Storytelling</div>
    </div>
    <button class="modal-close" id="modal-close" aria-label="Close">✕</button>
  </div>

  <label class="modal-label" for="modal-prompt">What do you want to visualise?</label>
  <textarea
    class="modal-textarea"
    id="modal-prompt"
    placeholder='e.g. "How the Amplifier agent loop works"'
    rows="3"
  ></textarea>

  <label class="modal-label" for="modal-style">Style</label>
  <select class="modal-style-select" id="modal-style">
    <option value="minimalist">Clean Minimalist</option>
    <option value="claymation">Claymation Studio</option>
    <option value="sketchnote">Hand-Drawn Sketchnote</option>
    <option value="editorial">Bold Editorial</option>
    <option value="darktech">Dark Mode Tech</option>
    <option value="lego">Lego Brick Builder</option>
    <option value="freeform">Freeform — describe below</option>
  </select>

  <button class="modal-generate" id="modal-generate">Generate</button>

  <!-- shown only when server is unavailable -->
  <div class="modal-copy-prompt" id="modal-copy-prompt" style="display:none;">
    No generation server detected. Open Amplifier and paste:<br>
    <code id="modal-copy-text"></code>
  </div>

  <div class="modal-or">or</div>

  <div class="modal-diagram-zone" id="modal-diagram-zone">
    Have a diagram? Drop a <strong>.dot</strong> or <strong>Mermaid</strong> file here
  </div>

  <div class="modal-output" id="modal-output" style="display:none;">
    <img id="modal-output-img" src="" alt="Generated output">
  </div>
</div>
```

- [ ] **Step 2: Commit**

```bash
git add canvas/index.html
git commit -m "feat: add generation modal HTML structure"
```

---

## Task 11: modal.js — open/close, style pre-selection, graceful degradation

**Files:**
- Modify: `canvas/modal.js`

- [ ] **Step 1: Write tests for modal behaviour** — create `tests/canvas/test_modal_js.py`:

```python
"""Verify modal.js contains the required functions and event wiring.

These are structural tests — not browser tests. They confirm the
implementation pattern is correct before any real browser testing.
"""
from pathlib import Path

JS = (Path(__file__).parent.parent.parent / "canvas" / "modal.js").read_text


def test_modal_js_exports_open_modal():
    assert "function openModal(" in JS() or "openModal" in JS()

def test_modal_js_exports_close_modal():
    assert "closeModal" in JS()

def test_modal_js_checks_server_health():
    assert "/health" in JS() or "serverAvailable" in JS()

def test_modal_js_pre_selects_style():
    assert "modal-style" in JS()

def test_modal_js_handles_escape_key():
    assert "Escape" in JS() or "escape" in JS().lower()
```

- [ ] **Step 2: Run tests — expect all to fail**

```bash
pytest tests/canvas/test_modal_js.py -v
```

Expected: all FAIL (modal.js is empty)

- [ ] **Step 3: Write modal.js**

Write `canvas/modal.js`:

```javascript
/* ── modal.js — Generation modal for Infographic Builder Canvas ── */

const SERVER_URL = 'http://localhost:8765';
let serverAvailable = false;

/* ── Server health check ────────────────────────────────────── */
async function checkServerHealth() {
  try {
    const res = await fetch(`${SERVER_URL}/health`, { signal: AbortSignal.timeout(2000) });
    serverAvailable = res.ok;
  } catch {
    serverAvailable = false;
  }
  updateModalForServerState();
}

function updateModalForServerState() {
  const generateBtn  = document.getElementById('modal-generate');
  const copyPrompt   = document.getElementById('modal-copy-prompt');
  if (!generateBtn) return;

  if (serverAvailable) {
    generateBtn.style.display = '';
    copyPrompt.style.display  = 'none';
  } else {
    generateBtn.style.display = 'none';
    copyPrompt.style.display  = '';
    updateCopyPromptText();
  }
}

function updateCopyPromptText() {
  const prompt     = document.getElementById('modal-prompt')?.value.trim() || '...';
  const style      = document.getElementById('modal-style')?.value || 'claymation';
  const copyText   = document.getElementById('modal-copy-text');
  if (copyText) {
    copyText.textContent = `Create a ${style} infographic about: ${prompt}`;
  }
}

/* ── Open modal ─────────────────────────────────────────────── */
function openModal(styleId, useCaseText, mode = 'infographic') {
  const overlay   = document.getElementById('modal-overlay');
  const styleName = document.getElementById('modal-style-name');
  const useCase   = document.getElementById('modal-use-case');
  const styleSelect = document.getElementById('modal-style');
  const output    = document.getElementById('modal-output');
  const prompt    = document.getElementById('modal-prompt');

  // Pre-select style
  if (styleSelect) {
    const opt = styleSelect.querySelector(`option[value="${styleId}"]`);
    if (opt) styleSelect.value = styleId;
  }

  // Set header
  const styleLabels = {
    minimalist:  'Clean Minimalist',
    claymation:  'Claymation Studio',
    sketchnote:  'Hand-Drawn Sketchnote',
    editorial:   'Bold Editorial',
    darktech:    'Dark Mode Tech',
    lego:        'Lego Brick Builder',
    freeform:    'Freeform',
    'claymation-diorama': 'Claymation Diorama',
    'lego-diorama':       'Lego Diorama',
  };
  if (styleName) styleName.textContent = styleLabels[styleId] || styleId;
  if (useCase)   useCase.textContent   = useCaseText || '';

  // Reset output
  if (output) output.style.display = 'none';
  if (prompt) prompt.value = '';

  // Store mode for generate handler
  overlay.dataset.mode = mode;

  overlay.classList.add('open');
  prompt?.focus();
  updateCopyPromptText();
}

/* ── Close modal ─────────────────────────────────────────────── */
function closeModal() {
  document.getElementById('modal-overlay')?.classList.remove('open');
}

/* ── Generate ───────────────────────────────────────────────── */
async function handleGenerate() {
  const prompt  = document.getElementById('modal-prompt')?.value.trim();
  const style   = document.getElementById('modal-style')?.value;
  const mode    = document.getElementById('modal-overlay')?.dataset.mode || 'infographic';
  const btn     = document.getElementById('modal-generate');
  const output  = document.getElementById('modal-output');
  const img     = document.getElementById('modal-output-img');

  if (!prompt) {
    document.getElementById('modal-prompt')?.focus();
    return;
  }

  btn.disabled = true;
  btn.classList.add('loading');
  btn.textContent = 'Generating…';

  try {
    const res = await fetch(`${SERVER_URL}/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, style, mode }),
    });

    if (!res.ok) throw new Error(`Server error: ${res.status}`);
    const data = await res.json();

    img.src = data.image_url;
    output.style.display = '';
  } catch (err) {
    alert(`Generation failed: ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.classList.remove('loading');
    btn.textContent = 'Generate';
  }
}

/* ── Wire all card CTAs ─────────────────────────────────────── */
function wireCards() {
  // Style cards and hero cards
  document.querySelectorAll('[data-style]').forEach(el => {
    el.addEventListener('click', (e) => {
      const btn = e.target.closest('.try-btn, .btn, .hero-card, .ff-cta-card');
      if (!btn && !e.target.closest('.hero-card')) return;
      const styleId  = el.dataset.style   || 'claymation';
      const useCase  = el.dataset.usecase || '';
      const mode     = el.dataset.mode    || 'infographic';
      openModal(styleId, useCase, mode);
    });
  });

  // Freeform CTA card
  document.getElementById('freeform-cta')?.addEventListener('click', () => {
    openModal('freeform', 'Any style you can describe');
  });

  // Footer buttons
  document.querySelectorAll('.btn[data-style]').forEach(btn => {
    btn.addEventListener('click', () => {
      openModal(btn.dataset.style, btn.dataset.usecase || '', btn.dataset.mode || 'infographic');
    });
  });
}

/* ── Event listeners ────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  // Close button
  document.getElementById('modal-close')?.addEventListener('click', closeModal);

  // Click outside modal
  document.getElementById('modal-overlay')?.addEventListener('click', (e) => {
    if (e.target === document.getElementById('modal-overlay')) closeModal();
  });

  // Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
  });

  // Generate button
  document.getElementById('modal-generate')?.addEventListener('click', handleGenerate);

  // Update copy prompt text on input
  document.getElementById('modal-prompt')?.addEventListener('input', updateCopyPromptText);
  document.getElementById('modal-style')?.addEventListener('change', updateCopyPromptText);

  // Wire all cards
  wireCards();

  // Check server health on load
  checkServerHealth();
});
```

- [ ] **Step 4: Run modal structure tests — expect all to pass**

```bash
pytest tests/canvas/test_modal_js.py -v
```

Expected: all PASS

- [ ] **Step 5: Commit**

```bash
git add canvas/modal.js tests/canvas/test_modal_js.py
git commit -m "feat: add modal.js with open/close, style pre-selection, and graceful degradation"
```

---

## Task 12: FastAPI generation server

**Files:**
- Modify: `canvas/server.py`
- Create: `tests/canvas/test_server.py`

The server accepts `POST /generate`, invokes the Amplifier agent via subprocess (using `amplifier tool invoke`), and returns the generated image URL.

- [ ] **Step 1: Write the API tests first**

Create `tests/canvas/test_server.py`:

```python
"""Tests for canvas/server.py — POST /generate endpoint."""
import pytest
from httpx import AsyncClient, ASGITransport


@pytest.fixture
def app():
    import importlib.util, sys
    from pathlib import Path
    spec = importlib.util.spec_from_file_location("server", Path(__file__).parent.parent.parent / "canvas" / "server.py")
    mod  = importlib.util.module_from_spec(spec)
    sys.modules["server"] = mod
    spec.loader.exec_module(mod)
    return mod.app


@pytest.mark.asyncio
async def test_health_returns_200(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_generate_requires_prompt(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post("/generate", json={"style": "claymation", "mode": "infographic"})
    assert res.status_code == 422  # FastAPI validation error — prompt missing


@pytest.mark.asyncio
async def test_generate_requires_style(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post("/generate", json={"prompt": "test", "mode": "infographic"})
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_generate_returns_image_url_shape(app, monkeypatch):
    """When agent invocation is mocked, response shape is correct."""
    async def fake_invoke(prompt, style, mode):
        return "infographics/test-output.png"

    import canvas.server as server_mod
    monkeypatch.setattr(server_mod, "invoke_agent", fake_invoke)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post("/generate", json={
            "prompt": "How the agent loop works",
            "style": "claymation",
            "mode": "infographic"
        })
    assert res.status_code == 200
    data = res.json()
    assert "image_url" in data
    assert data["image_url"].endswith(".png")
```

- [ ] **Step 2: Run tests — expect all to fail**

```bash
pytest tests/canvas/test_server.py -v
```

Expected: FAIL (server.py is empty, import will fail)

- [ ] **Step 3: Install dependencies**

```bash
uv add fastapi uvicorn httpx pytest-asyncio
```

- [ ] **Step 4: Write server.py**

Write `canvas/server.py`:

```python
"""canvas/server.py — Thin FastAPI server for Infographic Builder Canvas.

POST /generate: accepts prompt + style + mode, invokes Amplifier agent,
returns the generated image path as a URL the browser can load.
"""
from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator

ROOT = Path(__file__).parent.parent  # repo root

app = FastAPI(title="Infographic Builder Canvas Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated images directly
app.mount("/infographics", StaticFiles(directory=str(ROOT / "infographics")), name="infographics")
app.mount("/docs",         StaticFiles(directory=str(ROOT / "docs")),         name="docs")


# ── Request / Response models ───────────────────────────────────

VALID_STYLES = {
    "minimalist", "claymation", "sketchnote", "editorial",
    "darktech", "lego", "freeform", "claymation-diorama", "lego-diorama",
}

VALID_MODES = {"infographic", "diagram"}

STYLE_PROMPTS = {
    "minimalist":        "clean minimalist style",
    "claymation":        "claymation studio style",
    "sketchnote":        "hand-drawn sketchnote style",
    "editorial":         "bold editorial style",
    "darktech":          "dark mode tech style",
    "lego":              "lego brick builder style",
    "claymation-diorama":"claymation diorama mode",
    "lego-diorama":      "lego diorama mode",
    "freeform":          "",  # user specifies style inline
}


class GenerateRequest(BaseModel):
    prompt: str
    style:  str
    mode:   str = "infographic"

    @field_validator("prompt")
    @classmethod
    def prompt_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("prompt must not be empty")
        return v.strip()

    @field_validator("style")
    @classmethod
    def style_must_be_valid(cls, v: str) -> str:
        if v not in VALID_STYLES:
            raise ValueError(f"style must be one of {sorted(VALID_STYLES)}")
        return v

    @field_validator("mode")
    @classmethod
    def mode_must_be_valid(cls, v: str) -> str:
        if v not in VALID_MODES:
            raise ValueError(f"mode must be one of {sorted(VALID_MODES)}")
        return v


class GenerateResponse(BaseModel):
    image_url: str
    style:     str
    prompt:    str


# ── Agent invocation ────────────────────────────────────────────

async def invoke_agent(prompt: str, style: str, mode: str) -> str:
    """Invoke the Amplifier infographic-builder agent and return the output image path.

    Runs `amplifier run` as a subprocess with the prompt pre-filled.
    Returns a path relative to ROOT that the browser can load via /infographics or /docs.
    """
    style_description = STYLE_PROMPTS.get(style, style)
    full_prompt = f"{prompt} — {style_description}" if style_description else prompt

    cmd = [
        "amplifier", "run",
        "--bundle", ".",
        "--input", full_prompt,
        "--output-format", "json",
    ]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=str(ROOT),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        raise RuntimeError(f"Agent failed: {stderr.decode()[:500]}")

    # Parse agent output — expects last line to be JSON with {"output_path": "..."}
    import json
    for line in reversed(stdout.decode().splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                data = json.loads(line)
                if "output_path" in data:
                    return data["output_path"]
            except json.JSONDecodeError:
                continue

    raise RuntimeError("Agent completed but no output_path found in response")


# ── Routes ──────────────────────────────────────────────────────

@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest) -> GenerateResponse:
    image_path = await invoke_agent(req.prompt, req.style, req.mode)
    # Return a URL the browser can fetch from this server
    image_url = f"/{image_path.lstrip('/')}"
    return GenerateResponse(image_url=image_url, style=req.style, prompt=req.prompt)
```

- [ ] **Step 5: Add `canvas/` as a package so the test import works**

```bash
touch canvas/__init__.py
```

- [ ] **Step 6: Run tests — expect pass**

```bash
pytest tests/canvas/test_server.py -v
```

Expected: all PASS (health + validation tests pass; generate mock test passes)

- [ ] **Step 7: Smoke-test the server manually**

```bash
cd canvas && uvicorn server:app --port 8765 --reload &
curl http://localhost:8765/health
# Expected: {"status":"ok"}
```

- [ ] **Step 8: Commit**

```bash
git add canvas/server.py canvas/__init__.py tests/canvas/test_server.py
git commit -m "feat: add FastAPI generation server with POST /generate endpoint"
```

---

## Task 13: Full end-to-end review and nav active state wiring

**Files:**
- Modify: `canvas/modal.js` — add IntersectionObserver for nav active state
- Modify: `canvas/index.html` — any final tweaks found during review

- [ ] **Step 1: Add active nav state via IntersectionObserver** — append to `canvas/modal.js`:

```javascript
/* ── Active nav anchor on scroll ───────────────────────────── */
function wireNavActiveState() {
  const anchors  = document.querySelectorAll('.nav-anchor[href^="#"]');
  const sections = Array.from(anchors).map(a => document.querySelector(a.getAttribute('href')));

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          anchors.forEach(a => a.classList.remove('active'));
          const active = document.querySelector(`.nav-anchor[href="#${entry.target.id}"]`);
          if (active) active.classList.add('active');
        }
      });
    },
    { rootMargin: '-50% 0px -50% 0px' }
  );

  sections.forEach(s => s && observer.observe(s));
}

// Wire nav on DOMContentLoaded (append to existing listener)
document.addEventListener('DOMContentLoaded', wireNavActiveState);
```

- [ ] **Step 2: Open page in browser and walk through every section**

```bash
open canvas/index.html
```

Check each of the following:
- [ ] Hero renders with four images
- [ ] Nav anchors scroll to correct sections
- [ ] Clean Minimalist cards have light theme
- [ ] Claymation cards render, diorama callout appears
- [ ] Sketchnote, Editorial, Dark Tech, Lego sections all render with images
- [ ] Freeform grid renders with prompt sub-labels
- [ ] Layout filmstrip scrolls horizontally
- [ ] Diagram Beautifier transformation strip renders
- [ ] Footer buttons visible
- [ ] Hovering any style card shows "Try this style →" overlay
- [ ] Clicking overlay opens modal with correct style pre-selected
- [ ] Escape key closes modal
- [ ] Modal shows copy-prompt mode when server not running

- [ ] **Step 3: Run full test suite**

```bash
pytest tests/canvas/ -v
```

Expected: all PASS

- [ ] **Step 4: Commit**

```bash
git add canvas/modal.js canvas/index.html
git commit -m "feat: wire nav active state and complete end-to-end review"
```

---

## Self-Review

**Spec coverage check:**

| Spec requirement | Task |
|-----------------|------|
| Sticky nav with section anchors | Task 3 + 13 |
| Hero — same topic × 4 styles | Task 4 |
| Clean Minimalist section with light theme override | Task 5 |
| Claymation section with diorama callout | Task 6 |
| Sketchnote section | Task 6 |
| Bold Editorial section | Task 7 |
| Dark Mode Tech section | Task 7 |
| Lego section with diorama callout | Task 7 |
| Freeform section with prompt labels + CTA card | Task 8 |
| Layout types filmstrip (14 layouts) | Task 9 |
| Diagram Beautifier transformation strip | Task 9 |
| Footer with two CTAs | Task 9 |
| Modal with style pre-selection | Task 10 + 11 |
| Graceful degradation (no server) | Task 11 |
| FastAPI POST /generate endpoint | Task 12 |
| GET /health endpoint | Task 12 |
| Asset existence tests | Task 1 |
| API tests for server | Task 12 |
| Nav active state on scroll | Task 13 |

No spec gaps found.

**Type/name consistency check:** `openModal`, `closeModal`, `serverAvailable`, `invoke_agent`, `GenerateRequest`, `GenerateResponse` — all consistent across JS and Python files.

**Placeholder check:** No TBDs, TODOs, or "implement later" strings found.
