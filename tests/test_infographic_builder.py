"""
Tests for agents/infographic-builder.md structure and correctness.

Covers (task-6 quality fix suggestions):
1. Execution model banner has parenthetical caveat about aesthetic selection
2. Steps 1–8 are present in order with no gaps or duplicates
3. Step 3 contains sub-parts a, b, c, d
4. Step 3c ends with the halt instruction
5. Cross-reference in step 2 says 'step 6' (not 'step 5')
"""

from pathlib import Path

AGENT_FILE = Path(__file__).parent.parent / "agents" / "infographic-builder.md"


def read_agent() -> str:
    return AGENT_FILE.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Execution model banner
# ---------------------------------------------------------------------------


def test_execution_model_has_aesthetic_caveat():
    """Execution model note must include a caveat about the conditional multi-turn
    nature introduced by step 3's aesthetic selection halt."""
    content = read_agent()
    assert "unless aesthetic" in content.lower(), (
        "Execution model banner must contain a caveat like "
        "'(unless aesthetic selection is required — see Step 3)'"
    )


def test_execution_model_caveat_references_step_3():
    """The caveat must reference Step 3 so readers can find the relevant section."""
    content = read_agent()
    # Find the execution model paragraph
    exec_model_start = content.index("**Execution model:**")
    exec_model_end = content.index("\n\n", exec_model_start)
    exec_model_text = content[exec_model_start:exec_model_end]
    assert "Step 3" in exec_model_text or "step 3" in exec_model_text.lower(), (
        "Execution model caveat must reference Step 3"
    )


# ---------------------------------------------------------------------------
# Step numbering: 1 through 8, in order
# ---------------------------------------------------------------------------


def test_steps_1_through_8_present():
    """All eight steps must be present in the workflow section."""
    content = read_agent()
    for n in range(1, 9):
        assert f"{n}. **" in content, (
            f"Step {n} not found in agents/infographic-builder.md"
        )


def test_step_numbering_sequential():
    """Steps must appear in ascending numerical order (no transpositions)."""
    content = read_agent()
    positions = []
    for n in range(1, 9):
        idx = content.find(f"\n{n}. **")
        assert idx != -1, f"Step {n} not found"
        positions.append(idx)
    assert positions == sorted(positions), (
        f"Steps are not in sequential order: positions={positions}"
    )


def test_no_step_9_or_higher():
    """There must be no step 9 or beyond (workflow ends at step 8)."""
    content = read_agent()
    assert "\n9. **" not in content, "Unexpected step 9 found in workflow"


# ---------------------------------------------------------------------------
# Step 3: Aesthetic selection — sub-parts a, b, c, d
# ---------------------------------------------------------------------------


def _get_step_3_block(content: str) -> str:
    """Extract text between '3. **Aesthetic selection**' and '4. **'."""
    start = content.index("3. **Aesthetic selection**")
    end = content.index("4. **", start)
    return content[start:end]


def test_step_3_has_subpart_a():
    """Step 3 must contain sub-part a (layout recommendation)."""
    block = _get_step_3_block(read_agent())
    assert "**a." in block or "**a. " in block, "Step 3 sub-part a missing"


def test_step_3_has_subpart_b():
    """Step 3 must contain sub-part b (inline style check / two-turn shortcut)."""
    block = _get_step_3_block(read_agent())
    assert "**b." in block or "**b. " in block, "Step 3 sub-part b missing"


def test_step_3_has_subpart_c():
    """Step 3 must contain sub-part c (present options and halt)."""
    block = _get_step_3_block(read_agent())
    assert "**c." in block or "**c. " in block, "Step 3 sub-part c missing"


def test_step_3_has_subpart_d():
    """Step 3 must contain sub-part d (load aesthetic template)."""
    block = _get_step_3_block(read_agent())
    assert "**d." in block or "**d. " in block, "Step 3 sub-part d missing"


def test_step_3b_two_turn_shortcut():
    """Step 3b must mention the two-turn shortcut."""
    block = _get_step_3_block(read_agent())
    assert "two-turn shortcut" in block, (
        "Step 3b must mention the 'two-turn shortcut'"
    )


def test_step_3c_has_six_numbered_options():
    """Step 3c menu must list options 1 through 6."""
    block = _get_step_3_block(read_agent())
    for n in range(1, 7):
        assert f"{n}." in block, f"Step 3c menu missing option {n}"


def test_step_3c_halt_instruction():
    """Step 3c must end with the halt instruction."""
    block = _get_step_3_block(read_agent())
    assert "stop and wait for the user's selection" in block, (
        "Step 3c must contain 'stop and wait for the user's selection'"
    )


# ---------------------------------------------------------------------------
# Cross-reference: step 2 says 'step 6'
# ---------------------------------------------------------------------------


def test_step_2_cross_reference_says_step_6():
    """The 'skip the review' override in step 2 must reference 'step 6'."""
    content = read_agent()
    # Find step 2 block
    start = content.index("2. **Analyze content density**")
    end = content.index("3. **Aesthetic selection**", start)
    step_2_block = content[start:end]
    assert "step 6" in step_2_block, (
        "Step 2 cross-reference must say 'step 6' (not 'step 5')"
    )
    assert "step 5" not in step_2_block, (
        "Step 2 must not reference 'step 5' (quality review is now step 6)"
    )
