from pathlib import Path

DIAGRAM_STYLE_GUIDE = Path(__file__).parent.parent / "docs" / "diagram-style-guide.md"


def test_file_exists() -> None:
    """docs/diagram-style-guide.md must exist."""
    assert DIAGRAM_STYLE_GUIDE.exists(), "docs/diagram-style-guide.md not found"


def test_scoping_disclaimer_present() -> None:
    """File must state its scope — 'ONLY' and 'diagram-beautifier' must both appear."""
    content = DIAGRAM_STYLE_GUIDE.read_text()
    assert "ONLY" in content, "Scope disclaimer missing 'ONLY'"
    assert "diagram-beautifier" in content, (
        "Scope disclaimer missing 'diagram-beautifier'"
    )


def test_node_shape_table_present() -> None:
    """File must contain a 'Node Shapes' section heading."""
    content = DIAGRAM_STYLE_GUIDE.read_text()
    assert "Node Shapes" in content, "'Node Shapes' section heading not found"


def test_dark_mode_tech_has_hexagon_for_ai_agent_steps() -> None:
    """Dark Mode Tech aesthetic must specify Hexagon for AI Agent steps."""
    content = DIAGRAM_STYLE_GUIDE.read_text()
    assert "Dark Mode Tech" in content, "'Dark Mode Tech' aesthetic not found"
    assert "Hexagon" in content, (
        "'Hexagon' shape not found for Dark Mode Tech AI Agent steps"
    )


def test_clean_minimalist_has_orthogonal_connector_constraint() -> None:
    """Clean Minimalist must require orthogonal connectors and forbid diagonals."""
    content = DIAGRAM_STYLE_GUIDE.read_text()
    assert "Orthogonal only" in content, "'Orthogonal only' connector rule not found"
    assert "Diagonal edges strictly forbidden" in content, (
        "Diagonal edges constraint not found"
    )


def test_dark_mode_tech_has_single_legend_constraint() -> None:
    """Dark Mode Tech must specify exactly ONE legend box."""
    content = DIAGRAM_STYLE_GUIDE.read_text()
    assert "ONE" in content, "'ONE' legend constraint not found"
    assert "legend" in content.lower(), "'legend' not mentioned in the file"


def test_connector_styling_table_present() -> None:
    """File must contain a 'Connector Styling' section heading."""
    content = DIAGRAM_STYLE_GUIDE.read_text()
    assert "Connector Styling" in content, (
        "'Connector Styling' section heading not found"
    )


def test_quality_bar_directive_present() -> None:
    """File must contain the quality bar opening directive."""
    content = DIAGRAM_STYLE_GUIDE.read_text()
    assert "dramatically more visually impressive" in content, (
        "Quality bar directive ('dramatically more visually impressive') not found"
    )


def test_color_category_mapping_guidance_present() -> None:
    """File must contain color-category mapping guidance (any casing)."""
    content = DIAGRAM_STYLE_GUIDE.read_text()
    assert "color-category mapping" in content.lower(), (
        "'Color-category mapping' guidance not found"
    )
