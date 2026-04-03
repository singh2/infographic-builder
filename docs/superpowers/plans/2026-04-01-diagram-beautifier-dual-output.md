# Diagram Beautifier Dual-Output (Polished + Cinematic) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the diagram-beautifier from "aesthetic coating" to "visual translation" by introducing a topology manifest layer and dual-output generation (Polished + Cinematic always produced together, presented side-by-side).

**Architecture:** Extract topology to a structured text manifest → use that manifest as the structural spec for two independent generation passes (Polished and Cinematic) → quality review both independently → present side-by-side. No reference image is passed to the Cinematic path. For Polished, the reference image (PNG input only) is passed with an explicit completeness-only guard.

**Tech Stack:** pytest >= 8.0, Python >= 3.11. All tests are text assertions on markdown files — no mocking, no network calls. Tests read `.md` files and assert on text content.

**Design spec:** `docs/superpowers/specs/2026-04-01-diagram-beautifier-dual-output-design.md`

---

## File Map

| Action | File | Responsibility |
|--------|------|----------------|
| Modify | `agents/diagram-beautifier.md` | Restructure workflow: add semantic extraction, remove render step, split beautify/review into Polished+Cinematic, update output format |
| Modify | `tests/test_diagram_beautifier_agent.py` | Rename existing step helpers/tests for renumbering, add new tests for all changed steps |
| Modify | `docs/diagram-style-guide.md` | Add Polished vs Cinematic philosophy section and per-aesthetic Cinematic guidance |
| Modify | `tests/test_diagram_style_guide.py` | Add tests for new style guide sections |

---

## Important Context

**Current step structure** in `agents/diagram-beautifier.md`:
```
1. Parse / analyze        5. Panel decomposition     9. Return results
2. Dependency check       6. Beautify
3. Aesthetic selection     7. Quality review
4. Render to plain PNG    8. Assemble
```

**After all changes:**
```
1. Parse / analyze + semantic extraction     5. Beautify (5a Polished, 5b Cinematic)
2. Dependency check                          6. Quality review (6a Polished, 6b Cinematic)
3. Aesthetic selection                       7. Assemble
4. Panel decomposition                      8. Present side-by-side
```

Step 4 (Render to plain PNG) is **removed**. Old 5→4, 6→5, 7→6, 8→7, 9→8.

**Existing test count:** 276 passing (24 in `test_diagram_beautifier_agent.py`, 9 in `test_diagram_style_guide.py`).

**Test patterns to follow** — all tests in these files use this style:
```python
AGENT_FILE = Path(__file__).parent.parent / "agents" / "diagram-beautifier.md"

def _read_agent() -> str:
    return AGENT_FILE.read_text(encoding="utf-8")

def _get_step_N_block(content: str) -> str:
    start = content.find("N. **Step Title**")
    assert start != -1, "Step N header not found"
    end = content.find("N+1. **Next Step**", start)
    return content[start:end] if end != -1 else content[start:]
```

---

### Task 1: Add semantic extraction to Step 1

**Files:**
- Modify: `tests/test_diagram_beautifier_agent.py` (add helper + 3 tests)
- Modify: `agents/diagram-beautifier.md` (Step 1, around line 128)

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_diagram_beautifier_agent.py`:

```python
def _get_step_1_block(content: str) -> str:
    start = content.find("1. **Parse the source")
    assert start != -1, "Step 1 header not found"
    end = content.find("2. **Dependency check", start)
    return content[start:end] if end != -1 else content[start:]


def test_step1_mentions_topology_manifest() -> None:
    """Step 1 must describe producing a topology manifest."""
    content = _read_agent()
    block = _get_step_1_block(content)
    assert "topology manifest" in block.lower(), (
        "Step 1 must mention 'topology manifest'.\n"
        f"Actual block:\n{block}"
    )


def test_step1_mentions_hero_candidate() -> None:
    """Step 1 must describe identifying a hero candidate node."""
    content = _read_agent()
    block = _get_step_1_block(content)
    assert "hero candidate" in block.lower(), (
        "Step 1 must mention 'hero candidate'.\n"
        f"Actual block:\n{block}"
    )


def test_step1_lists_semantic_node_types() -> None:
    """Step 1 must list semantic node types: terminal, decision, process."""
    content = _read_agent()
    block = _get_step_1_block(content)
    lower = block.lower()
    assert "terminal" in lower, f"Step 1 must mention 'terminal' node type.\nActual block:\n{block}"
    assert "decision" in lower, f"Step 1 must mention 'decision' node type.\nActual block:\n{block}"
    assert "process" in lower, f"Step 1 must mention 'process' node type.\nActual block:\n{block}"
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run: `python3 -m pytest tests/test_diagram_beautifier_agent.py::test_step1_mentions_topology_manifest tests/test_diagram_beautifier_agent.py::test_step1_mentions_hero_candidate tests/test_diagram_beautifier_agent.py::test_step1_lists_semantic_node_types -v`
Expected: 3 FAILED — Step 1 doesn't mention "topology manifest", "hero candidate", or "terminal"/"decision"/"process" yet.

- [ ] **Step 3: Add semantic extraction to Step 1 in the agent file**

In `agents/diagram-beautifier.md`, find this text in Step 1 (around line 126–128):

```markdown
   **If input is `.dot` or Mermaid source text:**
   Use `diagram_beautifier.parser.parse_diagram_source()` to produce the
   normalized structure: nodes, edges, subgraphs, node_count, edge_count.
   Proceed through all 9 steps.
```

Replace with:

```markdown
   **If input is `.dot` or Mermaid source text:**
   Use `diagram_beautifier.parser.parse_diagram_source()` to produce the
   normalized structure: nodes, edges, subgraphs, node_count, edge_count.
   Proceed through the full workflow.

   **Semantic extraction** -- After parsing or analyzing, produce the topology manifest:

   - **Node inventory**: every node with semantic type -- `terminal` (start/end ovals), `decision` (diamonds), `process` (rectangles), `subprocess` (subgraph members)
   - **Connectivity profile**: nodes with 3+ edges are load-bearing; note them
   - **Critical path**: main trunk from entry terminal to exit terminal
   - **Semantic legend**: if a color-coded legend exists, map every category to its node names explicitly (e.g. "Script Steps: Check Environment, Discover Recipes, ...")
   - **Hero candidate**: the highest-connectivity decision node, or where branches converge -- this becomes the visual focal point for Cinematic generation
   - **Edge labels**: all text on connectors
   - **Subgroup structure**: any clusters that inform visual grouping

   Store this as plain text. It drives both generation prompts. The reference image no longer plays the structural spec role.
```

- [ ] **Step 4: Run all tests to verify they pass**

Run: `python3 -m pytest tests/test_diagram_beautifier_agent.py -v`
Expected: All 27 tests PASS (24 existing + 3 new).

- [ ] **Step 5: Commit**

```bash
git add tests/test_diagram_beautifier_agent.py agents/diagram-beautifier.md
git commit -m "feat: add semantic extraction / topology manifest to Step 1"
```

---

### Task 2: Remove Step 4, renumber all steps, update existing tests

This is the largest task because it touches many places in both files simultaneously. The agent file's step structure changes and the test file must stay in sync.

**Files:**
- Modify: `tests/test_diagram_beautifier_agent.py` (add 2 new tests, rename helpers/functions, remove 2 obsolete tests, update workflow test)
- Modify: `agents/diagram-beautifier.md` (remove Step 4, renumber 5→4 through 9→8, update meta/principles/input-types)

- [ ] **Step 1: Write the two new failing tests**

Append to `tests/test_diagram_beautifier_agent.py`:

```python
def test_step4_is_panel_decomposition() -> None:
    """After removing old Step 4 (render), Step 4 must be panel decomposition."""
    content = _read_agent()
    start = content.find("4. **Panel decomposition**")
    assert start != -1, (
        "Step 4 must be 'Panel decomposition' after renumbering.\n"
        "Could not find '4. **Panel decomposition**' in agent file."
    )


def test_no_render_step() -> None:
    """The 'Render to plain PNG' step must be completely removed."""
    content = _read_agent()
    assert "Render to plain PNG" not in content, (
        "The old 'Render to plain PNG' step must be removed entirely."
    )
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run: `python3 -m pytest tests/test_diagram_beautifier_agent.py::test_step4_is_panel_decomposition tests/test_diagram_beautifier_agent.py::test_no_render_step -v`
Expected: 2 FAILED — Step 4 is still "Render to plain PNG".

- [ ] **Step 3: Modify the agent file — remove Step 4 and renumber**

Make ALL of the following edits to `agents/diagram-beautifier.md`:

**Edit 3a — Frontmatter comment** (line 2):

Find:
```
# Workflow: 1-parse 2-dependency 3-aesthetic 4-render 5-decompose 6-beautify 7-review 8-assemble 9-return
```
Replace with:
```
# Workflow: 1-parse 2-dependency 3-aesthetic 4-decompose 5-beautify 6-review 7-assemble 8-present
```

**Edit 3b — Meta description** (lines 6–13):

Find:
```
  description: |
    Expert diagram beautifier that takes Graphviz (.dot), Mermaid diagram
    source files, or existing diagram PNGs and renders them as beautiful
    infographic-quality visuals
    using the existing visual styling system, preserving the original diagram's
    topology and labels. Uses a render-first architecture: renders plain PNG
    via CLI tools, then beautifies with nano-banana using the rendered image
    as a structural reference.
```
Replace with:
```
  description: |
    Expert diagram beautifier that takes Graphviz (.dot), Mermaid diagram
    source files, or existing diagram PNGs and transforms them into
    publication-quality visuals using a dual-output system. Extracts the
    diagram's topology into a structured manifest, then generates both
    Polished (document-ready) and Cinematic (presentation-ready) variants
    in the selected aesthetic, preserving topology and labels exactly.
```

**Edit 3c — Execution model** (lines 47–49):

Find:
```
**Execution model:** You run as a sub-session. Parse the diagram, verify
dependencies, render a plain reference PNG, then beautify using nano-banana
*(unless style selection is required -- see Step 3)*.
```
Replace with:
```
**Execution model:** You run as a sub-session. Parse the diagram, extract
the topology manifest, verify dependencies, then generate both Polished and
Cinematic variants using nano-banana *(unless style selection is required --
see Step 3)*.
```

**Edit 3d — Operating Principle 1** (lines 65–67):

Find:
```
1. **Render first, beautify second** -- always render the source to a plain PNG
   as the structural anchor before any beautification (for PNG input, the
   provided file serves as the structural anchor directly -- no render needed)
```
Replace with:
```
1. **Topology manifest first, generate second** -- always extract the diagram's
   structure into a topology manifest before any generation. The manifest (not
   a reference image) is the structural specification for both variants.
```

**Edit 3e — Input Types, source path** (line 79):

Find:
```
Steps 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 (full workflow)
```
Replace with:
```
Steps 1 → 2 → 3 → 4 → 5a/5b → 6a/6b → 7 → 8 (full workflow)
```

**Edit 3f — Input Types, PNG path** (lines 81–86):

Find:
```
**PNG path** (`.png` file):
- Step 1: Check for pre-computed analysis from root session first (see below)
- Step 2: **Skip** -- no CLI dependency needed
- Step 3: Aesthetic selection (same as source path)
- Step 4: **Skip render** -- use the `.png` directly as `reference_image_path`
- Steps 5 → 6 → 7 → 8 → 9: same as source path
```
Replace with:
```
**PNG path** (`.png` file):
- Step 1: Check for pre-computed analysis from root session first (see below)
- Step 2: **Skip** -- no CLI dependency needed
- Step 3: Aesthetic selection (same as source path)
- Steps 4 → 5a/5b → 6a/6b → 7 → 8: same as source path
  - For Polished (5a): the provided PNG is used as `reference_image_path` with completeness-only guard
  - For Cinematic (5b): no reference image is used
```

**Edit 3g — Step 1, pre-analysis path** (around lines 111–113):

Find (first occurrence in the PRE-ANALYSIS block):
```
   skip Steps 2 and 4.
```
Replace with:
```
   skip Step 2.
```

Find (second occurrence in the PNG-without-preanalysis block):
```
   Skip Steps 2 and 4 — proceed directly to Step 3 (aesthetic selection).
```
Replace with:
```
   Skip Step 2 — proceed directly to Step 3 (aesthetic selection).
```

**Edit 3h — Step 3, add dual-variant note** (around line 143):

Find:
```
   **Check for inline style specification.** If the user already described an
   aesthetic (e.g., "beautify in claymation style"), skip to step 4. This is
   the **two-turn shortcut**.
```
Replace with:
```
   **Check for inline style specification.** If the user already described an
   aesthetic (e.g., "beautify in claymation style"), skip to step 4. This is
   the **two-turn shortcut**.

   The selected aesthetic applies to both the Polished and Cinematic variants.
```

**Edit 3i — Remove Step 4 entirely** (lines 163–170):

Delete this entire block:
```
4. **Render to plain PNG** (source path only -- skip for PNG input): Render the
   source to a structurally faithful but visually plain PNG using the appropriate
   CLI tool:
   - Graphviz: `dot -Tpng -Gdpi=150 input.dot -o /tmp/diagram_plain.png`
   - Mermaid: `mmdc -i input.mmd -o /tmp/diagram_plain.png -w 2048 -H 1536 --scale 2`

   **For PNG input:** use the provided `.png` file directly as `reference_image_path`.
   No rendering step is needed -- the PNG is already the structural reference.

```

**Edit 3j — Renumber Step 5 → 4, add dual-variant note** (line 172):

Find:
```
5. **Panel decomposition**: Based on node count and subgraph structure, decide
```
Replace with:
```
4. **Panel decomposition**: Based on node count and subgraph structure, decide
```

Also find (at the end of the panel decomposition block):
```
   Use `diagram_beautifier.decompose.decide_panels()` for the decision.
```
Replace with:
```
   Use `diagram_beautifier.decompose.decide_panels()` for the decision.

   Run once. The result applies to both Polished and Cinematic variants.
```

**Edit 3k — Renumber Step 6 → 5:**

Find: `6. **Beautify**:`
Replace with: `5. **Beautify**:`

**Edit 3l — Renumber Step 7 → 6:**

Find: `7. **Quality review**:`
Replace with: `6. **Quality review**:`

**Edit 3m — Renumber Step 8 → 7:**

Find: `8. **Assemble**`
Replace with: `7. **Assemble**`

**Edit 3n — Renumber Step 9 → 8:**

Find: `9. **Return results**:`
Replace with: `8. **Return results**:`

- [ ] **Step 4: Update existing tests for renumbering**

Make ALL of the following edits to `tests/test_diagram_beautifier_agent.py`:

**Edit 4a — Rename `test_workflow_has_9_steps` → `test_workflow_has_8_steps`:**

Find:
```python
def test_workflow_has_9_steps() -> None:
    content = _read_agent()
    for n in range(1, 10):
        assert f"{n}. **" in content or f"{n}." in content, f"Step {n} not found"
```
Replace with:
```python
def test_workflow_has_8_steps() -> None:
    content = _read_agent()
    for n in range(1, 9):
        assert f"{n}. **" in content or f"{n}." in content, f"Step {n} not found"
```

**Edit 4b — Update `test_workflow_step_order` — remove "render" keyword:**

Find:
```python
    keywords_in_order = [
        "parse",
        "dependency",
        "aesthetic",
        "render",
        "decompos",
        "beautif",
        "review",
        "assembl",
        "return",
    ]
```
Replace with:
```python
    keywords_in_order = [
        "parse",
        "dependency",
        "aesthetic",
        "decompos",
        "beautif",
        "review",
        "assembl",
        "return",
    ]
```

**Edit 4c — Remove `test_agent_mentions_render_first`:**

Delete this entire function:
```python
def test_agent_mentions_render_first() -> None:
    content = _read_agent()
    lower = content.lower()
    assert "render" in lower and "reference" in lower
```

**Edit 4d — Remove `test_agent_skips_render_for_png`:**

Delete this entire function:
```python
def test_agent_skips_render_for_png() -> None:
    """Agent must mention skipping the render step for PNG input."""
    content = _read_agent()
    lower = content.lower()
    assert "skip" in lower and "png" in lower and "render" in lower
```

**Edit 4e — Rename `_get_step_6_block` → `_get_step_5_block`, update search strings:**

Find:
```python
def _get_step_6_block(content: str) -> str:
    start = content.find("6. **Beautify**")
    assert start != -1, "Step 6 header '6. **Beautify**' not found in agent file"
    end = content.find("7. **Quality review**", start)
    return content[start:end] if end != -1 else content[start:]
```
Replace with:
```python
def _get_step_5_block(content: str) -> str:
    start = content.find("5. **Beautify**")
    assert start != -1, "Step 5 header '5. **Beautify**' not found in agent file"
    end = content.find("6. **Quality review**", start)
    return content[start:end] if end != -1 else content[start:]
```

**Edit 4f — Rename `_get_step_7_block` → `_get_step_6_block`, update search strings:**

Find:
```python
def _get_step_7_block(content: str) -> str:
    start = content.find("7. **Quality review**")
    assert start != -1, "Step 7 header '7. **Quality review**' not found in agent file"
    end = content.find("8. **Assemble**", start)
    return content[start:end] if end != -1 else content[start:]
```
Replace with:
```python
def _get_step_6_block(content: str) -> str:
    start = content.find("6. **Quality review**")
    assert start != -1, "Step 6 header '6. **Quality review**' not found in agent file"
    end = content.find("7. **Assemble**", start)
    return content[start:end] if end != -1 else content[start:]
```

**Edit 4g — Rename `test_step6_has_quality_bar_directive` → `test_step5_has_quality_bar_directive`, use `_get_step_5_block`:**

Find:
```python
def test_step6_has_quality_bar_directive() -> None:
    """Step 6 must include a quality bar directive about being dramatically more
    visually impressive or publication quality."""
    content = _read_agent()
    block = _get_step_6_block(content)
    assert (
        "dramatically more visually impressive" in block
        or "publication quality" in block
    ), (
        "Step 6 must include a quality bar directive "
        "('dramatically more visually impressive' or 'publication quality').\n"
        f"Actual step 6 block:\n{block}"
    )
```
Replace with:
```python
def test_step5_has_quality_bar_directive() -> None:
    """Step 5 must include a quality bar directive about being dramatically more
    visually impressive or publication quality."""
    content = _read_agent()
    block = _get_step_5_block(content)
    assert (
        "dramatically more visually impressive" in block
        or "publication quality" in block
    ), (
        "Step 5 must include a quality bar directive "
        "('dramatically more visually impressive' or 'publication quality').\n"
        f"Actual step 5 block:\n{block}"
    )
```

**Edit 4h — Rename `test_step6_prompt_construction_order_aesthetic_before_structural` → `test_step5_prompt_construction_order_aesthetic_before_structural`, use `_get_step_5_block`:**

Find:
```python
def test_step6_prompt_construction_order_aesthetic_before_structural() -> None:
    """Step 6 must describe aesthetic properties before structural preservation,
    and both must be present."""
    content = _read_agent()
    block = _get_step_6_block(content)
    assert "aesthetic properties" in block.lower(), (
        f"Step 6 must mention 'aesthetic properties'.\nActual step 6 block:\n{block}"
    )
    assert "structural preservation" in block.lower(), (
        f"Step 6 must mention 'structural preservation'.\nActual step 6 block:\n{block}"
    )
    aesthetic_pos = block.lower().find("aesthetic properties")
    structural_pos = block.lower().find("structural preservation")
    assert aesthetic_pos < structural_pos, (
        "Step 6 must list 'aesthetic properties' before 'structural preservation'.\n"
        f"aesthetic_pos={aesthetic_pos}, structural_pos={structural_pos}\n"
        f"Actual step 6 block:\n{block}"
    )
```
Replace with:
```python
def test_step5_prompt_construction_order_aesthetic_before_structural() -> None:
    """Step 5 must describe aesthetic properties before structural preservation,
    and both must be present."""
    content = _read_agent()
    block = _get_step_5_block(content)
    assert "aesthetic properties" in block.lower(), (
        f"Step 5 must mention 'aesthetic properties'.\nActual step 5 block:\n{block}"
    )
    assert "structural preservation" in block.lower(), (
        f"Step 5 must mention 'structural preservation'.\nActual step 5 block:\n{block}"
    )
    aesthetic_pos = block.lower().find("aesthetic properties")
    structural_pos = block.lower().find("structural preservation")
    assert aesthetic_pos < structural_pos, (
        "Step 5 must list 'aesthetic properties' before 'structural preservation'.\n"
        f"aesthetic_pos={aesthetic_pos}, structural_pos={structural_pos}\n"
        f"Actual step 5 block:\n{block}"
    )
```

**Edit 4i — Rename `test_step6_references_diagram_style_guide` → `test_agent_references_diagram_style_guide`:**

(This test checks the full file, not a step block, so the name should reflect that.)

Find:
```python
def test_step6_references_diagram_style_guide() -> None:
    """The agent file must reference 'diagram-style-guide.md' in the Design Knowledge section."""
    content = _read_agent()
    assert "diagram-style-guide.md" in content, (
        "Agent file must reference 'diagram-style-guide.md' in Design Knowledge section."
    )
```
Replace with:
```python
def test_agent_references_diagram_style_guide() -> None:
    """The agent file must reference 'diagram-style-guide.md' in the Design Knowledge section."""
    content = _read_agent()
    assert "diagram-style-guide.md" in content, (
        "Agent file must reference 'diagram-style-guide.md' in Design Knowledge section."
    )
```

**Edit 4j — Rename `test_step7_has_color_category_fidelity_dimension` → `test_step6_has_color_category_fidelity_dimension`, use `_get_step_6_block`:**

Find:
```python
def test_step7_has_color_category_fidelity_dimension() -> None:
    """Step 7 must include 'color-category fidelity' as an 8th quality dimension."""
    content = _read_agent()
    block = _get_step_7_block(content)
    assert "color-category fidelity" in block.lower(), (
        "Step 7 must include 'color-category fidelity' dimension.\n"
        f"Actual step 7 block:\n{block}"
    )
```
Replace with:
```python
def test_step6_has_color_category_fidelity_dimension() -> None:
    """Step 6 must include 'color-category fidelity' as an 8th quality dimension."""
    content = _read_agent()
    block = _get_step_6_block(content)
    assert "color-category fidelity" in block.lower(), (
        "Step 6 must include 'color-category fidelity' dimension.\n"
        f"Actual step 6 block:\n{block}"
    )
```

**Edit 4k — Rename `test_step7_color_category_fidelity_scoped_to_legend_diagrams` → `test_step6_color_category_fidelity_scoped_to_legend_diagrams`, use `_get_step_6_block`:**

Find:
```python
def test_step7_color_category_fidelity_scoped_to_legend_diagrams() -> None:
    """Color-category fidelity must be scoped to diagrams with a semantic legend."""
    content = _read_agent()
    block = _get_step_7_block(content)
    assert "semantic legend" in block.lower(), (
        "Step 7 color-category fidelity must be scoped with 'semantic legend' qualifier.\n"
        f"Actual step 7 block:\n{block}"
    )
```
Replace with:
```python
def test_step6_color_category_fidelity_scoped_to_legend_diagrams() -> None:
    """Color-category fidelity must be scoped to diagrams with a semantic legend."""
    content = _read_agent()
    block = _get_step_6_block(content)
    assert "semantic legend" in block.lower(), (
        "Step 6 color-category fidelity must be scoped with 'semantic legend' qualifier.\n"
        f"Actual step 6 block:\n{block}"
    )
```

- [ ] **Step 5: Run the two new tests to verify they pass**

Run: `python3 -m pytest tests/test_diagram_beautifier_agent.py::test_step4_is_panel_decomposition tests/test_diagram_beautifier_agent.py::test_no_render_step -v`
Expected: 2 PASSED.

- [ ] **Step 6: Run the full test suite to confirm no regressions**

Run: `python3 -m pytest -x -q`
Expected: 276 passed (count unchanged: +2 new, -2 removed = net 0).

- [ ] **Step 7: Commit**

```bash
git add agents/diagram-beautifier.md tests/test_diagram_beautifier_agent.py
git commit -m "refactor: remove render step, renumber workflow steps 5-9 → 4-8"
```

---

### Task 3: Split Step 5 into 5a Polished and 5b Cinematic

This is the core generation split. The current Step 5 "Beautify" gets two sub-paths.

**Files:**
- Modify: `tests/test_diagram_beautifier_agent.py` (add 6 tests)
- Modify: `agents/diagram-beautifier.md` (replace Step 5 content, update nano-banana table)

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_diagram_beautifier_agent.py`:

```python
def test_step5_has_polished_subsection() -> None:
    """Step 5 must have a Polished subsection labelled 5a."""
    content = _read_agent()
    block = _get_step_5_block(content)
    assert "5a" in block, f"Step 5 must contain '5a' for Polished.\nActual block:\n{block}"
    assert "polished" in block.lower(), f"Step 5 must mention 'Polished'.\nActual block:\n{block}"


def test_step5_has_cinematic_subsection() -> None:
    """Step 5 must have a Cinematic subsection labelled 5b."""
    content = _read_agent()
    block = _get_step_5_block(content)
    assert "5b" in block, f"Step 5 must contain '5b' for Cinematic.\nActual block:\n{block}"
    assert "cinematic" in block.lower(), f"Step 5 must mention 'Cinematic'.\nActual block:\n{block}"


def test_step5_cinematic_has_no_reference_image() -> None:
    """Step 5 Cinematic must explicitly state no reference image is used."""
    content = _read_agent()
    block = _get_step_5_block(content)
    assert "no `reference_image_path`" in block.lower() or "no reference image" in block.lower(), (
        "Step 5 Cinematic must state 'No reference_image_path' or 'no reference image'.\n"
        f"Actual block:\n{block}"
    )


def test_step5_cinematic_has_hero_element_instruction() -> None:
    """Step 5 Cinematic must designate a hero element as the visual focal point."""
    content = _read_agent()
    block = _get_step_5_block(content)
    lower = block.lower()
    assert "hero" in lower, f"Step 5 must mention 'hero' element.\nActual block:\n{block}"
    assert "focal point" in lower, f"Step 5 must mention 'focal point'.\nActual block:\n{block}"


def test_step5_cinematic_has_spatial_freedom_statement() -> None:
    """Step 5 Cinematic must include a spatial freedom statement."""
    content = _read_agent()
    block = _get_step_5_block(content)
    lower = block.lower()
    assert "spatial freedom" in lower or "not bound by the original" in lower, (
        "Step 5 Cinematic must include 'spatial freedom' or 'not bound by the original'.\n"
        f"Actual block:\n{block}"
    )


def test_step5_polished_has_reference_image_guard() -> None:
    """Step 5 Polished must describe the reference image guard for PNG input."""
    content = _read_agent()
    block = _get_step_5_block(content)
    lower = block.lower()
    assert "completeness" in lower or "verify no nodes" in lower, (
        "Step 5 Polished must describe reference image guard "
        "('completeness' or 'verify no nodes').\n"
        f"Actual block:\n{block}"
    )
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run: `python3 -m pytest tests/test_diagram_beautifier_agent.py::test_step5_has_polished_subsection tests/test_diagram_beautifier_agent.py::test_step5_has_cinematic_subsection tests/test_diagram_beautifier_agent.py::test_step5_cinematic_has_no_reference_image tests/test_diagram_beautifier_agent.py::test_step5_cinematic_has_hero_element_instruction tests/test_diagram_beautifier_agent.py::test_step5_cinematic_has_spatial_freedom_statement tests/test_diagram_beautifier_agent.py::test_step5_polished_has_reference_image_guard -v`
Expected: 6 FAILED — Step 5 doesn't have Polished/Cinematic subsections yet.

- [ ] **Step 3: Replace Step 5 content in the agent file**

In `agents/diagram-beautifier.md`, find the entire Step 5 block — everything from `5. **Beautify**:` up to (but not including) `6. **Quality review**:`. Replace with:

```markdown
5. **Beautify**: Generate both variants. Steps 5a and 5b can run in parallel.

   **5a. Polished**

   Prompt construction (in this order):
   1. **Quality bar** (always first): "This should be dramatically more visually
      impressive than the source — publication quality, not a recolored version."
   2. **Aesthetic properties** (second): background, node style, typography, color
      palette, lighting, texture, mood from the selected aesthetic template
   3. **Node shape and connector guidance** (third): use the per-aesthetic
      shape and connector table in the Diagram Style Guide. Apply the exact shape
      and connector spec for the selected aesthetic.
   4. **Color-category mapping** (fourth): if the source has a semantic color
      legend, explicitly list every category and its node names. Do not rely on
      the reference image alone — state it explicitly.
   5. **Structural preservation** (last): "Preserve exact topology: N nodes,
      [layout direction] flow. Labels: [all node labels listed]. All connections
      must be maintained."

   For **PNG input**: pass the provided PNG as `reference_image_path` with this
   guard: "Use this image ONLY to verify that no nodes or connections were missed.
   Do not replicate its proportions, spacing, arrow lengths, visual style, or
   layout algorithm. Draw this fresh."
   For **source input**: do NOT pass any `reference_image_path`.

   **Multi-panel path (Polished):**
   - Panel 1 generated first (style anchor)
   - Call `nano-banana analyze` on Panel 1 for style reconciliation
   - Panels 2-N reference Panel 1 for style consistency AND their own
     subgraph structure via the structural preservation modifier

   **5b. Cinematic**

   No `reference_image_path` -- ever, for any input type.

   Prompt construction (in this order):
   1. **Quality bar**: "Create something visually striking and memorable — not a
      diagram that looks better, but something that makes someone stop and look.
      The structure is the script. The aesthetic is the medium."
   2. **Hero element**: "[hero candidate from manifest] is the visual focal point
      of this composition. Give it emphasis, scale, or treatment that surrounding
      nodes don't have."
   3. **Aesthetic properties** from the selected template
   4. **Connector vocabulary** (aesthetic-native — see Diagram Style Guide
      Cinematic section):
      - Clean Minimalist: sweeping arcs, not orthogonal segments
      - Dark Mode Tech: glowing bezier curves from source-node to destination-node color
      - Sketchnote: wobbly gestural ink arrows
      - Claymation: rope or ribbon connectors
      - Lego: rigid brick-peg connector rods
      - Bold Editorial: heavy directional strokes
   5. **Color-category mapping** (same as 5a)
   6. **Spatial freedom**: "Node positions should serve the visual composition and
      chosen aesthetic. You are not bound by the original diagram's layout
      proportions, spacing, or flow algorithm."
   7. **Structural preservation** (same as 5a)

   **Multi-panel path (Cinematic):**
   - Same decomposition as Polished (from Step 4)
   - Panel 1 generated first (style anchor)
   - Panels 2-N reference Panel 1 for style consistency

```

Also update the **Using nano-banana generate** table. Find:

```markdown
| `reference_image_path` | **yes** | Plain rendered PNG (structural anchor) |
```
Replace with:
```markdown
| `reference_image_path` | conditional | Polished + PNG input only (completeness guard). Never for Cinematic. |
```

- [ ] **Step 4: Run all tests to verify they pass**

Run: `python3 -m pytest tests/test_diagram_beautifier_agent.py -v`
Expected: 33 PASSED (27 after Tasks 1+2, plus 6 new).

- [ ] **Step 5: Commit**

```bash
git add agents/diagram-beautifier.md tests/test_diagram_beautifier_agent.py
git commit -m "feat: split Step 5 into Polished and Cinematic generation paths"
```

---

### Task 4: Split Step 6 into 6a and 6b quality reviews

**Files:**
- Modify: `tests/test_diagram_beautifier_agent.py` (add 4 tests)
- Modify: `agents/diagram-beautifier.md` (replace Step 6 content)

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_diagram_beautifier_agent.py`:

```python
def test_step6_has_polished_review_subsection() -> None:
    """Step 6 must have a Polished quality review subsection labelled 6a."""
    content = _read_agent()
    block = _get_step_6_block(content)
    assert "6a" in block, f"Step 6 must contain '6a' for Polished review.\nActual block:\n{block}"
    assert "polished" in block.lower(), f"Step 6 must mention 'Polished'.\nActual block:\n{block}"


def test_step6_has_cinematic_review_subsection() -> None:
    """Step 6 must have a Cinematic quality review subsection labelled 6b."""
    content = _read_agent()
    block = _get_step_6_block(content)
    assert "6b" in block, f"Step 6 must contain '6b' for Cinematic review.\nActual block:\n{block}"
    assert "cinematic" in block.lower(), f"Step 6 must mention 'Cinematic'.\nActual block:\n{block}"


def test_step6_cinematic_names_manifest_as_ground_truth() -> None:
    """Step 6 Cinematic review must name the topology manifest as sole ground truth."""
    content = _read_agent()
    block = _get_step_6_block(content)
    lower = block.lower()
    assert "sole ground truth" in lower or "topology manifest is the" in lower, (
        "Step 6 Cinematic review must name topology manifest as 'sole ground truth'.\n"
        f"Actual block:\n{block}"
    )


def test_step6_cinematic_has_missing_node_refinement_instruction() -> None:
    """Step 6 Cinematic must describe what to do when nodes are missing."""
    content = _read_agent()
    block = _get_step_6_block(content)
    lower = block.lower()
    assert "missing" in lower, f"Step 6 must mention 'missing' nodes.\nActual block:\n{block}"
    assert "refinement" in lower, f"Step 6 must mention 'refinement' pass.\nActual block:\n{block}"
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run: `python3 -m pytest tests/test_diagram_beautifier_agent.py::test_step6_has_polished_review_subsection tests/test_diagram_beautifier_agent.py::test_step6_has_cinematic_review_subsection tests/test_diagram_beautifier_agent.py::test_step6_cinematic_names_manifest_as_ground_truth tests/test_diagram_beautifier_agent.py::test_step6_cinematic_has_missing_node_refinement_instruction -v`
Expected: 4 FAILED — Step 6 doesn't have 6a/6b subsections yet.

- [ ] **Step 3: Replace Step 6 content in the agent file**

In `agents/diagram-beautifier.md`, find the entire Step 6 block — everything from `6. **Quality review**:` up to (but not including) `7. **Assemble**`. Replace with:

```markdown
6. **Quality review**: Run independently for each variant.

   **6a. Polished quality review**

   Analyze using `nano-banana analyze` with the same 8 dimensions:
   - Standard 5 dimensions (content accuracy, layout quality, visual clarity,
     prompt fidelity, aesthetic fidelity)
   - **Label fidelity** -- check all text labels against topology manifest
     ground truth
   - **Structural accuracy** -- verify node count and major connections against
     manifest
   - **Color-category fidelity** (diagrams with a semantic legend only): for
     each category in the original legend (e.g. Script Step, AI Agent Step,
     Condition, Start/End), verify that the same node names appear under the
     same category in the output. Flag any node whose category assignment
     changed from the source.

   Max 1 refinement pass. Target only specific issues identified.

   **6b. Cinematic quality review**

   Same 8 dimensions. **The topology manifest is the sole ground truth** --
   there is no reference image fallback. This quality review is the primary
   confidence mechanism for the Cinematic path.

   If any nodes are missing, the refinement pass re-prompts with: "The
   following nodes from the topology manifest are absent from the output:
   [missing node names]. Include all of them."

   Max 1 refinement pass.

```

- [ ] **Step 4: Run all tests to verify they pass**

Run: `python3 -m pytest tests/test_diagram_beautifier_agent.py -v`
Expected: 37 PASSED (33 from Task 3 + 4 new).

- [ ] **Step 5: Commit**

```bash
git add agents/diagram-beautifier.md tests/test_diagram_beautifier_agent.py
git commit -m "feat: split Step 6 into independent Polished and Cinematic quality reviews"
```

---

### Task 5: Update Step 8 to side-by-side output presentation

**Files:**
- Modify: `tests/test_diagram_beautifier_agent.py` (add helper + 3 tests, update `test_workflow_step_order`)
- Modify: `agents/diagram-beautifier.md` (replace Step 8 content, update Output Contract)

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_diagram_beautifier_agent.py`:

```python
def _get_step_8_block(content: str) -> str:
    start = content.find("8. **Present side-by-side**")
    assert start != -1, "Step 8 header '8. **Present side-by-side**' not found in agent file"
    return content[start:]


def test_step8_is_present_side_by_side() -> None:
    """Step 8 header must be 'Present side-by-side'."""
    content = _read_agent()
    assert "8. **Present side-by-side**" in content, (
        "Step 8 must have header 'Present side-by-side'."
    )


def test_step8_mentions_both_variants() -> None:
    """Step 8 must mention both Polished and Cinematic variants."""
    content = _read_agent()
    block = _get_step_8_block(content)
    assert "polished" in block.lower(), f"Step 8 must mention 'Polished'.\nActual block:\n{block}"
    assert "cinematic" in block.lower(), f"Step 8 must mention 'Cinematic'.\nActual block:\n{block}"


def test_step8_offers_refinement_options() -> None:
    """Step 8 must offer refinement options to the user."""
    content = _read_agent()
    block = _get_step_8_block(content)
    assert "refine" in block.lower(), (
        "Step 8 must offer refinement options (mention 'refine').\n"
        f"Actual block:\n{block}"
    )
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run: `python3 -m pytest tests/test_diagram_beautifier_agent.py::test_step8_is_present_side_by_side tests/test_diagram_beautifier_agent.py::test_step8_mentions_both_variants tests/test_diagram_beautifier_agent.py::test_step8_offers_refinement_options -v`
Expected: 3 FAILED — Step 8 still says "Return results".

- [ ] **Step 3: Replace Step 8 content and update related sections in the agent file**

In `agents/diagram-beautifier.md`, find the Step 8 line:

```markdown
8. **Return results**: image path(s) + design rationale + quality review summary
   (including label fidelity and structural accuracy results) + suggestions for
   next steps
```

Replace with:

```markdown
8. **Present side-by-side**: Output both variants together. No upfront mode
   choice was required -- the user responds to what they see.

   Present:
   - **Polished** -- [path] -- [two-sentence design rationale: what aesthetic
     properties were applied and why the selected layout serves this diagram type]
   - **Cinematic** -- [path] -- [two-sentence design rationale: what creative
     choices were made and what the hero element is]

   Then offer:
   - Pick one for refinement ("refine the Polished" / "refine the Cinematic")
   - Request a different aesthetic (both variants regenerated)
   - Request adjustments to either variant specifically
```

Also update the **Output Contract** section. Find:

```markdown
## Output Contract

Your response MUST include:
- The generated image path(s) (or a clear error if generation failed)
- A brief design rationale (2-4 sentences)
- Quality review summary (standard dimensions + label fidelity + structural accuracy + color-category fidelity for legend diagrams)
- Suggested next steps
```

Replace with:

```markdown
## Output Contract

Your response MUST include:
- Both variant image paths (Polished + Cinematic), or a clear error if generation failed
- A two-sentence design rationale per variant
- Quality review summary per variant (standard dimensions + label fidelity + structural accuracy + color-category fidelity for legend diagrams)
- Refinement options (pick one, request different aesthetic, or adjust either)
```

Also update `test_workflow_step_order` — change "return" to "present" in the keywords list.

Find in `tests/test_diagram_beautifier_agent.py`:
```python
    keywords_in_order = [
        "parse",
        "dependency",
        "aesthetic",
        "decompos",
        "beautif",
        "review",
        "assembl",
        "return",
    ]
```
Replace with:
```python
    keywords_in_order = [
        "parse",
        "dependency",
        "aesthetic",
        "decompos",
        "beautif",
        "review",
        "assembl",
        "present",
    ]
```

- [ ] **Step 4: Run all tests to verify they pass**

Run: `python3 -m pytest tests/test_diagram_beautifier_agent.py -v`
Expected: 40 PASSED (37 from Task 4 + 3 new).

Run full suite: `python3 -m pytest -x -q`
Expected: 300 passed.

- [ ] **Step 5: Commit**

```bash
git add agents/diagram-beautifier.md tests/test_diagram_beautifier_agent.py
git commit -m "feat: update Step 8 to side-by-side output presentation"
```

---

### Task 6: Add Polished vs Cinematic philosophy to diagram-style-guide.md

**Files:**
- Modify: `tests/test_diagram_style_guide.py` (add 4 tests)
- Modify: `docs/diagram-style-guide.md` (add new section)

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_diagram_style_guide.py`:

```python
def test_polished_vs_cinematic_section_present() -> None:
    """Style guide must contain a 'Polished vs Cinematic' section."""
    content = _read_style_guide()
    assert "## Polished vs Cinematic" in content, (
        "'## Polished vs Cinematic' section heading not found in diagram style guide."
    )


def test_polished_described_as_document_ready() -> None:
    """Polished variant must be described as document-ready."""
    content = _read_style_guide()
    lower = content.lower()
    assert "document-ready" in lower or "document ready" in lower, (
        "Polished must be described as 'document-ready' or 'document ready'."
    )


def test_cinematic_described_as_presentation_ready() -> None:
    """Cinematic variant must be described as presentation-ready."""
    content = _read_style_guide()
    lower = content.lower()
    assert "presentation-ready" in lower or "presentation ready" in lower, (
        "Cinematic must be described as 'presentation-ready' or 'presentation ready'."
    )


def test_hero_candidate_mentioned_in_cinematic_description() -> None:
    """The Polished vs Cinematic section must mention 'hero candidate'."""
    content = _read_style_guide()
    # Find the section
    start = content.find("## Polished vs Cinematic")
    assert start != -1, "'## Polished vs Cinematic' section not found"
    end = content.find("\n## ", start + 1)
    section = content[start:end] if end != -1 else content[start:]
    assert "hero candidate" in section.lower(), (
        "Polished vs Cinematic section must mention 'hero candidate'.\n"
        f"Actual section:\n{section}"
    )
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run: `python3 -m pytest tests/test_diagram_style_guide.py::test_polished_vs_cinematic_section_present tests/test_diagram_style_guide.py::test_polished_described_as_document_ready tests/test_diagram_style_guide.py::test_cinematic_described_as_presentation_ready tests/test_diagram_style_guide.py::test_hero_candidate_mentioned_in_cinematic_description -v`
Expected: 4 FAILED.

- [ ] **Step 3: Add the Polished vs Cinematic section to the style guide**

In `docs/diagram-style-guide.md`, find this text (around line 13–14):

```markdown
---

## Node Shapes
```

Insert BEFORE `## Node Shapes` (after the `---` separator):

```markdown

## Polished vs Cinematic

Every diagram beautification produces two variants simultaneously. Understanding
the difference helps write better generation prompts.

**Polished** is the document-ready variant. The aesthetic is applied faithfully:
better spacing, better typography, better colors, better node shapes — but the
visual character is coherent with professional expectations. A technical reader
would look at the Polished output and say *"yes, that's what I meant, but
beautiful."* Connectors are clean and appropriate to the aesthetic. Spatial
composition is fresh (not anchored to the DOT layout) but not surprising.

**Cinematic** is the presentation-ready variant. The diagram's topology is the
script; the aesthetic is the medium. Editorial choices are made about emphasis,
atmosphere, and depth. The hero candidate from the topology manifest is given
visual prominence. Connectors use the full expressive vocabulary of the
aesthetic. Spatial composition serves the visual over the functional. A viewer
encountering this for the first time should stop and look.

The two variants share: the same aesthetic selection, the same topology manifest,
the same quality review dimensions. They differ in: reference image use
(Polished: guard instruction; Cinematic: none), connector style (Polished: clean;
Cinematic: expressive), spatial freedom (Polished: fresh but coherent; Cinematic:
fully compositional), and quality bar language.

---

```

- [ ] **Step 4: Run all tests to verify they pass**

Run: `python3 -m pytest tests/test_diagram_style_guide.py -v`
Expected: 13 PASSED (9 existing + 4 new).

- [ ] **Step 5: Commit**

```bash
git add docs/diagram-style-guide.md tests/test_diagram_style_guide.py
git commit -m "feat: add Polished vs Cinematic philosophy to diagram style guide"
```

---

### Task 7: Add per-aesthetic Cinematic guidance to diagram-style-guide.md

**Files:**
- Modify: `tests/test_diagram_style_guide.py` (add 4 tests)
- Modify: `docs/diagram-style-guide.md` (add new section)

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_diagram_style_guide.py`:

```python
def test_cinematic_guidance_section_present() -> None:
    """Style guide must contain a 'Cinematic Guidance Per Aesthetic' section."""
    content = _read_style_guide()
    assert "## Cinematic Guidance Per Aesthetic" in content, (
        "'## Cinematic Guidance Per Aesthetic' section heading not found."
    )


def test_cinematic_dark_mode_has_bokeh_or_holographic() -> None:
    """Dark Mode Tech Cinematic guidance must mention bokeh or holographic."""
    content = _read_style_guide()
    start = content.find("## Cinematic Guidance Per Aesthetic")
    assert start != -1, "Cinematic Guidance section not found"
    section = content[start:]
    lower = section.lower()
    assert "bokeh" in lower or "holographic" in lower, (
        "Dark Mode Tech Cinematic must mention 'bokeh' or 'holographic'.\n"
        f"Actual section:\n{section}"
    )


def test_cinematic_clean_minimalist_has_sweeping_arcs() -> None:
    """Clean Minimalist Cinematic guidance must mention sweeping arcs."""
    content = _read_style_guide()
    start = content.find("## Cinematic Guidance Per Aesthetic")
    assert start != -1, "Cinematic Guidance section not found"
    section = content[start:]
    assert "sweeping arcs" in section.lower(), (
        "Clean Minimalist Cinematic must mention 'sweeping arcs'.\n"
        f"Actual section:\n{section}"
    )


def test_cinematic_claymation_has_scene_description() -> None:
    """Claymation Cinematic guidance must describe a full scene."""
    content = _read_style_guide()
    start = content.find("## Cinematic Guidance Per Aesthetic")
    assert start != -1, "Cinematic Guidance section not found"
    section = content[start:]
    lower = section.lower()
    assert "full scene" in lower, (
        "Claymation Cinematic must describe 'full scene'.\n"
        f"Actual section:\n{section}"
    )
    assert "claymation" in lower, (
        "Claymation Cinematic guidance must mention 'Claymation'.\n"
        f"Actual section:\n{section}"
    )
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run: `python3 -m pytest tests/test_diagram_style_guide.py::test_cinematic_guidance_section_present tests/test_diagram_style_guide.py::test_cinematic_dark_mode_has_bokeh_or_holographic tests/test_diagram_style_guide.py::test_cinematic_clean_minimalist_has_sweeping_arcs tests/test_diagram_style_guide.py::test_cinematic_claymation_has_scene_description -v`
Expected: 4 FAILED.

- [ ] **Step 3: Add the Cinematic Guidance Per Aesthetic section to the style guide**

In `docs/diagram-style-guide.md`, find the end of the `## Connector Styling` section. The section ends with the table row for Lego Brick Builder. Find:

```markdown
| **Lego Brick Builder** | Rigid brick-peg connector rods. | — |

---

## Prompt Construction Rules
```

Insert BETWEEN the `---` and `## Prompt Construction Rules`:

```markdown

## Cinematic Guidance Per Aesthetic

For each aesthetic, what makes the Cinematic variant distinct from Polished.
Apply these when constructing Cinematic generation prompts.

| Aesthetic | What makes Cinematic distinct |
|---|---|
| **Clean Minimalist** | Sweeping arcs instead of orthogonal segments. Scale variation: decision nodes slightly larger, terminal nodes slightly smaller. Generous breathing room interpreted as deliberate whitespace composition. |
| **Dark Mode Tech** | Environmental depth: ambient bokeh glow emanating from key processing nodes. Holographic node quality: nodes appear to float with depth layers. Glowing bezier edges trace source-to-destination color gradients. |
| **Bold Editorial** | Nodes become graphic elements: color-blocked panels with heavy typographic labels. Dramatic directional lighting creates strong shadows. The hero node gets a full-bleed color treatment. |
| **Hand-Drawn Sketchnote** | Gestural organic spacing: nodes are placed as a human would place them, not on a grid. Wobbly arrows with varying weight. The hero node gets a hand-drawn callout or emphasis circle. |
| **Claymation Studio** | Full scene: nodes exist as sculpted characters or objects in a clay environment. Rope or ribbon connectors. The hero node is physically larger or more prominently placed in the scene. |
| **Lego Brick Builder** | Nodes are brick constructions on a full baseplate scene. Brick-peg connector rods. The hero node has the most elaborate brick construction. |

---

```

- [ ] **Step 4: Run all tests to verify they pass**

Run: `python3 -m pytest tests/test_diagram_style_guide.py -v`
Expected: 17 PASSED (13 from Task 6 + 4 new).

- [ ] **Step 5: Run the full test suite to confirm everything passes**

Run: `python3 -m pytest -x -q`
Expected: 300 passed (276 original + 26 new - 2 removed = 300).

- [ ] **Step 6: Commit**

```bash
git add docs/diagram-style-guide.md tests/test_diagram_style_guide.py
git commit -m "feat: add per-aesthetic Cinematic guidance to diagram style guide"
```