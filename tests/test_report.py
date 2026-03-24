"""
Tests for eval/report.py — RED phase.

All tests in this file will fail with ModuleNotFoundError until eval/report.py
is implemented.

Covers:
- aggregate_scores: mean composite, dimension averages, scenario count, best/worst
- interpret_band: band labels for score ranges
- generate_markdown_report: composite scores, scenario names, dimension averages,
  interpretive band
- baseline comparison: with and without baseline showing/omitting trends
"""

from __future__ import annotations

import re

from eval.report import aggregate_scores, generate_markdown_report, interpret_band

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

# SCENARIO_SCORES: two evaluated scenarios used across all tests.
#
# dns:
#   composite_score  = 3.75
#   content_accuracy = 3.5
#   typography       = 3.0
#   (other dimensions filled in to be consistent)
#
# neural-networks:
#   composite_score  = 2.95
#   content_accuracy = 3.5
#   typography       = 2.0
#
# Aggregated expectations:
#   mean composite        = (3.75 + 2.95) / 2 = 3.35
#   avg content_accuracy  = (3.5 + 3.5) / 2   = 3.5
#   avg typography        = (3.0 + 2.0) / 2   = 2.5
#   best scenario         = 'dns'
#   worst scenario        = 'neural-networks'
#   interpret_band(3.35)  = 'Acceptable'

SCENARIO_SCORES: list[dict] = [
    {
        "scenario": "dns",
        "composite_score": 3.75,
        "scores": {
            "content_accuracy": {
                "score": 3.5,
                "evidence": "Good accuracy.",
                "improvement": "Minor gaps.",
            },
            "narrative_structure": {
                "score": 4.0,
                "evidence": "Clear flow.",
                "improvement": "None.",
            },
            "visual_explanation": {
                "score": 4.0,
                "evidence": "Good visuals.",
                "improvement": "None.",
            },
            "typography": {
                "score": 3.0,
                "evidence": "Readable.",
                "improvement": "Size up body text.",
            },
            "visual_quality": {
                "score": 4.0,
                "evidence": "Clean design.",
                "improvement": "None.",
            },
        },
    },
    {
        "scenario": "neural-networks",
        "composite_score": 2.95,
        "scores": {
            "content_accuracy": {
                "score": 3.5,
                "evidence": "Acceptable.",
                "improvement": "Add citations.",
            },
            "narrative_structure": {
                "score": 3.0,
                "evidence": "Adequate.",
                "improvement": "Clearer transitions.",
            },
            "visual_explanation": {
                "score": 3.0,
                "evidence": "Decent.",
                "improvement": "Simplify diagrams.",
            },
            "typography": {
                "score": 2.0,
                "evidence": "Hard to read.",
                "improvement": "Increase contrast.",
            },
            "visual_quality": {
                "score": 3.0,
                "evidence": "Average.",
                "improvement": "More polish.",
            },
        },
    },
]


# ---------------------------------------------------------------------------
# aggregate_scores
# ---------------------------------------------------------------------------


def test_aggregate_scores_computes_mean_composite() -> None:
    """aggregate_scores returns the arithmetic mean of all composite_score values.

    Expected: (3.75 + 2.95) / 2 = 3.35
    """
    result = aggregate_scores(SCENARIO_SCORES)
    expected = (3.75 + 2.95) / 2
    assert abs(result["mean_composite"] - expected) < 1e-9, (
        f"Expected mean_composite {expected}, got {result['mean_composite']}"
    )


def test_aggregate_scores_computes_dimension_averages() -> None:
    """aggregate_scores computes per-dimension averages across all scenarios.

    content_accuracy: (3.5 + 3.5) / 2 = 3.5
    typography:       (3.0 + 2.0) / 2 = 2.5
    """
    result = aggregate_scores(SCENARIO_SCORES)
    dim_avgs = result["dimension_averages"]
    assert abs(dim_avgs["content_accuracy"] - 3.5) < 1e-9, (
        f"Expected content_accuracy avg 3.5, got {dim_avgs['content_accuracy']}"
    )
    assert abs(dim_avgs["typography"] - 2.5) < 1e-9, (
        f"Expected typography avg 2.5, got {dim_avgs['typography']}"
    )


def test_aggregate_scores_includes_scenario_count() -> None:
    """aggregate_scores result includes scenario_count equal to the number of inputs."""
    result = aggregate_scores(SCENARIO_SCORES)
    assert result["scenario_count"] == 2, (
        f"Expected scenario_count 2, got {result['scenario_count']}"
    )


def test_aggregate_scores_finds_best_and_worst() -> None:
    """aggregate_scores identifies the scenario with the highest composite as best
    and the one with the lowest as worst.

    best  = 'dns'             (composite 3.75)
    worst = 'neural-networks' (composite 2.95)
    """
    result = aggregate_scores(SCENARIO_SCORES)
    assert result["best_scenario"] == "dns", (
        f"Expected best_scenario 'dns', got {result['best_scenario']}"
    )
    assert result["worst_scenario"] == "neural-networks", (
        f"Expected worst_scenario 'neural-networks', got {result['worst_scenario']}"
    )


# ---------------------------------------------------------------------------
# interpret_band
# ---------------------------------------------------------------------------


def test_interpret_band_high_quality() -> None:
    """interpret_band returns 'High quality' for scores >= 4.0."""
    assert interpret_band(4.2) == "High quality", (
        f"Expected 'High quality' for 4.2, got {interpret_band(4.2)!r}"
    )


def test_interpret_band_acceptable() -> None:
    """interpret_band returns 'Acceptable' for scores in [3.0, 4.0)."""
    assert interpret_band(3.5) == "Acceptable", (
        f"Expected 'Acceptable' for 3.5, got {interpret_band(3.5)!r}"
    )


def test_interpret_band_below_bar() -> None:
    """interpret_band returns 'Below bar' for scores in [2.0, 3.0)."""
    assert interpret_band(2.5) == "Below bar", (
        f"Expected 'Below bar' for 2.5, got {interpret_band(2.5)!r}"
    )


def test_interpret_band_failed() -> None:
    """interpret_band returns 'Failed' for scores below 2.0."""
    assert interpret_band(1.5) == "Failed", (
        f"Expected 'Failed' for 1.5, got {interpret_band(1.5)!r}"
    )


# ---------------------------------------------------------------------------
# generate_markdown_report — structure
# ---------------------------------------------------------------------------


def test_report_contains_composite_scores() -> None:
    """generate_markdown_report output includes each scenario's composite score.

    Both '3.75' (dns) and '2.95' (neural-networks) must appear in the report.
    """
    report = generate_markdown_report(SCENARIO_SCORES)
    assert "3.75" in report, "Report must contain composite score '3.75' for dns"
    assert "2.95" in report, (
        "Report must contain composite score '2.95' for neural-networks"
    )


def test_report_contains_scenario_names() -> None:
    """generate_markdown_report output names both evaluated scenarios."""
    report = generate_markdown_report(SCENARIO_SCORES)
    assert "dns" in report, "Report must reference scenario 'dns'"
    assert "neural-networks" in report, (
        "Report must reference scenario 'neural-networks'"
    )


def test_report_contains_dimension_averages() -> None:
    """generate_markdown_report output includes aggregated dimension averages.

    The report should contain the dimension average values (e.g. '3.5' for
    content_accuracy and '2.5' for typography).
    """
    report = generate_markdown_report(SCENARIO_SCORES)
    # At minimum the report must contain dimension-level summary information.
    # We check for at least one of the known average values.
    has_content_avg = "3.5" in report or "content_accuracy" in report.lower()
    has_typo_avg = "2.5" in report or "typography" in report.lower()
    assert has_content_avg, "Report must include content_accuracy dimension information"
    assert has_typo_avg, "Report must include typography dimension information"


def test_report_contains_interpretive_band() -> None:
    """generate_markdown_report includes the interpretive quality band for the run.

    mean_composite = 3.35 → interpret_band → 'Acceptable'
    """
    report = generate_markdown_report(SCENARIO_SCORES)
    assert "Acceptable" in report, (
        "Report must contain interpretive band label 'Acceptable' for mean_composite 3.35"
    )


# ---------------------------------------------------------------------------
# generate_markdown_report — baseline comparison
# ---------------------------------------------------------------------------


def test_report_with_baseline_shows_trends() -> None:
    """When a baseline dict is supplied, the report includes trend information.

    dns baseline = 3.0, actual composite = 3.75 → delta = +0.75.
    The report should contain either '+0.75' or the word 'improved'.
    """
    baseline = {"dns": 3.0, "neural-networks": 3.2}
    report = generate_markdown_report(SCENARIO_SCORES, baseline=baseline)
    has_delta = "+0.75" in report or "improved" in report.lower()
    assert has_delta, (
        "Report with baseline must indicate dns improved by +0.75 "
        "(expected '+0.75' or 'improved' in output)"
    )


def test_report_without_baseline_omits_trends() -> None:
    """When no baseline is supplied, the report must not contain trend indicators.

    Checks that '+' delta strings and the word 'improved' are absent.
    """
    report = generate_markdown_report(SCENARIO_SCORES)
    # The report should not contain any delta indicators without a baseline.
    assert "improved" not in report.lower(), (
        "Report without baseline must not contain 'improved'"
    )
    # A bare '+' could appear in other contexts (e.g. markdown), so we check
    # for the specific delta pattern: a '+' followed by digits like '+0.75'.
    delta_pattern = re.compile(r"\+\d+\.\d+")
    assert not delta_pattern.search(report), (
        "Report without baseline must not contain delta patterns like '+0.75'"
    )
