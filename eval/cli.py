"""CLI entry point for the infographic evaluation harness.

Provides two subcommands:
  evaluate  — Score a single scenario against PNG images in a directory.
  report    — Aggregate *_scores.json files from a run directory into a
              markdown summary report.
"""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from typing import Any

import yaml

from eval.report import generate_markdown_report
from eval.rubric import evaluate_image


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_scenario(scenario_file: str, scenario_name: str) -> dict[str, Any]:
    """Load a single scenario by name from a scenarios YAML file.

    Args:
        scenario_file: Path to the YAML file containing a ``scenarios`` list.
        scenario_name: The ``name`` field of the scenario to load.

    Returns:
        The matching scenario dict.

    Raises:
        ValueError: If no scenario with the given name is found.
    """
    with open(scenario_file, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)

    scenarios: list[dict[str, Any]] = data.get("scenarios", [])
    for scenario in scenarios:
        if scenario.get("name") == scenario_name:
            return scenario

    raise ValueError(
        f"Scenario '{scenario_name}' not found in '{scenario_file}'. "
        f"Available: {[s.get('name') for s in scenarios]}"
    )


# ---------------------------------------------------------------------------
# Subcommand: evaluate
# ---------------------------------------------------------------------------


def cmd_evaluate(args: Any) -> None:
    """Run evaluation for a single scenario.

    Finds all PNG images in *args.image_dir* (sorted), calls
    :func:`~eval.rubric.evaluate_image`, appends ``scenario_name`` to the
    result dict, and writes JSON to *args.output* (indent=2).

    Prints ``Scored {name}: composite={score}`` on completion.
    """
    scenario = _load_scenario(args.scenario_file, args.scenario_name)

    image_dir = Path(args.image_dir)
    image_paths = sorted(str(p) for p in image_dir.glob("*.png"))

    result: dict[str, Any] = asyncio.run(evaluate_image(scenario, image_paths))
    result["scenario_name"] = args.scenario_name

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    score = result.get("composite_score", 0.0)
    print(f"Scored {args.scenario_name}: composite={score}")


# ---------------------------------------------------------------------------
# Subcommand: report
# ---------------------------------------------------------------------------


def cmd_report(args: Any) -> None:
    """Aggregate score JSON files into a markdown report.

    Loads all ``*_scores.json`` files from *args.run_dir* (sorted rglob).
    If *args.baseline_dir* is provided, loads matching score files from
    that directory to build a baseline mapping.

    Calls :func:`~eval.report.generate_markdown_report`, writes the result
    to ``run_dir/summary.md``, and prints
    ``Report written to {path} ({count} scenarios)``.
    """
    run_dir = Path(args.run_dir)
    score_files = sorted(run_dir.rglob("*_scores.json"))

    results: list[dict[str, Any]] = []
    for score_file in score_files:
        data = json.loads(score_file.read_text(encoding="utf-8"))
        # Ensure the 'scenario' key is populated (report.py uses it)
        if "scenario" not in data and "scenario_name" in data:
            data["scenario"] = data["scenario_name"]
        results.append(data)

    # Build optional baseline mapping: scenario_name -> composite_score
    baseline: dict[str, float] | None = None
    if getattr(args, "baseline_dir", None):
        baseline_dir = Path(args.baseline_dir)
        baseline = {}
        for baseline_file in sorted(baseline_dir.rglob("*_scores.json")):
            baseline_data = json.loads(baseline_file.read_text(encoding="utf-8"))
            name = baseline_data.get("scenario_name") or baseline_data.get(
                "scenario", ""
            )
            if name:
                baseline[name] = baseline_data.get("composite_score", 0.0)

    markdown = generate_markdown_report(results, baseline=baseline)

    summary_path = run_dir / "summary.md"
    summary_path.write_text(markdown, encoding="utf-8")

    count = len(results)
    print(f"Report written to {summary_path} ({count} scenarios)")


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    """Construct and return the top-level argument parser."""
    parser = argparse.ArgumentParser(
        prog="eval",
        description="Infographic evaluation harness.",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Subcommand to run.")

    # ---- evaluate subcommand -----------------------------------------------
    evaluate_parser = subparsers.add_parser(
        "evaluate",
        help="Evaluate a single scenario against PNG images.",
    )
    evaluate_parser.add_argument(
        "--scenario-file",
        required=True,
        help="Path to the scenarios YAML file.",
    )
    evaluate_parser.add_argument(
        "--scenario-name",
        required=True,
        help="Name of the scenario to evaluate.",
    )
    evaluate_parser.add_argument(
        "--image-dir",
        required=True,
        help="Directory containing PNG images to evaluate.",
    )
    evaluate_parser.add_argument(
        "--output",
        required=True,
        help="Output path for the JSON score file.",
    )
    evaluate_parser.set_defaults(func=cmd_evaluate)

    # ---- report subcommand -------------------------------------------------
    report_parser = subparsers.add_parser(
        "report",
        help="Generate a markdown report from *_scores.json files.",
    )
    report_parser.add_argument(
        "--run-dir",
        required=True,
        help="Directory containing *_scores.json files from an evaluation run.",
    )
    report_parser.add_argument(
        "--baseline-dir",
        required=False,
        default=None,
        help="Optional directory with baseline *_scores.json files for trend comparison.",
    )
    report_parser.set_defaults(func=cmd_report)

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Parse arguments and dispatch to the appropriate subcommand."""
    parser = _build_parser()
    args = parser.parse_args()

    if not hasattr(args, "func") or args.func is None:
        parser.print_help()
        return

    args.func(args)
