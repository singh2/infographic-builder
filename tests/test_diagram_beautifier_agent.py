"""Tests for agents/diagram-beautifier.md structure and correctness."""
from pathlib import Path

AGENT_FILE = Path(__file__).parent.parent / "agents" / "diagram-beautifier.md"


def _read_agent() -> str:
    return AGENT_FILE.read_text(encoding="utf-8")


def test_agent_file_exists() -> None:
    assert AGENT_FILE.exists(), f"Agent file not found: {AGENT_FILE}"


def test_agent_has_yaml_frontmatter() -> None:
    content = _read_agent()
    assert content.startswith("---"), "Agent file must start with '---' frontmatter"
    second_delimiter = content.index("---", 3)
    assert second_delimiter > 3


def test_agent_frontmatter_has_meta_name() -> None:
    content = _read_agent()
    frontmatter_end = content.index("---", 3)
    frontmatter = content[:frontmatter_end]
    assert "name: diagram-beautifier" in frontmatter


def test_agent_frontmatter_has_model_role() -> None:
    content = _read_agent()
    frontmatter_end = content.index("---", 3)
    frontmatter = content[:frontmatter_end]
    assert "image-gen" in frontmatter


def test_workflow_has_9_steps() -> None:
    content = _read_agent()
    for n in range(1, 10):
        assert f"{n}. **" in content or f"{n}." in content, f"Step {n} not found"


def test_workflow_step_order() -> None:
    content = _read_agent()
    keywords_in_order = ["parse", "dependency", "aesthetic", "render", "decompos", "beautif", "review", "assembl", "return"]
    lower = content.lower()
    last_pos = -1
    for keyword in keywords_in_order:
        pos = lower.find(keyword)
        assert pos != -1, f"Keyword '{keyword}' not found"
        assert pos > last_pos, f"Keyword '{keyword}' out of order"
        last_pos = pos


def test_agent_mentions_render_first() -> None:
    content = _read_agent()
    lower = content.lower()
    assert "render" in lower and "reference" in lower


def test_agent_mentions_structural_preservation() -> None:
    content = _read_agent()
    lower = content.lower()
    assert "structural preservation" in lower or "preserve" in lower


def test_agent_mentions_label_fidelity() -> None:
    content = _read_agent()
    assert "label fidelity" in content.lower()


def test_agent_mentions_nano_banana() -> None:
    content = _read_agent()
    assert "nano-banana" in content


def test_agent_mentions_stitch_panels() -> None:
    content = _read_agent()
    assert "stitch_panels" in content


def test_agent_references_style_guide() -> None:
    content = _read_agent()
    assert "style-guide" in content or "style guide" in content.lower()


def test_agent_mentions_png_input() -> None:
    """Agent must describe PNG file as a supported input type."""
    content = _read_agent()
    assert ".png" in content


def test_agent_skips_render_for_png() -> None:
    """Agent must mention skipping the render step for PNG input."""
    content = _read_agent()
    lower = content.lower()
    assert "skip" in lower or "png" in lower and "render" in lower


def test_agent_uses_analyze_for_png_ground_truth() -> None:
    """Agent must mention using nano-banana analyze on PNG for label ground truth."""
    content = _read_agent()
    assert "analyze" in content.lower() and ".png" in content
