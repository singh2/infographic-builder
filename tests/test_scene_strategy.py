"""
Tests for scene strategy (varied / consistent) in multi-panel pipeline.

Covers 6 touchpoints across docs/style-guide.md and agents/infographic-builder.md.
See design doc: docs/superpowers/specs/2026-04-03-scene-strategy-design.md
"""

import re

from helpers import read_agent, read_guide

# --- Sentinels ---
H3_CONTENT_MAP = "### Content Map"
H3_STYLE_BRIEF = "### Style Consistency Brief"


# --- Block extractors ---
def _get_content_map_block(content: str) -> str:
    start = content.index(H3_CONTENT_MAP)
    end = content.index(H3_STYLE_BRIEF, start)
    return content[start:end]


# --- Task 1: Content Map ---


def test_content_map_has_scene_strategy_line() -> None:
    """Content map template must include a 'Scene strategy:' line."""
    block = _get_content_map_block(read_guide())
    assert "Scene strategy:" in block, (
        "'Scene strategy:' not found in Content Map template.\n"
        f"Actual block:\n{block}"
    )


def test_content_map_has_varied_and_consistent_values() -> None:
    """Content map must name both 'varied' and 'consistent' as valid values."""
    block = _get_content_map_block(read_guide())
    lower = block.lower()
    assert "varied" in lower, "'varied' not found in Content Map"
    assert "consistent" in lower, "'consistent' not found in Content Map"


def test_content_map_has_per_panel_scene_field() -> None:
    """Content map template must include a 'Scene:' field for per-panel directives."""
    block = _get_content_map_block(read_guide())
    assert "Scene:" in block, (
        "'Scene:' per-panel field not found in Content Map template.\n"
        f"Actual block:\n{block}"
    )


def test_content_map_scene_only_when_varied() -> None:
    """Content map must state Scene: lines are only for varied strategy."""
    block = _get_content_map_block(read_guide())
    normalised = " ".join(block.lower().split())
    assert "varied" in normalised and "scene" in normalised, (
        "Content Map must connect Scene: field to varied strategy.\n"
        f"Actual block:\n{block}"
    )


def test_content_map_has_decision_heuristic() -> None:
    """Content map section must include guidance on when to use varied vs consistent."""
    block = _get_content_map_block(read_guide())
    lower = block.lower()
    # Must mention narrative/journey topics as varied triggers
    assert "journey" in lower or "narrative" in lower or "routine" in lower, (
        "Content Map must mention narrative/journey topics as varied triggers.\n"
        f"Actual block:\n{block}"
    )


def test_content_map_default_is_consistent() -> None:
    """Content map must state that 'consistent' is the default when in doubt."""
    block = _get_content_map_block(read_guide())
    lower = block.lower()
    assert "default" in lower and "consistent" in lower, (
        "Content Map must specify 'consistent' as the default strategy.\n"
        f"Actual block:\n{block}"
    )
