"""
Tests for the Layout Types table additions in docs/style-guide.md.

Acceptance criteria (task-2):
1. The Flowchart row now says 'Flowchart / process flow diagram' with expanded use cases.
2. Two new rows appear after Mind map: Storyboard journey and Long-form explainer panel.
3. The table now has 14 rows (12 original + 2 new), counting the header and separator.
4. Mind Map is NOT duplicated.
5. Commit message: "feat: add Storyboard Journey and Long-Form Explainer layouts, enrich Flowchart entry"
   (criterion 5 is verified manually via `git log` — commit message assertions are fragile in tests)
"""

import re

from helpers import H2_LAYOUT_TYPES, read_guide


def _get_layout_table(content: str) -> str:
    """Extract the Layout Types table block."""
    start = content.index(H2_LAYOUT_TYPES)
    # Find end: next H2 heading after Layout Types
    next_h2 = re.search(r"\n## ", content[start + len(H2_LAYOUT_TYPES) :])
    end = start + len(H2_LAYOUT_TYPES) + next_h2.start() if next_h2 else len(content)
    return content[start:end]


def _count_table_rows(table_block: str) -> int:
    """Count all pipe-delimited table rows (header + separator + data rows)."""
    return len(re.findall(r"^\|", table_block, re.MULTILINE))


# ---------------------------------------------------------------------------
# Criterion 1: Flowchart row updated to 'Flowchart / process flow diagram'
# ---------------------------------------------------------------------------


def test_flowchart_row_updated():
    """Flowchart row must say 'Flowchart / process flow diagram'."""
    content = read_guide()
    table = _get_layout_table(content)
    assert "Flowchart / process flow diagram" in table, (
        "Flowchart row must include 'Flowchart / process flow diagram'"
    )


def test_flowchart_row_old_text_gone():
    """Old flowchart text 'Flowchart with decision nodes' must be replaced."""
    content = read_guide()
    table = _get_layout_table(content)
    assert "Flowchart with decision nodes" not in table, (
        "Old flowchart text 'Flowchart with decision nodes' should be replaced"
    )


def test_flowchart_row_expanded_use_cases():
    """Flowchart row must include expanded use cases (algorithms, logic flows)."""
    content = read_guide()
    table = _get_layout_table(content)
    assert "algorithms" in table, (
        "Flowchart row must include 'algorithms' in its use cases"
    )
    assert "logic flows" in table, (
        "Flowchart row must include 'logic flows' in its use cases"
    )


# ---------------------------------------------------------------------------
# Criterion 2: Two new rows after Mind map
# ---------------------------------------------------------------------------


def test_storyboard_journey_row_present():
    """Storyboard journey row must be present in the Layout Types table."""
    content = read_guide()
    table = _get_layout_table(content)
    assert "Storyboard journey" in table, (
        "Storyboard journey row missing from Layout Types table"
    )


def test_long_form_explainer_row_present():
    """Long-form explainer panel row must be present in the Layout Types table."""
    content = read_guide()
    table = _get_layout_table(content)
    assert "Long-form explainer panel" in table, (
        "Long-form explainer panel row missing from Layout Types table"
    )


def test_new_rows_appear_after_mind_map():
    """Storyboard journey and Long-form explainer panel must appear after Mind map."""
    content = read_guide()
    table = _get_layout_table(content)

    mind_map_idx = table.index("Mind map / radial")
    storyboard_idx = table.index("Storyboard journey")
    long_form_idx = table.index("Long-form explainer panel")

    assert mind_map_idx < storyboard_idx, (
        "Storyboard journey must appear after Mind map row"
    )
    assert mind_map_idx < long_form_idx, (
        "Long-form explainer panel must appear after Mind map row"
    )
    assert storyboard_idx < long_form_idx, (
        "Storyboard journey must appear before Long-form explainer panel"
    )


# ---------------------------------------------------------------------------
# Criterion 3: Table has 14 rows (header + separator + 12 data rows)
# ---------------------------------------------------------------------------


def test_layout_table_has_16_rows():
    """Layout Types table must have exactly 16 pipe-delimited rows after adding 2 new layouts.

    Baseline: 14 rows (1 header + 1 separator + 12 data rows).
    After task-2: 16 rows (1 header + 1 separator + 14 data rows).
    """
    content = read_guide()
    table = _get_layout_table(content)
    row_count = _count_table_rows(table)
    assert row_count == 16, (
        f"Layout Types table must have 16 rows (header + separator + 14 data), found {row_count}"
    )


# ---------------------------------------------------------------------------
# Criterion 4: Mind Map is NOT duplicated
# ---------------------------------------------------------------------------


def test_mind_map_not_duplicated():
    """Mind map / radial must appear exactly once in the Layout Types table."""
    content = read_guide()
    table = _get_layout_table(content)
    occurrences = table.count("Mind map / radial")
    assert occurrences == 1, (
        f"'Mind map / radial' must appear exactly once, found {occurrences} times"
    )
