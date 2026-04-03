"""Rubric-based evaluation logic for AI-generated infographics.

Provides:
- DIMENSION_WEIGHTS: weighted scoring dimensions (single-panel)
- MULTI_PANEL_DIMENSION_WEIGHTS: weighted scoring dimensions (multi-panel)
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

# Multi-panel scenarios redistribute weight to include cross-panel consistency.
# This dimension is only scored when panel_count > 1.
MULTI_PANEL_DIMENSION_WEIGHTS: dict[str, float] = {
    "content_accuracy": 0.17,
    "narrative_structure": 0.12,
    "visual_explanation": 0.22,
    "typography": 0.17,
    "visual_quality": 0.17,
    "cross_panel_consistency": 0.15,
}


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

_RUBRIC_DIMENSIONS = """
### Scoring Rubric (each dimension scored 1–5)

**1. Content Accuracy (20%)**
Evaluates factual correctness, data integrity, label accuracy, and structural
fidelity to the brief. Enumerate every visible text label and data point before
scoring — check each against the brief.
- *Behavioral anchors*:
  5 = every label, number, and concept matches the brief; no duplicates, no
    nonsensical text, no extraneous elements.
  4 = all key content present and correct; at most one minor omission or
    imprecise label that does not mislead.
  3 = most content correct but 1-2 clear errors (wrong value, missing step,
    slightly misleading claim).
  2 = multiple errors or structural problems — duplicate labels, wrong diagram
    shape, garbled text, missing key concepts from the brief.
  1 = pervasive inaccuracies — hallucinated data, fundamentally wrong structure,
    or content unrelated to the brief.
- *AI failure modes*: hallucinated statistics, incorrect labels, conflated
  concepts, duplicate labels or step numbers, nonsensical or garbled text,
  wrong diagram shape (e.g. triple loop instead of figure eight), random visual
  elements unrelated to the topic (unexplained hands, figures, objects),
  placeholder text that was never filled in.
- *Score ≤ 3 if*: any label or step number appears more than once without
  semantic reason, OR any visible text is nonsensical/garbled, OR the diagram
  shape contradicts the stated structure (e.g. "infinite loop" rendered as
  something other than a figure eight).
- *Score ≤ 2 if*: multiple items from the above list occur in the same image.

**2. Narrative Structure (15%)**
Evaluates logical flow, clear entry/exit points, and coherent story progression.
- *Behavioral anchors*: 5 = intuitive reading path, strong intro and conclusion;
  3 = structure exists but transitions are weak; 1 = no discernible narrative.
- *AI failure modes*: random ordering, missing connective tissue between sections.

**3. Visual Explanation (25%)**
Evaluates how effectively visuals communicate the core idea (diagrams, icons,
metaphors, data encodings).
- *Behavioral anchors*: 5 = visuals alone convey the message; 3 = visuals
  assist but text carries the load; 1 = visuals confuse or are decorative only.
- *AI failure modes*: generic stock-art feel, mismatched metaphors, over-cluttered
  diagrams.

**4. Typography & Legibility (20%)**
Evaluates font hierarchy, contrast, type size, and overall readability.
- *Behavioral anchors*: 5 = clear hierarchy, all text readable at target size;
  3 = mostly readable with minor issues; 1 = poor contrast or illegible text.
- *AI failure modes*: uniform weight with no hierarchy, low-contrast colour pairings,
  decorative fonts used for body copy.

**5. Visual Quality & Consistency (20% single-panel / 17% multi-panel)**
Evaluates overall polish, colour palette coherence, icon consistency, compositional
integrity, and brand alignment WITHIN each panel.
- *Behavioral anchors*:
  5 = professional finish, unified visual language, every element belongs and
    serves the composition; no artifacts, no unexplained elements.
  4 = polished with at most one minor rough edge (slight alignment issue,
    one element slightly out of place).
  3 = mostly consistent but noticeable issues — an unexplained element,
    awkward spatial composition, or inconsistent rendering in one area.
  2 = multiple compositional problems — random elements that don't belong,
    disembodied body parts, figures that break spatial logic, clashing styles
    within the same panel.
  1 = inconsistent or amateurish — no unified visual language.
- *AI failure modes*: mismatched icon styles, clashing colours, uneven padding,
  random visual artifacts (unexplained hands, floating objects, extra figures
  with no narrative purpose), unrealistic spatial arrangements (people facing
  wrong directions, physically impossible compositions), elements that look
  copy-pasted or disconnected from the scene.
- *Score ≤ 3 if*: any clearly unintended element is visible (disembodied hand,
  random figure, floating object unrelated to content).

**6. Cross-Panel Consistency (15% — multi-panel only)**
Evaluates visual consistency ACROSS panels. All panels must look like they came
from the same designer — identical border treatment, background color, typography,
accent colors, icon rendering style, divider lines, and density.
- *Behavioral anchors*: 5 = panels are visually indistinguishable in style;
  3 = same general feel but noticeable drift in 1-2 elements (e.g., border on
  one panel but not another, different icon detail level); 1 = panels look like
  separate designs — different borders, colors, rendering styles.
- *AI failure modes*: Panel 1 has no border but Panel 3 has one; icon style shifts
  from flat monochrome to multi-colored detailed; divider lines change thickness
  or color; one panel introduces colors not in the shared palette.
- *Score 1 if*: any panel has a border/frame treatment that differs from Panel 1,
  OR icon rendering style visibly changes between panels, OR new colors appear
  that weren't in Panel 1.
"""

_DIMENSION_ENTRY = (
    '    "{key}": {{"score": <int 1-5>, "evidence": "...", "improvement": "..."}}'
)


def _build_json_schema(*, multi_panel: bool) -> str:
    """Build the JSON output schema, adding cross_panel_consistency for multi-panel."""
    dims = list(DIMENSION_WEIGHTS.keys())
    if multi_panel:
        dims += [k for k in MULTI_PANEL_DIMENSION_WEIGHTS if k not in DIMENSION_WEIGHTS]
    entries = ",\n".join(_DIMENSION_ENTRY.format(key=d) for d in dims)

    note = ""
    if multi_panel:
        note = (
            "\nNote: for multi-panel infographics, "
            "`cross_panel_consistency` is REQUIRED.\n"
        )

    return f"""
### Required JSON Output

Respond with **only** a JSON object matching this schema (no markdown fences).
{note}
```
{{
  "dimensions": {{
{entries}
  }},
  "prompt_fidelity": {{
    "score": <int 1-5>,
    "evidence": "...",
    "improvement": "..."
  }},
  "composite_score": <float — will be recalculated; provide your estimate>,
  "overall_impression": "...",
  "top_strength": "...",
  "top_weakness": "...",
  "reasoning": "..."
}}
```
"""


def build_rubric_prompt(scenario: dict[str, Any], image_paths: list[str]) -> str:
    """Construct the full evaluation prompt for the given scenario.

    Args:
        scenario: Scenario dict with keys ``topic``, ``audience``,
            ``style_direction``, and ``prompt``.
        image_paths: List of image file paths to evaluate; its length
            determines the panel count (>1 adds multi-panel consistency
            section).

    Returns:
        A complete evaluation prompt string ready to send to the vision model.
    """
    panel_count = len(image_paths)
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
            "CRITICAL: This infographic spans multiple panels. You MUST compare panels "
            "against each other — not just evaluate each one in isolation. Panel 1 is "
            "the style anchor. Every subsequent panel must match Panel 1's visual system.",
            "",
            "Check these specific cross-panel dimensions (score in dimension 6):",
            "",
            "- **Border treatment**: Does every panel have the same frame/border "
            "presence? If Panel 1 has no border, no other panel should have one.",
            "- **Background**: Same shade, texture, and treatment across all panels.",
            "- **Color palette**: Same accent colors everywhere. No panel introduces "
            "colors that weren't in Panel 1.",
            "- **Icon rendering**: Same style (flat/outlined/detailed/3D) and same "
            "color treatment across all panels.",
            "- **Divider lines**: Same thickness, color, and style in every panel.",
            "- **Typography**: Same fonts, weights, and sizes for comparable hierarchy "
            "levels.",
            "- **Spacing/margins**: Consistent outer margins and internal padding.",
            "- **Rendering approach**: All panels use the same approach (all flat, all "
            "illustrated, all 3D — never mixed).",
            "",
            "Score cross_panel_consistency 1 if ANY of these drift between panels. "
            "The most common AI failure: Panel 1 is flat monochrome but a later panel "
            "introduces multi-colored icons, borders, or illustrated elements.",
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
        "(1 = completely ignored, 5 = fully realised). Note any elements from the "
        "brief that are missing or misrepresented.",
        "",
    ]

    lines.append(_build_json_schema(multi_panel=panel_count > 1))

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Score parser / validator
# ---------------------------------------------------------------------------


def parse_scores(raw_json_str: str, *, panel_count: int = 1) -> dict[str, Any]:
    """Parse and validate the model's JSON evaluation response.

    Recalculates ``composite_score`` from dimension scores and weights —
    the model-supplied value is never trusted.  For multi-panel scenarios
    (``panel_count > 1``), the ``cross_panel_consistency`` dimension is
    required and weighted at 15%.

    Args:
        raw_json_str: Raw JSON string from the model.
        panel_count: Number of panels evaluated (>1 activates multi-panel
            weights and requires ``cross_panel_consistency``).

    Returns:
        Validated and normalised evaluation dict.

    Raises:
        ValueError: If the JSON is malformed, required dimensions are missing,
            or any score is outside the valid 1–5 range.
    """
    # --- parse ---
    try:
        data: dict[str, Any] = json.loads(raw_json_str)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc}") from exc

    dimensions: dict[str, Any] = data.get("dimensions", {})

    # --- select weight set based on panel count ---
    weights = MULTI_PANEL_DIMENSION_WEIGHTS if panel_count > 1 else DIMENSION_WEIGHTS

    # --- validate presence ---
    missing = set(weights.keys()) - set(dimensions.keys())
    if missing:
        raise ValueError(
            f"Missing dimension(s) in evaluation response: {sorted(missing)}"
        )

    # --- validate ranges and recalculate composite ---
    composite: float = 0.0
    for dim, weight in weights.items():
        score = dimensions[dim].get("score")
        if not isinstance(score, int) or score < 1 or score > 5:
            raise ValueError(
                f"Score for '{dim}' is out of range (got {score!r}; must be int 1–5)"
            )
        composite += score * weight

    # Return a normalised copy with recalculated composite and spec-mandated keys
    return {
        "scores": dimensions,
        "prompt_fidelity": data.get("prompt_fidelity"),
        "composite_score": composite,
        "overall_impression": data.get("overall_impression"),
        "top_strength": data.get("top_strength"),
        "top_weakness": data.get("top_weakness"),
        "reasoning": data.get("reasoning"),
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

    text_prompt = build_rubric_prompt(scenario, image_paths)

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
        model="gpt-5.4-2026-03-05",
        max_completion_tokens=4096,
        temperature=0.2,
        messages=[{"role": "user", "content": content}],  # type: ignore[arg-type]
    )

    raw: str = response.choices[0].message.content or ""

    # Strip markdown code fences if the model wraps its JSON
    raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    raw = re.sub(r"\s*```$", "", raw.strip())

    return parse_scores(raw, panel_count=len(image_paths))
