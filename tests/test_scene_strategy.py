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


# --- Sentinels ---
H2_PROMPT_ENGINEERING = "## Prompt Engineering"
H3_MULTI_PANEL = "### Multi-Panel Composition"  # next H3 after prompt list


def _get_prompt_engineering_block(content: str) -> str:
    start = content.index(H2_PROMPT_ENGINEERING)
    end = content.index("### ", start + len(H2_PROMPT_ENGINEERING))
    return content[start:end]


# --- Task 2: Prompt Engineering ---


def test_prompt_engineering_has_scene_directive_element() -> None:
    """Prompt Engineering list must include a scene directive element."""
    block = _get_prompt_engineering_block(read_guide())
    lower = block.lower()
    assert "scene directive" in lower, (
        "'scene directive' not found in Prompt Engineering section.\n"
        f"Actual block:\n{block}"
    )


def test_prompt_engineering_scene_directive_is_multi_panel_only() -> None:
    """Scene directive element must be scoped to multi-panel varied only."""
    block = _get_prompt_engineering_block(read_guide())
    lower = block.lower()
    assert "multi-panel" in lower and "varied" in lower, (
        "Scene directive must be scoped to 'multi-panel' and 'varied'.\n"
        f"Actual block:\n{block}"
    )


# --- Sentinels ---
H3_REF_IMAGE_CHAINING = "### Reference Image Chaining"


def _get_style_brief_block(content: str) -> str:
    start = content.index(H3_STYLE_BRIEF)
    end = content.index(H3_REF_IMAGE_CHAINING, start)
    return content[start:end]


# --- Task 3: Style Brief ---


def test_style_brief_mentions_varied_background() -> None:
    """Style brief section must note that Background changes for varied strategy."""
    block = _get_style_brief_block(read_guide())
    lower = block.lower()
    assert "varied" in lower and "scene directive" in lower, (
        "Style Brief must mention varied strategy and scene directive for Background.\n"
        f"Actual block:\n{block}"
    )


# --- Sentinels ---
H3_RECONCILIATION = "### Post-Panel 1 Style Reconciliation"
H3_PANEL_NAMING = "### Panel Naming Convention"


def _get_reconciliation_block(content: str) -> str:
    start = content.index(H3_RECONCILIATION)
    end = content.index(H3_PANEL_NAMING, start)
    return content[start:end]


# --- Task 4: Reconciliation ---


def test_reconciliation_has_varied_scoping_note() -> None:
    """Reconciliation section must note that background is panel-specific for varied."""
    block = _get_reconciliation_block(read_guide())
    lower = block.lower()
    assert "varied" in lower, (
        "Reconciliation must mention varied strategy.\n"
        f"Actual block:\n{block}"
    )


def test_reconciliation_varied_scopes_background() -> None:
    """Reconciliation varied note must distinguish background from style properties."""
    block = _get_reconciliation_block(read_guide())
    normalised = " ".join(block.lower().split())
    assert "background" in normalised and "style" in normalised, (
        "Reconciliation varied note must distinguish background from style.\n"
        f"Actual block:\n{block}"
    )
