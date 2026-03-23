"""
Tests for the Style Consistency Brief template in docs/style-guide.md.

Acceptance criteria:
1. 'Aesthetic' is the first field in the Style Consistency Brief (before Background).
2. The bracket hint shows both curated and freeform examples.
3. The Background field hint is updated to say 'from the aesthetic template'.
4. The rest of the brief fields are unchanged.
5. Commit message: "feat: add Aesthetic field to Style Consistency Brief template"
"""

import re

from helpers import read_guide

STYLE_BRIEF_HEADER = "STYLE BRIEF (apply to all panels):"


def _get_style_brief_block(content: str) -> str:
    """Extract the fenced code block containing the Style Consistency Brief."""
    # Find the STYLE BRIEF header inside a fenced block
    idx = content.index(STYLE_BRIEF_HEADER)
    # Walk back to find the opening ```
    before = content[:idx]
    fence_start = before.rfind("```")
    assert fence_start != -1, "Could not find opening ``` for Style Brief block"

    # Walk forward to find the closing ```
    after = content[idx:]
    fence_end = after.index("```")
    return content[fence_start : idx + fence_end + 3]


def _get_brief_fields(content: str) -> list[str]:
    """Return ordered list of field names (text after '- ') from the brief block."""
    block = _get_style_brief_block(content)
    # Each field line looks like: "- FieldName: ..."
    matches = re.findall(r"^- (\w[\w /]+):", block, re.MULTILINE)
    return matches


# ---------------------------------------------------------------------------
# Criterion 1: Aesthetic is the FIRST field (before Background)
# ---------------------------------------------------------------------------


def test_aesthetic_is_first_field():
    """'Aesthetic' must be the first field in the Style Consistency Brief."""
    content = read_guide()
    fields = _get_brief_fields(content)
    assert fields, "No fields found in Style Consistency Brief"
    assert fields[0] == "Aesthetic", (
        f"First field must be 'Aesthetic', got: '{fields[0]}'"
    )


def test_aesthetic_before_background():
    """'Aesthetic' must appear before 'Background' in the brief."""
    content = read_guide()
    fields = _get_brief_fields(content)
    assert "Aesthetic" in fields, (
        "'Aesthetic' field not found in Style Consistency Brief"
    )
    assert "Background" in fields, (
        "'Background' field not found in Style Consistency Brief"
    )
    assert fields.index("Aesthetic") < fields.index("Background"), (
        "'Aesthetic' must come before 'Background'"
    )


# ---------------------------------------------------------------------------
# Criterion 2: Bracket hint shows both curated and freeform examples
# ---------------------------------------------------------------------------


def test_aesthetic_hint_has_curated_example():
    """The Aesthetic bracket hint must include a curated name example."""
    content = read_guide()
    block = _get_style_brief_block(content)
    # The curated example from the spec is "Claymation Studio"
    assert "Claymation Studio" in block, (
        "Aesthetic hint must include curated example 'Claymation Studio'"
    )


def test_aesthetic_hint_has_freeform_example():
    """The Aesthetic bracket hint must include a freeform description example."""
    content = read_guide()
    block = _get_style_brief_block(content)
    # The freeform example from the spec is "vintage travel poster"
    assert "vintage travel poster" in block, (
        "Aesthetic hint must include freeform example 'vintage travel poster'"
    )


# ---------------------------------------------------------------------------
# Criterion 3: Background hint updated to say 'from the aesthetic template'
# ---------------------------------------------------------------------------


def test_background_hint_references_aesthetic_template():
    """The Background field hint must reference 'from the aesthetic template'."""
    content = read_guide()
    block = _get_style_brief_block(content)
    assert "from the aesthetic template" in block, (
        "Background hint must say 'from the aesthetic template'"
    )


# ---------------------------------------------------------------------------
# Criterion 4: All other brief fields are unchanged
# ---------------------------------------------------------------------------

EXPECTED_REMAINING_FIELDS = [
    "Primary colors",
    "Accent color",
    "Typography",
    "Icons",
    "Border/separator",
    "Header chrome",
    "Aspect ratio",
]


def test_remaining_fields_unchanged():
    """All original brief fields (except Background hint) must still be present."""
    content = read_guide()
    fields = _get_brief_fields(content)
    for expected in EXPECTED_REMAINING_FIELDS:
        assert expected in fields, (
            f"Expected field '{expected}' missing from Style Consistency Brief"
        )


def test_field_order_after_aesthetic():
    """After Aesthetic and Background, the remaining fields must be in original order."""
    content = read_guide()
    fields = _get_brief_fields(content)
    # After inserting Aesthetic as first, expected full order is:
    expected_order = [
        "Aesthetic",
        "Background",
        "Primary colors",
        "Accent color",
        "Typography",
        "Icons",
        "Border/separator",
        "Header chrome",
        "Aspect ratio",
    ]
    assert fields == expected_order, (
        f"Field order mismatch.\nExpected: {expected_order}\nGot:      {fields}"
    )
