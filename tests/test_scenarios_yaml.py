"""
Tests for eval/scenarios.yaml structure and completeness.

Verifies that the scenarios file exists, is valid YAML, contains exactly
18 scenarios, and that each scenario has all required fields.
"""

from __future__ import annotations

import pathlib

import pytest
import yaml

SCENARIOS_PATH = pathlib.Path("eval/scenarios.yaml")

REQUIRED_FIELDS = {"name", "topic", "panels", "audience", "style_direction", "prompt"}

EXPECTED_NAMES = {
    # 1-panel
    "mechanical-keyboard",
    "noise-canceling-headphones",
    "saas-metrics-dashboard",
    # 2-panel
    "developer-survey-results",
    "dns",
    "campfire",
    "agile-vs-waterfall",
    "okr-cascade",
    "customer-discovery-funnel",
    # 3-panel
    "neural-networks",
    "surfing",
    "incubation-lifecycle",
    "cicd-pipeline",
    # 4-panel
    "llm-pipeline",
    "song-to-spotify",
    # 5-panel
    "ai-everyday-life",
    "coffee-bean",
    # 6-panel
    "history-of-internet",
}

EXPECTED_PANEL_COUNTS = {
    "mechanical-keyboard": 1,
    "noise-canceling-headphones": 1,
    "saas-metrics-dashboard": 1,
    "developer-survey-results": 2,
    "dns": 2,
    "campfire": 2,
    "agile-vs-waterfall": 2,
    "okr-cascade": 2,
    "customer-discovery-funnel": 2,
    "neural-networks": 3,
    "surfing": 3,
    "incubation-lifecycle": 3,
    "cicd-pipeline": 3,
    "llm-pipeline": 4,
    "song-to-spotify": 4,
    "ai-everyday-life": 5,
    "coffee-bean": 5,
    "history-of-internet": 6,
}


@pytest.fixture(scope="module")
def scenarios() -> list[dict]:
    """Load scenarios from eval/scenarios.yaml."""
    assert SCENARIOS_PATH.exists(), f"{SCENARIOS_PATH} does not exist"
    with SCENARIOS_PATH.open() as fh:
        data = yaml.safe_load(fh)
    assert isinstance(data, dict), "scenarios.yaml top-level must be a mapping"
    assert "scenarios" in data, "scenarios.yaml must have a 'scenarios' key"
    return data["scenarios"]


def test_scenarios_file_exists() -> None:
    """eval/scenarios.yaml must exist."""
    assert SCENARIOS_PATH.exists(), f"{SCENARIOS_PATH} does not exist"


def test_scenarios_is_valid_yaml() -> None:
    """eval/scenarios.yaml must be parseable YAML."""
    with SCENARIOS_PATH.open() as fh:
        data = yaml.safe_load(fh)
    assert data is not None


def test_scenarios_count(scenarios: list[dict]) -> None:
    """There must be exactly 18 scenarios."""
    assert len(scenarios) == 18, f"Expected 18 scenarios, got {len(scenarios)}"


def test_each_scenario_has_required_fields(scenarios: list[dict]) -> None:
    """Every scenario must have name, topic, panels, audience, style_direction, and prompt."""
    for scenario in scenarios:
        missing = REQUIRED_FIELDS - set(scenario.keys())
        assert not missing, (
            f"Scenario {scenario.get('name', '<unknown>')} is missing fields: {missing}"
        )


def test_scenario_names_are_unique(scenarios: list[dict]) -> None:
    """Every scenario name must be unique."""
    names = [s["name"] for s in scenarios]
    assert len(names) == len(set(names)), "Duplicate scenario names found"


def test_scenario_names_match_expected(scenarios: list[dict]) -> None:
    """Scenario names must match the expected set of 18 names."""
    names = {s["name"] for s in scenarios}
    assert names == EXPECTED_NAMES, (
        f"Unexpected names: {names - EXPECTED_NAMES}, "
        f"missing names: {EXPECTED_NAMES - names}"
    )


def test_panel_counts_are_integers(scenarios: list[dict]) -> None:
    """panels field must be an integer for every scenario."""
    for scenario in scenarios:
        assert isinstance(scenario["panels"], int), (
            f"Scenario {scenario['name']}: panels must be int, got {type(scenario['panels'])}"
        )


def test_panel_counts_match_expected(scenarios: list[dict]) -> None:
    """Each scenario must have the correct panel count."""
    for scenario in scenarios:
        name = scenario["name"]
        expected = EXPECTED_PANEL_COUNTS[name]
        assert scenario["panels"] == expected, (
            f"Scenario {name}: expected panels={expected}, got {scenario['panels']}"
        )


def test_all_text_fields_are_non_empty(scenarios: list[dict]) -> None:
    """topic, audience, style_direction, and prompt must be non-empty strings."""
    text_fields = ["topic", "audience", "style_direction", "prompt"]
    for scenario in scenarios:
        for field in text_fields:
            value = scenario[field]
            assert isinstance(value, str) and value.strip(), (
                f"Scenario {scenario['name']}: field '{field}' must be a non-empty string"
            )


def test_python_c_verification_output(capsys) -> None:
    """Simulate the python -c verification from the acceptance criteria."""
    with SCENARIOS_PATH.open() as fh:
        data = yaml.safe_load(fh)
    scenarios = data["scenarios"]
    print(f"{len(scenarios)} scenarios loaded")
    captured = capsys.readouterr()
    assert captured.out.strip() == "18 scenarios loaded"
