"""
Tests for eval/rubric.py — RED phase.

All tests in this file will fail with ModuleNotFoundError until eval/rubric.py
is implemented (task-6).

Covers:
- parse_scores happy path
- composite score recalculation (weighted average)
- error handling (invalid JSON, missing dimensions, out-of-range scores)
- DIMENSION_WEIGHTS constant validation
- build_rubric_prompt structure
"""

from __future__ import annotations

import json
import copy

import pytest

from eval.rubric import DIMENSION_WEIGHTS, build_rubric_prompt, parse_scores

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

# A valid raw LLM response dict with all required rubric fields.
# composite_score is intentionally set to 8.0 so recalculation tests can
# verify that parse_scores overwrites it with the weighted average.
#
# Weighted composite:
#   content_accuracy   8 × 0.20 = 1.60
#   narrative_structure 6 × 0.15 = 0.90
#   visual_explanation  9 × 0.25 = 2.25
#   typography          7 × 0.20 = 1.40
#   visual_quality      8 × 0.20 = 1.60
#   ─────────────────────────────────────
#   computed composite               7.75
VALID_RESPONSE: dict = {
    "dimensions": {
        "content_accuracy": {
            "score": 8,
            "evidence": "Data is accurate and well-sourced throughout.",
            "improvement": "Minor footnote clarification would help.",
        },
        "narrative_structure": {
            "score": 6,
            "evidence": "Logical flow exists but transitions could be stronger.",
            "improvement": "Strengthen the introductory framing.",
        },
        "visual_explanation": {
            "score": 9,
            "evidence": "Excellent use of visual metaphors and diagrams.",
            "improvement": "None significant.",
        },
        "typography": {
            "score": 7,
            "evidence": "Consistent font hierarchy maintained.",
            "improvement": "Body text could be slightly larger for readability.",
        },
        "visual_quality": {
            "score": 8,
            "evidence": "Good colour usage and overall composition.",
            "improvement": "Some icons lack polish.",
        },
    },
    "prompt_fidelity": {
        "score": 8,
        "evidence": "Follows the original prompt closely.",
        "improvement": "One minor element from the brief is missing.",
    },
    "composite_score": 8.0,  # intentionally wrong — recalculated by parse_scores
    "summary": "A well-crafted infographic with strong visual explanation.",
    "strengths": ["Clear data visualisation", "Consistent typography"],
    "weaknesses": ["Minor icon inconsistency"],
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _as_json_string(data: dict) -> str:
    """Serialise *data* to a compact JSON string."""
    return json.dumps(data)


# ---------------------------------------------------------------------------
# parse_scores — happy path
# ---------------------------------------------------------------------------


def test_parse_scores_returns_all_dimension_scores() -> None:
    """parse_scores returns a mapping that contains all five dimension keys."""
    result = parse_scores(_as_json_string(VALID_RESPONSE))
    dimensions = result["dimensions"]
    expected_keys = {
        "content_accuracy",
        "narrative_structure",
        "visual_explanation",
        "typography",
        "visual_quality",
    }
    assert expected_keys.issubset(dimensions.keys()), (
        f"Missing dimension keys: {expected_keys - set(dimensions.keys())}"
    )


def test_parse_scores_includes_evidence_and_improvement() -> None:
    """Each dimension entry in the result has 'evidence' and 'improvement' fields."""
    result = parse_scores(_as_json_string(VALID_RESPONSE))
    for dim_name, dim_data in result["dimensions"].items():
        assert "evidence" in dim_data, (
            f"Dimension '{dim_name}' is missing 'evidence' field"
        )
        assert "improvement" in dim_data, (
            f"Dimension '{dim_name}' is missing 'improvement' field"
        )


def test_parse_scores_includes_composite() -> None:
    """parse_scores result contains a 'composite_score' key."""
    result = parse_scores(_as_json_string(VALID_RESPONSE))
    assert "composite_score" in result, "Result is missing 'composite_score' key"


def test_parse_scores_includes_prompt_fidelity() -> None:
    """parse_scores result contains a 'prompt_fidelity' key."""
    result = parse_scores(_as_json_string(VALID_RESPONSE))
    assert "prompt_fidelity" in result, "Result is missing 'prompt_fidelity' key"


def test_parse_scores_includes_summary_fields() -> None:
    """parse_scores result contains 'summary', 'strengths', and 'weaknesses'."""
    result = parse_scores(_as_json_string(VALID_RESPONSE))
    for field in ("summary", "strengths", "weaknesses"):
        assert field in result, f"Result is missing '{field}' field"


# ---------------------------------------------------------------------------
# parse_scores — composite recalculation
# ---------------------------------------------------------------------------


def test_parse_scores_recalculates_composite() -> None:
    """parse_scores overwrites composite_score with the correct weighted average.

    Expected: 8*0.20 + 6*0.15 + 9*0.25 + 7*0.20 + 8*0.20 = 7.75
    The fixture supplies 8.0 so this directly tests recalculation logic.
    """
    result = parse_scores(_as_json_string(VALID_RESPONSE))
    expected = (
        8 * 0.20  # content_accuracy
        + 6 * 0.15  # narrative_structure
        + 9 * 0.25  # visual_explanation
        + 7 * 0.20  # typography
        + 8 * 0.20  # visual_quality
    )
    assert abs(result["composite_score"] - expected) < 1e-9, (
        f"Expected composite_score {expected}, got {result['composite_score']}"
    )


# ---------------------------------------------------------------------------
# parse_scores — error handling
# ---------------------------------------------------------------------------


def test_parse_scores_rejects_invalid_json() -> None:
    """parse_scores raises ValueError containing 'Invalid JSON' for malformed input."""
    with pytest.raises(ValueError, match="Invalid JSON"):
        parse_scores("{not valid json")


def test_parse_scores_rejects_missing_dimensions() -> None:
    """parse_scores raises ValueError matching 'Missing.*dimension' when a
    required dimension key is absent from the response."""
    incomplete = {
        "dimensions": {
            # 'content_accuracy' deliberately omitted
            "narrative_structure": {
                "score": 7,
                "evidence": "ok",
                "improvement": "none",
            },
            "visual_explanation": {"score": 7, "evidence": "ok", "improvement": "none"},
            "typography": {"score": 7, "evidence": "ok", "improvement": "none"},
            "visual_quality": {"score": 7, "evidence": "ok", "improvement": "none"},
        },
        "prompt_fidelity": {"score": 7, "evidence": "ok", "improvement": "none"},
        "composite_score": 7.0,
        "summary": "ok",
        "strengths": [],
        "weaknesses": [],
    }
    with pytest.raises(ValueError, match=r"Missing.*dimension"):
        parse_scores(_as_json_string(incomplete))


def test_parse_scores_rejects_out_of_range_score() -> None:
    """parse_scores raises ValueError containing 'out of range' when a dimension
    score is outside the valid 1–10 band."""
    out_of_range = copy.deepcopy(VALID_RESPONSE)
    out_of_range["dimensions"]["content_accuracy"]["score"] = 11  # invalid
    with pytest.raises(ValueError, match="out of range"):
        parse_scores(_as_json_string(out_of_range))


# ---------------------------------------------------------------------------
# DIMENSION_WEIGHTS validation
# ---------------------------------------------------------------------------


def test_dimension_weights_sum_to_one() -> None:
    """DIMENSION_WEIGHTS values must sum to exactly 1.0."""
    total = sum(DIMENSION_WEIGHTS.values())
    assert abs(total - 1.0) < 1e-9, f"DIMENSION_WEIGHTS sum to {total}, expected 1.0"


def test_dimension_weights_match_design() -> None:
    """DIMENSION_WEIGHTS must contain the five specified dimensions with the
    correct individual weights from the design spec."""
    expected = {
        "content_accuracy": 0.20,
        "narrative_structure": 0.15,
        "visual_explanation": 0.25,
        "typography": 0.20,
        "visual_quality": 0.20,
    }
    assert set(DIMENSION_WEIGHTS.keys()) == set(expected.keys()), (
        f"Unexpected keys: {set(DIMENSION_WEIGHTS.keys()) ^ set(expected.keys())}"
    )
    for dim, weight in expected.items():
        assert abs(DIMENSION_WEIGHTS[dim] - weight) < 1e-9, (
            f"DIMENSION_WEIGHTS['{dim}'] = {DIMENSION_WEIGHTS[dim]}, expected {weight}"
        )


# ---------------------------------------------------------------------------
# build_rubric_prompt — structure
# ---------------------------------------------------------------------------

# A minimal scenario dict for prompt-building tests.
_SCENARIO = {
    "name": "test-scenario",
    "topic": "How neural networks learn",
    "audience": "Software engineers",
    "style_direction": "Technical, minimal",
    "prompt": "Create an infographic explaining backpropagation step by step.",
}


def test_build_rubric_prompt_contains_all_dimensions() -> None:
    """build_rubric_prompt output mentions all five scoring dimensions by name."""
    prompt = build_rubric_prompt(_SCENARIO, panel_count=1)
    for label in (
        "Content Accuracy",
        "Narrative Structure",
        "Visual Explanation",
        "Typography",
        "Visual Quality",
    ):
        assert label in prompt, f"Expected dimension label '{label}' in rubric prompt"


def test_build_rubric_prompt_contains_scenario_context() -> None:
    """build_rubric_prompt embeds the scenario topic and/or prompt in the output."""
    prompt = build_rubric_prompt(_SCENARIO, panel_count=1)
    # At least one identifying piece of the scenario should appear.
    assert _SCENARIO["topic"] in prompt or _SCENARIO["prompt"] in prompt, (
        "Rubric prompt does not include scenario context (topic or prompt)"
    )


def test_build_rubric_prompt_contains_json_instruction() -> None:
    """build_rubric_prompt output instructs the model to respond in JSON."""
    prompt = build_rubric_prompt(_SCENARIO, panel_count=1)
    assert "json" in prompt.lower() or "JSON" in prompt, (
        "Rubric prompt must contain a JSON response instruction"
    )


def test_build_rubric_prompt_contains_chain_of_thought_instruction() -> None:
    """build_rubric_prompt output includes a chain-of-thought instruction
    (e.g. 'think step by step', 'reasoning', 'chain of thought', etc.)."""
    prompt = build_rubric_prompt(_SCENARIO, panel_count=1)
    cot_patterns = [
        "step by step",
        "reasoning",
        "chain of thought",
        "think through",
        "before scoring",
    ]
    lowered = prompt.lower()
    assert any(pattern in lowered for pattern in cot_patterns), (
        "Rubric prompt must include a chain-of-thought instruction. "
        f"Checked patterns: {cot_patterns}"
    )


def test_build_rubric_prompt_includes_multi_panel_instruction() -> None:
    """For panel_count > 1, build_rubric_prompt includes multi-panel evaluation
    guidance containing 'Multi-Panel Evaluation' and 'cross-panel'."""
    prompt = build_rubric_prompt(_SCENARIO, panel_count=3)
    assert "Multi-Panel Evaluation" in prompt, (
        "Expected 'Multi-Panel Evaluation' in prompt for panel_count=3"
    )
    assert "cross-panel" in prompt, "Expected 'cross-panel' in prompt for panel_count=3"


def test_build_rubric_prompt_excludes_multi_panel_instruction_for_single_panel() -> (
    None
):
    """For panel_count=1, build_rubric_prompt must NOT include multi-panel
    evaluation guidance."""
    prompt = build_rubric_prompt(_SCENARIO, panel_count=1)
    assert "Multi-Panel Evaluation" not in prompt, (
        "Multi-panel guidance must not appear in single-panel rubric prompts"
    )
    assert "cross-panel" not in prompt, (
        "'cross-panel' must not appear in single-panel rubric prompts"
    )
