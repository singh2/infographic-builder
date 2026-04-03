# Multi-Candidate Selection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate 3 Panel 1 candidates (or 3 single-panel candidates) with meaningful variation, present them to the user, and continue the pipeline from the winner.

**Architecture:** The changes are purely in the agent definition markdown (`agents/infographic-builder.md`) and the style guide markdown (`docs/style-guide.md`). No Python code changes. All tests are structural text assertions against these markdown files. The variation cascade, dealbreaker check, and presentation format are specified as agent instructions.

**Tech Stack:** Markdown (agent definition + style guide), pytest (structural tests)

**Spec:** `docs/superpowers/specs/2026-04-03-multi-candidate-selection-design.md`

---

### Task 1: Add variation cascade to style guide

Define the three-tier variation cascade in the style guide so the agent knows what to vary based on user input.

**Files:**
- Modify: `docs/style-guide.md` (insert new section after Aesthetics, before Layout Types)
- Test: `tests/test_variation_cascade.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_variation_cascade.py`:

```python
from helpers import read_guide


def _get_variation_cascade_section(content):
    start = content.index("## Variation Cascade")
    end = content.index("\n## ", start + 1)
    return content[start:end]


def test_variation_cascade_section_exists():
    assert "## Variation Cascade" in read_guide()


def test_tier_1_varies_aesthetic():
    section = _get_variation_cascade_section(read_guide())
    assert "Tier 1" in section
    assert "aesthetic" in section.lower()


def test_tier_2_varies_by_aesthetic_type():
    section = _get_variation_cascade_section(read_guide())
    assert "Tier 2" in section
    assert "environment" in section.lower()
    assert "composition" in section.lower()


def test_tier_2_3d_styles_vary_environment():
    section = _get_variation_cascade_section(read_guide())
    lower = section.lower()
    claymation_pos = lower.find("claymation")
    lego_pos = lower.find("lego")
    assert claymation_pos != -1
    assert lego_pos != -1
    # Both should be associated with environment
    assert "environment" in lower


def test_tier_2_flat_styles_vary_composition():
    section = _get_variation_cascade_section(read_guide())
    lower = section.lower()
    assert "clean minimalist" in lower
    assert "dark mode tech" in lower
    assert "composition" in lower


def test_tier_3_model_freedom():
    section = _get_variation_cascade_section(read_guide())
    assert "Tier 3" in section
    assert "model freedom" in section.lower() or "visual interpretation" in section.lower()


def test_composition_directions_defined():
    section = _get_variation_cascade_section(read_guide())
    lower = section.lower()
    assert "central focal point" in lower or "central focus" in lower
    assert "scene-based" in lower or "scene based" in lower
    assert "diagrammatic" in lower or "structured" in lower
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_variation_cascade.py -v`
Expected: All FAIL — section doesn't exist yet.

- [ ] **Step 3: Add the Variation Cascade section to the style guide**

Insert the following in `docs/style-guide.md` after the Freeform Aesthetics sub-section (after line ~143, before `## Layout Types`):

```markdown
## Variation Cascade

When generating multi-candidate Panel 1 options, what to vary depends on what
the user already locked in. Vary the highest-impact axis that hasn't been
constrained.

### Tier 1: Vary aesthetic (highest diversity)

**When:** User specified a topic but no aesthetic.

Generate 3 candidates, each in a different curated aesthetic. Pick 3
contrasting styles to maximize visual diversity (e.g., Claymation Studio +
Dark Mode Tech + Bold Editorial — not three similar styles).

### Tier 2: Vary based on aesthetic type (medium diversity)

**When:** User specified an aesthetic (inline or via reference image).

The variation axis adapts to the aesthetic:

| Aesthetic | Second axis | Why |
|-----------|-------------|-----|
| Claymation Studio | **Environment/setting** | 3D styles produce dramatically different results with different environments |
| Lego Brick Builder | **Environment/setting** | Baseplate scenes vary visually more than composition shifts |
| Clean Minimalist | **Composition** | Flat styles differentiate best through spatial arrangement |
| Dark Mode Tech | **Composition** | Same |
| Bold Editorial | **Composition** | Same |
| Hand-Drawn Sketchnote | **Composition** | Same |
| Freeform | **Composition** | Default to composition for user-described aesthetics |

**Composition directions** (for non-3D aesthetics):
- Central focal point — hero subject centered, labels radiate outward
- Scene-based — environment tells the story, subject embedded in context
- Structured/diagrammatic — clean sections, data-forward, clear hierarchy

**Environment directions** (for 3D aesthetics):
- Pick 3 contrasting settings appropriate to the topic using content judgment.
  For "brewing espresso": kitchen counter, coffee shop diorama, abstract studio.
  For "daily routine": bedroom, outdoor trail, garden.

### Tier 3: Model freedom (lowest diversity)

**When:** User specified both aesthetic and layout.

Generate 3 candidates with identical constraints. Append to each prompt:
"Explore a distinct visual interpretation." Rely on model variance for
diversity.
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_variation_cascade.py -v`
Expected: All PASS.

- [ ] **Step 5: Commit**

```bash
git add docs/style-guide.md tests/test_variation_cascade.py
git commit -m "feat: add variation cascade to style guide with 3-tier priority"
```

---

### Task 2: Add dealbreaker check to style guide

Define the lightweight quality check that runs before presenting candidates.

**Files:**
- Modify: `docs/style-guide.md` (insert new sub-section inside Quality Review Criteria)
- Test: `tests/test_dealbreaker_check.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_dealbreaker_check.py`:

```python
from helpers import read_guide


def _get_dealbreaker_section(content):
    start = content.index("### Dealbreaker Check")
    end = content.index("\n### ", start + 1)
    return content[start:end]


def test_dealbreaker_check_section_exists():
    assert "### Dealbreaker Check" in read_guide()


def test_dealbreaker_checks_text_legibility():
    section = _get_dealbreaker_section(read_guide())
    lower = section.lower()
    assert "text" in lower and "legib" in lower


def test_dealbreaker_checks_core_content():
    section = _get_dealbreaker_section(read_guide())
    lower = section.lower()
    assert "content" in lower and "present" in lower


def test_dealbreaker_checks_aesthetic_match():
    section = _get_dealbreaker_section(read_guide())
    lower = section.lower()
    assert "aesthetic" in lower


def test_dealbreaker_regenerate_on_failure():
    section = _get_dealbreaker_section(read_guide())
    lower = section.lower()
    assert "regenerate" in lower


def test_dealbreaker_drop_after_second_failure():
    section = _get_dealbreaker_section(read_guide())
    lower = section.lower()
    assert "drop" in lower or "discard" in lower
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_dealbreaker_check.py -v`
Expected: All FAIL — section doesn't exist yet.

- [ ] **Step 3: Add the Dealbreaker Check sub-section to the style guide**

Insert in `docs/style-guide.md` inside the Quality Review Criteria section, after the 5-dimension evaluation prompt template closing ``` (after line ~409) and before `### Cross-Panel Visual Comparison`:

```markdown
### Dealbreaker Check (Multi-Candidate Pre-Screen)

Before presenting multi-candidate options to the user, run a lightweight
binary check on each candidate using `nano-banana analyze`:

```
Quick quality check — answer PASS or FAIL for each:
1. TEXT LEGIBILITY: Is all visible text legible? No garbled or hallucinated words?
2. CORE CONTENT: Are the title and key data points from the prompt visible?
3. AESTHETIC MATCH: Does the output match the requested visual style?

If ANY dimension is FAIL, the overall verdict is FAIL.
```

This is NOT the full 5-dimension review. It is a fast pass to catch broken
outputs before the user sees them.

**If a candidate fails:** Silently regenerate it once with the same prompt. If
it fails again, drop it from the candidate set. Present 2 candidates instead
of 3. Minimum: 2 candidates. If only 1 survives, present it with a note that
other candidates failed quality checks.
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_dealbreaker_check.py -v`
Expected: All PASS.

- [ ] **Step 5: Commit**

```bash
git add docs/style-guide.md tests/test_dealbreaker_check.py
git commit -m "feat: add dealbreaker check for multi-candidate pre-screening"
```

---

### Task 3: Modify Step 3 to defer aesthetic selection for Tier 1

When the user didn't specify an aesthetic, remove the text menu at Step 3d. Aesthetic selection is deferred to the candidate presentation at Step 5b.

**Files:**
- Modify: `agents/infographic-builder.md` (Step 3, lines 109–126)
- Test: `tests/test_infographic_builder.py` (add new tests)

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_infographic_builder.py`:

```python
def test_step_3d_defers_to_multi_candidate():
    block = _get_step_3_block(read_agent())
    lower = block.lower()
    assert "multi-candidate" in lower or "candidate" in lower
    assert "step 5b" in lower or "step 5" in lower


def test_step_3d_no_longer_halts():
    block = _get_step_3_block(read_agent())
    # The old halt instruction should be removed from 3d
    # Halt now lives in step 5b-iii instead
    assert "stop and wait" not in block.lower() or "5b" in block.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_infographic_builder.py::test_step_3d_defers_to_multi_candidate tests/test_infographic_builder.py::test_step_3d_no_longer_halts -v`
Expected: FAIL — current Step 3d still has the text menu and halt.

- [ ] **Step 3: Modify Step 3d in the agent definition**

Replace the content of Step 3d (lines 109–126 of `agents/infographic-builder.md`) with:

```markdown
    **d. If no style was specified**, defer aesthetic selection to the
    multi-candidate presentation at step 5b. The user will pick from 3
    real images in different aesthetics rather than choosing from a text
    menu. Do not halt here — proceed directly to step 4, which will
    plan 3 design variants (one per aesthetic candidate).
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_infographic_builder.py -v`
Expected: All PASS (new and existing tests).

- [ ] **Step 5: Commit**

```bash
git add agents/infographic-builder.md tests/test_infographic_builder.py
git commit -m "feat: defer aesthetic selection to multi-candidate presentation"
```

---

### Task 4: Modify Step 4 to support per-candidate design plans

When aesthetic is unspecified (Tier 1), Step 4 runs once per candidate aesthetic. Otherwise it runs once as today.

**Files:**
- Modify: `agents/infographic-builder.md` (Step 4, around line 134)
- Test: `tests/test_infographic_builder.py` (add new test)

- [ ] **Step 1: Write the failing test**

Add to `tests/test_infographic_builder.py`:

```python
def _get_step_4_block(content):
    start = content.index("4. **")
    end = content.index("\n5. **", start)
    return content[start:end]


def test_step_4_supports_per_candidate_plans():
    block = _get_step_4_block(read_agent())
    lower = block.lower()
    assert "candidate" in lower or "tier 1" in lower or "per aesthetic" in lower
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_infographic_builder.py::test_step_4_supports_per_candidate_plans -v`
Expected: FAIL.

- [ ] **Step 3: Add per-candidate note to Step 4**

Add the following paragraph to the end of Step 4 in `agents/infographic-builder.md`:

```markdown
    **Multi-candidate mode (Tier 1 — aesthetic unspecified):** Run this step
    once per candidate aesthetic, producing 3 lightweight design plans. Each
    plan applies a different aesthetic template to the same content. Layout
    type may differ per candidate if a different layout better suits the style.
    For Tiers 2 and 3, run this step once since the aesthetic is shared.
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_infographic_builder.py -v`
Expected: All PASS.

- [ ] **Step 5: Commit**

```bash
git add agents/infographic-builder.md tests/test_infographic_builder.py
git commit -m "feat: support per-candidate design plans in Step 4"
```

---

### Task 5: Expand Step 5b into multi-candidate generation + selection

This is the core change. Replace the single Panel 1 generation with 3-candidate generation, dealbreaker check, presentation, and user selection halt.

**Files:**
- Modify: `agents/infographic-builder.md` (Step 5b, lines 157–158, and single-panel path, lines 146–149)
- Test: `tests/test_multi_candidate.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_multi_candidate.py`:

```python
from helpers import read_agent


def _get_step_5_block(content):
    start = content.index("5. **Generate the image")
    end = content.index("\n6. **", start)
    return content[start:end]


def test_step_5b_generates_3_candidates():
    block = _get_step_5_block(read_agent())
    assert "3 candidates" in block.lower() or "three candidates" in block.lower()


def test_step_5b_has_sub_steps():
    block = _get_step_5_block(read_agent())
    assert "5b-i" in block or "5b-i." in block
    assert "5b-ii" in block or "5b-ii." in block
    assert "5b-iii" in block or "5b-iii." in block


def test_step_5b_i_generates_in_parallel():
    block = _get_step_5_block(read_agent())
    lower = block.lower()
    assert "parallel" in lower


def test_step_5b_ii_runs_dealbreaker_check():
    block = _get_step_5_block(read_agent())
    lower = block.lower()
    assert "dealbreaker" in lower


def test_step_5b_iii_presents_and_halts():
    block = _get_step_5_block(read_agent())
    lower = block.lower()
    assert "present" in lower
    assert "wait" in lower or "halt" in lower or "stop" in lower


def test_step_5b_iii_includes_rationale():
    block = _get_step_5_block(read_agent())
    lower = block.lower()
    assert "rationale" in lower


def test_step_5b_references_variation_cascade():
    block = _get_step_5_block(read_agent())
    lower = block.lower()
    assert "variation cascade" in lower or "tier" in lower


def test_reconciliation_runs_on_chosen_candidate():
    block = _get_step_5_block(read_agent())
    lower = block.lower()
    assert "chosen" in lower or "selected" in lower or "winner" in lower


def test_single_panel_also_generates_3_candidates():
    block = _get_step_5_block(read_agent())
    single_start = block.lower().find("single-panel")
    assert single_start != -1
    single_section = block[single_start:single_start + 500].lower()
    assert "3 candidates" in single_section or "three candidates" in single_section


def test_single_panel_user_pick_is_final():
    block = _get_step_5_block(read_agent())
    single_start = block.lower().find("single-panel")
    assert single_start != -1
    single_section = block[single_start:single_start + 500].lower()
    assert "final" in single_section or "done" in single_section
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_multi_candidate.py -v`
Expected: All FAIL.

- [ ] **Step 3: Rewrite Step 5 single-panel and multi-panel 5b in the agent definition**

Replace the single-panel path (lines 146–149) and Step 5b (lines 157–158) of `agents/infographic-builder.md` with:

```markdown
    **Single-panel path:**
    Generate 3 candidates in parallel, varying based on the Variation Cascade
    in the Style Guide (Tier 1 if no aesthetic specified, Tier 2 or 3
    otherwise). Run the Dealbreaker Check on each candidate. Present all
    passing candidates to the user with a one-sentence rationale per
    candidate describing what makes it different. **Stop and wait for the
    user's selection.** The user's pick is the final output — no further
    quality review.

    **Multi-panel path** -- follow these sub-steps IN ORDER. Do not skip or
    reorder. Each sub-step must complete before the next begins.

    **5a. Content map + style brief.** Build both artifacts (see Multi-Panel
    Composition in the Style Guide) before any generation call.

    **5b. Generate 3 Panel 1 candidates.**

    **5b-i.** Generate 3 candidates in parallel. The variation axis is
    determined by the Variation Cascade in the Style Guide — Tier 1 (aesthetic)
    if no aesthetic was specified, Tier 2 (environment or composition based
    on aesthetic type) if an aesthetic was locked, or Tier 3 (model freedom)
    if both aesthetic and layout were specified. All 3 calls run concurrently.

    **5b-ii.** Run the Dealbreaker Check (see Style Guide) on each candidate.
    Silently regenerate failures once. Drop candidates that fail twice.
    Minimum 2 candidates.

    **5b-iii.** Present all passing candidates to the user. For each
    candidate, show the image path and a one-sentence rationale describing
    what makes it different — the aesthetic name for Tier 1 variation, the
    spatial approach for composition variation, or the environment for
    setting variation. End with: "Pick one, or tell me what you'd like to
    adjust." **Stop and wait for the user's selection.** Do not proceed to
    reconciliation until the user has chosen.

    **5c. Reconcile style brief (REQUIRED GATE).** Call `nano-banana analyze`
    on the **chosen** Panel 1 candidate using the reconciliation prompt from
    the Style Guide. **OVERWRITE** your original style brief with the analysis
    output. Do not merge — replace entirely. **You MUST NOT generate any
    subsequent panel until this step has produced a reconciled brief.** This
    is a hard gate, not a suggestion. The two rejected candidates are
    discarded.
```

Leave Step 5d (Panels 2-N) unchanged.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_multi_candidate.py -v`
Expected: All PASS.

- [ ] **Step 5: Run full test suite**

Run: `pytest tests/ -v`
Expected: All PASS. If any existing tests fail due to Step 5b text changes,
update those tests to match the new wording (the old "Generate Panel 1 ONLY"
language no longer appears in 5b).

- [ ] **Step 6: Commit**

```bash
git add agents/infographic-builder.md tests/test_multi_candidate.py
git commit -m "feat: expand Step 5b into multi-candidate generation with user selection"
```

---

### Task 6: Update existing tests for changed wording

The Step 5b text changed from "Generate Panel 1 ONLY" to "Generate 3 Panel 1
candidates." Any existing tests that assert on the old wording need updating.

**Files:**
- Modify: `tests/test_infographic_builder.py` (fix any broken assertions)
- Modify: `tests/test_style_consistency_brief.py` (if it references Step 5b wording)

- [ ] **Step 1: Run full test suite to find failures**

Run: `pytest tests/ -v`
Look for: FAIL messages referencing Step 5b or "Panel 1 ONLY" or old wording.

- [ ] **Step 2: Fix each failing test**

For each failing test, update the assertion to match the new wording. Keep the
test's intent — if it was checking that Panel 1 is generated before Panels 2-N,
update it to check that the 3-candidate generation + selection happens before
Panels 2-N.

- [ ] **Step 3: Run full test suite to verify all pass**

Run: `pytest tests/ -v`
Expected: All PASS.

- [ ] **Step 4: Commit**

```bash
git add tests/
git commit -m "test: update existing tests for multi-candidate Step 5b wording"
```

---

### Task 7: Commit spec and plan, verify clean state

**Files:**
- Stage: `docs/superpowers/specs/2026-04-03-multi-candidate-selection-design.md`
- Stage: `docs/superpowers/plans/2026-04-03-multi-candidate-selection-plan.md`

- [ ] **Step 1: Run full test suite one final time**

Run: `pytest tests/ -v`
Expected: All PASS.

- [ ] **Step 2: Commit spec and plan**

```bash
git add docs/superpowers/specs/2026-04-03-multi-candidate-selection-design.md
git add docs/superpowers/plans/2026-04-03-multi-candidate-selection-plan.md
git commit -m "docs: add multi-candidate selection design spec and implementation plan"
```

- [ ] **Step 3: Verify clean git status**

Run: `git status`
Expected: clean working tree (only untracked files outside the feature scope).