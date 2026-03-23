"""
Shared test helpers for docs/style-guide.md and agents/infographic-builder.md
test suites.

Centralises file path constants, section heading sentinels, and read helpers
so multiple test modules can import them without duplication.
"""

from pathlib import Path

STYLE_GUIDE = Path(__file__).parent.parent / "docs" / "style-guide.md"
AGENT_FILE = Path(__file__).parent.parent / "agents" / "infographic-builder.md"

H2_LAYOUT_TYPES = "## Layout Types"


def read_guide() -> str:
    return STYLE_GUIDE.read_text(encoding="utf-8")


def read_agent() -> str:
    return AGENT_FILE.read_text(encoding="utf-8")
