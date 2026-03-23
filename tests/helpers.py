"""
Shared test helpers for docs/style-guide.md test suites.

Centralises the file path constant, the section heading sentinel, and the
read helper so multiple test modules can import them without duplication.
"""

from pathlib import Path

STYLE_GUIDE = Path(__file__).parent.parent / "docs" / "style-guide.md"

H2_LAYOUT_TYPES = "## Layout Types"


def read_guide() -> str:
    return STYLE_GUIDE.read_text(encoding="utf-8")
