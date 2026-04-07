import pytest
from helpers import read_guide, read_agent

EXTENDED_LIBRARY_STYLES = [
    "Minecraft Voxel",
    "Comic Book / Graphic Novel",
    "Gundam / Mobile Suit Mecha",
    "Warhammer 40K",
    "Pixel Art (8-bit)",
    "Cyberpunk / Neon",
    "Vintage Science Poster",
    "Blueprint / Schematic",
    "Knolling (Flat Lay)",
    "Da Vinci Notebook",
    "Storybook Watercolor",
    "Pop Art (Warhol / Lichtenstein)",
    "Neon Nightlife / Neon Sign",
    "Vintage Travel Poster (WPA / Art Deco)",
    "Paper Cutout",
    "Graffiti Wall",
    "Chalkboard Art",
]


# ── Style Guide: Extended Library Section ────────────────────────────────────


def test_extended_library_section_exists():
    content = read_guide()
    assert "## Extended Library" in content


@pytest.mark.parametrize("style_name", EXTENDED_LIBRARY_STYLES)
def test_style_has_heading(style_name):
    content = read_guide()
    assert f"### {style_name}" in content, f"Missing heading: ### {style_name}"


@pytest.mark.parametrize("style_name", EXTENDED_LIBRARY_STYLES)
def test_style_has_tagline(style_name):
    content = read_guide()
    heading_pos = content.find(f"### {style_name}")
    assert heading_pos != -1, f"Heading not found for {style_name}"
    section = content[heading_pos : heading_pos + 400]
    assert "\n> " in section, f"Missing blockquote tagline after ### {style_name}"


@pytest.mark.parametrize("style_name", EXTENDED_LIBRARY_STYLES)
def test_style_has_affinity_tags(style_name):
    content = read_guide()
    heading_pos = content.find(f"### {style_name}")
    assert heading_pos != -1, f"Heading not found for {style_name}"
    next_heading = content.find("\n###", heading_pos + 4)
    section = (
        content[heading_pos:next_heading]
        if next_heading != -1
        else content[heading_pos:]
    )
    assert "**Content affinity:**" in section, (
        f"Missing **Content affinity:** in ### {style_name}"
    )


# ── Agent: Step 2 content types (Task 2) ─────────────────────────────────────


def test_agent_step2_outputs_content_types():
    content = read_agent()
    assert "Content types:" in content


# ── Agent: Step 3 style preview (Task 3) ─────────────────────────────────────


def test_agent_step3_has_style_preview():
    content = read_agent()
    assert "swap a style by name" in content


# ── Agent: Step 5B extended library pool (Task 4) ────────────────────────────


def test_agent_step5b_has_extended_library_pool():
    content = read_agent()
    assert "extended library" in content.lower()
    assert "affinity" in content.lower()
