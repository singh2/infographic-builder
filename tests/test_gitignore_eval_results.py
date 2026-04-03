"""Tests that .gitignore contains the eval-results/ block as specified."""

import os


GITIGNORE_PATH = os.path.join(os.path.dirname(__file__), "..", ".gitignore")


def read_gitignore() -> str:
    with open(GITIGNORE_PATH, "r") as f:
        return f.read()


def test_gitignore_contains_eval_results_pattern():
    """eval-results/ pattern must be present in .gitignore."""
    content = read_gitignore()
    assert "eval-results/" in content, "eval-results/ pattern not found in .gitignore"


def test_gitignore_contains_eval_results_comment():
    """The block comment for eval-results must be present."""
    content = read_gitignore()
    assert "# Evaluation harness output (timestamped results directories)" in content, (
        "eval-results block comment not found in .gitignore"
    )


def test_gitignore_preserves_existing_content():
    """Existing .gitignore content must be intact."""
    content = read_gitignore()
    existing_patterns = [
        "/infographic*.png",
        "/infographic*.jpg",
        "*.jpeg",
        "# Keep docs images",
        "!docs/*.png",
        "# Amplifier local settings (entire directory",
        ".amplifier/",
        "# OS files",
        ".DS_Store",
    ]
    for pattern in existing_patterns:
        assert pattern in content, (
            f"Existing entry '{pattern}' was removed from .gitignore"
        )


def test_gitignore_eval_results_block_follows_ds_store():
    """The eval-results block must appear after the .DS_Store line."""
    content = read_gitignore()
    ds_store_pos = content.find(".DS_Store")
    eval_results_pos = content.find("eval-results/")
    assert ds_store_pos != -1, ".DS_Store not found in .gitignore"
    assert eval_results_pos != -1, "eval-results/ not found in .gitignore"
    assert eval_results_pos > ds_store_pos, (
        "eval-results/ block must appear after .DS_Store"
    )


def test_gitignore_eval_results_block_is_present():
    """The eval-results/ pattern must exist in .gitignore."""
    content = read_gitignore()
    lines = [line.strip() for line in content.splitlines()]
    assert "eval-results/" in lines, "eval-results/ must be present in .gitignore"
