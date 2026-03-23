"""
Tests for agents/infographic-builder.md — Task 7 changes.

Acceptance criteria:
1. Step 4 mentions 'selected aesthetic template' and
   'Aesthetics section of the Style Guide'.
2. Step 4 says 'The aesthetic drives these decisions — not ad-hoc choices.'
3. Step 6 says 'five dimensions' (not 'four').
4. Step 6 lists 'aesthetic fidelity' at the end of the dimension list.
"""

from helpers import read_agent


def _get_step_4_block(content: str) -> str:
    """Extract text between '4. **Plan the design**' and '5. **'."""
    start = content.index("4. **Plan the design**")
    end = content.index("5. **", start)
    return content[start:end]


def _get_step_6_block(content: str) -> str:
    """Extract text between '6. **Quality review**' and '7. **'."""
    start = content.index("6. **Quality review**")
    end = content.index("7. **", start)
    return content[start:end]


# ---------------------------------------------------------------------------
# Step 4: Plan the design — aesthetic template references
# ---------------------------------------------------------------------------


def test_step_4_mentions_selected_aesthetic_template():
    """Step 4 must reference 'selected aesthetic template'."""
    block = _get_step_4_block(read_agent())
    assert "selected aesthetic template" in block, (
        "Step 4 must mention 'selected aesthetic template' but it was not found.\n"
        f"Actual step 4 block:\n{block}"
    )


def test_step_4_mentions_aesthetics_section_of_style_guide():
    """Step 4 must reference the 'Aesthetics section of the Style Guide'.

    The phrase may span a line break in the markdown source, so we normalise
    whitespace before searching.
    """
    block = _get_step_4_block(read_agent())
    # Collapse newlines + leading spaces so the phrase is searchable even when
    # it wraps across two lines (e.g. "…Aesthetics\n   section of the Style Guide")
    normalised = " ".join(block.split())
    assert "Aesthetics section of the Style Guide" in normalised, (
        "Step 4 must mention 'Aesthetics section of the Style Guide' but it was not found.\n"
        f"Actual step 4 block:\n{block}"
    )


def test_step_4_says_aesthetic_drives_decisions():
    """Step 4 must say 'The aesthetic drives these decisions — not ad-hoc choices.'"""
    block = _get_step_4_block(read_agent())
    assert "The aesthetic drives these decisions" in block, (
        "Step 4 must contain 'The aesthetic drives these decisions — not ad-hoc choices.' "
        "but it was not found.\n"
        f"Actual step 4 block:\n{block}"
    )


def test_step_4_says_not_ad_hoc_choices():
    """Step 4 must explicitly say 'not ad-hoc choices'."""
    block = _get_step_4_block(read_agent())
    assert "not ad-hoc choices" in block, (
        "Step 4 must contain 'not ad-hoc choices' but it was not found.\n"
        f"Actual step 4 block:\n{block}"
    )


# ---------------------------------------------------------------------------
# Step 6: Quality review — five dimensions
# ---------------------------------------------------------------------------


def test_step_6_says_five_dimensions():
    """Step 6 must say 'five dimensions', not 'four dimensions'."""
    block = _get_step_6_block(read_agent())
    assert "five dimensions" in block, (
        "Step 6 must say 'five dimensions' but it was not found.\n"
        f"Actual step 6 block:\n{block}"
    )


def test_step_6_does_not_say_four_dimensions():
    """Step 6 must NOT say 'four dimensions' (old wording)."""
    block = _get_step_6_block(read_agent())
    assert "four dimensions" not in block, (
        "Step 6 still says 'four dimensions' — update it to 'five dimensions'.\n"
        f"Actual step 6 block:\n{block}"
    )


def test_step_6_lists_aesthetic_fidelity():
    """Step 6 must list 'aesthetic fidelity' in the dimension list."""
    block = _get_step_6_block(read_agent())
    assert "aesthetic fidelity" in block, (
        "Step 6 must list 'aesthetic fidelity' as the 5th dimension but it was not found.\n"
        f"Actual step 6 block:\n{block}"
    )


def test_step_6_aesthetic_fidelity_appears_after_prompt_fidelity():
    """'aesthetic fidelity' must appear after 'prompt fidelity' in step 6."""
    block = _get_step_6_block(read_agent())
    pos_prompt = block.find("prompt fidelity")
    pos_aesthetic = block.find("aesthetic fidelity")
    assert pos_prompt != -1, "Step 6 must list 'prompt fidelity'"
    assert pos_aesthetic != -1, "Step 6 must list 'aesthetic fidelity'"
    assert pos_aesthetic > pos_prompt, (
        "'aesthetic fidelity' must appear after 'prompt fidelity' in step 6"
    )
