"""
Tests for the Dealbreaker Check sub-section in docs/style-guide.md.

Acceptance criteria:
1. `### Dealbreaker Check` heading exists inside the Quality Review Criteria section.
2. The section describes a text-legibility binary check.
3. The section describes a core-content-present binary check.
4. The section describes an aesthetic-match binary check.
5. Failure handling: silently regenerate once on failure.
6. Drop / discard the candidate if it fails a second time.
"""

from helpers import read_guide


# ── Helpers ──────────────────────────────────────────────────────────────────


def _get_dealbreaker_section(content: str) -> str:
    start = content.index("### Dealbreaker Check")
    end = content.index("\n### ", start + 1)
    return content[start:end]


# ── Tests ─────────────────────────────────────────────────────────────────────


def test_dealbreaker_check_section_exists():
    """'### Dealbreaker Check' heading must exist in the style guide."""
    content = read_guide()
    assert "### Dealbreaker Check" in content, (
        "'### Dealbreaker Check' heading not found in docs/style-guide.md"
    )


def test_dealbreaker_checks_text_legibility():
    """The dealbreaker section must mention text legibility as a binary check."""
    content = read_guide()
    section = _get_dealbreaker_section(content)
    lower = section.lower()
    assert "text" in lower, "Expected 'text' in dealbreaker section"
    assert "legib" in lower, (
        "Expected 'legib' (legible/legibility) in dealbreaker section"
    )


def test_dealbreaker_checks_core_content():
    """The dealbreaker section must mention core content being present."""
    content = read_guide()
    section = _get_dealbreaker_section(content)
    lower = section.lower()
    assert "content" in lower, "Expected 'content' in dealbreaker section"
    assert "present" in lower, "Expected 'present' in dealbreaker section"


def test_dealbreaker_checks_aesthetic_match():
    """The dealbreaker section must mention aesthetic match as a check."""
    content = read_guide()
    section = _get_dealbreaker_section(content)
    assert "aesthetic" in section.lower(), "Expected 'aesthetic' in dealbreaker section"


def test_dealbreaker_regenerate_on_failure():
    """The dealbreaker section must specify regenerating once on failure."""
    content = read_guide()
    section = _get_dealbreaker_section(content)
    assert "regenerate" in section.lower(), (
        "Expected 'regenerate' in dealbreaker section (failure handling policy)"
    )


def test_dealbreaker_drop_after_second_failure():
    """The dealbreaker section must specify dropping/discarding after a second failure."""
    content = read_guide()
    section = _get_dealbreaker_section(content)
    lower = section.lower()
    assert "drop" in lower or "discard" in lower, (
        "Expected 'drop' or 'discard' in dealbreaker section (second-failure policy)"
    )
