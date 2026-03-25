"""Tests for recipes/evaluate.yaml evaluation pipeline recipe.

Validates that the recipe file exists, is valid YAML, and has the correct
structure with all 5 required steps and proper metadata.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml


RECIPE_PATH = Path("recipes/evaluate.yaml")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_recipe() -> dict:
    """Load and parse the evaluate.yaml recipe file."""
    with open(RECIPE_PATH, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


# ---------------------------------------------------------------------------
# File existence and parseability
# ---------------------------------------------------------------------------


def test_recipe_file_exists() -> None:
    """recipes/evaluate.yaml must exist."""
    assert RECIPE_PATH.exists(), f"{RECIPE_PATH} does not exist"


def test_recipe_is_valid_yaml() -> None:
    """recipes/evaluate.yaml must be valid (parseable) YAML."""
    content = RECIPE_PATH.read_text(encoding="utf-8")
    parsed = yaml.safe_load(content)
    assert isinstance(parsed, dict), "YAML root must be a mapping"


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------


def test_recipe_name() -> None:
    """Recipe name must be 'evaluate-infographic-quality'."""
    recipe = load_recipe()
    assert recipe.get("name") == "evaluate-infographic-quality"


def test_recipe_version() -> None:
    """Recipe version must be '2.0.0'."""
    recipe = load_recipe()
    assert recipe.get("version") == "2.0.0"


def test_recipe_tags() -> None:
    """Recipe tags must include evaluation, quality, rubric, batch."""
    recipe = load_recipe()
    tags = recipe.get("tags", [])
    required_tags = {"evaluation", "quality", "rubric", "batch"}
    assert required_tags.issubset(set(tags)), (
        f"Missing tags: {required_tags - set(tags)}"
    )


# ---------------------------------------------------------------------------
# Context
# ---------------------------------------------------------------------------


def test_recipe_context_scenarios_file() -> None:
    """Context must define scenarios_file pointing to eval/scenarios.yaml."""
    recipe = load_recipe()
    context = recipe.get("context", {})
    assert "scenarios_file" in context, "context.scenarios_file is missing"
    assert context["scenarios_file"] == "eval/scenarios.yaml"


# ---------------------------------------------------------------------------
# Steps — existence and count
# ---------------------------------------------------------------------------


def test_recipe_has_five_steps() -> None:
    """Recipe must have exactly 5 steps."""
    recipe = load_recipe()
    steps = recipe.get("steps", [])
    assert len(steps) == 5, f"Expected 5 steps, got {len(steps)}"


def _get_step_ids(recipe: dict) -> list[str]:
    return [step.get("id", "") for step in recipe.get("steps", [])]


def test_recipe_has_setup_step() -> None:
    """Recipe must have a 'setup' step."""
    recipe = load_recipe()
    ids = _get_step_ids(recipe)
    assert "setup" in ids, f"'setup' step missing. Found: {ids}"


def test_recipe_has_load_scenarios_step() -> None:
    """Recipe must have a 'load-scenarios' step."""
    recipe = load_recipe()
    ids = _get_step_ids(recipe)
    assert "load-scenarios" in ids, f"'load-scenarios' step missing. Found: {ids}"


def test_recipe_has_generate_infographics_step() -> None:
    """Recipe must have a 'generate-infographics' step."""
    recipe = load_recipe()
    ids = _get_step_ids(recipe)
    assert "generate-infographics" in ids, (
        f"'generate-infographics' step missing. Found: {ids}"
    )


def test_recipe_has_evaluate_scenarios_step() -> None:
    """Recipe must have an 'evaluate-scenarios' step."""
    recipe = load_recipe()
    ids = _get_step_ids(recipe)
    assert "evaluate-scenarios" in ids, (
        f"'evaluate-scenarios' step missing. Found: {ids}"
    )


def test_recipe_has_generate_report_step() -> None:
    """Recipe must have a 'generate-report' step."""
    recipe = load_recipe()
    ids = _get_step_ids(recipe)
    assert "generate-report" in ids, f"'generate-report' step missing. Found: {ids}"


# ---------------------------------------------------------------------------
# Step details — setup
# ---------------------------------------------------------------------------


def _get_step(recipe: dict, step_id: str) -> dict:
    for step in recipe.get("steps", []):
        if step.get("id") == step_id:
            return step
    pytest.fail(f"Step '{step_id}' not found in recipe")


def test_setup_step_is_bash() -> None:
    """'setup' step must be a bash step."""
    recipe = load_recipe()
    step = _get_step(recipe, "setup")
    assert step.get("type") == "bash"


def test_setup_step_has_output() -> None:
    """'setup' step must define an output (run_dir)."""
    recipe = load_recipe()
    step = _get_step(recipe, "setup")
    assert step.get("output") == "run_dir"


def test_setup_step_creates_timestamped_dir() -> None:
    """'setup' step command must create eval-results directory."""
    recipe = load_recipe()
    step = _get_step(recipe, "setup")
    command = step.get("command", "")
    assert "eval-results" in command


# ---------------------------------------------------------------------------
# Step details — load-scenarios
# ---------------------------------------------------------------------------


def test_load_scenarios_is_bash() -> None:
    """'load-scenarios' step must be a bash step."""
    recipe = load_recipe()
    step = _get_step(recipe, "load-scenarios")
    assert step.get("type") == "bash"


def test_load_scenarios_has_output() -> None:
    """'load-scenarios' step must define an output (scenarios)."""
    recipe = load_recipe()
    step = _get_step(recipe, "load-scenarios")
    assert step.get("output") == "scenarios"


def test_load_scenarios_uses_python() -> None:
    """'load-scenarios' step command must use Python to load YAML and print JSON."""
    recipe = load_recipe()
    step = _get_step(recipe, "load-scenarios")
    command = step.get("command", "")
    assert "python" in command
    assert "json" in command.lower()


# ---------------------------------------------------------------------------
# Step details — generate-infographics
# ---------------------------------------------------------------------------


def test_generate_infographics_has_foreach() -> None:
    """'generate-infographics' step must iterate over scenarios."""
    recipe = load_recipe()
    step = _get_step(recipe, "generate-infographics")
    foreach_val = step.get("foreach", "")
    assert "scenarios" in foreach_val


def test_generate_infographics_has_as_scenario() -> None:
    """'generate-infographics' step must bind iteration variable as 'scenario'."""
    recipe = load_recipe()
    step = _get_step(recipe, "generate-infographics")
    assert step.get("as") == "scenario"


def _get_sub_step(recipe: dict, parent_id: str, sub_id: str) -> dict:
    parent = _get_step(recipe, parent_id)
    for sub in parent.get("steps", []):
        if sub.get("id") == sub_id:
            return sub
    pytest.fail(f"Sub-step '{sub_id}' not found in '{parent_id}'")


def test_generate_infographics_delegates_to_agent() -> None:
    """'generate-infographics' generate sub-step must delegate to infographic-builder agent."""
    recipe = load_recipe()
    sub = _get_sub_step(recipe, "generate-infographics", "generate")
    agent = sub.get("agent", "")
    assert "infographic-builder" in agent


def test_generate_infographics_has_timeout() -> None:
    """'generate-infographics' generate sub-step must have timeout of 1800."""
    recipe = load_recipe()
    sub = _get_sub_step(recipe, "generate-infographics", "generate")
    assert sub.get("timeout") == 1800


def test_generate_infographics_on_error_continue() -> None:
    """'generate-infographics' generate sub-step must have on_error: continue."""
    recipe = load_recipe()
    sub = _get_sub_step(recipe, "generate-infographics", "generate")
    assert sub.get("on_error") == "continue"


# ---------------------------------------------------------------------------
# Step details — evaluate-scenarios
# ---------------------------------------------------------------------------


def test_evaluate_scenarios_has_foreach() -> None:
    """'evaluate-scenarios' step must iterate over scenarios."""
    recipe = load_recipe()
    step = _get_step(recipe, "evaluate-scenarios")
    foreach_val = step.get("foreach", "")
    assert "scenarios" in foreach_val


def test_evaluate_scenarios_is_bash() -> None:
    """'evaluate-scenarios' step must be a bash step."""
    recipe = load_recipe()
    step = _get_step(recipe, "evaluate-scenarios")
    assert step.get("type") == "bash"


def test_evaluate_scenarios_on_error_continue() -> None:
    """'evaluate-scenarios' step must have on_error: continue."""
    recipe = load_recipe()
    step = _get_step(recipe, "evaluate-scenarios")
    assert step.get("on_error") == "continue"


def test_evaluate_scenarios_has_timeout() -> None:
    """'evaluate-scenarios' step must have timeout of 120."""
    recipe = load_recipe()
    step = _get_step(recipe, "evaluate-scenarios")
    assert step.get("timeout") == 120


def test_evaluate_scenarios_runs_python_eval() -> None:
    """'evaluate-scenarios' step command must invoke python3 -m eval evaluate."""
    recipe = load_recipe()
    step = _get_step(recipe, "evaluate-scenarios")
    command = step.get("command", "")
    assert "python3 -m eval evaluate" in command


# ---------------------------------------------------------------------------
# Step details — generate-report
# ---------------------------------------------------------------------------


def test_generate_report_is_bash() -> None:
    """'generate-report' step must be a bash step."""
    recipe = load_recipe()
    step = _get_step(recipe, "generate-report")
    assert step.get("type") == "bash"


def test_generate_report_runs_python_eval_report() -> None:
    """'generate-report' step command must invoke python3 -m eval report."""
    recipe = load_recipe()
    step = _get_step(recipe, "generate-report")
    command = step.get("command", "")
    assert "python3 -m eval report" in command
    assert "run_dir" in command or "run-dir" in command
