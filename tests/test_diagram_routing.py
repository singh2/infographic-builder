"""Tests for root routing updates to detect diagram input and delegate."""
from pathlib import Path

BUNDLE_FILE = Path(__file__).parent.parent / "bundle.md"
AWARENESS_FILE = Path(__file__).parent.parent / "context" / "infographic-awareness.md"


def test_bundle_references_diagram_awareness() -> None:
    content = BUNDLE_FILE.read_text(encoding="utf-8")
    assert "diagram-beautifier-awareness" in content


def test_infographic_awareness_mentions_diagram_detection() -> None:
    content = AWARENESS_FILE.read_text(encoding="utf-8")
    assert "diagram" in content.lower()


def test_infographic_awareness_mentions_dot_pattern() -> None:
    content = AWARENESS_FILE.read_text(encoding="utf-8")
    assert ".dot" in content


def test_infographic_awareness_mentions_mermaid_pattern() -> None:
    content = AWARENESS_FILE.read_text(encoding="utf-8")
    lower = content.lower()
    assert "flowchart" in lower or "mermaid" in lower


def test_infographic_awareness_mentions_digraph_pattern() -> None:
    content = AWARENESS_FILE.read_text(encoding="utf-8")
    assert "digraph" in content


def test_infographic_awareness_routes_diagrams_to_beautifier() -> None:
    content = AWARENESS_FILE.read_text(encoding="utf-8")
    assert "diagram-beautifier" in content


def test_infographic_awareness_preserves_existing_delegation() -> None:
    content = AWARENESS_FILE.read_text(encoding="utf-8")
    assert "infographic-builder" in content


def test_diagram_awareness_mentions_png_extension() -> None:
    """diagram-beautifier-awareness.md must mention .png as a detectable input."""
    content = (Path(__file__).parent.parent / "context" / "diagram-beautifier-awareness.md").read_text(encoding="utf-8")
    assert ".png" in content


def test_infographic_awareness_routes_png_diagrams_to_beautifier() -> None:
    """infographic-awareness.md must describe routing PNG diagram input to diagram-beautifier."""
    content = (Path(__file__).parent.parent / "context" / "infographic-awareness.md").read_text(encoding="utf-8")
    assert ".png" in content
