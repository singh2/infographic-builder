"""
Tests for the Variation Cascade section in docs/style-guide.md.

Acceptance criteria:
1. A '## Variation Cascade' section exists in the style guide.
2. Tier 1 (vary aesthetic) is defined: triggers when no aesthetic specified, generates 3
   candidates in different aesthetics for maximum visual diversity.
3. Tier 2 (vary by aesthetic type) is defined: maps each aesthetic to its variation axis
   (environment/setting for 3D styles, composition for flat styles).
4. 3D aesthetics (Claymation, Lego) are mapped to environment/setting variation.
5. Flat aesthetics (Clean Minimalist, Dark Mode Tech) are mapped to composition variation.
6. Tier 3 (model freedom) is defined: identical constraints, nudge for distinct interpretation.
7. Three composition directions are defined: central focal point, scene-based,
   structured/diagrammatic.
"""

from helpers import read_guide


def _get_variation_cascade_section(content):
    start = content.index("## Variation Cascade")
    end = content.index("\n## ", start + 1)
    return content[start:end]


# ---------------------------------------------------------------------------
# Criterion 1: ## Variation Cascade section exists
# ---------------------------------------------------------------------------


def test_variation_cascade_section_exists():
    """'## Variation Cascade' must be a top-level section in the style guide."""
    content = read_guide()
    assert "## Variation Cascade" in content, (
        "'## Variation Cascade' section not found in style guide"
    )


# ---------------------------------------------------------------------------
# Criterion 2: Tier 1 — vary aesthetic
# ---------------------------------------------------------------------------


def test_tier_1_varies_aesthetic():
    """Tier 1 must specify: no aesthetic given, generate 3 candidates in different aesthetics."""
    content = read_guide()
    section = _get_variation_cascade_section(content)
    lower = section.lower()
    assert "tier 1" in lower, "Tier 1 not defined in Variation Cascade section"
    assert "aesthetic" in lower, "Tier 1 must reference aesthetics"
    # Must generate 3 candidates
    assert "3" in section, "Tier 1 must specify generating 3 candidates"
    # Must maximize visual diversity
    assert "diversity" in lower or "diverse" in lower, (
        "Tier 1 must mention visual diversity"
    )


# ---------------------------------------------------------------------------
# Criterion 3: Tier 2 — vary by aesthetic type (environment + composition)
# ---------------------------------------------------------------------------


def test_tier_2_varies_by_aesthetic_type():
    """Tier 2 must reference both 'environment' and 'composition' as variation axes."""
    content = read_guide()
    section = _get_variation_cascade_section(content)
    lower = section.lower()
    assert "tier 2" in lower, "Tier 2 not defined in Variation Cascade section"
    assert "environment" in lower, "Tier 2 must mention environment as a variation axis"
    assert "composition" in lower, "Tier 2 must mention composition as a variation axis"


# ---------------------------------------------------------------------------
# Criterion 4: 3D styles (Claymation, Lego) → environment variation
# ---------------------------------------------------------------------------


def test_tier_2_3d_styles_vary_environment():
    """Claymation Studio and Lego Brick Builder must be mapped to environment/setting variation."""
    content = read_guide()
    section = _get_variation_cascade_section(content)
    # Check that each 3D aesthetic's table row pairs it with Environment/setting
    # A table row looks like: "| Claymation Studio | Environment/setting |"
    claymation_row = next(
        (line for line in section.splitlines() if "Claymation" in line and "|" in line),
        None,
    )
    assert claymation_row is not None, "Claymation Studio table row not found"
    assert "Environment" in claymation_row or "environment" in claymation_row, (
        f"Claymation Studio must map to Environment/setting, got: {claymation_row!r}"
    )
    lego_row = next(
        (line for line in section.splitlines() if "Lego" in line and "|" in line),
        None,
    )
    assert lego_row is not None, "Lego Brick Builder table row not found"
    assert "Environment" in lego_row or "environment" in lego_row, (
        f"Lego Brick Builder must map to Environment/setting, got: {lego_row!r}"
    )


# ---------------------------------------------------------------------------
# Criterion 5: Flat styles (Clean Minimalist, Dark Mode Tech) → composition variation
# ---------------------------------------------------------------------------


def test_tier_2_flat_styles_vary_composition():
    """Clean Minimalist and Dark Mode Tech must be mapped to composition variation."""
    content = read_guide()
    section = _get_variation_cascade_section(content)
    # Check that each flat aesthetic's table row pairs it with Composition
    # A table row looks like: "| Clean Minimalist | Composition |"
    minimalist_row = next(
        (
            line
            for line in section.splitlines()
            if "Clean Minimalist" in line and "|" in line
        ),
        None,
    )
    assert minimalist_row is not None, "Clean Minimalist table row not found"
    assert "Composition" in minimalist_row or "composition" in minimalist_row, (
        f"Clean Minimalist must map to Composition, got: {minimalist_row!r}"
    )
    dark_mode_row = next(
        (
            line
            for line in section.splitlines()
            if "Dark Mode Tech" in line and "|" in line
        ),
        None,
    )
    assert dark_mode_row is not None, "Dark Mode Tech table row not found"
    assert "Composition" in dark_mode_row or "composition" in dark_mode_row, (
        f"Dark Mode Tech must map to Composition, got: {dark_mode_row!r}"
    )


# ---------------------------------------------------------------------------
# Criterion 6: Tier 3 — model freedom
# ---------------------------------------------------------------------------


def test_tier_3_model_freedom():
    """Tier 3 must describe identical constraints with a nudge for distinct visual interpretation."""
    content = read_guide()
    section = _get_variation_cascade_section(content)
    lower = section.lower()
    assert "tier 3" in lower, "Tier 3 not defined in Variation Cascade section"
    # Must mention identical/same constraints
    assert "identical" in lower or "same" in lower, (
        "Tier 3 must specify identical constraints across candidates"
    )
    # Must include a nudge for distinct interpretation
    assert "interpret" in lower or "interpretation" in lower or "distinct" in lower, (
        "Tier 3 must nudge toward a distinct visual interpretation"
    )


# ---------------------------------------------------------------------------
# Criterion 7: Three composition directions defined
# ---------------------------------------------------------------------------


def test_composition_directions_defined():
    """Three composition directions must be defined: central focal point, scene-based,
    and diagrammatic/structured."""
    content = read_guide()
    section = _get_variation_cascade_section(content)
    lower = section.lower()
    assert "central focal point" in lower, (
        "Composition direction 'central focal point' must be defined"
    )
    assert "scene-based" in lower or "scene based" in lower, (
        "Composition direction 'scene-based' must be defined"
    )
    assert "diagrammatic" in lower or "structured" in lower, (
        "Composition direction 'diagrammatic/structured' must be defined"
    )
