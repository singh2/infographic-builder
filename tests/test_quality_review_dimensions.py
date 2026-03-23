"""
Tests for the Quality Review Criteria section in docs/style-guide.md.

Acceptance criteria:
1. Dimension 5 (AESTHETIC FIDELITY) appears after dimension 4, checking background
   treatment, icon style, typography feel, lighting, and overall mood.
2. The Summary line says 'all 5 dimensions' (not 'all 4').
3. The rest of the evaluation template is unchanged.
4. Commit message: "feat: add AESTHETIC FIDELITY as 5th quality review dimension"
"""

from helpers import read_guide

# ── Sentinels ──────────────────────────────────────────────────────────────────

H2_QUALITY_REVIEW = "## Quality Review Criteria"
DIM4_HEADING = "4. PROMPT FIDELITY:"
DIM5_HEADING = "5. AESTHETIC FIDELITY:"
SUMMARY_5_DIMS = "all 5 dimensions"


# ── Helpers ────────────────────────────────────────────────────────────────────


def _quality_review_block(text: str) -> str:
    """Return the text from the Quality Review Criteria heading to end of file."""
    idx = text.find(H2_QUALITY_REVIEW)
    assert idx != -1, f"'{H2_QUALITY_REVIEW}' heading not found in style-guide.md"
    return text[idx:]


# ── Tests ──────────────────────────────────────────────────────────────────────


def test_dimension_5_aesthetic_fidelity_present():
    """Dimension 5 AESTHETIC FIDELITY heading must exist in the evaluation block."""
    block = _quality_review_block(read_guide())
    assert DIM5_HEADING in block, (
        f"Expected '{DIM5_HEADING}' in Quality Review Criteria block, but it was not found."
    )


def test_dimension_5_appears_after_dimension_4():
    """Dimension 5 must appear after dimension 4 in the file."""
    text = read_guide()
    pos4 = text.find(DIM4_HEADING)
    pos5 = text.find(DIM5_HEADING)
    assert pos4 != -1, f"'{DIM4_HEADING}' not found"
    assert pos5 != -1, f"'{DIM5_HEADING}' not found"
    assert pos5 > pos4, (
        f"'{DIM5_HEADING}' (pos {pos5}) must appear after '{DIM4_HEADING}' (pos {pos4})"
    )


def test_dimension_5_checks_required_aspects():
    """Dimension 5 description must mention background treatment, icon style,
    typography feel, lighting, and overall mood."""
    block = _quality_review_block(read_guide())
    # Find the dim-5 paragraph
    idx5 = block.find(DIM5_HEADING)
    assert idx5 != -1
    # Grab up to 600 chars after the heading for context
    excerpt = block[idx5 : idx5 + 600]

    required_phrases = [
        "background treatment",
        "icon style",
        "typography feel",
        "lighting",
        "overall mood",
    ]
    for phrase in required_phrases:
        assert phrase in excerpt.lower(), (
            f"Expected phrase '{phrase}' in dimension 5 description, but it was absent.\n"
            f"Excerpt:\n{excerpt}"
        )


def test_summary_says_all_5_dimensions():
    """The Summary line must say 'all 5 dimensions', not 'all 4'."""
    block = _quality_review_block(read_guide())
    assert SUMMARY_5_DIMS in block, (
        f"Expected '{SUMMARY_5_DIMS}' in Quality Review Criteria block.\n"
        "Did you forget to update the Summary line?"
    )


def test_summary_does_not_say_all_4_dimensions():
    """The Summary line must NOT say 'all 4 dimensions' (old wording)."""
    block = _quality_review_block(read_guide())
    assert "all 4 dimensions" not in block, (
        "Found 'all 4 dimensions' in Quality Review Criteria block — "
        "please update the Summary line to 'all 5 dimensions'."
    )


def test_original_4_dimensions_unchanged():
    """The first 4 dimension headings must still be present and in order."""
    text = read_guide()
    expected_dims = [
        "1. CONTENT ACCURACY:",
        "2. LAYOUT QUALITY:",
        "3. VISUAL CLARITY:",
        "4. PROMPT FIDELITY:",
    ]
    positions = []
    for dim in expected_dims:
        pos = text.find(dim)
        assert pos != -1, (
            f"Expected dimension heading '{dim}' not found — it may have been accidentally removed."
        )
        positions.append(pos)

    for i in range(1, len(positions)):
        assert positions[i] > positions[i - 1], (
            f"Dimension headings are out of order: '{expected_dims[i]}' should come after '{expected_dims[i - 1]}'"
        )
