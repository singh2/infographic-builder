"""Score aggregation and markdown report generation for infographic evaluation.

Provides:
- interpret_band: maps a composite score to a quality band label
- aggregate_scores: summarises a list of evaluation results
- generate_markdown_report: renders a full markdown evaluation report
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DIMENSION_LABELS: dict[str, str] = {
    "content_accuracy": "Content Accuracy",
    "narrative_structure": "Narrative Structure",
    "visual_explanation": "Visual Explanation",
    "typography": "Typography & Legibility",
    "visual_quality": "Visual Quality & Consistency",
}

_DIMENSION_WEIGHTS: dict[str, float] = {
    "content_accuracy": 0.20,
    "narrative_structure": 0.15,
    "visual_explanation": 0.25,
    "typography": 0.20,
    "visual_quality": 0.20,
}


# ---------------------------------------------------------------------------
# interpret_band
# ---------------------------------------------------------------------------


def interpret_band(composite: float) -> str:
    """Map a composite score to a human-readable quality band.

    Bands:
        4.0 – 5.0  →  'High quality'
        3.0 – 3.9  →  'Acceptable'
        2.0 – 2.9  →  'Below bar'
        1.0 – 1.9  →  'Failed'

    Args:
        composite: A numeric composite score (typically 1.0–5.0).

    Returns:
        Quality band label string.
    """
    if composite >= 4.0:
        return "High quality"
    if composite >= 3.0:
        return "Acceptable"
    if composite >= 2.0:
        return "Below bar"
    return "Failed"


# ---------------------------------------------------------------------------
# aggregate_scores
# ---------------------------------------------------------------------------


def aggregate_scores(results: list[dict]) -> dict:
    """Compute summary statistics across a list of evaluation results.

    Args:
        results: List of result dicts, each containing at minimum
            ``scenario``, ``composite_score``, and ``scores`` keys.

    Returns:
        A dict with:
        - ``mean_composite``: arithmetic mean of all composite scores.
        - ``dimension_averages``: per-dimension score averages (rounded to
          2 decimal places).
        - ``scenario_count``: number of scenarios evaluated.
        - ``best_scenario``: scenario name with the highest composite score.
        - ``worst_scenario``: scenario name with the lowest composite score.

        All numeric fields are 0 / empty strings when *results* is empty.
    """
    if not results:
        return {
            "mean_composite": 0.0,
            "dimension_averages": {},
            "scenario_count": 0,
            "best_scenario": "",
            "worst_scenario": "",
        }

    composites = [r["composite_score"] for r in results]
    mean_composite = sum(composites) / len(composites)

    # Per-dimension averages
    dim_totals: dict[str, float] = {}
    dim_counts: dict[str, int] = {}
    for result in results:
        for dim, data in result.get("scores", {}).items():
            score = data["score"] if isinstance(data, dict) else data
            dim_totals[dim] = dim_totals.get(dim, 0.0) + score
            dim_counts[dim] = dim_counts.get(dim, 0) + 1

    dimension_averages = {
        dim: round(dim_totals[dim] / dim_counts[dim], 2) for dim in dim_totals
    }

    best = max(results, key=lambda r: r["composite_score"])
    worst = min(results, key=lambda r: r["composite_score"])

    return {
        "mean_composite": mean_composite,
        "dimension_averages": dimension_averages,
        "scenario_count": len(results),
        "best_scenario": best["scenario"],
        "worst_scenario": worst["scenario"],
    }


# ---------------------------------------------------------------------------
# generate_markdown_report
# ---------------------------------------------------------------------------


def generate_markdown_report(
    results: list[dict],
    baseline: dict[str, float] | None = None,
) -> str:
    """Generate a full markdown evaluation report.

    Args:
        results: List of evaluation result dicts (same format as accepted by
            :func:`aggregate_scores`).
        baseline: Optional mapping of ``scenario_name -> composite_score``
            from a prior run.  When supplied, per-scenario trend indicators
            are added to the report.

    Returns:
        A multi-line markdown string.
    """
    agg = aggregate_scores(results)
    mean = agg["mean_composite"]
    band = interpret_band(mean)

    lines: list[str] = []

    # ------------------------------------------------------------------ header
    lines.append("# Infographic Evaluation Report")
    lines.append("")

    # ---------------------------------------------------------- summary section
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Scenarios evaluated**: {agg['scenario_count']}")
    lines.append(f"- **Mean composite score**: {mean:.2f} ({band})")
    if agg["best_scenario"]:
        lines.append(f"- **Best scenario**: {agg['best_scenario']}")
    if agg["worst_scenario"]:
        lines.append(f"- **Worst scenario**: {agg['worst_scenario']}")
    lines.append("")

    # -------------------------------------------------- dimension averages table
    lines.append("## Dimension Averages")
    lines.append("")
    lines.append("| Dimension | Average | Weight |")
    lines.append("|-----------|---------|--------|")
    for dim_key in _DIMENSION_WEIGHTS:
        label = _DIMENSION_LABELS.get(dim_key, dim_key)
        weight_pct = f"{int(_DIMENSION_WEIGHTS[dim_key] * 100)}%"
        avg = agg["dimension_averages"].get(dim_key, 0.0)
        lines.append(f"| {label} | {avg:.2f} | {weight_pct} |")
    lines.append("")

    # ------------------------------------------------- per-scenario results
    lines.append("## Per-Scenario Results")
    lines.append("")

    sorted_results = sorted(results, key=lambda r: r["composite_score"], reverse=True)

    for result in sorted_results:
        name = result["scenario"]
        composite = result["composite_score"]
        scenario_band = interpret_band(composite)

        # Build optional trend indicator
        trend = ""
        if baseline is not None:
            baseline_score = baseline.get(name)
            if baseline_score is not None:
                delta = composite - baseline_score
                if abs(delta) < 1e-9:
                    trend = " — unchanged vs baseline"
                elif delta > 0:
                    trend = f" — +{delta:.2f} vs baseline"
                else:
                    trend = f" — {delta:.2f} vs baseline"

        lines.append(f"### {name} — {composite:.2f} ({scenario_band}){trend}")
        lines.append("")

        # Dimension scores table
        scores = result.get("scores", {})
        lines.append("| Dimension | Score | Evidence |")
        lines.append("|-----------|-------|----------|")
        for dim_key in _DIMENSION_WEIGHTS:
            if dim_key not in scores:
                continue
            dim_data = scores[dim_key]
            label = _DIMENSION_LABELS.get(dim_key, dim_key)
            score_val = dim_data["score"] if isinstance(dim_data, dict) else dim_data
            evidence = (
                dim_data.get("evidence", "") if isinstance(dim_data, dict) else ""
            )
            lines.append(f"| {label} | {score_val} | {evidence} |")
        lines.append("")

        # Strength / Weakness (highest / lowest scoring dimension)
        dim_scores = {
            k: (v["score"] if isinstance(v, dict) else v)
            for k, v in scores.items()
            if k in _DIMENSION_WEIGHTS
        }
        if dim_scores:
            best_dim = max(dim_scores, key=lambda k: dim_scores[k])
            worst_dim = min(dim_scores, key=lambda k: dim_scores[k])
            lines.append(
                f"**Strength**: {_DIMENSION_LABELS.get(best_dim, best_dim)} "
                f"({dim_scores[best_dim]:.1f})"
            )
            lines.append(
                f"**Weakness**: {_DIMENSION_LABELS.get(worst_dim, worst_dim)} "
                f"({dim_scores[worst_dim]:.1f})"
            )
            lines.append("")

    return "\n".join(lines)
