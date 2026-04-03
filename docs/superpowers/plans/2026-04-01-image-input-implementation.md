# Image Input for Infographic Builder — Implementation Plan

> **Execution:** Use the subagent-driven-development workflow to implement this plan.

**Goal:** Add image input support to the infographic-builder so users can provide a PNG as a style reference or content source.

**Architecture:** A single `nano-banana analyze` call extracts three things from user-provided PNGs: diagram classification, content summary, and aesthetic description. The root session routes based on diagram classification (existing) and a new style-intent fork. The infographic-builder agent accepts enriched context and threads reference images through generation.

**Tech Stack:** Markdown agent definitions, pytest text assertions (no mocking, no runtime code)

**Design spec:** `docs/superpowers/specs/2026-04-01-image-input-infographic-builder-design.md` (Approved)

---

## Prerequisite: all existing tests pass

Before starting any task, confirm the baseline:

```bash
python3 -m pytest tests/test_diagram_routing.py tests/test_infographic_builder.py tests/test_style_consistency_brief.py tests/test_style_guide_aesthetics.py -v
```

Expected: **50 passed** in under 1 second. If anything fails, stop and fix it before proceeding.

---

### Task 1: Enrich the analyze prompt

**Files:**
- Modify: `context/infographic-awareness.md` (lines 62–68 — the analyze prompt)
- Test: `tests/test_diagram_routing.py` (append new tests)

**Step 1: Write the failing tests**

Open `tests/test_diagram_routing.py` and append these two tests at the bottom of the file:

```python


# ---------------------------------------------------------------------------
# Enriched analyze prompt: content_summary + aesthetic_description
# ---------------------------------------------------------------------------


def test_analyze_prompt_extracts_content_summary() -> None:
    """The enriched analyze prompt must instruct extraction of content_summary."""
    content = AWARENESS_FILE.read_text(encoding="utf-8")
    lower = content.lower()
    assert "content summary" in lower or "content_summary" in lower, (
        "Analyze prompt must mention content summary extraction.\n"
        f"File content:\n{content}"
    )


def test_analyze_prompt_extracts_aesthetic_description() -> None:
    """The enriched analyze prompt must instruct extraction of aesthetic_description."""
    content = AWARENESS_FILE.read_text(encoding="utf-8")
    lower = content.lower()
    assert "aesthetic description" in lower or "aesthetic_description" in lower, (
        "Analyze prompt must mention aesthetic description extraction.\n"
        f"File content:\n{content}"
    )
```

**Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_diagram_routing.py::test_analyze_prompt_extracts_content_summary tests/test_diagram_routing.py::test_analyze_prompt_extracts_aesthetic_description -v
```

Expected: **2 FAILED** — neither phrase exists in the file yet.

**Step 3: Update the analyze prompt**

In `context/infographic-awareness.md`, find this exact text:

```
1. Run `nano-banana analyze` on the PNG with this exact prompt:
   ```
   Is this image a structured diagram — such as a flowchart, architecture diagram,
   sequence diagram, network diagram, ER diagram, or process flow?
   Answer YES or NO. If YES: list all visible node/step labels and estimate the
   node count.
   ```
```

Replace the entire block (from `1. Run` through the closing `` ``` ``) with:

```
1. Run `nano-banana analyze` on the PNG with this exact prompt:
   ```
   Analyze this image and provide three things:

   1. DIAGRAM CLASSIFICATION: Is this image a structured diagram — such as a
      flowchart, architecture diagram, sequence diagram, network diagram, ER
      diagram, or process flow? Answer YES or NO. If YES: list all visible
      node/step labels and estimate the node count.

   2. CONTENT SUMMARY: What is this image about? Describe the subject matter,
      key elements, data, and concepts depicted.

   3. AESTHETIC DESCRIPTION: What does this image look like visually? Describe
      the color palette, typography character, mood, visual style, layout
      approach, and any distinctive design elements.
   ```
```

**Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_diagram_routing.py -v
```

Expected: **All passed** (14 existing + 2 new = 16 total).

**Step 5: Commit**

```bash
git add context/infographic-awareness.md tests/test_diagram_routing.py
git commit -m "feat: enrich analyze prompt with content_summary and aesthetic_description"
```

---

### Task 2: Style intent detection routing

**Files:**
- Modify: `context/infographic-awareness.md` (lines 70–74 — the routing decision)
- Test: `tests/test_diagram_routing.py` (append new tests)

**Step 1: Write the failing tests**

Open `tests/test_diagram_routing.py` and append these four tests at the bottom:

```python


# ---------------------------------------------------------------------------
# Style intent detection routing
# ---------------------------------------------------------------------------


def test_style_intent_detection_section_exists() -> None:
    """infographic-awareness.md must have a style intent detection section."""
    content = AWARENESS_FILE.read_text(encoding="utf-8")
    lower = content.lower()
    assert "style intent" in lower, (
        "Must contain a 'style intent' detection section"
    )


def test_style_intent_signals_listed() -> None:
    """The style intent section must list known style signal phrases."""
    content = AWARENESS_FILE.read_text(encoding="utf-8")
    lower = content.lower()
    assert "in the style of" in lower, "Must list 'in the style of' as a signal"
    assert "make it look like" in lower, "Must list 'make it look like' as a signal"


def test_no_style_signal_discards_aesthetic() -> None:
    """When no style signal is detected, aesthetic_description must be discarded."""
    content = AWARENESS_FILE.read_text(encoding="utf-8")
    lower = content.lower()
    assert "discard" in lower, (
        "Must describe discarding aesthetic_description when no style signal"
    )


def test_style_signal_passes_image_path() -> None:
    """When style signal detected, image_path must be passed to the agent."""
    content = AWARENESS_FILE.read_text(encoding="utf-8")
    assert "image_path" in content, (
        "Must mention passing image_path when style signal is detected"
    )
```

**Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_diagram_routing.py::test_style_intent_detection_section_exists tests/test_diagram_routing.py::test_style_intent_signals_listed tests/test_diagram_routing.py::test_no_style_signal_discards_aesthetic tests/test_diagram_routing.py::test_style_signal_passes_image_path -v
```

Expected: **4 FAILED** — none of this language exists yet.

**Step 3: Add style intent detection to the routing section**

In `context/infographic-awareness.md`, find this exact text:

```
   - Answer is **NO** → delegate to `infographic-builder:infographic-builder`

**This analyze step takes ~10 seconds
```

Replace it with:

```
   - Answer is **NO** → proceed to step 3 (style intent detection)

3. **Style intent detection** (only when routing to infographic-builder):

   Check the user's text prompt for explicit style intent signals:
   - "feels like this"
   - "in the style of"
   - "make it look like"
   - "matching this aesthetic"

   **If no style signal detected** (default): pass only `content_summary` to
   the infographic-builder. Discard `aesthetic_description` silently. Do NOT
   pass `image_path` to the agent.

   **If style signal detected**: pass `content_summary`, `aesthetic_description`,
   AND `image_path` to the infographic-builder.

**This analyze step takes ~10 seconds
```

**Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_diagram_routing.py -v
```

Expected: **All passed** (16 existing + 4 new = 20 total).

**Step 5: Commit**

```bash
git add context/infographic-awareness.md tests/test_diagram_routing.py
git commit -m "feat: add style intent detection routing for image input"
```

---

### Task 3: Step 1 — accept content_summary

**Files:**
- Modify: `agents/infographic-builder.md` (Step 1 only)
- Test: `tests/test_infographic_builder.py` (append new tests)

**Step 1: Write the failing tests**

Open `tests/test_infographic_builder.py` and append these tests at the bottom:

```python


# ---------------------------------------------------------------------------
# Task: Step 1 accepts content_summary from root session
# ---------------------------------------------------------------------------


def _get_step_1_block(content: str) -> str:
    """Extract text between '1. **Parse the request**' and '2. **'."""
    start = content.index("1. **Parse the request**")
    end = content.index("2. **", start)
    return content[start:end]


def test_step_1_accepts_content_summary():
    """Step 1 must mention accepting content_summary from root session."""
    block = _get_step_1_block(read_agent())
    lower = block.lower()
    assert "content_summary" in lower, (
        "Step 1 must describe accepting content_summary.\n"
        f"Actual block:\n{block}"
    )


def test_step_1_content_summary_becomes_subject_matter():
    """Step 1 must say content_summary becomes the subject matter."""
    block = _get_step_1_block(read_agent())
    lower = block.lower()
    assert "subject matter" in lower, (
        "Step 1 must say content_summary becomes the subject matter.\n"
        f"Actual block:\n{block}"
    )
```

**Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_infographic_builder.py::test_step_1_accepts_content_summary tests/test_infographic_builder.py::test_step_1_content_summary_becomes_subject_matter -v
```

Expected: **2 FAILED** — Step 1 currently says only "subject matter, data to include, tone, target medium" with no mention of `content_summary`.

**Step 3: Add content_summary instructions to Step 1**

In `agents/infographic-builder.md`, find this exact text:

```
1. **Parse the request**: subject matter, data to include, tone, target medium

2. **Analyze content density**
```

Replace it with:

```
1. **Parse the request**: subject matter, data to include, tone, target medium

   If `content_summary` is provided by the root session, it becomes the subject
   matter. The user's text prompt supplies intent and modifiers (tone, format,
   constraints); `content_summary` supplies the topic. When the text prompt
   already fully specifies the topic, treat `content_summary` as supplementary
   detail.

2. **Analyze content density**
```

**Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_infographic_builder.py -v
```

Expected: **All passed** (19 existing + 2 new = 21 total).

**Step 5: Commit**

```bash
git add agents/infographic-builder.md tests/test_infographic_builder.py
git commit -m "feat: accept content_summary in infographic-builder Step 1"
```

---

### Task 4: Step 3 — aesthetic_description skips menu

**Files:**
- Modify: `agents/infographic-builder.md` (Step 3 only)
- Test: `tests/test_infographic_builder.py` (append new tests)

**Step 1: Write the failing tests**

Open `tests/test_infographic_builder.py` and append these tests at the bottom:

```python


# ---------------------------------------------------------------------------
# Task: Step 3 — aesthetic_description from root session skips menu
# ---------------------------------------------------------------------------


def test_step_3_has_subpart_e():
    """Step 3 must contain sub-part e (re-lettered from d after inserting style reference)."""
    block = _get_step_3_block(read_agent())
    assert "**e." in block or "**e. " in block, "Step 3 sub-part e missing"


def test_step_3_aesthetic_description_skips_menu():
    """Step 3 must describe skipping the 6-option menu when aesthetic_description is present."""
    block = _get_step_3_block(read_agent())
    lower = block.lower()
    assert "aesthetic_description" in lower, (
        "Step 3 must mention aesthetic_description"
    )
    assert "skip" in lower, (
        "Step 3 must describe skipping the menu when aesthetic_description is present"
    )


def test_step_3_style_reference_translates_7_dimensions():
    """Step 3 must describe translating aesthetic_description to 7 style dimensions."""
    block = _get_step_3_block(read_agent())
    lower = block.lower()
    for dim in ["palette", "typography", "icons", "background", "lighting", "texture", "mood"]:
        assert dim in lower, (
            f"Step 3 must mention style dimension '{dim}' in "
            f"aesthetic_description translation.\nActual block:\n{block}"
        )
```

**Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_infographic_builder.py::test_step_3_has_subpart_e tests/test_infographic_builder.py::test_step_3_aesthetic_description_skips_menu tests/test_infographic_builder.py::test_step_3_style_reference_translates_7_dimensions -v
```

Expected: **3 FAILED** — Step 3 currently has sub-parts a–d only, with no mention of `aesthetic_description`.

**Step 3: Add style reference sub-part and re-letter existing sub-parts**

This is the largest single edit. In `agents/infographic-builder.md`, find the exact text starting from sub-part b through sub-part d (the entire block from `**b. Check for inline` to the end of sub-part d):

```
   **b. Check for inline style specification.** If the user already described
   an aesthetic in their original request (e.g., "make a claymation infographic
   about DNS", "dark mode tech style"), skip to step 4 using that aesthetic.
   This is the **two-turn shortcut** — no proposal needed.

   **c. If no style was specified**, present the aesthetic options and halt:
```

Replace it with:

```
   **b. Check for `aesthetic_description` from root session.** If the root
   session provided an `aesthetic_description` (via style reference mode),
   translate it into the same 7 style dimensions used by existing templates:
   palette, typography, icons, background, lighting, texture, and mood. Skip
   the 6-option menu entirely and proceed to step 4. This is the **style
   reference shortcut** — the user's reference image drives the aesthetic.

   **c. Check for inline style specification.** If the user already described
   an aesthetic in their original request (e.g., "make a claymation infographic
   about DNS", "dark mode tech style"), skip to step 4 using that aesthetic.
   This is the **two-turn shortcut** — no proposal needed.

   **d. If no style was specified**, present the aesthetic options and halt:
```

Then, in the same file, find:

```
   **d. Load the aesthetic template.** If the user picks a numbered option,
```

Replace with:

```
   **e. Load the aesthetic template.** If the user picks a numbered option,
```

**Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_infographic_builder.py -v
```

Expected: **All passed** (21 existing + 3 new = 24 total). Critically, all existing sub-part tests (a, b, c, d) still pass because:
- Sub-part a is unchanged
- The new b exists (style reference)
- Old b → new c (inline style / two-turn shortcut still present)
- Old c → new d (menu still present)
- Old d → new e (load template)

**Step 5: Commit**

```bash
git add agents/infographic-builder.md tests/test_infographic_builder.py
git commit -m "feat: skip aesthetic menu when aesthetic_description is present"
```

---

### Task 5: Step 5 — reference_image_path in style mode

**Files:**
- Modify: `agents/infographic-builder.md` (Step 5 only)
- Test: `tests/test_infographic_builder.py` (append new tests)

**Step 1: Write the failing tests**

Open `tests/test_infographic_builder.py` and append these tests at the bottom:

```python


# ---------------------------------------------------------------------------
# Task: Step 5 — reference_image_path modes for image input
# ---------------------------------------------------------------------------


def _get_step_5_block(content: str) -> str:
    """Extract text between '5. **Generate the image(s)**' and '6. **'."""
    start = content.index("5. **Generate the image(s)**")
    end = content.index("6. **", start)
    return content[start:end]


def test_step_5_describes_style_reference_mode():
    """Step 5 must describe style reference mode for image input."""
    block = _get_step_5_block(read_agent())
    lower = block.lower()
    assert "style reference" in lower, (
        "Step 5 must describe style reference mode.\n"
        f"Actual block:\n{block}"
    )


def test_step_5_describes_content_source_mode():
    """Step 5 must describe content source mode where image_path is NOT passed."""
    block = _get_step_5_block(read_agent())
    lower = block.lower()
    assert "content source" in lower, (
        "Step 5 must describe content source mode.\n"
        f"Actual block:\n{block}"
    )
    assert "intentionally not" in lower or "not passed" in lower, (
        "Step 5 must say image_path is intentionally not passed in content source mode.\n"
        f"Actual block:\n{block}"
    )


def test_step_5_multi_panel_uses_reference_image_paths_plural():
    """Step 5 must mention reference_image_paths (plural) for multi-panel style reference."""
    block = _get_step_5_block(read_agent())
    assert "reference_image_paths" in block, (
        "Step 5 must mention reference_image_paths (plural) for multi-panel.\n"
        f"Actual block:\n{block}"
    )


def test_step_5_two_anchors_panel_1_and_image_path():
    """Step 5 multi-panel style reference must describe two anchors: Panel 1 + original image."""
    block = _get_step_5_block(read_agent())
    lower = block.lower()
    assert "cross-panel consistency" in lower, (
        "Must describe Panel 1 anchor for cross-panel consistency"
    )
    assert "aesthetic fidelity" in lower, (
        "Must describe original image anchor for aesthetic fidelity"
    )
```

**Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_infographic_builder.py::test_step_5_describes_style_reference_mode tests/test_infographic_builder.py::test_step_5_describes_content_source_mode tests/test_infographic_builder.py::test_step_5_multi_panel_uses_reference_image_paths_plural tests/test_infographic_builder.py::test_step_5_two_anchors_panel_1_and_image_path -v
```

Expected: **4 FAILED** — Step 5 currently has no image input modes section.

**Step 3: Add image input modes to Step 5**

In `agents/infographic-builder.md`, find this exact text at the end of Step 5:

```
   - If no output paths are specified, follow the Panel Naming Convention
     in the Style Guide

6. **Quality review**:
```

Replace it with:

```
   - If no output paths are specified, follow the Panel Naming Convention
     in the Style Guide

   **Image input modes** (when the root session provides an image):

   | Mode | Panel 1 | Panels 2-N |
   |---|---|---|
   | Style reference, single panel | `reference_image_path = image_path` | — |
   | Style reference, multi-panel | `reference_image_path = image_path` | `reference_image_paths = [panel_1_path, image_path]` |
   | Content source (no style reference) | No reference image passed | Panel 1 for chaining only (existing) |

   In **style reference mode**, the user's original image anchors the aesthetic:
   - Single panel: set `reference_image_path` to the original `image_path`.
   - Multi-panel: Panel 1 uses `reference_image_path = image_path`. Panels
     2-N use `reference_image_paths = [panel_1_path, image_path]` — two
     anchors for cross-panel consistency (Panel 1) and aesthetic fidelity
     (original image).

   In **content source mode**, `image_path` is intentionally NOT passed to
   nano-banana generate. The content summary (text) is sufficient, and
   passing a raw whiteboard photo or screenshot would pollute the generated
   aesthetic.

6. **Quality review**:
```

**Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_infographic_builder.py -v
```

Expected: **All passed** (24 existing + 4 new = 28 total).

**Step 5: Commit**

```bash
git add agents/infographic-builder.md tests/test_infographic_builder.py
git commit -m "feat: add reference_image_path modes for image input in Step 5"
```

---

### Task 6: Style guide — multi-panel reference_image_paths

**Files:**
- Modify: `docs/style-guide.md` (the `### Reference Image Chaining` section)
- Test: `tests/test_style_consistency_brief.py` (append new tests)

**Step 1: Write the failing tests**

Open `tests/test_style_consistency_brief.py` and append these tests at the bottom:

```python


# ---------------------------------------------------------------------------
# Task: reference_image_paths (plural) in Reference Image Chaining
# ---------------------------------------------------------------------------


def _get_reference_chaining_block(content: str) -> str:
    """Extract the Reference Image Chaining section."""
    start = content.index("### Reference Image Chaining")
    next_h3 = content.find("\n### ", start + 1)
    return content[start:next_h3] if next_h3 != -1 else content[start:]


def test_reference_chaining_documents_plural_paths():
    """Reference Image Chaining must document reference_image_paths (plural)."""
    block = _get_reference_chaining_block(read_guide())
    assert "reference_image_paths" in block, (
        "Reference Image Chaining must document reference_image_paths (plural).\n"
        f"Actual block:\n{block}"
    )


def test_reference_chaining_two_anchor_pattern():
    """Reference Image Chaining must describe the two-anchor pattern for style reference."""
    block = _get_reference_chaining_block(read_guide())
    lower = block.lower()
    assert "cross-panel consistency" in lower, (
        "Must describe Panel 1 anchor for cross-panel consistency"
    )
    assert "aesthetic fidelity" in lower, (
        "Must describe original image anchor for aesthetic fidelity"
    )


def test_reference_chaining_mentions_image_path():
    """The two-anchor pattern must reference image_path."""
    block = _get_reference_chaining_block(read_guide())
    assert "image_path" in block, (
        "Must reference image_path in the two-anchor pattern"
    )
```

**Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_style_consistency_brief.py::test_reference_chaining_documents_plural_paths tests/test_style_consistency_brief.py::test_reference_chaining_two_anchor_pattern tests/test_style_consistency_brief.py::test_reference_chaining_mentions_image_path -v
```

Expected: **3 FAILED** — no reference_image_paths documentation exists yet.

**Step 3: Add style reference multi-panel documentation**

In `docs/style-guide.md`, find this exact text in the Reference Image Chaining section:

```
Panel 1 MUST be generated first and alone. Panels 2-N may be generated in
parallel since they all reference Panel 1, not each other.

### Post-Panel 1 Style Reconciliation
```

Replace it with:

```
Panel 1 MUST be generated first and alone. Panels 2-N may be generated in
parallel since they all reference Panel 1, not each other.

**Style reference mode (multi-panel):** When the root session provides an
`image_path` for style reference, the reference image chaining uses a
two-anchor pattern:

- **Panel 1**: `reference_image_path = image_path` (user's reference image
  anchors the aesthetic)
- **Panels 2-N**: `reference_image_paths = [panel_1_path, image_path]` — two
  anchors: Panel 1 for cross-panel consistency, and the original `image_path`
  for aesthetic fidelity

This is the first use of `reference_image_paths` (plural) in the project.
The two-anchor approach ensures Panels 2-N stay consistent with both Panel 1
and the original style reference.

### Post-Panel 1 Style Reconciliation
```

**Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_style_consistency_brief.py -v
```

Expected: **All passed** (7 existing + 3 new = 10 total).

**Step 5: Commit**

```bash
git add docs/style-guide.md tests/test_style_consistency_brief.py
git commit -m "feat: document reference_image_paths in multi-panel style guide section"
```

---

### Task 7: Style guide — Style Reference Mode in Aesthetics

**Files:**
- Modify: `docs/style-guide.md` (the `## Aesthetics` section)
- Test: `tests/test_style_guide_aesthetics.py` (append new tests)

**Step 1: Write the failing tests**

Open `tests/test_style_guide_aesthetics.py` and append these tests at the bottom:

```python


# ---------------------------------------------------------------------------
# Task: Style Reference Mode subsection in ## Aesthetics
# ---------------------------------------------------------------------------


def test_style_reference_mode_subsection_in_aesthetics():
    """### Style Reference Mode must exist within ## Aesthetics."""
    content = read_guide()
    aesthetics_idx = content.index(H2_AESTHETICS)
    layout_idx = content.index(H2_LAYOUT_TYPES)
    block = content[aesthetics_idx:layout_idx]
    assert "### Style Reference Mode" in block, (
        "### Style Reference Mode subsection must exist within ## Aesthetics"
    )


def test_style_reference_mode_skips_menu():
    """Style Reference Mode must describe skipping the 6-option menu."""
    content = read_guide()
    start = content.index("### Style Reference Mode")
    next_h3 = content.find("\n### ", start + 1)
    block = content[start:next_h3] if next_h3 != -1 else content[start:]
    lower = block.lower()
    assert "skip" in lower, "Style Reference Mode must describe skipping the menu"
    assert "menu" in lower or "6-option" in lower, (
        "Style Reference Mode must reference the menu being skipped"
    )


def test_style_reference_mode_translates_7_dimensions():
    """Style Reference Mode must describe translating to 7 style dimensions."""
    content = read_guide()
    start = content.index("### Style Reference Mode")
    next_h3 = content.find("\n### ", start + 1)
    block = content[start:next_h3] if next_h3 != -1 else content[start:]
    lower = block.lower()
    for dim in ["palette", "typography", "icons", "background", "lighting", "texture", "mood"]:
        assert dim in lower, (
            f"Style Reference Mode must mention dimension '{dim}'"
        )
```

**Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_style_guide_aesthetics.py::test_style_reference_mode_subsection_in_aesthetics tests/test_style_guide_aesthetics.py::test_style_reference_mode_skips_menu tests/test_style_guide_aesthetics.py::test_style_reference_mode_translates_7_dimensions -v
```

Expected: **3 FAILED** — no Style Reference Mode subsection exists yet.

**Step 3: Add Style Reference Mode subsection**

In `docs/style-guide.md`, find this exact text (end of Lego section, before Freeform):

```
- **Diorama compatible:** Yes — see Representation Mode above

### Freeform Aesthetics
```

Replace it with:

```
- **Diorama compatible:** Yes — see Representation Mode above

### Style Reference Mode

When the root session provides an `aesthetic_description` (extracted from a
user-provided reference image), the 6-option menu is skipped entirely. The
agent translates the aesthetic description into the same 7 style dimensions
used by the curated templates above: palette, typography, icons, background,
lighting, texture, and mood.

This produces the same shape of input that downstream steps (4–8) always
expect — no special casing required. The reference image's visual character
drives the aesthetic instead of a curated template or freeform description.

### Freeform Aesthetics
```

**Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_style_guide_aesthetics.py -v
```

Expected: **All passed** (10 existing + 3 new = 13 total). The existing `test_freeform_is_last_subsection_before_layout_types` still passes because `### Freeform Aesthetics` remains the last `###` subsection before `## Layout Types`.

**Step 5: Commit**

```bash
git add docs/style-guide.md tests/test_style_guide_aesthetics.py
git commit -m "feat: add Style Reference Mode to style guide Aesthetics section"
```

---

## Final verification

After all 7 tasks are complete, run the full test suite to confirm nothing is broken:

```bash
python3 -m pytest tests/ -v
```

Expected: **All passed** — the original 50 tests plus 21 new tests = **71 total**.

Breakdown of new tests by file:
- `tests/test_diagram_routing.py`: +6 (2 from Task 1 + 4 from Task 2)
- `tests/test_infographic_builder.py`: +9 (2 from Task 3 + 3 from Task 4 + 4 from Task 5)
- `tests/test_style_consistency_brief.py`: +3 (Task 6)
- `tests/test_style_guide_aesthetics.py`: +3 (Task 7)