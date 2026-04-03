"""
Tests for eval/scenarios.yaml structure and completeness.

Verifies that the scenarios file exists, is valid YAML, contains exactly
32 scenarios, and that each scenario has all required fields.
"""

from __future__ import annotations

import pathlib

import pytest
import yaml

SCENARIOS_PATH = pathlib.Path("eval/scenarios.yaml")

REQUIRED_FIELDS = {"name", "topic", "panels", "audience", "style_direction", "prompt"}

EXPECTED_NAMES = {
    # Specified -- full visual spec
    "mechanical-keyboard",
    "noise-canceling-headphones",
    "saas-metrics-dashboard",
    "developer-survey-results",
    "neural-networks",
    "cicd-pipeline",
    "llm-pipeline",
    "song-to-spotify",
    "ai-everyday-life",
    "coffee-bean",
    "history-of-internet",
    # Natural -- conversational, agent decides layout/aesthetic
    "dns",
    "campfire",
    "agile-vs-waterfall",
    "okr-cascade",
    "customer-discovery-funnel",
    "photosynthesis",
    # Aesthetic -- named curated aesthetic
    "surfing",
    "incubation-lifecycle",
    "devops-lifecycle",
    "sleep-stages",
    "solar-system",
    "eisenhower-matrix",
    # README showcase
    "engineering-onboarding",
    "espresso-brewing-diorama",
    "star-wars-ranking",
    # Materialistic 3D
    "kubernetes-architecture-3d",
    "data-pipeline-materialistic-3d",
    # Reference image
    "amplifier-delegation-styled",
    "product-metrics-watercolor",
    # Live data
    "amplifier-repo-architecture",
    "infographic-builder-recent-changes",
}

EXPECTED_PANEL_COUNTS = {
    # Specified
    "mechanical-keyboard": 1,
    "noise-canceling-headphones": 1,
    "saas-metrics-dashboard": 1,
    "developer-survey-results": 2,
    "neural-networks": 3,
    "cicd-pipeline": 3,
    "llm-pipeline": 4,
    "song-to-spotify": 4,
    "ai-everyday-life": 5,
    "coffee-bean": 5,
    "history-of-internet": 6,
    # Natural
    "dns": 2,
    "campfire": 2,
    "agile-vs-waterfall": 2,
    "okr-cascade": 2,
    "customer-discovery-funnel": 2,
    "photosynthesis": 2,
    # Aesthetic
    "surfing": 3,
    "incubation-lifecycle": 3,
    "devops-lifecycle": 1,
    "sleep-stages": 2,
    "solar-system": 3,
    "eisenhower-matrix": 1,
    # README showcase
    "engineering-onboarding": 3,
    "espresso-brewing-diorama": 1,
    "star-wars-ranking": 2,
    # Materialistic 3D
    "kubernetes-architecture-3d": 1,
    "data-pipeline-materialistic-3d": 1,
    # Reference image
    "amplifier-delegation-styled": 1,
    "product-metrics-watercolor": 1,
    # Live data
    "amplifier-repo-architecture": 2,
    "infographic-builder-recent-changes": 2,
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
    """There must be exactly 32 scenarios."""
    assert len(scenarios) == 32, f"Expected 32 scenarios, got {len(scenarios)}"


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
    """Scenario names must match the expected set of 32 names."""
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
    assert captured.out.strip() == "32 scenarios loaded"
