"""
Tests for eval/cli.py — RED phase.

Covers:
- _load_scenario: loads a scenario by name from YAML, raises on missing name
- cmd_evaluate: writes JSON output, prints scored message (mocks evaluate_image)
- cmd_report: loads *_scores.json files, writes summary.md, prints report message
- main / argparse: --help exits cleanly for top-level, evaluate, and report subcommands
- __main__: module is importable and calls main()
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest


# ---------------------------------------------------------------------------
# _load_scenario
# ---------------------------------------------------------------------------


def test_load_scenario_returns_correct_entry(tmp_path: Path) -> None:
    """_load_scenario returns the matching scenario dict from a YAML file."""
    from eval.cli import _load_scenario

    yaml_content = """
scenarios:
  - name: foo
    topic: Foo Topic
    panels: 1
    audience: Everyone
    style_direction: Clean
    prompt: Make a foo infographic.
  - name: bar
    topic: Bar Topic
    panels: 2
    audience: Developers
    style_direction: Dark
    prompt: Make a bar infographic.
"""
    scenario_file = tmp_path / "scenarios.yaml"
    scenario_file.write_text(yaml_content)

    result = _load_scenario(str(scenario_file), "bar")

    assert result["name"] == "bar"
    assert result["topic"] == "Bar Topic"


def test_load_scenario_raises_on_missing_name(tmp_path: Path) -> None:
    """_load_scenario raises ValueError when the scenario name is not found."""
    from eval.cli import _load_scenario

    yaml_content = """
scenarios:
  - name: foo
    topic: Foo Topic
    panels: 1
    audience: Everyone
    style_direction: Clean
    prompt: Make a foo infographic.
"""
    scenario_file = tmp_path / "scenarios.yaml"
    scenario_file.write_text(yaml_content)

    with pytest.raises(ValueError):
        _load_scenario(str(scenario_file), "nonexistent")


# ---------------------------------------------------------------------------
# cmd_evaluate
# ---------------------------------------------------------------------------


def test_cmd_evaluate_writes_json_output(tmp_path: Path) -> None:
    """cmd_evaluate writes a JSON file to --output with the evaluation result."""
    from eval.cli import cmd_evaluate

    # Create a fake image directory with PNG files
    image_dir = tmp_path / "images"
    image_dir.mkdir()
    (image_dir / "panel_1.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    (image_dir / "panel_2.png").write_bytes(b"\x89PNG\r\n\x1a\n")

    # Create a minimal scenarios YAML
    scenarios_yaml = tmp_path / "scenarios.yaml"
    scenarios_yaml.write_text(
        """
scenarios:
  - name: test-scenario
    topic: Test
    panels: 2
    audience: Testers
    style_direction: Minimal
    prompt: Test prompt.
"""
    )

    output_path = tmp_path / "result.json"

    fake_result = {
        "scores": {
            "content_accuracy": {"score": 4, "evidence": "Good", "improvement": "None"},
            "narrative_structure": {
                "score": 4,
                "evidence": "Good",
                "improvement": "None",
            },
            "visual_explanation": {
                "score": 4,
                "evidence": "Good",
                "improvement": "None",
            },
            "typography": {"score": 4, "evidence": "Good", "improvement": "None"},
            "visual_quality": {"score": 4, "evidence": "Good", "improvement": "None"},
        },
        "composite_score": 4.0,
        "overall_impression": "Great",
        "top_strength": "Visuals",
        "top_weakness": "None",
        "reasoning": "Overall good.",
        "prompt_fidelity": {"score": 4, "evidence": "Good", "improvement": "None"},
    }

    args = SimpleNamespace(
        scenario_file=str(scenarios_yaml),
        scenario_name="test-scenario",
        image_dir=str(image_dir),
        output=str(output_path),
    )

    with patch("eval.cli.evaluate_image", new=AsyncMock(return_value=fake_result)):
        cmd_evaluate(args)

    assert output_path.exists(), "Output JSON file should be created"
    data = json.loads(output_path.read_text())
    assert data["composite_score"] == 4.0
    assert data["scenario_name"] == "test-scenario"


def test_cmd_evaluate_adds_scenario_name_to_result(tmp_path: Path) -> None:
    """cmd_evaluate adds scenario_name key to the JSON result."""
    from eval.cli import cmd_evaluate

    image_dir = tmp_path / "images"
    image_dir.mkdir()
    (image_dir / "panel.png").write_bytes(b"\x89PNG\r\n\x1a\n")

    scenarios_yaml = tmp_path / "scenarios.yaml"
    scenarios_yaml.write_text(
        """
scenarios:
  - name: my-scenario
    topic: Test
    panels: 1
    audience: Testers
    style_direction: Minimal
    prompt: Test prompt.
"""
    )

    output_path = tmp_path / "result.json"

    fake_result = {
        "scores": {},
        "composite_score": 3.5,
        "overall_impression": "OK",
        "top_strength": "X",
        "top_weakness": "Y",
        "reasoning": "Fine.",
        "prompt_fidelity": None,
    }

    args = SimpleNamespace(
        scenario_file=str(scenarios_yaml),
        scenario_name="my-scenario",
        image_dir=str(image_dir),
        output=str(output_path),
    )

    with patch("eval.cli.evaluate_image", new=AsyncMock(return_value=fake_result)):
        cmd_evaluate(args)

    data = json.loads(output_path.read_text())
    assert data["scenario_name"] == "my-scenario"


def test_cmd_evaluate_prints_scored_message(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    """cmd_evaluate prints 'Scored {name}: composite={score}' to stdout."""
    from eval.cli import cmd_evaluate

    image_dir = tmp_path / "images"
    image_dir.mkdir()
    (image_dir / "panel.png").write_bytes(b"\x89PNG\r\n\x1a\n")

    scenarios_yaml = tmp_path / "scenarios.yaml"
    scenarios_yaml.write_text(
        """
scenarios:
  - name: dns
    topic: How DNS Works
    panels: 1
    audience: Developers
    style_direction: Minimal
    prompt: DNS prompt.
"""
    )

    output_path = tmp_path / "result.json"
    fake_result = {
        "scores": {},
        "composite_score": 3.75,
        "overall_impression": "Good",
        "top_strength": "X",
        "top_weakness": "Y",
        "reasoning": "Fine.",
        "prompt_fidelity": None,
    }

    args = SimpleNamespace(
        scenario_file=str(scenarios_yaml),
        scenario_name="dns",
        image_dir=str(image_dir),
        output=str(output_path),
    )

    with patch("eval.cli.evaluate_image", new=AsyncMock(return_value=fake_result)):
        cmd_evaluate(args)

    captured = capsys.readouterr()
    assert "Scored dns" in captured.out
    assert "composite=" in captured.out


def test_cmd_evaluate_uses_sorted_png_glob(tmp_path: Path) -> None:
    """cmd_evaluate passes sorted PNG image paths to evaluate_image."""
    from eval.cli import cmd_evaluate

    image_dir = tmp_path / "images"
    image_dir.mkdir()
    (image_dir / "panel_3.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    (image_dir / "panel_1.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    (image_dir / "panel_2.png").write_bytes(b"\x89PNG\r\n\x1a\n")

    scenarios_yaml = tmp_path / "scenarios.yaml"
    scenarios_yaml.write_text(
        """
scenarios:
  - name: test-scenario
    topic: Test
    panels: 3
    audience: All
    style_direction: Bold
    prompt: Test prompt.
"""
    )

    output_path = tmp_path / "result.json"
    fake_result = {
        "scores": {},
        "composite_score": 3.0,
        "overall_impression": "OK",
        "top_strength": "X",
        "top_weakness": "Y",
        "reasoning": "Fine.",
        "prompt_fidelity": None,
    }

    captured_paths: list[list[str]] = []

    async def fake_evaluate(scenario, image_paths):
        captured_paths.append(image_paths)
        return fake_result

    args = SimpleNamespace(
        scenario_file=str(scenarios_yaml),
        scenario_name="test-scenario",
        image_dir=str(image_dir),
        output=str(output_path),
    )

    with patch("eval.cli.evaluate_image", new=fake_evaluate):
        cmd_evaluate(args)

    assert len(captured_paths) == 1
    paths = captured_paths[0]
    assert len(paths) == 3
    # Should be sorted
    assert paths == sorted(paths)


# ---------------------------------------------------------------------------
# cmd_report
# ---------------------------------------------------------------------------


def test_cmd_report_writes_summary_md(tmp_path: Path) -> None:
    """cmd_report writes summary.md to run_dir."""
    from eval.cli import cmd_report

    run_dir = tmp_path / "run"
    run_dir.mkdir()

    # Write two fake *_scores.json files
    scores1 = {
        "scenario_name": "dns",
        "scenario": "dns",
        "composite_score": 3.75,
        "scores": {
            "content_accuracy": {"score": 4, "evidence": "Good", "improvement": "None"},
            "narrative_structure": {
                "score": 4,
                "evidence": "Good",
                "improvement": "None",
            },
            "visual_explanation": {
                "score": 4,
                "evidence": "Good",
                "improvement": "None",
            },
            "typography": {"score": 3, "evidence": "OK", "improvement": "Improve"},
            "visual_quality": {"score": 4, "evidence": "Good", "improvement": "None"},
        },
    }
    scores2 = {
        "scenario_name": "campfire",
        "scenario": "campfire",
        "composite_score": 3.0,
        "scores": {
            "content_accuracy": {"score": 3, "evidence": "OK", "improvement": "More"},
            "narrative_structure": {
                "score": 3,
                "evidence": "OK",
                "improvement": "More",
            },
            "visual_explanation": {"score": 3, "evidence": "OK", "improvement": "More"},
            "typography": {"score": 3, "evidence": "OK", "improvement": "More"},
            "visual_quality": {"score": 3, "evidence": "OK", "improvement": "More"},
        },
    }

    (run_dir / "dns_scores.json").write_text(json.dumps(scores1))
    (run_dir / "campfire_scores.json").write_text(json.dumps(scores2))

    args = SimpleNamespace(run_dir=str(run_dir), baseline_dir=None)
    cmd_report(args)

    summary_path = run_dir / "summary.md"
    assert summary_path.exists(), "summary.md should be written to run_dir"


def test_cmd_report_prints_report_written_message(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    """cmd_report prints 'Report written to {path} ({count} scenarios)'."""
    from eval.cli import cmd_report

    run_dir = tmp_path / "run"
    run_dir.mkdir()

    scores = {
        "scenario_name": "dns",
        "scenario": "dns",
        "composite_score": 3.75,
        "scores": {
            "content_accuracy": {"score": 4, "evidence": "Good", "improvement": "None"},
            "narrative_structure": {
                "score": 4,
                "evidence": "Good",
                "improvement": "None",
            },
            "visual_explanation": {
                "score": 4,
                "evidence": "Good",
                "improvement": "None",
            },
            "typography": {"score": 3, "evidence": "OK", "improvement": "Improve"},
            "visual_quality": {"score": 4, "evidence": "Good", "improvement": "None"},
        },
    }
    (run_dir / "dns_scores.json").write_text(json.dumps(scores))

    args = SimpleNamespace(run_dir=str(run_dir), baseline_dir=None)
    cmd_report(args)

    captured = capsys.readouterr()
    assert "Report written to" in captured.out
    assert "1 scenarios" in captured.out


def test_cmd_report_loads_baseline_when_provided(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    """cmd_report loads baseline *_scores.json from --baseline-dir when provided."""
    from eval.cli import cmd_report

    run_dir = tmp_path / "run"
    run_dir.mkdir()
    baseline_dir = tmp_path / "baseline"
    baseline_dir.mkdir()

    score_data = {
        "scenario_name": "dns",
        "scenario": "dns",
        "composite_score": 4.0,
        "scores": {
            "content_accuracy": {"score": 4, "evidence": "Good", "improvement": "None"},
            "narrative_structure": {
                "score": 4,
                "evidence": "Good",
                "improvement": "None",
            },
            "visual_explanation": {
                "score": 4,
                "evidence": "Good",
                "improvement": "None",
            },
            "typography": {"score": 4, "evidence": "OK", "improvement": "None"},
            "visual_quality": {"score": 4, "evidence": "Good", "improvement": "None"},
        },
    }
    baseline_data = {
        "scenario_name": "dns",
        "scenario": "dns",
        "composite_score": 3.0,
        "scores": score_data["scores"],
    }

    (run_dir / "dns_scores.json").write_text(json.dumps(score_data))
    (baseline_dir / "dns_scores.json").write_text(json.dumps(baseline_data))

    with patch("eval.cli.generate_markdown_report") as mock_report:
        mock_report.return_value = "# Report"
        args = SimpleNamespace(run_dir=str(run_dir), baseline_dir=str(baseline_dir))
        cmd_report(args)

    # generate_markdown_report should have been called with a baseline dict
    mock_report.assert_called_once()
    call_kwargs = mock_report.call_args
    # baseline should not be None when baseline_dir is provided
    baseline_arg = (
        call_kwargs[1].get("baseline") if call_kwargs[1] else call_kwargs[0][1]
    )
    assert baseline_arg is not None


def test_cmd_report_no_baseline_when_not_provided(tmp_path: Path) -> None:
    """cmd_report passes baseline=None to generate_markdown_report when --baseline-dir is absent."""
    from eval.cli import cmd_report

    run_dir = tmp_path / "run"
    run_dir.mkdir()

    score_data = {
        "scenario_name": "dns",
        "scenario": "dns",
        "composite_score": 3.75,
        "scores": {
            "content_accuracy": {"score": 4, "evidence": "Good", "improvement": "None"},
            "narrative_structure": {
                "score": 4,
                "evidence": "Good",
                "improvement": "None",
            },
            "visual_explanation": {
                "score": 4,
                "evidence": "Good",
                "improvement": "None",
            },
            "typography": {"score": 3, "evidence": "OK", "improvement": "Improve"},
            "visual_quality": {"score": 4, "evidence": "Good", "improvement": "None"},
        },
    }
    (run_dir / "dns_scores.json").write_text(json.dumps(score_data))

    with patch("eval.cli.generate_markdown_report") as mock_report:
        mock_report.return_value = "# Report"
        args = SimpleNamespace(run_dir=str(run_dir), baseline_dir=None)
        cmd_report(args)

    call_kwargs = mock_report.call_args
    baseline_arg = call_kwargs[1].get("baseline") if call_kwargs[1] else None
    assert baseline_arg is None


# ---------------------------------------------------------------------------
# main / argparse / --help
# ---------------------------------------------------------------------------


def test_main_evaluate_help_exits_cleanly() -> None:
    """python -m eval evaluate --help exits with code 0."""
    result = subprocess.run(
        [sys.executable, "-m", "eval", "evaluate", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Expected exit code 0, got {result.returncode}\n{result.stderr}"
    )
    assert "evaluate" in result.stdout.lower() or "usage" in result.stdout.lower()


def test_main_report_help_exits_cleanly() -> None:
    """python -m eval report --help exits with code 0."""
    result = subprocess.run(
        [sys.executable, "-m", "eval", "report", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Expected exit code 0, got {result.returncode}\n{result.stderr}"
    )
    assert "report" in result.stdout.lower() or "usage" in result.stdout.lower()


def test_main_top_level_help_exits_cleanly() -> None:
    """python -m eval --help exits with code 0."""
    result = subprocess.run(
        [sys.executable, "-m", "eval", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Expected exit code 0, got {result.returncode}\n{result.stderr}"
    )
    assert "usage" in result.stdout.lower()


def test_main_evaluate_help_shows_required_args() -> None:
    """evaluate --help shows --scenario-file, --scenario-name, --image-dir, --output."""
    result = subprocess.run(
        [sys.executable, "-m", "eval", "evaluate", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    for arg in ["--scenario-file", "--scenario-name", "--image-dir", "--output"]:
        assert arg in result.stdout, f"'{arg}' not found in evaluate --help output"


def test_main_report_help_shows_required_args() -> None:
    """report --help shows --run-dir and --baseline-dir."""
    result = subprocess.run(
        [sys.executable, "-m", "eval", "report", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "--run-dir" in result.stdout, "'--run-dir' not found in report --help output"
    assert "--baseline-dir" in result.stdout, (
        "'--baseline-dir' not found in report --help output"
    )


# ---------------------------------------------------------------------------
# __main__ module
# ---------------------------------------------------------------------------


def test_main_module_is_importable() -> None:
    """eval.__main__ is importable without error."""
    import importlib

    mod = importlib.import_module("eval.__main__")
    assert mod is not None


def test_main_function_exists_in_cli() -> None:
    """eval.cli.main is callable."""
    from eval.cli import main

    assert callable(main)
