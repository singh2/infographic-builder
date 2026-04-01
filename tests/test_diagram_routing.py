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
    assert ".png" in content and "diagram-beautifier" in content


def test_infographic_awareness_analyze_before_routing_png() -> None:
    """infographic-awareness.md must instruct analyzing PNG before routing, not using keywords."""
    content = AWARENESS_FILE.read_text(encoding="utf-8")
    lower = content.lower()
    # Must mention analyzing the image, not just keywords
    assert "analyze" in lower and ".png" in lower


def test_infographic_awareness_mandatory_routing_language() -> None:
    """infographic-awareness.md must use mandatory/imperative routing language for PNG."""
    content = AWARENESS_FILE.read_text(encoding="utf-8")
    # Should have strong mandatory language, not advisory
    assert "MANDATORY" in content or "DO NOT" in content or "NEVER" in content


def test_infographic_awareness_passes_analysis_to_beautifier() -> None:
    """infographic-awareness.md must describe passing pre-analysis to diagram-beautifier."""
    content = AWARENESS_FILE.read_text(encoding="utf-8")
    lower = content.lower()
    assert "pre-analysis" in lower or "pre_analysis" in lower or "ground truth" in lower


def test_infographic_awareness_analyze_before_routing_png() -> None:
    """Routing must instruct analyzing the PNG before making routing decision."""
    content = AWARENESS_FILE.read_text(encoding="utf-8")
    lower = content.lower()
    assert "analyze" in lower and "png" in lower


def test_infographic_awareness_passes_analysis_to_agent() -> None:
    """Routing must instruct passing the analysis result to diagram-beautifier."""
    content = AWARENESS_FILE.read_text(encoding="utf-8")
    assert "passing" in content.lower() or "pass" in content.lower()


def test_infographic_awareness_no_keyword_dependency_for_png() -> None:
    """Routing must not rely on user keywords for PNG — must use image analysis."""
    content = AWARENESS_FILE.read_text(encoding="utf-8")
    lower = content.lower()
    # The routing section must instruct to analyze the image, not check keywords
    assert "do not" in lower or "always analyze" in lower or "regardless" in lower


# ---------------------------------------------------------------------------
# Enriched analyze prompt: content_summary + aesthetic_description
# ---------------------------------------------------------------------------

def test_analyze_prompt_extracts_content_summary() -> None:
    """The enriched analyze prompt must instruct extraction of content_summary."""
    content = AWARENESS_FILE.read_text(encoding="utf-8")
    lower = content.lower()
    assert "content summary" in lower or "content_summary" in lower, (
        "Analyze prompt must mention content summary extraction.\n"
        f"File content:\n{content}"
    )

def test_analyze_prompt_extracts_aesthetic_description() -> None:
    """The enriched analyze prompt must instruct extraction of aesthetic_description."""
    content = AWARENESS_FILE.read_text(encoding="utf-8")
    lower = content.lower()
    assert "aesthetic description" in lower or "aesthetic_description" in lower, (
        "Analyze prompt must mention aesthetic description extraction.\n"
        f"File content:\n{content}"
    )
