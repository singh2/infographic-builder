"""
Tests for eval/scenarios.yaml structure and completeness.

Verifies that the scenarios file exists, is valid YAML, contains exactly
40 scenarios, that each scenario has all required fields including metadata
tags, and that the tag values are drawn from the documented allowed sets.
See eval/EVAL_PHILOSOPHY.md for the coverage framework.
"""

from __future__ import annotations

import pathlib

import pytest
import yaml

SCENARIOS_PATH = pathlib.Path("eval/scenarios.yaml")

REQUIRED_FIELDS = {
    "name", "topic", "panels", "audience", "style_direction", "prompt",
    "tier", "prompt_weight", "aesthetic",
}

VALID_TIERS = {"core", "extended"}
VALID_PROMPT_WEIGHTS = {"minimal", "natural", "specified"}
VALID_AESTHETICS = {
    "clean-minimalist", "dark-mode-tech", "bold-editorial", "sketchnote",
    "claymation", "lego", "freeform", "agent-selected", "reference-image",
    "materialistic-3d",
}
VALID_CAPABILITIES = {"diorama", "reference-image", "content-source", "live-data", "materialistic-3d"}
CURATED_AESTHETICS = {"clean-minimalist", "dark-mode-tech", "bold-editorial", "sketchnote", "claymation", "lego"}

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
    # Reference image and content source
    "amplifier-delegation-styled",
    "reference-image-multi-panel",
    "product-metrics-watercolor",
    "content-source-chart",
    # Live data
    "amplifier-repo-architecture",
    "infographic-builder-recent-changes",
    # Minimal -- one per curated aesthetic
    "minimal-claymation",
    "minimal-dark-tech",
    "minimal-editorial",
    "minimal-sketchnote",
    "minimal-lego",
    "minimal-clean",
    # New scenario
    "barista-day-claymation",
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
    # Reference image and content source
    "amplifier-delegation-styled": 1,
    "reference-image-multi-panel": 3,
    "product-metrics-watercolor": 1,
    "content-source-chart": 1,
    # Live data
    "amplifier-repo-architecture": 2,
    "infographic-builder-recent-changes": 2,
    # Minimal
    "minimal-claymation": 1,
    "minimal-dark-tech": 1,
    "minimal-editorial": 1,
    "minimal-sketchnote": 1,
    "minimal-lego": 1,
    "minimal-clean": 1,
    # New scenario
    "barista-day-claymation": 3,
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
    """There must be exactly 41 scenarios."""
    assert len(scenarios) == 41, f"Expected 41 scenarios, got {len(scenarios)}"


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
    """Scenario names must match the expected set of 40 names."""
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
    assert captured.out.strip() == "41 scenarios loaded"


# ---------------------------------------------------------------------------
# Metadata field validation (tier, prompt_weight, aesthetic, capability)
# See eval/EVAL_PHILOSOPHY.md for the allowed value sets.
# ---------------------------------------------------------------------------


def test_tier_values_are_valid(scenarios: list[dict]) -> None:
    """Every scenario's tier must be 'core' or 'extended'."""
    for scenario in scenarios:
        assert scenario["tier"] in VALID_TIERS, (
            f"Scenario {scenario['name']}: invalid tier '{scenario['tier']}'. "
            f"Must be one of {VALID_TIERS}"
        )


def test_prompt_weight_values_are_valid(scenarios: list[dict]) -> None:
    """Every scenario's prompt_weight must be 'minimal', 'natural', or 'specified'."""
    for scenario in scenarios:
        assert scenario["prompt_weight"] in VALID_PROMPT_WEIGHTS, (
            f"Scenario {scenario['name']}: invalid prompt_weight '{scenario['prompt_weight']}'. "
            f"Must be one of {VALID_PROMPT_WEIGHTS}"
        )


def test_aesthetic_values_are_valid(scenarios: list[dict]) -> None:
    """Every scenario's aesthetic must be a known value from the philosophy doc."""
    for scenario in scenarios:
        assert scenario["aesthetic"] in VALID_AESTHETICS, (
            f"Scenario {scenario['name']}: invalid aesthetic '{scenario['aesthetic']}'. "
            f"Must be one of {VALID_AESTHETICS}"
        )


def test_capability_values_are_valid(scenarios: list[dict]) -> None:
    """If a scenario has a capability list, all values must be known."""
    for scenario in scenarios:
        caps = scenario.get("capability", [])
        for cap in caps:
            assert cap in VALID_CAPABILITIES, (
                f"Scenario {scenario['name']}: invalid capability '{cap}'. "
                f"Must be one of {VALID_CAPABILITIES}"
            )


def test_minimal_covers_all_curated_aesthetics(scenarios: list[dict]) -> None:
    """Every curated aesthetic must have at least one minimal-weight scenario.

    This is the primary coverage health check from eval/EVAL_PHILOSOPHY.md.
    The minimal column is the regression canary for creative quality.
    """
    minimal_aesthetics = {
        s["aesthetic"] for s in scenarios if s.get("prompt_weight") == "minimal"
    }
    missing = CURATED_AESTHETICS - minimal_aesthetics
    assert not missing, (
        f"Curated aesthetics missing minimal coverage: {missing}. "
        f"Add a minimal scenario for each."
    )


def test_core_tier_covers_all_curated_aesthetics(scenarios: list[dict]) -> None:
    """Every curated aesthetic must appear in at least one core scenario."""
    core_aesthetics = {
        s["aesthetic"] for s in scenarios if s.get("tier") == "core"
    }
    missing = CURATED_AESTHETICS - core_aesthetics
    assert not missing, (
        f"Curated aesthetics missing core coverage: {missing}. "
        f"Add a core scenario for each."
    )
