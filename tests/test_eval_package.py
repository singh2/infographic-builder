"""
Tests for the eval package initialisation.

Verifies that the package is importable and exposes the correct module docstring.
"""


def test_eval_package_is_importable() -> None:
    """eval can be imported without error."""
    import eval  # noqa: F401


def test_eval_package_docstring() -> None:
    """eval.__doc__ matches the required docstring exactly."""
    import eval

    expected = "Evaluation harness for AI-generated infographic quality."
    assert eval.__doc__ == expected, (
        f"Expected docstring {expected!r}, got {eval.__doc__!r}"
    )
