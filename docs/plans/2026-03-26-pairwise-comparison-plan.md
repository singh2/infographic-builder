# Pairwise Model Comparison Implementation Plan

> **Execution:** Use the subagent-driven-development workflow to implement this plan.

**Goal:** Add a `compare` CLI subcommand that takes two evaluation run directories, sends images from both to GPT-5.4 as a pairwise judge, and produces a markdown report showing which model is better per-dimension and overall.

**Architecture:** A new `eval/compare.py` module with four public functions (prompt builder, JSON parser, async API caller, report renderer) plus a `compare` subcommand added to `eval/cli.py`. Follows the same patterns as the existing `eval/rubric.py` and `eval/report.py` modules — pure functions for prompt building and report rendering, async for the API call, mocked OpenAI in tests.

**Tech Stack:** Python 3.11+, OpenAI SDK (AsyncOpenAI, GPT-5.4), pytest, argparse, PyYAML

**Design Document:** `docs/plans/2026-03-26-pairwise-comparison-design.md`

---

## Important Context for Implementer

### Dimension Name Differences

The **existing** `eval/rubric.py` uses dimension keys `typography` and `visual_quality`. The **new** pairwise comparison module uses different keys: `typography_legibility` and `visual_quality_consistency`. This is intentional — the comparison is a separate evaluation concern with its own dimension set. Do not reuse the constants from `rubric.py`.

### Pairwise Dimension Keys

- Single-panel (5): `content_accuracy`, `narrative_structure`, `visual_explanation`, `typography_legibility`, `visual_quality_consistency`
- Multi-panel (6): same 5 + `cross_panel_consistency`

### Private Import

`eval/compare.py` imports `_encode_image` from `eval/rubric.py`. This is a private function (underscore prefix) but both modules are in the same package, so this is acceptable. The import is: `from eval.rubric import _encode_image`.

---

## Task 1: `build_pairwise_prompt()` + Constants

**Files:**
- Create: `eval/compare.py`
- Create: `tests/test_compare.py`

### Step 1: Write the failing tests

Create `tests/test_compare.py` with the initial test suite for the prompt builder:

```python
"""Tests for eval/compare.py — pairwise model comparison."""

from __future__ import annotations

import json

import pytest

from eval.compare import (
    DIMENSION_LABELS,
    MULTI_PANEL_PAIRWISE_DIMENSIONS,
    PAIRWISE_DIMENSIONS,
    build_pairwise_prompt,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_MULTI_PANEL_SCENARIO: dict = {
    "name": "dns",
    "topic": "How DNS Works",
    "audience": "Developers",
    "panels": 2,
    "style_direction": "Technical, minimal",
    "prompt": "Create an infographic about DNS resolution.",
}

_SINGLE_PANEL_SCENARIO: dict = {
    "name": "mechanical-keyboard",
    "topic": "The Anatomy of a Mechanical Keyboard",
    "audience": "Tech enthusiasts",
    "panels": 1,
    "style_direction": "Dark with RGB accents",
    "prompt": "Create a single-panel infographic about mechanical keyboards.",
}


# ---------------------------------------------------------------------------
# build_pairwise_prompt — scenario context
# ---------------------------------------------------------------------------


def test_build_pairwise_prompt_contains_scenario_context() -> None:
    """build_pairwise_prompt includes topic and audience from the scenario."""
    prompt = build_pairwise_prompt(
        _MULTI_PANEL_SCENARIO,
        ["a1.png", "a2.png"],
        ["b1.png", "b2.png"],
        "Model A",
        "Model B",
    )
    assert _MULTI_PANEL_SCENARIO["topic"] in prompt
    assert _MULTI_PANEL_SCENARIO["audience"] in prompt


# ---------------------------------------------------------------------------
# build_pairwise_prompt — dimensions
# ---------------------------------------------------------------------------


def test_build_pairwise_prompt_contains_6_dimensions_multi_panel() -> None:
    """For multi-panel scenarios, prompt mentions all 6 dimension labels."""
    prompt = build_pairwise_prompt(
        _MULTI_PANEL_SCENARIO,
        ["a1.png", "a2.png"],
        ["b1.png", "b2.png"],
        "Model A",
        "Model B",
    )
    for label in (
        "Content Accuracy",
        "Narrative Structure",
        "Visual Explanation",
        "Typography",
        "Visual Quality",
        "Cross-Panel Consistency",
    ):
        assert label in prompt, f"Expected '{label}' in multi-panel prompt"


def test_build_pairwise_prompt_contains_5_dimensions_single_panel() -> None:
    """For single-panel scenarios, prompt has 5 dimensions (no cross-panel)."""
    prompt = build_pairwise_prompt(
        _SINGLE_PANEL_SCENARIO, ["a1.png"], ["b1.png"], "Model A", "Model B"
    )
    assert "Content Accuracy" in prompt
    assert "Cross-Panel Consistency" not in prompt


# ---------------------------------------------------------------------------
# build_pairwise_prompt — rationale-first + JSON schema
# ---------------------------------------------------------------------------


def test_build_pairwise_prompt_contains_rationale_first_instruction() -> None:
    """Prompt instructs the evaluator to provide rationale before winner."""
    prompt = build_pairwise_prompt(
        _MULTI_PANEL_SCENARIO,
        ["a1.png", "a2.png"],
        ["b1.png", "b2.png"],
        "Model A",
        "Model B",
    )
    lowered = prompt.lower()
    assert "rationale" in lowered
    assert "before" in lowered


def test_build_pairwise_prompt_contains_json_schema() -> None:
    """Prompt includes JSON output schema with valid winner enum values."""
    prompt = build_pairwise_prompt(
        _MULTI_PANEL_SCENARIO,
        ["a1.png", "a2.png"],
        ["b1.png", "b2.png"],
        "Model A",
        "Model B",
    )
    assert "model_a" in prompt
    assert "model_b" in prompt
    assert "tie" in prompt


# ---------------------------------------------------------------------------
# build_pairwise_prompt — image labels
# ---------------------------------------------------------------------------


def test_build_pairwise_prompt_labels_images_multi_panel() -> None:
    """Prompt references images with 'Model A - Panel 1' style labels."""
    prompt = build_pairwise_prompt(
        _MULTI_PANEL_SCENARIO,
        ["a1.png", "a2.png"],
        ["b1.png", "b2.png"],
        "Model A",
        "Model B",
    )
    assert "Model A - Panel 1" in prompt
    assert "Model A - Panel 2" in prompt
    assert "Model B - Panel 1" in prompt
    assert "Model B - Panel 2" in prompt


def test_build_pairwise_prompt_labels_images_single_panel() -> None:
    """For single-panel, prompt references Panel 1 only (no Panel 2)."""
    prompt = build_pairwise_prompt(
        _SINGLE_PANEL_SCENARIO, ["a1.png"], ["b1.png"], "Model A", "Model B"
    )
    assert "Model A - Panel 1" in prompt
    assert "Model B - Panel 1" in prompt
    assert "Panel 2" not in prompt
```

### Step 2: Run tests to verify they fail

```bash
python -m pytest tests/test_compare.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'eval.compare'`

### Step 3: Write the implementation

Create `eval/compare.py`:

```python
"""Pairwise model comparison for AI-generated infographics.

Provides:
- PAIRWISE_DIMENSIONS: dimension keys for single-panel comparison
- MULTI_PANEL_PAIRWISE_DIMENSIONS: dimension keys for multi-panel comparison
- DIMENSION_LABELS: human-readable labels for each dimension
- build_pairwise_prompt: constructs the GPT-5.4 pairwise judge prompt
- parse_pairwise_result: validates the pairwise JSON response
- compare_scenario: async entry-point that calls OpenAI GPT-5.4 vision
- generate_comparison_report: renders a markdown comparison report
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PAIRWISE_DIMENSIONS: list[str] = [
    "content_accuracy",
    "narrative_structure",
    "visual_explanation",
    "typography_legibility",
    "visual_quality_consistency",
]

MULTI_PANEL_PAIRWISE_DIMENSIONS: list[str] = PAIRWISE_DIMENSIONS + [
    "cross_panel_consistency",
]

VALID_WINNERS: set[str] = {"model_a", "model_b", "tie"}

DIMENSION_LABELS: dict[str, str] = {
    "content_accuracy": "Content Accuracy",
    "narrative_structure": "Narrative Structure",
    "visual_explanation": "Visual Explanation",
    "typography_legibility": "Typography & Legibility",
    "visual_quality_consistency": "Visual Quality & Consistency",
    "cross_panel_consistency": "Cross-Panel Consistency",
}

_DIMENSION_DESCRIPTIONS: dict[str, str] = {
    "content_accuracy": (
        "Evaluates factual correctness, data integrity, and absence of "
        "misleading claims. Look for hallucinated statistics, incorrect "
        "labels, or conflated concepts."
    ),
    "narrative_structure": (
        "Evaluates logical flow, clear entry/exit points, and coherent "
        "story progression. Look for random ordering or missing connective "
        "tissue between sections."
    ),
    "visual_explanation": (
        "Evaluates how effectively visuals communicate the core idea — "
        "diagrams, icons, metaphors, data encodings. Can the message be "
        "understood from visuals alone?"
    ),
    "typography_legibility": (
        "Evaluates font hierarchy, contrast, type size, and overall "
        "readability. Look for uniform weight with no hierarchy, "
        "low-contrast colour pairings, or decorative fonts for body copy."
    ),
    "visual_quality_consistency": (
        "Evaluates overall polish, colour palette coherence, icon "
        "consistency, and professional finish within each panel."
    ),
    "cross_panel_consistency": (
        "Evaluates visual consistency across panels — borders, backgrounds, "
        "colors, icons, typography, spacing. All panels should look like "
        "they came from the same designer."
    ),
}


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------


def build_pairwise_prompt(
    scenario: dict[str, Any],
    image_paths_a: list[str],
    image_paths_b: list[str],
    label_a: str,
    label_b: str,
) -> str:
    """Construct the pairwise judge prompt for comparing two models' outputs.

    Images are labeled with generic "Model A" / "Model B" identifiers in the
    prompt (not the user-provided labels) to keep the judge neutral.  The
    *label_a* and *label_b* parameters are accepted for API consistency and
    used in the report, not in the prompt text.

    Args:
        scenario: Scenario dict with ``topic``, ``audience``, ``panels``,
            ``style_direction``, and ``prompt`` keys.
        image_paths_a: Image file paths from Model A.
        image_paths_b: Image file paths from Model B.
        label_a: Human-readable label for Model A (used in report, not prompt).
        label_b: Human-readable label for Model B (used in report, not prompt).

    Returns:
        A complete pairwise comparison prompt string.
    """
    panel_count = scenario.get("panels", 1)
    multi_panel = panel_count > 1
    dims = MULTI_PANEL_PAIRWISE_DIMENSIONS if multi_panel else PAIRWISE_DIMENSIONS

    topic = scenario.get("topic", "")
    audience = scenario.get("audience", "")

    lines: list[str] = [
        "## Pairwise Infographic Comparison",
        "",
        "You are an expert visual communication evaluator. Compare two sets of "
        "infographic panels produced by different models for the same scenario. "
        "Determine which model produced better output on each evaluation "
        "dimension.",
        "",
        "### Scenario Context",
        f"- **Topic**: {topic}",
        f"- **Audience**: {audience}",
        f"- **Panel count**: {panel_count}",
        "",
        "### Images",
        "",
        "The following images are provided in order:",
    ]

    img_idx = 1
    for i in range(len(image_paths_a)):
        lines.append(f"{img_idx}. Model A - Panel {i + 1}")
        img_idx += 1
    for i in range(len(image_paths_b)):
        lines.append(f"{img_idx}. Model B - Panel {i + 1}")
        img_idx += 1

    lines += [
        "",
        "### Evaluation Dimensions",
        "",
        "For each dimension, provide your detailed rationale FIRST, then "
        "select a winner. Think through your assessment before making a "
        "judgment.",
        "",
    ]

    for idx, dim in enumerate(dims, start=1):
        label = DIMENSION_LABELS[dim]
        desc = _DIMENSION_DESCRIPTIONS[dim]
        lines.append(f"**{idx}. {label}**")
        lines.append(desc)
        lines.append("")

    lines += [
        "### Instructions",
        "",
        "For EACH dimension:",
        "1. Analyze both models' output carefully",
        "2. Write a detailed rationale explaining your comparison",
        '3. THEN select a winner: "model_a", "model_b", or "tie"',
        "",
        "After all dimensions, write an overall rationale summarizing your "
        "comparison, then select an overall winner.",
        "",
        "CRITICAL: You MUST provide rationale BEFORE selecting a winner at "
        "every level. Reason first, judge second.",
        "",
    ]

    # JSON schema
    dim_entries = ",\n".join(
        f'    "{d}": {{"rationale": "...", "winner": "model_a|model_b|tie"}}'
        for d in dims
    )

    lines += [
        "### Required JSON Output",
        "",
        "Respond with **only** a JSON object matching this schema "
        "(no markdown fences).",
        "",
        "```",
        "{",
        '  "dimensions": {',
        dim_entries,
        "  },",
        '  "overall_rationale": "...",',
        '  "overall_winner": "model_a|model_b|tie"',
        "}",
        "```",
    ]

    return "\n".join(lines)
```

### Step 4: Run tests to verify they pass

```bash
python -m pytest tests/test_compare.py -v
```

Expected: All 7 tests PASS.

### Step 5: Commit

```bash
git add eval/compare.py tests/test_compare.py && git commit -m "feat(eval): add build_pairwise_prompt() and comparison constants"
```

---

## Task 2: `parse_pairwise_result()`

**Files:**
- Modify: `eval/compare.py`
- Modify: `tests/test_compare.py`

### Step 1: Write the failing tests

Append to `tests/test_compare.py`:

```python
from eval.compare import parse_pairwise_result

# ---------------------------------------------------------------------------
# Fixtures — valid pairwise results
# ---------------------------------------------------------------------------

VALID_SINGLE_PANEL_RESULT: dict = {
    "dimensions": {
        "content_accuracy": {
            "rationale": "Model A includes the authoritative NS step.",
            "winner": "model_a",
        },
        "narrative_structure": {
            "rationale": "Both have clear progression.",
            "winner": "tie",
        },
        "visual_explanation": {
            "rationale": "Model B uses more distinct icons.",
            "winner": "model_b",
        },
        "typography_legibility": {
            "rationale": "Model B has cleaner text rendering.",
            "winner": "model_b",
        },
        "visual_quality_consistency": {
            "rationale": "Model B has a more contemporary palette.",
            "winner": "model_b",
        },
    },
    "overall_rationale": "Model B wins on 3 of 5 dimensions.",
    "overall_winner": "model_b",
}

VALID_MULTI_PANEL_RESULT: dict = {
    **VALID_SINGLE_PANEL_RESULT,
    "dimensions": {
        **VALID_SINGLE_PANEL_RESULT["dimensions"],
        "cross_panel_consistency": {
            "rationale": "Both maintain consistent style across panels.",
            "winner": "tie",
        },
    },
}


# ---------------------------------------------------------------------------
# parse_pairwise_result — happy path
# ---------------------------------------------------------------------------


def test_parse_pairwise_result_accepts_valid_single_panel() -> None:
    """Valid 5-dimension result is accepted for single-panel scenarios."""
    result = parse_pairwise_result(json.dumps(VALID_SINGLE_PANEL_RESULT), panel_count=1)
    assert "dimensions" in result
    assert len(result["dimensions"]) == 5
    assert result["overall_winner"] == "model_b"


def test_parse_pairwise_result_accepts_valid_multi_panel() -> None:
    """Valid 6-dimension result is accepted for multi-panel scenarios."""
    result = parse_pairwise_result(
        json.dumps(VALID_MULTI_PANEL_RESULT), panel_count=2
    )
    assert len(result["dimensions"]) == 6
    assert "cross_panel_consistency" in result["dimensions"]


# ---------------------------------------------------------------------------
# parse_pairwise_result — error handling
# ---------------------------------------------------------------------------


def test_parse_pairwise_result_rejects_invalid_json() -> None:
    """Raises ValueError for malformed JSON input."""
    with pytest.raises(ValueError, match="Invalid JSON"):
        parse_pairwise_result("{not valid", panel_count=1)


def test_parse_pairwise_result_rejects_missing_dimension() -> None:
    """Raises ValueError when a required dimension is missing."""
    incomplete = {
        "dimensions": {
            "content_accuracy": {"rationale": "ok", "winner": "tie"},
            # missing other 4 dimensions
        },
        "overall_rationale": "ok",
        "overall_winner": "tie",
    }
    with pytest.raises(ValueError, match=r"Missing.*dimension"):
        parse_pairwise_result(json.dumps(incomplete), panel_count=1)


def test_parse_pairwise_result_rejects_invalid_winner() -> None:
    """Raises ValueError when a winner value is not model_a/model_b/tie."""
    import copy

    bad = copy.deepcopy(VALID_SINGLE_PANEL_RESULT)
    bad["dimensions"]["content_accuracy"]["winner"] = "model_c"
    with pytest.raises(ValueError, match="Invalid winner"):
        parse_pairwise_result(json.dumps(bad), panel_count=1)


def test_parse_pairwise_result_rejects_empty_rationale() -> None:
    """Raises ValueError when a dimension rationale is empty."""
    import copy

    bad = copy.deepcopy(VALID_SINGLE_PANEL_RESULT)
    bad["dimensions"]["content_accuracy"]["rationale"] = ""
    with pytest.raises(ValueError, match="[Ee]mpty rationale"):
        parse_pairwise_result(json.dumps(bad), panel_count=1)


def test_parse_pairwise_result_rejects_missing_overall_winner() -> None:
    """Raises ValueError when overall_winner key is absent."""
    import copy

    bad = copy.deepcopy(VALID_SINGLE_PANEL_RESULT)
    del bad["overall_winner"]
    with pytest.raises(ValueError, match="overall_winner"):
        parse_pairwise_result(json.dumps(bad), panel_count=1)
```

### Step 2: Run tests to verify they fail

```bash
python -m pytest tests/test_compare.py -k "parse_pairwise" -v
```

Expected: FAIL — `ImportError: cannot import name 'parse_pairwise_result'`

### Step 3: Write the implementation

Add to `eval/compare.py` (after the prompt builder, before the end of file). First add `import json` to the imports at the top of the file:

```python
import json
```

Then add the function:

```python
# ---------------------------------------------------------------------------
# Result parser / validator
# ---------------------------------------------------------------------------


def parse_pairwise_result(
    raw_json_str: str,
    *,
    panel_count: int = 1,
) -> dict[str, Any]:
    """Parse and validate the pairwise judge JSON response.

    Args:
        raw_json_str: Raw JSON string from the model.
        panel_count: Number of panels in the scenario (>1 requires
            ``cross_panel_consistency`` dimension).

    Returns:
        Validated pairwise result dict with ``dimensions``,
        ``overall_rationale``, and ``overall_winner`` keys.

    Raises:
        ValueError: If the JSON is malformed, required dimensions are missing,
            winner values are invalid, or rationale is empty.
    """
    try:
        data: dict[str, Any] = json.loads(raw_json_str)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc}") from exc

    dimensions: dict[str, Any] = data.get("dimensions", {})

    # Select expected dimension set based on panel count
    expected_dims = (
        MULTI_PANEL_PAIRWISE_DIMENSIONS if panel_count > 1 else PAIRWISE_DIMENSIONS
    )

    # Validate all expected dimensions are present
    missing = set(expected_dims) - set(dimensions.keys())
    if missing:
        raise ValueError(
            f"Missing dimension(s) in pairwise result: {sorted(missing)}"
        )

    # Validate each dimension entry
    for dim_key in expected_dims:
        entry = dimensions[dim_key]

        rationale = entry.get("rationale")
        if not isinstance(rationale, str) or not rationale.strip():
            raise ValueError(
                f"Empty rationale for dimension '{dim_key}'"
            )

        winner = entry.get("winner")
        if winner not in VALID_WINNERS:
            raise ValueError(
                f"Invalid winner for dimension '{dim_key}': {winner!r} "
                f"(must be one of {sorted(VALID_WINNERS)})"
            )

    # Validate overall fields
    if "overall_winner" not in data:
        raise ValueError("Missing required key: overall_winner")

    if data["overall_winner"] not in VALID_WINNERS:
        raise ValueError(
            f"Invalid overall_winner: {data['overall_winner']!r} "
            f"(must be one of {sorted(VALID_WINNERS)})"
        )

    if "overall_rationale" not in data:
        raise ValueError("Missing required key: overall_rationale")

    return {
        "dimensions": dimensions,
        "overall_rationale": data["overall_rationale"],
        "overall_winner": data["overall_winner"],
    }
```

### Step 4: Run tests to verify they pass

```bash
python -m pytest tests/test_compare.py -v
```

Expected: All 14 tests PASS (7 from Task 1 + 7 from Task 2).

### Step 5: Commit

```bash
git add eval/compare.py tests/test_compare.py && git commit -m "feat(eval): add parse_pairwise_result() validator"
```

---

## Task 3: `compare_scenario()`

**Files:**
- Modify: `eval/compare.py`
- Modify: `tests/test_compare.py`

### Step 1: Write the failing tests

Append to `tests/test_compare.py`:

```python
import asyncio
import os
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

from eval.compare import compare_scenario


# ---------------------------------------------------------------------------
# compare_scenario — mocked OpenAI
# ---------------------------------------------------------------------------


def test_compare_scenario_returns_parsed_result(tmp_path: Path) -> None:
    """compare_scenario calls GPT-5.4 and returns a parsed pairwise result."""
    # Create dummy image files (just need valid file reads for _encode_image)
    img_a = tmp_path / "a_panel_1.png"
    img_a.write_bytes(b"\x89PNG\r\n\x1a\n")
    img_b = tmp_path / "b_panel_1.png"
    img_b.write_bytes(b"\x89PNG\r\n\x1a\n")

    scenario = {
        "name": "dns",
        "topic": "How DNS Works",
        "audience": "Developers",
        "panels": 1,
        "style_direction": "Minimal",
        "prompt": "DNS prompt.",
    }

    api_response_json = json.dumps(VALID_SINGLE_PANEL_RESULT)

    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = api_response_json

    mock_client = Mock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    with patch("openai.AsyncOpenAI", return_value=mock_client):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            result = asyncio.run(
                compare_scenario(
                    scenario, [str(img_a)], [str(img_b)], "Model A", "Model B"
                )
            )

    assert result["overall_winner"] == "model_b"
    assert "content_accuracy" in result["dimensions"]
    assert result["scenario"] == "dns"
    assert result["panels"] == 1


def test_compare_scenario_strips_markdown_fences(tmp_path: Path) -> None:
    """compare_scenario strips ```json fences from the API response."""
    img_a = tmp_path / "a.png"
    img_a.write_bytes(b"\x89PNG\r\n\x1a\n")
    img_b = tmp_path / "b.png"
    img_b.write_bytes(b"\x89PNG\r\n\x1a\n")

    scenario = {
        "name": "test",
        "topic": "Test",
        "audience": "Testers",
        "panels": 1,
        "style_direction": "Minimal",
        "prompt": "Test.",
    }

    # Wrap the valid JSON in markdown code fences
    fenced_response = "```json\n" + json.dumps(VALID_SINGLE_PANEL_RESULT) + "\n```"

    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = fenced_response

    mock_client = Mock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    with patch("openai.AsyncOpenAI", return_value=mock_client):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            result = asyncio.run(
                compare_scenario(
                    scenario, [str(img_a)], [str(img_b)], "Model A", "Model B"
                )
            )

    # Should still parse correctly after fence stripping
    assert result["overall_winner"] == "model_b"
```

### Step 2: Run tests to verify they fail

```bash
python -m pytest tests/test_compare.py -k "compare_scenario" -v
```

Expected: FAIL — `ImportError: cannot import name 'compare_scenario'`

### Step 3: Write the implementation

Add these imports at the top of `eval/compare.py`:

```python
import os
import re
```

Add the function to `eval/compare.py`:

```python
# ---------------------------------------------------------------------------
# Async comparison entry-point
# ---------------------------------------------------------------------------


async def compare_scenario(
    scenario: dict[str, Any],
    image_paths_a: list[str],
    image_paths_b: list[str],
    label_a: str,
    label_b: str,
) -> dict[str, Any]:
    """Compare two models' infographic outputs using GPT-5.4 vision.

    Builds the pairwise prompt, encodes images, calls the OpenAI API, and
    returns the validated result with ``scenario`` and ``panels`` metadata.

    Args:
        scenario: Scenario dict (name, topic, audience, panels, …).
        image_paths_a: Ordered image file paths from Model A.
        image_paths_b: Ordered image file paths from Model B.
        label_a: Human-readable label for Model A.
        label_b: Human-readable label for Model B.

    Returns:
        Validated pairwise result dict with added ``scenario`` and ``panels``
        keys.

    Raises:
        EnvironmentError: If ``OPENAI_API_KEY`` is not set.
        ValueError: If the model response cannot be parsed or validated.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "OPENAI_API_KEY environment variable is required for compare_scenario"
        )

    # Import here to avoid hard dependency at module-import time
    from openai import AsyncOpenAI  # noqa: PLC0415

    # Import the image encoder from rubric (same package, private helper)
    from eval.rubric import _encode_image  # noqa: PLC0415

    client = AsyncOpenAI(api_key=api_key)

    text_prompt = build_pairwise_prompt(
        scenario, image_paths_a, image_paths_b, label_a, label_b
    )

    # Build content: text prompt, then Model A images, then Model B images
    content: list[dict[str, Any]] = [{"type": "text", "text": text_prompt}]

    for path in image_paths_a + image_paths_b:
        encoded = _encode_image(path)
        content.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{encoded}",
                    "detail": "high",
                },
            }
        )

    response = await client.chat.completions.create(
        model="gpt-5.4-2026-03-05",
        max_completion_tokens=4096,
        temperature=0.2,
        messages=[{"role": "user", "content": content}],  # type: ignore[arg-type]
    )

    raw: str = response.choices[0].message.content or ""

    # Strip markdown code fences if the model wraps its JSON
    raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    raw = re.sub(r"\s*```$", "", raw.strip())

    panel_count = scenario.get("panels", 1)
    result = parse_pairwise_result(raw, panel_count=panel_count)

    # Add scenario metadata to the result
    result["scenario"] = scenario.get("name", "")
    result["panels"] = panel_count

    return result
```

### Step 4: Run tests to verify they pass

```bash
python -m pytest tests/test_compare.py -v
```

Expected: All 16 tests PASS (14 previous + 2 new).

### Step 5: Commit

```bash
git add eval/compare.py tests/test_compare.py && git commit -m "feat(eval): add compare_scenario() async API caller"
```

---

## Task 4: `generate_comparison_report()`

**Files:**
- Modify: `eval/compare.py`
- Modify: `tests/test_compare.py`

### Step 1: Write the failing tests

Append to `tests/test_compare.py`:

```python
from eval.compare import generate_comparison_report

# ---------------------------------------------------------------------------
# Fixtures — comparison results for report tests
# ---------------------------------------------------------------------------

# Two scenario results: dns (Model B wins 3-1-1) and campfire (Model A wins 3-2-0)
_REPORT_RESULTS: list[dict] = [
    {
        "scenario": "dns",
        "panels": 2,
        "dimensions": {
            "content_accuracy": {
                "rationale": "Model A includes authoritative NS step.",
                "winner": "model_a",
            },
            "narrative_structure": {
                "rationale": "Both have clear progression.",
                "winner": "tie",
            },
            "visual_explanation": {
                "rationale": "Model B uses more distinct icons.",
                "winner": "model_b",
            },
            "typography_legibility": {
                "rationale": "Model B has cleaner text.",
                "winner": "model_b",
            },
            "visual_quality_consistency": {
                "rationale": "Model B more polished.",
                "winner": "model_b",
            },
            "cross_panel_consistency": {
                "rationale": "Both consistent.",
                "winner": "tie",
            },
        },
        "overall_rationale": "Model B wins.",
        "overall_winner": "model_b",
    },
    {
        "scenario": "campfire",
        "panels": 1,
        "dimensions": {
            "content_accuracy": {
                "rationale": "Model A is more accurate.",
                "winner": "model_a",
            },
            "narrative_structure": {
                "rationale": "Model A has better flow.",
                "winner": "model_a",
            },
            "visual_explanation": {
                "rationale": "Model B has better visuals.",
                "winner": "model_b",
            },
            "typography_legibility": {
                "rationale": "Model A is more readable.",
                "winner": "model_a",
            },
            "visual_quality_consistency": {
                "rationale": "Model B is more polished.",
                "winner": "model_b",
            },
        },
        "overall_rationale": "Model A wins.",
        "overall_winner": "model_a",
    },
]

_REPORT_SKIPPED: list[dict[str, str]] = [
    {"scenario": "saas-metrics", "reason": "only in Run A"},
]


# ---------------------------------------------------------------------------
# generate_comparison_report — structure
# ---------------------------------------------------------------------------


def test_report_contains_model_labels() -> None:
    """Report includes both model labels in the header."""
    report = generate_comparison_report(
        _REPORT_RESULTS, "Nano Banana Pro", "Nano Banana 2", _REPORT_SKIPPED
    )
    assert "Nano Banana Pro" in report
    assert "Nano Banana 2" in report


def test_report_contains_scenario_count() -> None:
    """Report includes the count of compared scenarios."""
    report = generate_comparison_report(
        _REPORT_RESULTS, "Model A", "Model B", _REPORT_SKIPPED
    )
    # 2 compared out of 3 total (2 compared + 1 skipped)
    assert "2" in report


def test_report_contains_dimension_win_rate_table() -> None:
    """Report includes a dimension win-rate table with Model A/B headers."""
    report = generate_comparison_report(
        _REPORT_RESULTS, "Model A", "Model B", _REPORT_SKIPPED
    )
    assert "Dimension" in report
    assert "Content Accuracy" in report
    assert "Typography" in report


def test_report_contains_per_scenario_results() -> None:
    """Report includes per-scenario sections with dimension tables."""
    report = generate_comparison_report(
        _REPORT_RESULTS, "Model A", "Model B", _REPORT_SKIPPED
    )
    assert "dns" in report
    assert "campfire" in report
    assert "Scenario winner" in report


def test_report_contains_skipped_scenarios_section() -> None:
    """Report includes the skipped scenarios at the bottom."""
    report = generate_comparison_report(
        _REPORT_RESULTS, "Model A", "Model B", _REPORT_SKIPPED
    )
    assert "Skipped" in report
    assert "saas-metrics" in report
    assert "only in Run A" in report


def test_report_overall_winner_determined_by_scenarios() -> None:
    """Overall winner is based on scenario wins, not dimension wins.

    dns: Model B wins 3 dims, Model A wins 1, ties 2 → scenario winner: Model B
    campfire: Model A wins 3 dims, Model B wins 2 → scenario winner: Model A
    Overall: 1-1 tie in scenarios → overall is tie
    """
    report = generate_comparison_report(
        _REPORT_RESULTS, "Model A", "Model B", _REPORT_SKIPPED
    )
    # With 1 scenario each, overall should be a tie
    # The header line should indicate tie (wins 1, loses 1, ties 0)
    assert "Tie" in report or "tie" in report.lower()
```

### Step 2: Run tests to verify they fail

```bash
python -m pytest tests/test_compare.py -k "report" -v
```

Expected: FAIL — `ImportError: cannot import name 'generate_comparison_report'`

### Step 3: Write the implementation

Add to `eval/compare.py`:

```python
# ---------------------------------------------------------------------------
# Report helpers
# ---------------------------------------------------------------------------


def _determine_scenario_winner(dimensions: dict[str, dict[str, str]]) -> str:
    """Determine the scenario winner from dimension-level winners.

    Counts dimension wins for each model.  The model with more dimension wins
    takes the scenario.  Equal counts produce a tie.
    """
    a_wins = sum(1 for d in dimensions.values() if d["winner"] == "model_a")
    b_wins = sum(1 for d in dimensions.values() if d["winner"] == "model_b")
    if a_wins > b_wins:
        return "model_a"
    if b_wins > a_wins:
        return "model_b"
    return "tie"


# ---------------------------------------------------------------------------
# Report generator
# ---------------------------------------------------------------------------


def generate_comparison_report(
    results: list[dict[str, Any]],
    label_a: str,
    label_b: str,
    skipped: list[dict[str, str]],
) -> str:
    """Generate a full markdown pairwise comparison report.

    Args:
        results: List of pairwise result dicts (each with ``scenario``,
            ``panels``, ``dimensions``, ``overall_rationale``,
            ``overall_winner`` keys).
        label_a: Human-readable label for Model A.
        label_b: Human-readable label for Model B.
        skipped: List of dicts with ``scenario`` and ``reason`` keys for
            scenarios that were skipped.

    Returns:
        A multi-line markdown string.
    """
    # --- Compute scenario winners and overall winner -------------------------
    scenario_winners: list[str] = []
    for result in results:
        sw = _determine_scenario_winner(result["dimensions"])
        scenario_winners.append(sw)

    a_scenario_wins = scenario_winners.count("model_a")
    b_scenario_wins = scenario_winners.count("model_b")
    scenario_ties = scenario_winners.count("tie")

    if a_scenario_wins > b_scenario_wins:
        overall_winner = label_a
        overall_summary = (
            f"{label_a} (wins {a_scenario_wins}, "
            f"loses {b_scenario_wins}, ties {scenario_ties})"
        )
    elif b_scenario_wins > a_scenario_wins:
        overall_winner = label_b
        overall_summary = (
            f"{label_b} (wins {b_scenario_wins}, "
            f"loses {a_scenario_wins}, ties {scenario_ties})"
        )
    else:
        overall_winner = "Tie"
        overall_summary = (
            f"Tie ({label_a} wins {a_scenario_wins}, "
            f"{label_b} wins {b_scenario_wins}, ties {scenario_ties})"
        )

    total_scenarios = len(results) + len(skipped)

    lines: list[str] = []

    # --- Header --------------------------------------------------------------
    lines.append("# Pairwise Model Comparison")
    lines.append("")
    lines.append(f"**Model A:** {label_a}")
    lines.append(f"**Model B:** {label_b}")
    lines.append(f"**Scenarios compared:** {len(results)} of {total_scenarios}")
    lines.append(f"**Overall winner:** {overall_summary}")
    lines.append("")

    # --- Dimension win-rate table --------------------------------------------
    # Collect all dimension keys across results (union, preserving order)
    all_dims: list[str] = []
    for result in results:
        for dim_key in result["dimensions"]:
            if dim_key not in all_dims:
                all_dims.append(dim_key)

    lines.append("## Dimension Win Rates")
    lines.append("")
    lines.append(
        f"| Dimension | {label_a} Wins | {label_b} Wins | Ties |"
    )
    lines.append("|---|---|---|---|")

    for dim_key in all_dims:
        dim_label = DIMENSION_LABELS.get(dim_key, dim_key)
        a_w = sum(
            1
            for r in results
            if dim_key in r["dimensions"]
            and r["dimensions"][dim_key]["winner"] == "model_a"
        )
        b_w = sum(
            1
            for r in results
            if dim_key in r["dimensions"]
            and r["dimensions"][dim_key]["winner"] == "model_b"
        )
        t = sum(
            1
            for r in results
            if dim_key in r["dimensions"]
            and r["dimensions"][dim_key]["winner"] == "tie"
        )
        lines.append(f"| {dim_label} | {a_w} | {b_w} | {t} |")

    lines.append("")

    # --- Per-scenario results ------------------------------------------------
    lines.append("## Per-Scenario Results")
    lines.append("")

    for result, sw in zip(results, scenario_winners):
        scenario_name = result["scenario"]
        panel_count = result.get("panels", 1)
        dims = result["dimensions"]

        # Determine winner label for display
        if sw == "model_a":
            winner_display = f"**{label_a}**"
        elif sw == "model_b":
            winner_display = f"**{label_b}**"
        else:
            winner_display = "**Tie**"

        lines.append(f"### {scenario_name} ({panel_count} panels)")
        lines.append("")
        lines.append("| Dimension | Winner | Rationale |")
        lines.append("|---|---|---|")

        for dim_key, dim_data in dims.items():
            dim_label = DIMENSION_LABELS.get(dim_key, dim_key)
            winner_val = dim_data["winner"]
            if winner_val == "model_a":
                winner_text = label_a
            elif winner_val == "model_b":
                winner_text = label_b
            else:
                winner_text = "Tie"
            rationale = dim_data.get("rationale", "")
            lines.append(f"| {dim_label} | {winner_text} | {rationale} |")

        lines.append(f"| **Scenario winner** | {winner_display} | |")
        lines.append("")

    # --- Skipped scenarios ---------------------------------------------------
    if skipped:
        lines.append("## Skipped Scenarios")
        lines.append("")
        lines.append(
            "The following scenarios were present in only one run "
            "and could not be compared:"
        )
        lines.append("")
        for entry in skipped:
            lines.append(f"- {entry['scenario']} ({entry['reason']})")
        lines.append("")

    return "\n".join(lines)
```

### Step 4: Run tests to verify they pass

```bash
python -m pytest tests/test_compare.py -v
```

Expected: All 22 tests PASS (16 previous + 6 new).

### Step 5: Commit

```bash
git add eval/compare.py tests/test_compare.py && git commit -m "feat(eval): add generate_comparison_report() markdown renderer"
```

---

## Task 5: `compare` CLI Subcommand

**Files:**
- Modify: `eval/cli.py`
- Modify: `tests/test_cli.py`

### Step 1: Write the failing tests

Append to `tests/test_cli.py`:

```python
# ---------------------------------------------------------------------------
# compare subcommand
# ---------------------------------------------------------------------------


def test_main_compare_help_exits_cleanly() -> None:
    """python -m eval compare --help exits with code 0."""
    result = subprocess.run(
        [sys.executable, "-m", "eval", "compare", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Expected exit code 0, got {result.returncode}\n{result.stderr}"
    )
    assert "compare" in result.stdout.lower() or "usage" in result.stdout.lower()


def test_main_compare_help_shows_required_args() -> None:
    """compare --help shows --run-a, --run-b, --label-a, --label-b, --output."""
    result = subprocess.run(
        [sys.executable, "-m", "eval", "compare", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    for arg in ["--run-a", "--run-b", "--label-a", "--label-b", "--output"]:
        assert arg in result.stdout, f"'{arg}' not found in compare --help output"


def test_cmd_compare_produces_output_files(tmp_path: Path) -> None:
    """cmd_compare writes both a markdown report and a JSON results file."""
    from eval.cli import cmd_compare

    # Create two fake run directories with matching scenario subdirectories
    run_a = tmp_path / "run_a"
    run_b = tmp_path / "run_b"
    for run_dir in (run_a, run_b):
        scenario_dir = run_dir / "dns"
        scenario_dir.mkdir(parents=True)
        (scenario_dir / "panel_1.png").write_bytes(b"\x89PNG\r\n\x1a\n")

    # Create a scenarios YAML
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

    output_path = tmp_path / "comparison.md"

    # Mock compare_scenario to return a canned result
    fake_result = {
        "scenario": "dns",
        "panels": 1,
        "dimensions": {
            "content_accuracy": {"rationale": "A is better.", "winner": "model_a"},
            "narrative_structure": {"rationale": "Equal.", "winner": "tie"},
            "visual_explanation": {"rationale": "B is better.", "winner": "model_b"},
            "typography_legibility": {"rationale": "Equal.", "winner": "tie"},
            "visual_quality_consistency": {
                "rationale": "A is better.",
                "winner": "model_a",
            },
        },
        "overall_rationale": "Model A wins.",
        "overall_winner": "model_a",
    }

    args = SimpleNamespace(
        run_a=str(run_a),
        run_b=str(run_b),
        label_a="Test Model A",
        label_b="Test Model B",
        output=str(output_path),
        scenario_file=str(scenarios_yaml),
    )

    with patch(
        "eval.cli.compare_scenario", new=AsyncMock(return_value=fake_result)
    ):
        cmd_compare(args)

    # Markdown report should exist
    assert output_path.exists(), "Markdown comparison report should be created"
    report_text = output_path.read_text()
    assert "Test Model A" in report_text
    assert "Test Model B" in report_text
    assert "dns" in report_text

    # JSON results file should exist alongside the markdown
    json_path = output_path.parent / (output_path.stem + ".json")
    assert json_path.exists(), "JSON results file should be created"
    json_data = json.loads(json_path.read_text())
    assert isinstance(json_data, list)
    assert json_data[0]["scenario"] == "dns"


def test_cmd_compare_reports_skipped_scenarios(tmp_path: Path) -> None:
    """cmd_compare includes scenarios present in only one run as skipped."""
    from eval.cli import cmd_compare

    # Create run directories: dns in both, campfire only in run_a
    run_a = tmp_path / "run_a"
    run_b = tmp_path / "run_b"

    (run_a / "dns").mkdir(parents=True)
    (run_a / "dns" / "panel_1.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    (run_a / "campfire").mkdir(parents=True)
    (run_a / "campfire" / "panel_1.png").write_bytes(b"\x89PNG\r\n\x1a\n")

    (run_b / "dns").mkdir(parents=True)
    (run_b / "dns" / "panel_1.png").write_bytes(b"\x89PNG\r\n\x1a\n")

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
  - name: campfire
    topic: Campfire Safety
    panels: 1
    audience: Campers
    style_direction: Warm
    prompt: Campfire prompt.
"""
    )

    output_path = tmp_path / "comparison.md"

    fake_result = {
        "scenario": "dns",
        "panels": 1,
        "dimensions": {
            "content_accuracy": {"rationale": "ok.", "winner": "tie"},
            "narrative_structure": {"rationale": "ok.", "winner": "tie"},
            "visual_explanation": {"rationale": "ok.", "winner": "tie"},
            "typography_legibility": {"rationale": "ok.", "winner": "tie"},
            "visual_quality_consistency": {"rationale": "ok.", "winner": "tie"},
        },
        "overall_rationale": "Tie.",
        "overall_winner": "tie",
    }

    args = SimpleNamespace(
        run_a=str(run_a),
        run_b=str(run_b),
        label_a="Model A",
        label_b="Model B",
        output=str(output_path),
        scenario_file=str(scenarios_yaml),
    )

    with patch(
        "eval.cli.compare_scenario", new=AsyncMock(return_value=fake_result)
    ):
        cmd_compare(args)

    report_text = output_path.read_text()
    assert "campfire" in report_text
    assert "only in Run A" in report_text
```

### Step 2: Run tests to verify they fail

```bash
python -m pytest tests/test_cli.py -k "compare" -v
```

Expected: FAIL — `ImportError: cannot import name 'cmd_compare'` (or `AttributeError` for the missing subcommand)

### Step 3: Write the implementation

Modify `eval/cli.py`. Add the import at the top alongside the existing imports:

```python
from eval.compare import compare_scenario, generate_comparison_report
```

Add the `cmd_compare` function after `cmd_report`:

```python
# ---------------------------------------------------------------------------
# Subcommand: compare
# ---------------------------------------------------------------------------


def cmd_compare(args: Any) -> None:
    """Run pairwise comparison between two evaluation runs.

    Scans both run directories for scenario subdirectories, matches them by
    name, calls :func:`~eval.compare.compare_scenario` for each match, and
    writes a markdown comparison report and a JSON results file.
    """
    run_a = Path(args.run_a)
    run_b = Path(args.run_b)

    # Load all scenarios from the YAML for metadata lookup
    with open(args.scenario_file, encoding="utf-8") as fh:
        scenario_data = yaml.safe_load(fh)
    scenarios_by_name: dict[str, dict[str, Any]] = {
        s["name"]: s for s in scenario_data.get("scenarios", [])
    }

    # Discover scenario subdirectories in each run
    dirs_a = {d.name for d in run_a.iterdir() if d.is_dir()}
    dirs_b = {d.name for d in run_b.iterdir() if d.is_dir()}

    matched = sorted(dirs_a & dirs_b)
    only_a = sorted(dirs_a - dirs_b)
    only_b = sorted(dirs_b - dirs_a)

    # Build skipped list
    skipped: list[dict[str, str]] = []
    for name in only_a:
        skipped.append({"scenario": name, "reason": "only in Run A"})
    for name in only_b:
        skipped.append({"scenario": name, "reason": "only in Run B"})

    # Run comparisons
    async def _run_all() -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for scenario_name in matched:
            # Look up scenario metadata
            if scenario_name not in scenarios_by_name:
                skipped.append(
                    {"scenario": scenario_name, "reason": "not in scenarios YAML"}
                )
                continue

            scenario = scenarios_by_name[scenario_name]
            panel_count = scenario.get("panels", 1)

            # Collect images from each run
            pngs_a = sorted(
                str(p) for p in (run_a / scenario_name).glob("*.png")
            )
            pngs_b = sorted(
                str(p) for p in (run_b / scenario_name).glob("*.png")
            )

            if not pngs_a or not pngs_b:
                skipped.append(
                    {"scenario": scenario_name, "reason": "missing images"}
                )
                continue

            # Select first N images (1 for single-panel, 2 for multi-panel)
            n_images = 1 if panel_count == 1 else min(2, len(pngs_a), len(pngs_b))
            selected_a = pngs_a[:n_images]
            selected_b = pngs_b[:n_images]

            try:
                result = await compare_scenario(
                    scenario,
                    selected_a,
                    selected_b,
                    args.label_a,
                    args.label_b,
                )
                results.append(result)
            except Exception as exc:
                print(f"WARNING: Skipping {scenario_name}: {exc}")
                skipped.append(
                    {"scenario": scenario_name, "reason": f"error: {exc}"}
                )

        return results

    results = asyncio.run(_run_all())

    # Generate and write the markdown report
    report = generate_comparison_report(
        results, args.label_a, args.label_b, skipped
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")

    # Write JSON results alongside the markdown
    json_path = output_path.parent / (output_path.stem + ".json")
    json_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    compared = len(results)
    skipped_count = len(skipped)
    print(
        f"Comparison written to {output_path} "
        f"({compared} compared, {skipped_count} skipped)"
    )
```

Add the `compare` subparser inside the `_build_parser` function, after the `report` subparser block:

```python
    # ---- compare subcommand ------------------------------------------------
    compare_parser = subparsers.add_parser(
        "compare",
        help="Pairwise comparison of two evaluation runs.",
    )
    compare_parser.add_argument(
        "--run-a",
        required=True,
        help="Path to the first model's eval-results run directory.",
    )
    compare_parser.add_argument(
        "--run-b",
        required=True,
        help="Path to the second model's eval-results run directory.",
    )
    compare_parser.add_argument(
        "--label-a",
        required=True,
        help="Human-readable name for Model A (used in report).",
    )
    compare_parser.add_argument(
        "--label-b",
        required=True,
        help="Human-readable name for Model B (used in report).",
    )
    compare_parser.add_argument(
        "--output",
        required=True,
        help="Output path for the comparison markdown report.",
    )
    compare_parser.add_argument(
        "--scenario-file",
        default="eval/scenarios.yaml",
        help="Path to the scenarios YAML file (default: eval/scenarios.yaml).",
    )
    compare_parser.set_defaults(func=cmd_compare)
```

Update the module docstring at the top of `eval/cli.py` to include the new subcommand:

```python
"""CLI entry point for the infographic evaluation harness.

Provides subcommands:
  evaluate  — Score a single scenario against PNG images in a directory.
  report    — Aggregate *_scores.json files from a run directory into a
              markdown summary report.
  compare   — Pairwise comparison of two evaluation runs using GPT-5.4
              as a relative judge.

Image generation is handled by the infographic-builder agent via the
``recipes/evaluate.yaml`` recipe.  This CLI covers only scoring,
reporting, and comparison — the steps that don't require an Amplifier
agent session.
"""
```

### Step 4: Run tests to verify they pass

```bash
python -m pytest tests/test_cli.py -v
```

Expected: All tests PASS (existing CLI tests + 4 new compare tests).

### Step 5: Commit

```bash
git add eval/cli.py tests/test_cli.py && git commit -m "feat(eval): add compare CLI subcommand for pairwise model comparison"
```

---

## Task 6: End-to-End Verification

**Files:** None (read-only verification)

### Step 1: Run the full test suite

```bash
python -m pytest tests/test_compare.py tests/test_cli.py -v
```

Expected: All tests PASS. No failures, no warnings about missing imports.

### Step 2: Verify CLI --help output

```bash
python -m eval --help
```

Expected output should list three subcommands: `evaluate`, `report`, `compare`.

```bash
python -m eval compare --help
```

Expected output should show `--run-a`, `--run-b`, `--label-a`, `--label-b`, `--output`, `--scenario-file`.

### Step 3: Run type checking and linting

```bash
python -m pytest tests/ -v
```

Expected: Full test suite passes (all existing tests still pass alongside the new ones).

### Step 4: Verify no regressions in existing modules

```bash
python -m pytest tests/test_rubric.py tests/test_report.py -v
```

Expected: All existing rubric and report tests still PASS — the new compare module does not interfere with existing functionality.

### Step 5: Commit (if any fixes were needed)

Only if Steps 1–4 revealed issues that required fixes:

```bash
git add -A && git commit -m "fix(eval): address issues found during e2e verification"
```

---

## Summary

| Task | Function | Tests | File |
|------|----------|-------|------|
| 1 | `build_pairwise_prompt()` + constants | 7 | `eval/compare.py`, `tests/test_compare.py` |
| 2 | `parse_pairwise_result()` | 7 | `eval/compare.py`, `tests/test_compare.py` |
| 3 | `compare_scenario()` | 2 | `eval/compare.py`, `tests/test_compare.py` |
| 4 | `generate_comparison_report()` | 6 | `eval/compare.py`, `tests/test_compare.py` |
| 5 | `compare` CLI subcommand | 4 | `eval/cli.py`, `tests/test_cli.py` |
| 6 | End-to-end verification | 0 | — |
| **Total** | **4 public functions + 1 CLI subcommand** | **26** | **2 new + 2 modified** |