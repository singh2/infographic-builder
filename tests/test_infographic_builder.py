"""
Tests for agents/infographic-builder.md structure and correctness.

Covers (task-6 quality fix suggestions):
1. Execution model banner has parenthetical caveat about aesthetic selection
2. Steps 1–8 are present in order with no gaps or duplicates
3. Step 3 contains sub-parts a, b, c, d, e
4. Step 3d defers aesthetic selection to multi-candidate presentation (step 5b)
5. Cross-reference in step 2 says 'step 6' (not 'step 5')

Covers (task-8 output contract suggestions):
6. Output Contract suggestions line says 'try a different aesthetic' first
7. Step 8 Return results says 'different aesthetic' first
8. 'style variation' is removed from both locations
"""

from helpers import read_agent


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
# Step 3: Aesthetic selection — sub-parts a, b, c, d, e
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
    """Step 3 must contain sub-part b (aesthetic_description from root session)."""
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
    assert "two-turn shortcut" in block, "Step 3b must mention the 'two-turn shortcut'"


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


# ---------------------------------------------------------------------------
# Task-8: Output Contract and Step 8 suggestions — 'try a different aesthetic'
# ---------------------------------------------------------------------------


def _get_output_contract_block(content: str) -> str:
    """Extract text of the Output Contract section."""
    start = content.index("## Output Contract")
    end = (
        content.index("\n## ", start + 1)
        if "\n## " in content[start + 1 :]
        else len(content)
    )
    return content[start:end]


def _get_step_8_block(content: str) -> str:
    """Extract text of step 8 (Return results) up to the next section."""
    start = content.index("8. **Return results**")
    end = content.index("\n## ", start)
    return content[start:end]


def test_output_contract_suggests_different_aesthetic():
    """Output Contract suggestions must list 'try a different aesthetic' as first suggestion."""
    block = _get_output_contract_block(read_agent())
    assert "try a different aesthetic" in block, (
        "Output Contract suggestions must include 'try a different aesthetic'"
    )


def test_output_contract_no_style_variation():
    """Output Contract suggestions must NOT contain 'style variation' (replaced by 'different aesthetic')."""
    block = _get_output_contract_block(read_agent())
    assert "style variation" not in block, (
        "Output Contract must not contain 'style variation'; it should say 'try a different aesthetic'"
    )


def test_output_contract_different_aesthetic_before_layout():
    """In Output Contract suggestions, 'different aesthetic' must appear before 'different layout'."""
    block = _get_output_contract_block(read_agent())
    aesthetic_pos = block.find("different aesthetic")
    layout_pos = block.find("different layout")
    assert aesthetic_pos != -1, "Output Contract must mention 'different aesthetic'"
    assert layout_pos != -1, "Output Contract must mention 'different layout'"
    assert aesthetic_pos < layout_pos, (
        "'different aesthetic' must appear before 'different layout' in Output Contract"
    )


def test_step_8_suggests_different_aesthetic():
    """Step 8 Return results must list 'different aesthetic' as first suggestion."""
    block = _get_step_8_block(read_agent())
    assert "different aesthetic" in block, (
        "Step 8 must include 'different aesthetic' in its suggestions"
    )


def test_step_8_no_style_variation():
    """Step 8 must NOT contain 'style variation' (replaced by 'different aesthetic')."""
    block = _get_step_8_block(read_agent())
    assert "style variation" not in block, (
        "Step 8 must not contain 'style variation'; it should say 'different aesthetic'"
    )


def test_step_8_different_aesthetic_before_layout():
    """In Step 8 suggestions, 'different aesthetic' must appear before 'different layout'."""
    block = _get_step_8_block(read_agent())
    aesthetic_pos = block.find("different aesthetic")
    layout_pos = block.find("different layout")
    assert aesthetic_pos != -1, "Step 8 must mention 'different aesthetic'"
    assert layout_pos != -1, "Step 8 must mention 'different layout'"
    assert aesthetic_pos < layout_pos, (
        "'different aesthetic' must appear before 'different layout' in Step 8"
    )


# ---------------------------------------------------------------------------
# Task: Step 1 accepts content_summary from root session
# ---------------------------------------------------------------------------


def _get_step_1_block(content: str) -> str:
    """Extract text between '1. **Parse the request**' and '2. **'."""
    start = content.index("1. **Parse the request**")
    end = content.index("2. **", start)
    return content[start:end]


def test_step_1_accepts_content_summary():
    block = _get_step_1_block(read_agent())
    lower = block.lower()
    assert "content_summary" in lower


def test_step_1_content_summary_becomes_subject_matter():
    block = _get_step_1_block(read_agent())
    lower = block.lower()
    assert "subject matter" in lower


# ---------------------------------------------------------------------------
# Task: Step 3 — aesthetic_description from root session skips menu
# ---------------------------------------------------------------------------


def test_step_3_has_subpart_e():
    """Step 3 must contain sub-part e (load aesthetic template)."""
    block = _get_step_3_block(read_agent())
    assert "**e." in block or "**e. " in block


def test_step_3_aesthetic_description_skips_menu():
    """Step 3b must reference aesthetic_description and skip the menu."""
    block = _get_step_3_block(read_agent())
    lower = block.lower()
    assert "aesthetic_description" in lower
    assert "skip" in lower


def test_step_3_style_reference_translates_7_dimensions():
    """Step 3b must name all 7 style dimensions for translation."""
    block = _get_step_3_block(read_agent())
    lower = block.lower()
    for dim in [
        "palette",
        "typography",
        "icons",
        "background",
        "lighting",
        "texture",
        "mood",
    ]:
        assert dim in lower


# ---------------------------------------------------------------------------
# Task: Step 5 — reference_image_path modes for image input
# ---------------------------------------------------------------------------


def _get_step_5_block(content: str) -> str:
    start = content.index("5. **Generate the image(s)**")
    end = content.index("6. **", start)
    return content[start:end]


def test_step_5_describes_style_reference_mode():
    block = _get_step_5_block(read_agent())
    lower = block.lower()
    assert "style reference" in lower


def test_step_5_describes_content_source_mode():
    block = _get_step_5_block(read_agent())
    lower = block.lower()
    assert "content source" in lower
    assert "intentionally not" in lower or "not passed" in lower


def test_step_5_multi_panel_uses_reference_image_paths_plural():
    block = _get_step_5_block(read_agent())
    assert "reference_image_paths" in block


def test_step_5_two_anchors_panel_1_and_image_path():
    block = _get_step_5_block(read_agent())
    lower = block.lower()
    assert "cross-panel consistency" in lower
    assert "aesthetic fidelity" in lower


# ---------------------------------------------------------------------------
# Task 3: Step 3d defers aesthetic selection to multi-candidate presentation
# ---------------------------------------------------------------------------


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
