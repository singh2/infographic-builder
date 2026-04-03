# Scene Strategy (Varied / Consistent) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a scene strategy mechanism (`varied` / `consistent`) to the infographic builder's multi-panel pipeline so the agent can intentionally choose between uniform visual framing and per-panel scene variation.

**Architecture:** All changes are markdown instruction edits across two files: `docs/style-guide.md` (5 touchpoints) and `agents/infographic-builder.md` (1 touchpoint). Tests follow the existing project pattern — plain functions that load markdown and assert on expected phrases. A new test file `tests/test_scene_strategy.py` covers all 6 touchpoints. No Python logic changes.

**Tech Stack:** Markdown, pytest

**Design doc:** `docs/superpowers/specs/2026-04-03-scene-strategy-design.md`

---

## File Map

| Action | File | What changes |
|--------|------|-------------|
| Create | `tests/test_scene_strategy.py` | New test file — all scene strategy assertions |
| Modify | `docs/style-guide.md:204-222` | Content Map template gains `Scene strategy:` line and per-panel `Scene:` field |
| Modify | `docs/style-guide.md:175-182` | Prompt Engineering list gains 7th required element |
| Modify | `docs/style-guide.md:226-239` | Style Brief template gains varied-mode Background note |
| Modify | `docs/style-guide.md:289-311` | Reconciliation section gains varied-mode scoping note |
| Modify | `docs/style-guide.md:377-399` | Cross-panel critic gains varied-mode scoping preamble |
| Modify | `agents/infographic-builder.md:167-172` | Step 5d gains 4th consistency signal for varied scene directive |

**Note on line numbers:** Line numbers are approximate anchors from the current file. Use the sentinel strings (section headings, key phrases) to locate the exact insertion points, not line numbers.

---

### Task 1: Content Map — add scene strategy and per-panel scene directives

**Files:**
- Create: `tests/test_scene_strategy.py` (initial structure + Task 1 tests)
- Modify: `docs/style-guide.md` — the `### Content Map (No Duplication)` section

- [ ] **Step 1: Write the failing tests**

Create `tests/test_scene_strategy.py` with the initial test structure and Task 1 tests:

```python
"""
Tests for scene strategy (varied / consistent) in multi-panel pipeline.

Covers 6 touchpoints across docs/style-guide.md and agents/infographic-builder.md.
See design doc: docs/superpowers/specs/2026-04-03-scene-strategy-design.md
"""

import re

from helpers import read_agent, read_guide

# --- Sentinels ---
H3_CONTENT_MAP = "### Content Map"
H3_STYLE_BRIEF = "### Style Consistency Brief"


# --- Block extractors ---
def _get_content_map_block(content: str) -> str:
    start = content.index(H3_CONTENT_MAP)
    end = content.index(H3_STYLE_BRIEF, start)
    return content[start:end]


# --- Task 1: Content Map ---


def test_content_map_has_scene_strategy_line() -> None:
    """Content map template must include a 'Scene strategy:' line."""
    block = _get_content_map_block(read_guide())
    assert "Scene strategy:" in block, (
        "'Scene strategy:' not found in Content Map template.\n"
        f"Actual block:\n{block}"
    )


def test_content_map_has_varied_and_consistent_values() -> None:
    """Content map must name both 'varied' and 'consistent' as valid values."""
    block = _get_content_map_block(read_guide())
    lower = block.lower()
    assert "varied" in lower, "'varied' not found in Content Map"
    assert "consistent" in lower, "'consistent' not found in Content Map"


def test_content_map_has_per_panel_scene_field() -> None:
    """Content map template must include a 'Scene:' field for per-panel directives."""
    block = _get_content_map_block(read_guide())
    assert "Scene:" in block, (
        "'Scene:' per-panel field not found in Content Map template.\n"
        f"Actual block:\n{block}"
    )


def test_content_map_scene_only_when_varied() -> None:
    """Content map must state Scene: lines are only for varied strategy."""
    block = _get_content_map_block(read_guide())
    normalised = " ".join(block.lower().split())
    assert "varied" in normalised and "scene" in normalised, (
        "Content Map must connect Scene: field to varied strategy.\n"
        f"Actual block:\n{block}"
    )


def test_content_map_has_decision_heuristic() -> None:
    """Content map section must include guidance on when to use varied vs consistent."""
    block = _get_content_map_block(read_guide())
    lower = block.lower()
    # Must mention narrative/journey topics as varied triggers
    assert "journey" in lower or "narrative" in lower or "routine" in lower, (
        "Content Map must mention narrative/journey topics as varied triggers.\n"
        f"Actual block:\n{block}"
    )


def test_content_map_default_is_consistent() -> None:
    """Content map must state that 'consistent' is the default when in doubt."""
    block = _get_content_map_block(read_guide())
    lower = block.lower()
    assert "default" in lower and "consistent" in lower, (
        "Content Map must specify 'consistent' as the default strategy.\n"
        f"Actual block:\n{block}"
    )
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_scene_strategy.py -v`

Expected: 6 FAILED — Content Map does not yet have scene strategy content.

- [ ] **Step 3: Edit the Content Map section in style-guide.md**

Find the `### Content Map (No Duplication)` section in `docs/style-guide.md`. The current fenced code block shows:

```
CONTENT MAP:
Panel 1 -- [title]: [concepts/data ONLY in this panel]
Panel 2 -- [title]: [concepts/data ONLY in this panel]
...
Shared across panels: [series title, style brief only]
```

Replace the fenced code block with:

````
```
CONTENT MAP:
Scene strategy: [varied | consistent]

Panel 1 -- [title]: [concepts/data ONLY in this panel]
  Scene: [varied only — environment, perspective, key props for this panel]
Panel 2 -- [title]: [concepts/data ONLY in this panel]
  Scene: [varied only — distinct environment from Panel 1]
...
Shared across panels: [series title, style brief only]
```
````

After the existing Rules list (the 4 bullet points ending with the scoping line rule), add:

```markdown
**Scene strategy** — decided once per infographic at this stage:
- **`consistent`**: Same visual frame across all panels. Background, composition,
  and framing are identical. Use for comparisons, taxonomies, ranked lists, data
  breakdowns — topics where uniform framing highlights content differences.
- **`varied`**: Artistic style stays locked (palette, typography, icon rendering,
  lighting quality, borders). Environment, props, perspective, and composition
  vary per panel. Use for journeys, daily routines, recipes, multi-step processes
  with distinct physical settings — topics where each panel naturally maps to a
  different location.
- When `consistent`, the `Scene:` lines do not exist in the content map.
- When `varied`, each panel gets a 1-sentence scene directive — concrete and
  visual (e.g. "sunlit forest trail with layered clay trees" not "nature scene").
- **Default to `consistent` when in doubt.** This preserves current behavior.
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_scene_strategy.py -v`

Expected: 6 PASSED

- [ ] **Step 5: Run all existing style guide tests to verify no regressions**

Run: `python3 -m pytest tests/test_style_consistency_brief.py tests/test_quality_review_dimensions.py tests/test_style_guide_aesthetics.py tests/test_style_guide_layouts.py -v`

Expected: All PASSED — the Content Map section is upstream of these sections.

- [ ] **Step 6: Commit**

```bash
git add tests/test_scene_strategy.py docs/style-guide.md
git commit -m "feat: add scene strategy to content map template"
```

---

### Task 2: Prompt Engineering — add 7th required element

**Files:**
- Modify: `tests/test_scene_strategy.py` (add Task 2 tests)
- Modify: `docs/style-guide.md` — the `## Prompt Engineering` section

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_scene_strategy.py`:

```python
# --- Sentinels ---
H2_PROMPT_ENGINEERING = "## Prompt Engineering"
H3_MULTI_PANEL = "### Multi-Panel Composition"  # next H3 after prompt list


def _get_prompt_engineering_block(content: str) -> str:
    start = content.index(H2_PROMPT_ENGINEERING)
    end = content.index("### ", start + len(H2_PROMPT_ENGINEERING))
    return content[start:end]


# --- Task 2: Prompt Engineering ---


def test_prompt_engineering_has_scene_directive_element() -> None:
    """Prompt Engineering list must include a scene directive element."""
    block = _get_prompt_engineering_block(read_guide())
    lower = block.lower()
    assert "scene directive" in lower, (
        "'scene directive' not found in Prompt Engineering section.\n"
        f"Actual block:\n{block}"
    )


def test_prompt_engineering_scene_directive_is_multi_panel_only() -> None:
    """Scene directive element must be scoped to multi-panel varied only."""
    block = _get_prompt_engineering_block(read_guide())
    lower = block.lower()
    assert "multi-panel" in lower and "varied" in lower, (
        "Scene directive must be scoped to 'multi-panel' and 'varied'.\n"
        f"Actual block:\n{block}"
    )
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_scene_strategy.py::test_prompt_engineering_has_scene_directive_element tests/test_scene_strategy.py::test_prompt_engineering_scene_directive_is_multi_panel_only -v`

Expected: 2 FAILED

- [ ] **Step 3: Edit the Prompt Engineering section in style-guide.md**

Find the numbered list under `## Prompt Engineering` (items 1-6). After item 6 (`**Aspect ratio hint**`), add:

```markdown
7. **Scene directive** (multi-panel varied only) -- the distinct environment,
   perspective, or visual setting for THIS panel, drawn from the content map's
   Scene field. Omit for consistent strategy or single-panel infographics.
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_scene_strategy.py -v`

Expected: 8 PASSED (6 from Task 1 + 2 new)

- [ ] **Step 5: Commit**

```bash
git add tests/test_scene_strategy.py docs/style-guide.md
git commit -m "feat: add scene directive to prompt engineering requirements"
```

---

### Task 3: Style Brief — add varied-mode Background note

**Files:**
- Modify: `tests/test_scene_strategy.py` (add Task 3 tests)
- Modify: `docs/style-guide.md` — the `### Style Consistency Brief` section

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_scene_strategy.py`:

```python
# --- Sentinels ---
H3_REF_IMAGE_CHAINING = "### Reference Image Chaining"


def _get_style_brief_block(content: str) -> str:
    start = content.index(H3_STYLE_BRIEF)
    end = content.index(H3_REF_IMAGE_CHAINING, start)
    return content[start:end]


# --- Task 3: Style Brief ---


def test_style_brief_mentions_varied_background() -> None:
    """Style brief section must note that Background changes for varied strategy."""
    block = _get_style_brief_block(read_guide())
    lower = block.lower()
    assert "varied" in lower and "scene directive" in lower, (
        "Style Brief must mention varied strategy and scene directive for Background.\n"
        f"Actual block:\n{block}"
    )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_scene_strategy.py::test_style_brief_mentions_varied_background -v`

Expected: 1 FAILED

- [ ] **Step 3: Edit the Style Consistency Brief section in style-guide.md**

Find the Style Brief fenced code block. After the closing `` ``` `` of the brief template (after the `- Aspect ratio:` line), add:

```markdown
When the scene strategy is `varied`, set the Background field to
`"per scene directive"` instead of a fixed color or treatment. This prevents
the brief from contradicting per-panel scene directives. All other fields
(palette, typography, icons, borders, header chrome) remain fixed and apply
uniformly.
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_scene_strategy.py -v`

Expected: 9 PASSED

- [ ] **Step 5: Run style brief tests to verify no regressions**

Run: `python3 -m pytest tests/test_style_consistency_brief.py -v`

Expected: All PASSED

- [ ] **Step 6: Commit**

```bash
git add tests/test_scene_strategy.py docs/style-guide.md
git commit -m "feat: add varied-mode background note to style brief"
```

---

### Task 4: Reconciliation — add varied-mode scoping note

**Files:**
- Modify: `tests/test_scene_strategy.py` (add Task 4 tests)
- Modify: `docs/style-guide.md` — the `### Post-Panel 1 Style Reconciliation` section

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_scene_strategy.py`:

```python
# --- Sentinels ---
H3_RECONCILIATION = "### Post-Panel 1 Style Reconciliation"
H3_PANEL_NAMING = "### Panel Naming Convention"


def _get_reconciliation_block(content: str) -> str:
    start = content.index(H3_RECONCILIATION)
    end = content.index(H3_PANEL_NAMING, start)
    return content[start:end]


# --- Task 4: Reconciliation ---


def test_reconciliation_has_varied_scoping_note() -> None:
    """Reconciliation section must note that background is panel-specific for varied."""
    block = _get_reconciliation_block(read_guide())
    lower = block.lower()
    assert "varied" in lower, (
        "Reconciliation must mention varied strategy.\n"
        f"Actual block:\n{block}"
    )


def test_reconciliation_varied_scopes_background() -> None:
    """Reconciliation varied note must distinguish background from style properties."""
    block = _get_reconciliation_block(read_guide())
    normalised = " ".join(block.lower().split())
    assert "background" in normalised and "style" in normalised, (
        "Reconciliation varied note must distinguish background from style.\n"
        f"Actual block:\n{block}"
    )
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_scene_strategy.py::test_reconciliation_has_varied_scoping_note tests/test_scene_strategy.py::test_reconciliation_varied_scopes_background -v`

Expected: 2 FAILED

- [ ] **Step 3: Edit the Reconciliation section in style-guide.md**

Find the paragraph that ends with "The render wins, completely." (around line 311). After that paragraph, add:

```markdown
**Varied scene strategy note:** When the scene strategy is `varied`, the
reconciled brief carries the style DNA (typography, palette, icon rendering,
lighting quality, border treatment) but the background environment description
is specific to Panel 1's scene. Do not enforce Panel 1's background environment
on Panels 2-N — they have their own scene directives. All other style properties
from the reconciled brief apply uniformly.
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_scene_strategy.py -v`

Expected: 11 PASSED

- [ ] **Step 5: Commit**

```bash
git add tests/test_scene_strategy.py docs/style-guide.md
git commit -m "feat: add varied-mode scoping to reconciliation section"
```

---

### Task 5: Cross-Panel Critic — add varied-mode scoping preamble

**Files:**
- Modify: `tests/test_scene_strategy.py` (add Task 5 tests)
- Modify: `docs/style-guide.md` — the `### Cross-Panel Visual Comparison` section

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_scene_strategy.py`:

```python
# --- Sentinels ---
H3_CROSS_PANEL = "### Cross-Panel Visual Comparison"
H3_REFINEMENT = "### Refinement Rules"


def _get_cross_panel_block(content: str) -> str:
    start = content.index(H3_CROSS_PANEL)
    end = content.index(H3_REFINEMENT, start)
    return content[start:end]


# --- Task 5: Cross-Panel Critic ---


def test_cross_panel_has_varied_scoping_preamble() -> None:
    """Cross-panel critic must include a scoping preamble for varied strategy."""
    block = _get_cross_panel_block(read_guide())
    lower = block.lower()
    assert "varied" in lower, (
        "Cross-panel critic must mention varied strategy.\n"
        f"Actual block:\n{block}"
    )


def test_cross_panel_varied_distinguishes_style_from_environment() -> None:
    """Varied preamble must tell critic to check style, not environment."""
    block = _get_cross_panel_block(read_guide())
    normalised = " ".join(block.lower().split())
    # Must tell critic that environment differences are intentional
    assert "intentional" in normalised or "not drift" in normalised or "do not flag" in normalised, (
        "Varied preamble must state environment differences are intentional.\n"
        f"Actual block:\n{block}"
    )


def test_cross_panel_varied_preserves_style_enforcement() -> None:
    """Varied preamble must still enforce style consistency (typography, palette, etc.)."""
    block = _get_cross_panel_block(read_guide())
    lower = block.lower()
    # Must mention specific style properties that are still enforced
    style_properties_mentioned = sum(
        1 for prop in ["typography", "palette", "icon", "border"]
        if prop in lower
    )
    assert style_properties_mentioned >= 2, (
        "Varied preamble must name specific style properties still enforced.\n"
        f"Actual block:\n{block}"
    )
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_scene_strategy.py::test_cross_panel_has_varied_scoping_preamble tests/test_scene_strategy.py::test_cross_panel_varied_distinguishes_style_from_environment tests/test_scene_strategy.py::test_cross_panel_varied_preserves_style_enforcement -v`

Expected: 3 FAILED

- [ ] **Step 3: Edit the Cross-Panel Comparison section in style-guide.md**

Find the cross-panel comparison section. After the opening paragraph ("For Panels 2-N, add a visual comparison step...") and before the fenced prompt block, add:

```markdown
**Varied scene strategy:** When the content map declares `Scene strategy: varied`,
prepend this preamble to the comparison prompt:

> "These panels use a VARIED scene strategy — each panel intentionally depicts a
> different environment while sharing the same artistic style. When checking
> BACKGROUND, evaluate only the background STYLE (lighting quality, texture
> approach, depth-of-field treatment) — do NOT flag differences in background
> CONTENT (what the scene depicts). A forest and a kitchen are not drift if they
> share the same lighting quality, color temperature, and rendering approach.
> Only flag unintended style inconsistencies: mismatched typography weights,
> divergent accent colors, inconsistent icon rendering, or different border
> treatments."

When the scene strategy is `consistent` (or unset), use the comparison prompt
as-is — full 8-dimension enforcement including background content.
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_scene_strategy.py -v`

Expected: 14 PASSED

- [ ] **Step 5: Run quality review tests to verify no regressions**

Run: `python3 -m pytest tests/test_quality_review_dimensions.py -v`

Expected: All PASSED

- [ ] **Step 6: Commit**

```bash
git add tests/test_scene_strategy.py docs/style-guide.md
git commit -m "feat: add varied-mode scoping preamble to cross-panel critic"
```

---

### Task 6: Agent Step 5d — add scene directive as 4th consistency signal

**Files:**
- Modify: `tests/test_scene_strategy.py` (add Task 6 tests)
- Modify: `agents/infographic-builder.md` — Step 5d (Panels 2-N generation)

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_scene_strategy.py`:

```python
# --- Task 6: Agent Step 5d ---


def _get_agent_step_5_block(content: str) -> str:
    start = content.index("5. **Generate the image(s)**")
    end = content.index("6. **", start)
    return content[start:end]


def test_agent_step5d_has_scene_directive_signal() -> None:
    """Step 5d must mention scene directive as a signal for varied strategy."""
    block = _get_agent_step_5_block(read_agent())
    lower = block.lower()
    assert "scene directive" in lower, (
        "Step 5d must mention 'scene directive'.\n"
        f"Actual block:\n{block}"
    )


def test_agent_step5d_scene_scoped_to_varied() -> None:
    """Step 5d scene directive must be scoped to varied strategy."""
    block = _get_agent_step_5_block(read_agent())
    lower = block.lower()
    assert "varied" in lower, (
        "Step 5d scene directive must reference varied strategy.\n"
        f"Actual block:\n{block}"
    )


def test_agent_step5d_varied_locks_style() -> None:
    """Step 5d varied instruction must emphasize that style stays locked."""
    block = _get_agent_step_5_block(read_agent())
    normalised = " ".join(block.lower().split())
    assert "style" in normalised and ("match" in normalised or "lock" in normalised or "exact" in normalised), (
        "Step 5d must state that style stays locked for varied panels.\n"
        f"Actual block:\n{block}"
    )
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_scene_strategy.py::test_agent_step5d_has_scene_directive_signal tests/test_scene_strategy.py::test_agent_step5d_scene_scoped_to_varied tests/test_scene_strategy.py::test_agent_step5d_varied_locks_style -v`

Expected: 3 FAILED

- [ ] **Step 3: Edit Step 5d in agents/infographic-builder.md**

Find the Step 5d paragraph that describes the three consistency signals. It currently ends with "Panels 2-N may run in parallel since they all reference Panel 1, not each other." After that sentence, add:

```markdown

   **Varied scene strategy:** When the content map declares
   `Scene strategy: varied`, add a 4th signal to each Panel 2-N prompt —
   the scene directive from the content map: "This panel's ENVIRONMENT is:
   [scene description]. The artistic STYLE (lighting quality, color palette,
   typography, icon rendering, border treatment) must match Panel 1 exactly.
   The setting and composition are intentionally different." This gives the
   model explicit permission to change the environment while keeping the
   style locked. For `consistent` strategy, omit this — the three existing
   signals are sufficient.
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_scene_strategy.py -v`

Expected: 17 PASSED (all tests across all 6 tasks)

- [ ] **Step 5: Run all agent instruction tests to verify no regressions**

Run: `python3 -m pytest tests/test_infographic_builder.py tests/test_agent_plan_and_quality_steps.py -v`

Expected: All PASSED

- [ ] **Step 6: Run full test suite**

Run: `python3 -m pytest tests/ -v`

Expected: All PASSED — no regressions across the entire test suite.

- [ ] **Step 7: Commit**

```bash
git add tests/test_scene_strategy.py agents/infographic-builder.md
git commit -m "feat: add varied scene directive to agent step 5d"
```

---

## Self-Review Checklist

**Spec coverage:**
- [x] Content Map template — Task 1
- [x] Prompt Engineering 7th element — Task 2
- [x] Style Brief varied Background note — Task 3
- [x] Reconciliation varied scoping — Task 4
- [x] Cross-Panel Critic varied preamble — Task 5
- [x] Agent Step 5d scene directive signal — Task 6
- [x] Decision heuristic (when to use varied vs consistent) — Task 1 (in Content Map guidance)
- [x] Default to consistent — Task 1
- [x] Naming: no "cinematic" — verified, term not used anywhere in plan

**Not in scope (per design doc):**
- Eval rubric changes — design doc says "no immediate changes"
- New eval scenarios — separate task, not part of pipeline implementation
- `report.py` cross_panel_consistency bug — independent fix

**Placeholder scan:** No TBDs, TODOs, or "similar to Task N" references found.

**Type consistency:** No code types — all markdown edits. Sentinel strings used consistently.