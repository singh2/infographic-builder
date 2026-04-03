# Diagram Beautifier Quality & Visual Improvements

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix two gaps in the diagram-beautifier agent — a missing quality dimension and missing generation guidance — and document the generation rules in the shared style guide.

**Architecture:** Three changes: (1) add an 8th quality dimension (color-category semantic fidelity) to Step 7 of `agents/diagram-beautifier.md`, (2) add a `### Diagram Generation Guidance` subsection under Step 6 of the same file with quality bar, prompt ordering, per-aesthetic shape/connector table, and color-category mapping rules, (3) add a `## Diagram Generation` section to `docs/style-guide.md` as cross-reference documentation.

**Tech Stack:** Markdown agent definitions, pytest (text-assertion style — no mocking, tests read `.md` files and assert on text content)

---

## File Map

| Action | File | Responsibility |
|--------|------|----------------|
| Modify | `agents/diagram-beautifier.md` | Add 8th quality dimension to Step 7; add generation guidance to Step 6 |
| Modify | `tests/test_diagram_beautifier_agent.py` | Tests for both Step 7 and Step 6 additions |
| Modify | `docs/style-guide.md` | New `## Diagram Generation` section after `## Diorama Mode` |
| Create | `tests/test_style_guide_diagram_generation.py` | Tests for the new style-guide section |

---

### Task 1: Add color-category fidelity quality dimension (Step 7)

**Files:**
- Modify: `tests/test_diagram_beautifier_agent.py` (append new test)
- Modify: `agents/diagram-beautifier.md:190-196` (Step 7 quality review block)

- [ ] **Step 1: Write the failing test**

Append this test to the end of `tests/test_diagram_beautifier_agent.py`:

```python
def test_step7_has_color_category_fidelity() -> None:
    """Step 7 quality review must include color-category fidelity dimension."""
    content = _read_agent()
    start = content.index("7. **Quality review**")
    end = content.find("8. **Assemble**", start)
    block = content[start:end] if end != -1 else content[start:]
    assert "color-category fidelity" in block.lower(), (
        "Step 7 must mention 'color-category fidelity' but it was not found.\n"
        f"Actual step 7 block:\n{block}"
    )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_diagram_beautifier_agent.py::test_step7_has_color_category_fidelity -v`
Expected: FAIL — `AssertionError: Step 7 must mention 'color-category fidelity'`

- [ ] **Step 3: Add color-category fidelity to Step 7**

In `agents/diagram-beautifier.md`, find this block (around line 190):

```markdown
   - **Structural accuracy** -- verify node count and major connections

   Max 1 refinement pass per panel, targeting only specific issues identified.
```

Replace it with:

```markdown
   - **Structural accuracy** -- verify node count and major connections
   - **Color-category fidelity** (diagrams with semantic legends only) -- for
     each category in the original legend (e.g. Script Step, AI Agent Step,
     Condition, Start/End), verify that the same node names appear under the
     same category in the output. Flag any node that changed category.

   Max 1 refinement pass per panel, targeting only specific issues identified.
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_diagram_beautifier_agent.py::test_step7_has_color_category_fidelity -v`
Expected: PASS

- [ ] **Step 5: Run full existing test suite to confirm no regressions**

Run: `pytest tests/test_diagram_beautifier_agent.py -v`
Expected: All tests PASS (including all pre-existing tests)

- [ ] **Step 6: Commit**

```bash
git add agents/diagram-beautifier.md tests/test_diagram_beautifier_agent.py
git commit -m "feat: add color-category fidelity as 8th quality dimension to diagram-beautifier Step 7"
```

---

### Task 2: Add diagram generation guidance — quality bar directive (Step 6)

**Files:**
- Modify: `tests/test_diagram_beautifier_agent.py` (append new test)
- Modify: `agents/diagram-beautifier.md:177-188` (Step 6 beautify block)

This task adds the `### Diagram Generation Guidance` subsection header, quality bar directive, and prompt ordering rule. Tasks 3-4 add the remaining content to the same subsection.

- [ ] **Step 1: Write the failing tests**

Append these tests to the end of `tests/test_diagram_beautifier_agent.py`:

```python
def _get_step_6_block(content: str) -> str:
    """Extract Step 6 block (everything from Step 6 heading to Step 7 heading)."""
    start = content.index("6. **Beautify**")
    end = content.find("7. **Quality review**", start)
    return content[start:end] if end != -1 else content[start:]


def test_step6_has_generation_guidance_subsection() -> None:
    """Step 6 must contain a '### Diagram Generation Guidance' subsection."""
    content = _read_agent()
    block = _get_step_6_block(content)
    assert "### Diagram Generation Guidance" in block, (
        "Step 6 must have a '### Diagram Generation Guidance' subsection.\n"
        f"Actual step 6 block:\n{block}"
    )


def test_step6_has_quality_bar_directive() -> None:
    """Step 6 must include a quality bar directive about 'publication quality'."""
    content = _read_agent()
    block = _get_step_6_block(content)
    assert "publication quality" in block.lower(), (
        "Step 6 must mention 'publication quality' in the quality bar directive.\n"
        f"Actual step 6 block:\n{block}"
    )


def test_step6_has_prompt_ordering_rule() -> None:
    """Step 6 must specify aesthetic directive FIRST, structural preservation SECOND."""
    content = _read_agent()
    block = _get_step_6_block(content).lower()
    assert "aesthetic" in block and "first" in block, (
        "Step 6 must state aesthetic directive comes FIRST in prompt ordering.\n"
        f"Actual step 6 block:\n{block}"
    )
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_diagram_beautifier_agent.py::test_step6_has_generation_guidance_subsection tests/test_diagram_beautifier_agent.py::test_step6_has_quality_bar_directive tests/test_diagram_beautifier_agent.py::test_step6_has_prompt_ordering_rule -v`
Expected: All 3 FAIL

- [ ] **Step 3: Add generation guidance subsection to Step 6**

In `agents/diagram-beautifier.md`, find this block (around line 184):

```markdown
   **Multi-panel path:**
   - Panel 1 generated first with plain PNG as reference (style anchor)
   - Call `nano-banana analyze` on Panel 1 for style reconciliation
   - Panels 2-N reference Panel 1 for style consistency AND their own
     subgraph structure via the structural preservation modifier

7. **Quality review**
```

Replace it with:

```markdown
   **Multi-panel path:**
   - Panel 1 generated first with plain PNG as reference (style anchor)
   - Call `nano-banana analyze` on Panel 1 for style reconciliation
   - Panels 2-N reference Panel 1 for style consistency AND their own
     subgraph structure via the structural preservation modifier

   ### Diagram Generation Guidance

   **Quality bar directive** — include at the TOP of every generation prompt:

   > "This should be dramatically more visually impressive than the source
   > diagram — publication quality, not just a recolored version."

   **Prompt ordering rule:** Aesthetic directive FIRST, structural preservation
   SECOND. VLM models respond better when the visual direction leads and
   structural constraints follow.

   **Per-aesthetic shape and connector guidance:**

   | Aesthetic | Node shapes | Connector style | Special constraints |
   |---|---|---|---|
   | Clean Minimalist | Rounded rect (12px radius), diamond for conditions, stadium for start/end | Orthogonal only (H/V segments, 4px rounded joins). Diagonal edges forbidden. | Exactly 13 nodes on canvas. Legend: text + colored squares only, no floating sample nodes. |
   | Dark Mode Tech | Script Steps: rounded rect (6px). AI Agent Steps: hexagons. Conditions: diamonds. Start/End: stadium/pill | Curved bezier paths, gradient glow from source-node color to destination-node color, neon arrowheads | Exactly ONE legend box, bottom-right. Do not duplicate. |
   | Bold Editorial | All nodes: bold rectangular blocks with thick colored borders | Heavy straight lines with bold arrowheads | — |
   | Hand-Drawn Sketchnote | All nodes: wobbly hand-drawn outlines | Hand-drawn arrows, slightly curved | — |
   | Claymation Studio | All nodes: sculpted clay blobs/rounded forms | Rope/ribbon connectors | — |
   | Lego Brick Builder | All nodes: brick-built rectangular constructions | Brick-peg connector rods | — |

   **Color-category mapping rule:** When the source diagram has a semantic color
   legend, explicitly list every category → node mapping in the generation
   prompt. Do not rely on the model inferring it from the reference image.

7. **Quality review**
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_diagram_beautifier_agent.py::test_step6_has_generation_guidance_subsection tests/test_diagram_beautifier_agent.py::test_step6_has_quality_bar_directive tests/test_diagram_beautifier_agent.py::test_step6_has_prompt_ordering_rule -v`
Expected: All 3 PASS

- [ ] **Step 5: Run full test suite to confirm no regressions**

Run: `pytest tests/test_diagram_beautifier_agent.py -v`
Expected: All tests PASS

- [ ] **Step 6: Commit**

```bash
git add agents/diagram-beautifier.md tests/test_diagram_beautifier_agent.py
git commit -m "feat: add Diagram Generation Guidance subsection to diagram-beautifier Step 6"
```

---

### Task 3: Add tests for per-aesthetic table and color-category mapping in Step 6

**Files:**
- Modify: `tests/test_diagram_beautifier_agent.py` (append new tests)

These tests validate the per-aesthetic table and color-category mapping that were already added in Task 2's implementation. Writing them separately keeps each task focused.

- [ ] **Step 1: Write the tests**

Append these tests to the end of `tests/test_diagram_beautifier_agent.py`:

```python
def test_step6_has_per_aesthetic_table() -> None:
    """Step 6 must contain a table with all 6 aesthetics' shape/connector guidance."""
    content = _read_agent()
    block = _get_step_6_block(content)
    expected_aesthetics = [
        "Clean Minimalist",
        "Dark Mode Tech",
        "Bold Editorial",
        "Hand-Drawn Sketchnote",
        "Claymation Studio",
        "Lego Brick Builder",
    ]
    for aesthetic in expected_aesthetics:
        assert aesthetic in block, (
            f"Per-aesthetic table must include '{aesthetic}' but it was not found.\n"
            f"Actual step 6 block:\n{block}"
        )


def test_step6_table_has_connector_columns() -> None:
    """Per-aesthetic table must have Node shapes, Connector style, and Special constraints columns."""
    content = _read_agent()
    block = _get_step_6_block(content)
    lower = block.lower()
    assert "node shapes" in lower, "Table must have 'Node shapes' column header"
    assert "connector style" in lower, "Table must have 'Connector style' column header"
    assert "special constraints" in lower, "Table must have 'Special constraints' column header"


def test_step6_clean_minimalist_orthogonal_edges() -> None:
    """Clean Minimalist row must specify orthogonal-only edges (no diagonals)."""
    content = _read_agent()
    block = _get_step_6_block(content).lower()
    assert "orthogonal" in block, (
        "Clean Minimalist row must specify 'orthogonal' connector style.\n"
        f"Actual step 6 block:\n{block}"
    )


def test_step6_dark_mode_no_duplicate_legend() -> None:
    """Dark Mode Tech row must warn against duplicate legends."""
    content = _read_agent()
    block = _get_step_6_block(content).lower()
    assert "do not duplicate" in block or "don't duplicate" in block, (
        "Dark Mode Tech row must warn against duplicate legends.\n"
        f"Actual step 6 block:\n{block}"
    )


def test_step6_has_color_category_mapping_rule() -> None:
    """Step 6 must include a color-category mapping rule about semantic legends."""
    content = _read_agent()
    block = _get_step_6_block(content).lower()
    assert "color-category mapping" in block, (
        "Step 6 must mention 'color-category mapping' rule.\n"
        f"Actual step 6 block:\n{block}"
    )
    assert "semantic color legend" in block, (
        "Color-category mapping rule must mention 'semantic color legend'.\n"
        f"Actual step 6 block:\n{block}"
    )
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `pytest tests/test_diagram_beautifier_agent.py::test_step6_has_per_aesthetic_table tests/test_diagram_beautifier_agent.py::test_step6_table_has_connector_columns tests/test_diagram_beautifier_agent.py::test_step6_clean_minimalist_orthogonal_edges tests/test_diagram_beautifier_agent.py::test_step6_dark_mode_no_duplicate_legend tests/test_diagram_beautifier_agent.py::test_step6_has_color_category_mapping_rule -v`
Expected: All 5 PASS (implementation already done in Task 2)

- [ ] **Step 3: Run full test suite**

Run: `pytest tests/test_diagram_beautifier_agent.py -v`
Expected: All tests PASS

- [ ] **Step 4: Commit**

```bash
git add tests/test_diagram_beautifier_agent.py
git commit -m "test: add coverage for per-aesthetic table and color-category mapping in Step 6"
```

---

### Task 4: Add `## Diagram Generation` section to `docs/style-guide.md`

**Files:**
- Create: `tests/test_style_guide_diagram_generation.py`
- Modify: `docs/style-guide.md:152-153` (insert between `## Diorama Mode` and `## Layout Types`)

- [ ] **Step 1: Write the failing tests**

Create `tests/test_style_guide_diagram_generation.py` with this content:

```python
"""Tests for the Diagram Generation section in docs/style-guide.md.

Acceptance criteria:
1. A new '## Diagram Generation' section exists between '## Diorama Mode' and '## Layout Types'.
2. The section includes a scoping statement limiting it to diagram beautification only.
3. The section includes the prompt ordering rule (aesthetic first, structural second).
4. The section includes the quality bar directive ('publication quality').
5. The section references the per-aesthetic table in diagram-beautifier.md.
"""

import re

from helpers import H2_LAYOUT_TYPES, read_guide

H2_DIAGRAM_GENERATION = "## Diagram Generation"
H2_DIORAMA_MODE = "## Diorama Mode"


def _get_diagram_generation_section(content: str) -> str:
    """Extract the Diagram Generation section (from its H2 to the next H2)."""
    start = content.index(H2_DIAGRAM_GENERATION)
    next_h2 = re.search(r"\n## ", content[start + len(H2_DIAGRAM_GENERATION):])
    end = start + len(H2_DIAGRAM_GENERATION) + next_h2.start() if next_h2 else len(content)
    return content[start:end]


# ---------------------------------------------------------------------------
# Criterion 1: Section exists in the correct position
# ---------------------------------------------------------------------------


def test_diagram_generation_section_exists() -> None:
    """Style guide must have a '## Diagram Generation' section."""
    content = read_guide()
    assert H2_DIAGRAM_GENERATION in content, (
        f"'{H2_DIAGRAM_GENERATION}' section not found in style guide."
    )


def test_diagram_generation_after_diorama_before_layout() -> None:
    """'## Diagram Generation' must appear after '## Diorama Mode' and before '## Layout Types'."""
    content = read_guide()
    diorama_pos = content.index(H2_DIORAMA_MODE)
    diagram_gen_pos = content.index(H2_DIAGRAM_GENERATION)
    layout_pos = content.index(H2_LAYOUT_TYPES)
    assert diorama_pos < diagram_gen_pos < layout_pos, (
        f"Section ordering wrong: Diorama Mode ({diorama_pos}), "
        f"Diagram Generation ({diagram_gen_pos}), Layout Types ({layout_pos})"
    )


# ---------------------------------------------------------------------------
# Criterion 2: Scoping statement
# ---------------------------------------------------------------------------


def test_diagram_generation_scoped_to_diagram_beautifier() -> None:
    """Section must state it applies ONLY to diagram beautification."""
    content = read_guide()
    section = _get_diagram_generation_section(content).lower()
    assert "diagram beautif" in section, (
        "Section must mention 'diagram beautification' in scoping statement."
    )
    assert "only" in section, (
        "Section must include 'only' to explicitly scope to diagram beautification."
    )


# ---------------------------------------------------------------------------
# Criterion 3: Prompt ordering rule
# ---------------------------------------------------------------------------


def test_diagram_generation_prompt_ordering() -> None:
    """Section must specify aesthetic directive FIRST, structural preservation SECOND."""
    content = read_guide()
    section = _get_diagram_generation_section(content).lower()
    assert "aesthetic" in section and "first" in section, (
        "Section must state aesthetic directive comes FIRST."
    )


# ---------------------------------------------------------------------------
# Criterion 4: Quality bar directive
# ---------------------------------------------------------------------------


def test_diagram_generation_quality_bar() -> None:
    """Section must include the quality bar directive about 'publication quality'."""
    content = read_guide()
    section = _get_diagram_generation_section(content).lower()
    assert "publication quality" in section, (
        "Section must mention 'publication quality' in the quality bar directive."
    )


# ---------------------------------------------------------------------------
# Criterion 5: Reference back to diagram-beautifier.md
# ---------------------------------------------------------------------------


def test_diagram_generation_references_diagram_beautifier() -> None:
    """Section must reference the per-aesthetic table in diagram-beautifier.md."""
    content = read_guide()
    section = _get_diagram_generation_section(content).lower()
    assert "diagram-beautifier" in section, (
        "Section must reference 'diagram-beautifier' for the per-aesthetic table."
    )
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_style_guide_diagram_generation.py -v`
Expected: All 6 tests FAIL — `ValueError: substring not found` (section doesn't exist yet)

- [ ] **Step 3: Add the Diagram Generation section to the style guide**

In `docs/style-guide.md`, find this text (around line 152):

```markdown
If the user asks for a **"diorama"**, frame the prompt as characters acting
out a scene. Dioramas work best for linear sequential workflows.

## Layout Types
```

Replace it with:

```markdown
If the user asks for a **"diorama"**, frame the prompt as characters acting
out a scene. Dioramas work best for linear sequential workflows.

## Diagram Generation

> This section applies ONLY to diagram beautification (the `diagram-beautifier`
> agent). Infographic generation does not use this section.

When generating beautified diagrams, follow these rules in every generation
prompt:

**Quality bar directive** — include at the top of every diagram generation
prompt:

> "This should be dramatically more visually impressive than the source
> diagram — publication quality, not just a recolored version."

**Prompt ordering:** Aesthetic directive FIRST, structural preservation
SECOND. VLM models respond better when the visual direction leads and
structural constraints follow.

**Per-aesthetic shape and connector guidance:** The authoritative table of
node shapes, connector styles, and special constraints per aesthetic lives
in `agents/diagram-beautifier.md` under the `### Diagram Generation Guidance`
subsection. Refer to that table when constructing diagram generation prompts.

## Layout Types
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_style_guide_diagram_generation.py -v`
Expected: All 6 tests PASS

- [ ] **Step 5: Run all style-guide tests to confirm no regressions**

Run: `pytest tests/test_style_guide_aesthetics.py tests/test_style_guide_layouts.py tests/test_style_guide_diagram_generation.py -v`
Expected: All tests PASS across all 3 test files

- [ ] **Step 6: Commit**

```bash
git add docs/style-guide.md tests/test_style_guide_diagram_generation.py
git commit -m "feat: add Diagram Generation section to style guide with quality bar and prompt ordering rules"
```

---

### Task 5: Final validation — full test suite

**Files:** (none modified — verification only)

- [ ] **Step 1: Run the entire test suite**

Run: `pytest tests/ -v`
Expected: All tests PASS — no regressions across the entire project

- [ ] **Step 2: Verify the two modified files look correct**

Run:
```bash
grep -n "color-category fidelity" agents/diagram-beautifier.md
grep -n "### Diagram Generation Guidance" agents/diagram-beautifier.md
grep -n "## Diagram Generation" docs/style-guide.md
```

Expected:
- `color-category fidelity` appears once in Step 7 of `agents/diagram-beautifier.md`
- `### Diagram Generation Guidance` appears once in Step 6 of `agents/diagram-beautifier.md`
- `## Diagram Generation` appears once in `docs/style-guide.md`
