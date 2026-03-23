"""
Tests for the Aesthetics section in docs/style-guide.md.

Acceptance criteria:
1. The `> **Note:**` callout appears directly after the Default Style bullet list.
2. `## Aesthetics` is a new H2 section before `## Layout Types`.
3. All 6 aesthetics have `###` subheadings, a blockquote tagline, and 7 bullet-point properties
   (Background, Typography, Icons, Color palette, Lighting, Texture, Mood).
4. The `### Freeform Aesthetics` subsection is last, with 3 numbered rules.
5. `## Layout Types` still appears after the Aesthetics section, unmodified.
6. Commit message: "feat: add Aesthetics section with 6 curated prompt templates to style guide"
"""

import re
from pathlib import Path

STYLE_GUIDE = Path(__file__).parent.parent / "docs" / "style-guide.md"

EXPECTED_AESTHETICS = [
    "Clean Minimalist",
    "Dark Mode Tech",
    "Bold Editorial",
    "Hand-Drawn Sketchnote",
    "Claymation Studio",
    "Lego Brick Builder",
]

EXPECTED_PROPERTIES = [
    "Background",
    "Typography",
    "Icons",
    "Color palette",
    "Lighting",
    "Texture",
    "Mood",
]

H2_AESTHETICS = "## Aesthetics"
H2_LAYOUT_TYPES = "## Layout Types"
H3_FREEFORM = "### Freeform Aesthetics"


def read_guide() -> str:
    return STYLE_GUIDE.read_text(encoding="utf-8")


def _get_aesthetic_block(content: str, aesthetic: str) -> str:
    """Extract the markdown block for a single aesthetic (heading → next ### or end)."""
    start = content.index(H2_AESTHETICS)
    end = content.index(H2_LAYOUT_TYPES)
    section = content[start:end]

    pattern = rf"### \d+\. {re.escape(aesthetic)}"
    m = re.search(pattern, section)
    assert m, f"Heading not found for: {aesthetic}"

    next_heading = re.search(r"\n###", section[m.end() :])
    # block_end falls back to end of section if no next ### exists (only
    # correct while ### Freeform Aesthetics terminates the numbered list)
    block_end = m.end() + next_heading.start() if next_heading else len(section)
    return section[m.start() : block_end]


# ---------------------------------------------------------------------------
# Criterion 1: Note callout directly after Default Style bullet list
# ---------------------------------------------------------------------------


def test_note_callout_after_default_style():
    """The > **Note:** callout must appear directly after the Default Style bullets."""
    content = read_guide()
    # The last bullet of Default Style
    anchor = "- **Whitespace**: Generous -- let the content breathe"
    assert anchor in content, "Default Style anchor line not found"

    # After the anchor there should be a Note callout before the next heading
    idx = content.index(anchor)
    after_anchor = content[idx:]
    # Check that the Note blockquote appears before any next H2
    note_match = re.search(r"> \*\*Note:\*\*", after_anchor)
    assert note_match, "> **Note:** callout not found after Default Style"

    next_h2 = re.search(r"\n## ", after_anchor)
    assert next_h2, "No H2 heading found after Default Style"
    assert note_match.start() < next_h2.start(), (
        "> **Note:** callout must appear before the next H2 heading"
    )


# ---------------------------------------------------------------------------
# Criterion 2: ## Aesthetics H2 exists and comes before ## Layout Types
# ---------------------------------------------------------------------------


def test_aesthetics_h2_before_layout_types():
    """## Aesthetics must be a top-level section before ## Layout Types."""
    content = read_guide()
    assert H2_AESTHETICS in content, "## Aesthetics section not found"
    assert H2_LAYOUT_TYPES in content, "## Layout Types section not found"

    aesthetics_idx = content.index(H2_AESTHETICS)
    layout_idx = content.index(H2_LAYOUT_TYPES)
    assert aesthetics_idx < layout_idx, (
        "## Aesthetics must appear before ## Layout Types"
    )


# ---------------------------------------------------------------------------
# Criterion 3: All 6 aesthetics have ### subheadings, blockquote tagline, 7 properties
# ---------------------------------------------------------------------------


def test_all_six_aesthetics_present():
    """Each of the 6 named aesthetics must have a ### heading."""
    content = read_guide()
    for aesthetic in EXPECTED_AESTHETICS:
        pattern = rf"### \d+\. {re.escape(aesthetic)}"
        assert re.search(pattern, content), (
            f"Missing ### heading for aesthetic: {aesthetic}"
        )


def test_each_aesthetic_has_blockquote_tagline():
    """Each aesthetic block must contain a blockquote tagline (> ...)."""
    content = read_guide()
    for aesthetic in EXPECTED_AESTHETICS:
        block = _get_aesthetic_block(content, aesthetic)
        assert re.search(r"^> .+", block, re.MULTILINE), (
            f"Missing blockquote tagline for: {aesthetic}"
        )


def test_each_aesthetic_has_seven_properties():
    """Each aesthetic must have all 7 required bullet-point properties."""
    content = read_guide()
    for aesthetic in EXPECTED_AESTHETICS:
        block = _get_aesthetic_block(content, aesthetic)
        for prop in EXPECTED_PROPERTIES:
            assert f"**{prop}:**" in block, (
                f"Missing property '{prop}' in aesthetic: {aesthetic}"
            )


# ---------------------------------------------------------------------------
# Criterion 4: ### Freeform Aesthetics subsection with 3 numbered rules
# ---------------------------------------------------------------------------


def test_freeform_aesthetics_subsection_exists():
    """### Freeform Aesthetics must be a subsection within ## Aesthetics."""
    content = read_guide()
    assert H3_FREEFORM in content, "### Freeform Aesthetics subsection not found"

    aesthetics_idx = content.index(H2_AESTHETICS)
    layout_idx = content.index(H2_LAYOUT_TYPES)
    freeform_idx = content.index(H3_FREEFORM)

    assert aesthetics_idx < freeform_idx < layout_idx, (
        "### Freeform Aesthetics must be inside ## Aesthetics, before ## Layout Types"
    )


def test_freeform_has_three_numbered_rules():
    """### Freeform Aesthetics must contain exactly 3 numbered rules."""
    content = read_guide()
    start = content.index(H3_FREEFORM)
    end = content.index(H2_LAYOUT_TYPES)
    freeform_block = content[start:end]

    # Match numbered list items: "1.", "2.", "3."
    rules = re.findall(r"^\d+\.", freeform_block, re.MULTILINE)
    assert len(rules) == 3, (
        f"### Freeform Aesthetics must have 3 numbered rules, found {len(rules)}"
    )


def test_freeform_is_last_subsection_before_layout_types():
    """### Freeform Aesthetics must be the last ### subsection before ## Layout Types."""
    content = read_guide()
    aesthetics_idx = content.index(H2_AESTHETICS)
    layout_idx = content.index(H2_LAYOUT_TYPES)
    aesthetics_block = content[aesthetics_idx:layout_idx]

    subsections = list(re.finditer(r"^### .+", aesthetics_block, re.MULTILINE))
    assert subsections, "No ### subsections found in ## Aesthetics"

    last_subsection = subsections[-1].group()
    assert "Freeform Aesthetics" in last_subsection, (
        f"Last subsection must be Freeform Aesthetics, got: {last_subsection}"
    )


# ---------------------------------------------------------------------------
# Criterion 5: ## Layout Types still present and after ## Aesthetics
# ---------------------------------------------------------------------------


def test_layout_types_still_present():
    """## Layout Types must still appear after ## Aesthetics."""
    content = read_guide()
    assert H2_LAYOUT_TYPES in content, "## Layout Types section is missing!"

    aesthetics_idx = content.index(H2_AESTHETICS)
    layout_idx = content.index(H2_LAYOUT_TYPES)
    assert aesthetics_idx < layout_idx, "## Layout Types must follow ## Aesthetics"


def test_layout_types_content_intact():
    """## Layout Types table content must be unmodified."""
    content = read_guide()
    # Check a few known rows from the original table
    assert "Step-by-step process" in content, "Layout Types table content corrupted"
    assert "Comparison" in content, "Layout Types table content corrupted"
    assert "Statistics" in content, "Layout Types table content corrupted"
