"""Rubric-based evaluation logic for AI-generated infographics.

Provides:
- DIMENSION_WEIGHTS: weighted scoring dimensions
- REQUIRED_DIMENSIONS: set of required rubric keys
- build_rubric_prompt: constructs the GPT-4o evaluation prompt
- parse_scores: validates and normalises the model JSON response
- evaluate_image: async entry-point that calls OpenAI GPT-4o vision
"""

from __future__ import annotations

import base64
import json
import os
import re
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DIMENSION_WEIGHTS: dict[str, float] = {
    "content_accuracy": 0.20,
    "narrative_structure": 0.15,
    "visual_explanation": 0.25,
    "typography": 0.20,
    "visual_quality": 0.20,
}

REQUIRED_DIMENSIONS: set[str] = set(DIMENSION_WEIGHTS.keys())

# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

_RUBRIC_DIMENSIONS = """
### Scoring Rubric (each dimension scored 1–10)

**1. Content Accuracy (20%)**
Evaluates factual correctness, data integrity, and absence of misleading claims.
- *Behavioral anchors*: 9–10 = all data verifiable and accurate; 5–6 = minor errors
  or omissions; 1–2 = significant factual mistakes.
- *AI failure modes*: hallucinated statistics, incorrect labels, conflated concepts.

**2. Narrative Structure (15%)**
Evaluates logical flow, clear entry/exit points, and coherent story progression.
- *Behavioral anchors*: 9–10 = intuitive reading path, strong intro and conclusion;
  5–6 = structure exists but transitions are weak; 1–2 = no discernible narrative.
- *AI failure modes*: random ordering, missing connective tissue between sections.

**3. Visual Explanation (25%)**
Evaluates how effectively visuals communicate the core idea (diagrams, icons,
metaphors, data encodings).
- *Behavioral anchors*: 9–10 = visuals alone convey the message; 5–6 = visuals
  assist but text carries the load; 1–2 = visuals confuse or are decorative only.
- *AI failure modes*: generic stock-art feel, mismatched metaphors, over-cluttered
  diagrams.

**4. Typography & Legibility (20%)**
Evaluates font hierarchy, contrast, type size, and overall readability.
- *Behavioral anchors*: 9–10 = clear hierarchy, all text readable at target size;
  5–6 = mostly readable with minor issues; 1–2 = poor contrast or illegible text.
- *AI failure modes*: uniform weight with no hierarchy, low-contrast colour pairings,
  decorative fonts used for body copy.

**5. Visual Quality & Consistency (20%)**
Evaluates overall polish, colour palette coherence, icon consistency, and brand
alignment.
- *Behavioral anchors*: 9–10 = professional finish, unified visual language;
  5–6 = mostly consistent with occasional rough edges; 1–2 = inconsistent or amateurish.
- *AI failure modes*: mismatched icon styles, clashing colours, uneven padding.
"""

_JSON_SCHEMA = """
### Required JSON Output

Respond with **only** a JSON object matching this schema (no markdown fences):

```
{
  "dimensions": {
    "content_accuracy":    {"score": <int 1-10>, "evidence": "...", "improvement": "..."},
    "narrative_structure": {"score": <int 1-10>, "evidence": "...", "improvement": "..."},
    "visual_explanation":  {"score": <int 1-10>, "evidence": "...", "improvement": "..."},
    "typography":          {"score": <int 1-10>, "evidence": "...", "improvement": "..."},
    "visual_quality":      {"score": <int 1-10>, "evidence": "...", "improvement": "..."}
  },
  "prompt_fidelity": {
    "score": <int 1-10>,
    "evidence": "...",
    "improvement": "..."
  },
  "composite_score": <float — will be recalculated; provide your estimate>,
  "summary": "...",
  "strengths": ["...", "..."],
  "weaknesses": ["...", "..."]
}
```
"""


def build_rubric_prompt(scenario: dict[str, Any], panel_count: int = 1) -> str:
    """Construct the full evaluation prompt for the given scenario.

    Args:
        scenario: Scenario dict with keys ``topic``, ``audience``,
            ``style_direction``, and ``prompt``.
        panel_count: Number of panels in the infographic (>1 adds multi-panel
            consistency section).

    Returns:
        A complete evaluation prompt string ready to send to the vision model.
    """
    topic = scenario.get("topic", "")
    audience = scenario.get("audience", "")
    style_direction = scenario.get("style_direction", "")
    original_prompt = scenario.get("prompt", "")

    lines: list[str] = [
        "## Infographic Quality Evaluation",
        "",
        "You are an expert visual communication evaluator. Your task is to assess "
        "the quality of the infographic image(s) provided against the rubric below.",
        "",
        "### Scenario Context",
        f"- **Topic**: {topic}",
        f"- **Audience**: {audience}",
        f"- **Style direction**: {style_direction}",
        f"- **Panel count**: {panel_count}",
        f"- **Original brief**: {original_prompt}",
        "",
    ]

    # Multi-panel section — only when more than one panel
    if panel_count > 1:
        lines += [
            "### Multi-Panel Evaluation",
            "",
            "Because this infographic spans multiple panels, apply the following "
            "cross-panel consistency criteria in addition to the per-dimension rubric:",
            "",
            "- **Cross-panel colour coherence**: palette should be stable across panels.",
            "- **Cross-panel typographic consistency**: font choices and sizes must not "
            "shift unexpectedly.",
            "- **Cross-panel narrative continuity**: each panel must advance the story "
            "without redundancy or gaps.",
            "- **Cross-panel layout rhythm**: similar spatial grids and proportions across "
            "panels aid readability.",
            "",
        ]

    # Chain-of-thought instruction
    lines += [
        "### Evaluation Instructions",
        "",
        "Before scoring, think step by step through each dimension. For every dimension "
        "provide concrete evidence from the image and one specific improvement suggestion. "
        "Your reasoning should be observable and grounded in what is visually present.",
        "",
    ]

    lines.append(_RUBRIC_DIMENSIONS)

    # Prompt fidelity section
    lines += [
        "",
        "### Prompt Fidelity",
        "",
        "Score how closely the infographic follows the **Original brief** above "
        "(1 = completely ignored, 10 = fully realised). Note any elements from the "
        "brief that are missing or misrepresented.",
        "",
    ]

    lines.append(_JSON_SCHEMA)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Score parser / validator
# ---------------------------------------------------------------------------


def parse_scores(raw_json_str: str) -> dict[str, Any]:
    """Parse and validate the model's JSON evaluation response.

    Recalculates ``composite_score`` from dimension scores and weights —
    the model-supplied value is never trusted.

    Args:
        raw_json_str: Raw JSON string from the model.

    Returns:
        Validated and normalised evaluation dict.

    Raises:
        ValueError: If the JSON is malformed, required dimensions are missing,
            or any score is outside the valid 1–10 range.
    """
    # --- parse ---
    try:
        data: dict[str, Any] = json.loads(raw_json_str)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc}") from exc

    dimensions: dict[str, Any] = data.get("dimensions", {})

    # --- validate presence ---
    missing = REQUIRED_DIMENSIONS - set(dimensions.keys())
    if missing:
        raise ValueError(
            f"Missing dimension(s) in evaluation response: {sorted(missing)}"
        )

    # --- validate ranges and recalculate composite ---
    composite: float = 0.0
    for dim, weight in DIMENSION_WEIGHTS.items():
        score = dimensions[dim].get("score")
        if not isinstance(score, int) or score < 1 or score > 10:
            raise ValueError(
                f"Score for '{dim}' is out of range (got {score!r}; must be int 1–10)"
            )
        composite += score * weight

    # Return a normalised copy with recalculated composite
    return {
        "dimensions": dimensions,
        "prompt_fidelity": data.get("prompt_fidelity"),
        "composite_score": composite,
        "summary": data.get("summary"),
        "strengths": data.get("strengths", []),
        "weaknesses": data.get("weaknesses", []),
    }


# ---------------------------------------------------------------------------
# Image encoding helper
# ---------------------------------------------------------------------------


def _encode_image(image_path: str) -> str:
    """Base64-encode an image file for inclusion in an OpenAI vision request.

    Args:
        image_path: Filesystem path to the image.

    Returns:
        Base64-encoded string of the image bytes.
    """
    with open(image_path, "rb") as fh:
        return base64.b64encode(fh.read()).decode("utf-8")


# ---------------------------------------------------------------------------
# Async evaluation entry-point
# ---------------------------------------------------------------------------


async def evaluate_image(
    scenario: dict[str, Any],
    image_paths: list[str],
) -> dict[str, Any]:
    """Evaluate infographic image(s) using GPT-4o vision.

    Args:
        scenario: Scenario dict (topic, audience, style_direction, prompt, …).
        image_paths: Ordered list of image file paths to evaluate.

    Returns:
        Validated evaluation dict from :func:`parse_scores`.

    Raises:
        EnvironmentError: If ``OPENAI_API_KEY`` is not set.
        ValueError: If the model response cannot be parsed or validated.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "OPENAI_API_KEY environment variable is required for evaluate_image"
        )

    # Import here to avoid hard dependency at module-import time when only
    # using the prompt/parse utilities.
    from openai import AsyncOpenAI  # noqa: PLC0415

    client = AsyncOpenAI(api_key=api_key)

    panel_count = len(image_paths)
    text_prompt = build_rubric_prompt(scenario, panel_count=panel_count)

    # Build the content list: text instruction followed by each image
    content: list[dict[str, Any]] = [{"type": "text", "text": text_prompt}]
    for path in image_paths:
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
        model="gpt-4o",
        max_tokens=4096,
        temperature=0.2,
        messages=[{"role": "user", "content": content}],  # type: ignore[arg-type]
    )

    raw: str = response.choices[0].message.content or ""

    # Strip markdown code fences if the model wraps its JSON
    raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    raw = re.sub(r"\s*```$", "", raw.strip())

    return parse_scores(raw)
