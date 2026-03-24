# Evaluation Harness Implementation Plan

> **Execution:** Use the subagent-driven-development workflow to implement this plan.

**Goal:** Build a recipe-driven evaluation harness that scores AI-generated infographics using OpenAI vision (GPT-4o) across 5 quality dimensions, producing trend-trackable reports.

**Architecture:** A Python `eval/` package provides two modules — `rubric.py` (sends images + rubric prompt to OpenAI vision, returns structured JSON scores) and `report.py` (aggregates scored JSON into a markdown summary with baseline comparison). An Amplifier recipe (`recipes/evaluate.yaml`) orchestrates the full pipeline: generate infographics from test scenarios, evaluate each with OpenAI, produce a summary report. Test scenarios are defined in `eval/scenarios.yaml` — extracted from the existing inline recipe definitions plus 4 new Microsoft/incubation-audience scenarios.

**Tech Stack:** Python 3.11+, openai SDK, PyYAML, pytest, Amplifier recipe YAML

**Design Document:** `docs/plans/2026-03-20-evaluation-harness-design.md`

---

## Phase 1: Infrastructure & Scenarios (Tasks 1–4)

### Task 1: Create root pyproject.toml

**Files:**
- Create: `pyproject.toml`

**Context:** There is no root `pyproject.toml` yet. The only existing one is inside `modules/tool-stitch-panels/pyproject.toml` (an Amplifier module with its own package). We need a root-level project to manage the `eval/` package dependencies and pytest configuration.

**Step 1: Create `pyproject.toml`**

Create the file `pyproject.toml` at the project root with this content:

```toml
[project]
name = "infographic-eval"
version = "0.1.0"
description = "Evaluation harness for AI-generated infographic quality"
requires-python = ">=3.11"
license = { text = "MIT" }
dependencies = [
    "openai>=1.0",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = [".", "tests"]
```

> **Note on `pythonpath`:** The existing tests (e.g., `tests/test_style_guide_aesthetics.py`) use bare imports like `from helpers import read_guide`. Adding `"tests"` to `pythonpath` makes these continue to work. Adding `"."` makes `eval/` importable as a package.

**Step 2: Install the project in dev mode**

```bash
cd /Users/gurkaransingh/Desktop/Development/infographic-builder
pip install -e ".[dev]"
```

Expected: Installs successfully. The `openai`, `pyyaml`, and `pytest` packages are available.

**Step 3: Verify pytest still finds and passes existing tests**

```bash
cd /Users/gurkaransingh/Desktop/Development/infographic-builder
pytest tests/ -v
```

Expected: All existing tests pass (these are markdown structure tests that don't need any new dependencies).

**Step 4: Commit**

```bash
git add pyproject.toml && git commit -m "build: add root pyproject.toml with openai, pyyaml, pytest deps"
```

---

### Task 2: Create the eval package with `__init__.py`

**Files:**
- Create: `eval/__init__.py`

**Step 1: Create the `eval/` directory and `__init__.py`**

Create `eval/__init__.py` with this content:

```python
"""Evaluation harness for AI-generated infographic quality."""
```

**Step 2: Verify the package is importable**

```bash
cd /Users/gurkaransingh/Desktop/Development/infographic-builder
python -c "import eval; print(eval.__doc__)"
```

Expected: Prints `Evaluation harness for AI-generated infographic quality.`

**Step 3: Commit**

```bash
git add eval/__init__.py && git commit -m "feat: create eval package"
```

---

### Task 3: Add eval-results/ to .gitignore

**Files:**
- Modify: `.gitignore`

**Step 1: Append eval-results to .gitignore**

Add the following block to the end of the existing `.gitignore` file:

```gitignore

# Evaluation harness output (timestamped results directories)
eval-results/
```

The existing `.gitignore` currently ends with:

```
# OS files
.DS_Store
```

After your edit it should end with:

```
# OS files
.DS_Store

# Evaluation harness output (timestamped results directories)
eval-results/
```

**Step 2: Commit**

```bash
git add .gitignore && git commit -m "chore: add eval-results/ to .gitignore"
```

---

### Task 4: Create eval/scenarios.yaml

**Files:**
- Create: `eval/scenarios.yaml`

**Context:** The 14 existing scenarios are defined inline in two recipe files (`recipes/generate-sample-gallery.yaml` and `recipes/generate-sample-gallery-3.1-flash.yaml`). Each scenario has two fields: `name` (string) and `prompt` (multi-line string containing topic, panel count, style direction, and save path all in free-form natural language).

We extract all 14 and add 4 new Microsoft/incubation-audience scenarios. We add structured metadata fields (`topic`, `panels`, `style_direction`, `audience`) for use by the evaluation harness, while keeping the `prompt` field for generation.

> **Important:** The `prompt` field in each scenario contains a save path like `Save as ./samples/mechanical-keyboard.png`. The evaluation recipe will override this output path when generating, so the prompt's save path is the default for standalone gallery generation.

**Step 1: Create `eval/scenarios.yaml`**

Create `eval/scenarios.yaml` with this exact content:

```yaml
# =============================================================================
# Infographic Test Scenarios
# =============================================================================
#
# Shared scenario definitions for gallery generation and evaluation.
# Each scenario defines:
#   - name: unique identifier (used as directory name in eval-results/)
#   - topic: human-readable topic for evaluation context
#   - panels: number of panels expected
#   - audience: target audience description
#   - style_direction: brief style description for evaluator context
#   - prompt: full generation prompt for infographic-builder agent
#
# =============================================================================

scenarios:
  # ---------------------------------------------------------------------------
  # 1-panel scenarios
  # ---------------------------------------------------------------------------
  - name: "mechanical-keyboard"
    topic: "The Anatomy of a Mechanical Keyboard"
    panels: 1
    audience: "tech enthusiasts"
    style_direction: "dark background with RGB color accents"
    prompt: >
      Create a single-panel infographic about "The Anatomy of a Mechanical Keyboard".
      Show the key switch mechanism (spring, stem, housing), keycap layers, PCB,
      stabilizers, and plate mount. Use an exploded diagram layout. Dark background
      with RGB color accents (red, green, blue, purple). Bold sans-serif headers,
      9:16 aspect ratio.

  - name: "noise-canceling-headphones"
    topic: "How Noise-Canceling Headphones Work"
    panels: 1
    audience: "general tech audience"
    style_direction: "clean minimal, blue and gray palette"
    prompt: >
      Create a single-panel infographic about "How Noise-Canceling Headphones Work".
      Show ambient sound waves, microphone pickup, anti-phase wave generation, and
      combined output (silence). Use a horizontal flow diagram showing the wave
      cancellation process. Clean minimal style with a light gray background, blue
      and dark gray palette. 9:16 aspect ratio.

  - name: "saas-metrics-dashboard"
    topic: "Q3 2025 SaaS Metrics Dashboard"
    panels: 1
    audience: "business stakeholders, product managers"
    style_direction: "corporate navy blue and emerald green on white"
    prompt: >
      Create a single-panel infographic about "Q3 2025 SaaS Metrics Dashboard".
      Present these specific KPIs with large prominent numbers and supporting
      context: Monthly Recurring Revenue $4.2M (up 23% from Q2), Customer
      Churn Rate 2.3% (down from 3.1%), Customer Acquisition Cost $142 (target
      was $150), Net Promoter Score 72 (industry avg 41), Active Users 28,400
      (up 3,200 from Q2). Use a statistics/KPI layout with large numbers and
      icons. Clean corporate style with navy blue and emerald green on white
      background, accent gold for positive trends. 9:16 aspect ratio.

  # ---------------------------------------------------------------------------
  # 2-panel scenarios
  # ---------------------------------------------------------------------------
  - name: "developer-survey-results"
    topic: "2025 Developer Survey Results"
    panels: 2
    audience: "software engineers, engineering managers"
    style_direction: "modern tech, electric blue on dark background"
    prompt: >
      Create a 2-panel infographic about "2025 Developer Survey Results"
      presenting survey data with specific percentages and rankings.
      Panel 1 "Languages & Frameworks": Top 5 languages by usage --
      Python 68%, JavaScript 62%, TypeScript 51%, Go 29%, Rust 18%.
      Framework satisfaction scores -- React 4.1/5, Next.js 4.3/5,
      FastAPI 4.5/5, Django 3.9/5, Express 3.7/5.
      Panel 2 "Career & Compensation": Median salary by role -- Senior
      Engineer $185K, Staff Engineer $225K, Engineering Manager $210K,
      Principal Engineer $260K. Remote work breakdown -- Fully remote 42%,
      Hybrid 38%, In-office 20%. Job satisfaction 73% positive.
      Use a statistics layout with large numbers, ranking bars, and percentage
      callouts. Modern tech style with electric blue and cool gray on dark
      background, white text, clean sans-serif. 9:16 aspect ratio.

  - name: "dns"
    topic: "How DNS Works"
    panels: 2
    audience: "software engineers, networking learners"
    style_direction: "warm off-white editorial, teal and charcoal"
    prompt: >
      Create a 2-panel infographic about "How DNS Works".
      Panel 1 "The Lookup Begins": browser request, DNS resolver, root nameserver,
      TLD nameserver.
      Panel 2 "The Answer Returns": authoritative nameserver, IP address return,
      caching/TTL, browser connects.
      Warm off-white editorial style with teal and charcoal palette, golden yellow
      accents. 9:16 aspect ratio.

  - name: "campfire"
    topic: "The Science Behind a Perfect Campfire"
    panels: 2
    audience: "general audience, outdoor enthusiasts"
    style_direction: "warm illustrated, deep orange and amber on cream"
    prompt: >
      Create a 2-panel infographic about "The Science Behind a Perfect Campfire".
      Panel 1 "The Fire Triangle": fuel, heat, oxygen -- the three elements needed
      for combustion, plus best wood types (hardwood vs softwood).
      Panel 2 "Building Technique": tinder nest, kindling teepee, fuel logs,
      airflow management, and common mistakes.
      Warm illustrated style with deep orange, amber, and dark brown palette on a
      cream background. 9:16 aspect ratio.

  - name: "agile-vs-waterfall"
    topic: "Agile vs Waterfall"
    panels: 2
    audience: "engineering teams, project managers"
    style_direction: "corporate comparison, blue and green tones"
    prompt: >
      Create a 2-panel comparison infographic about "Agile vs Waterfall".
      Panel 1 "Waterfall": linear sequential phases (requirements, design,
      implementation, testing, deployment), plan-driven, heavy documentation,
      change is expensive.
      Panel 2 "Agile": iterative sprints (plan, build, test, review, repeat),
      adaptive, working software over documentation, embraces change.
      Use a clean corporate style with blue tones for Waterfall and green tones for
      Agile, light background. Side-by-side comparison layout within each panel.
      9:16 aspect ratio.

  - name: "okr-cascade"
    topic: "How OKRs Cascade from Company to Team"
    panels: 2
    audience: "product managers, engineering leads, incubation teams"
    style_direction: "clean corporate, blue gradient hierarchy"
    prompt: >
      Create a 2-panel infographic about "How OKRs Cascade from Company to Team".
      Panel 1 "Setting Direction": company-level objective, 3 key results,
      how leadership aligns on what matters most, timeframe (quarterly).
      Panel 2 "Team Alignment": how team OKRs derive from company KRs,
      example cascade (company KR to team objective to team KRs), tracking
      cadence (weekly check-ins, mid-quarter reviews), common pitfalls
      (too many OKRs, sandbagging, vanity metrics).
      Clean corporate style with a blue gradient showing hierarchy levels,
      light background, clear connecting arrows between levels. 9:16 aspect ratio.

  - name: "customer-discovery-funnel"
    topic: "Customer Discovery Funnel"
    panels: 2
    audience: "sales, marketing, product managers, incubation teams"
    style_direction: "modern funnel visualization, teal and coral"
    prompt: >
      Create a 2-panel infographic about "The Customer Discovery Funnel".
      Panel 1 "Research & Outreach": identifying target segments, cold outreach
      methods, scheduling discovery interviews, sample sizes needed (15-20
      interviews per segment), screening criteria.
      Panel 2 "Insights to Action": interview synthesis techniques (affinity
      mapping, jobs-to-be-done framework), pattern recognition, validating
      problem-solution fit, go/no-go decision criteria, pivoting vs persevering.
      Modern style with a funnel visualization narrowing from broad research
      to focused action. Teal and coral palette on white background. 9:16 aspect ratio.

  # ---------------------------------------------------------------------------
  # 3-panel scenarios
  # ---------------------------------------------------------------------------
  - name: "neural-networks"
    topic: "How Neural Networks Learn"
    panels: 3
    audience: "ML engineers, technical audience"
    style_direction: "technical diagram, gradient blues and purples on dark"
    prompt: >
      Create a 3-panel infographic about "How Neural Networks Learn".
      Panel 1 "Forward Pass": input data flows through layers (input, hidden,
      output), weights multiply signals, activation functions fire.
      Panel 2 "Backpropagation": error calculated at output, gradients flow backwards
      through the network, chain rule applies layer by layer.
      Panel 3 "Gradient Descent": weights updated to minimize loss, learning rate
      controls step size, training loop repeats until convergence.
      Technical diagram style with gradient blues and purples on a dark background,
      glowing node connections. 9:16 aspect ratio.

  - name: "surfing"
    topic: "What Happens When You Drop Into a Wave"
    panels: 3
    audience: "general audience, sports enthusiasts"
    style_direction: "vibrant ocean, deep blues and turquoise"
    prompt: >
      Create a 3-panel infographic about "What Happens When You Drop Into a Wave".
      Panel 1 "The Paddle": reading the swell, positioning in the lineup, timing
      the takeoff, catching the wave's energy.
      Panel 2 "The Pop-Up": chest push, back foot plants, front foot slides forward,
      low center of gravity, all in under 2 seconds.
      Panel 3 "The Ride": trimming the face, bottom turns, cutbacks, how wave energy
      propels the surfer.
      Vibrant ocean style with deep blues, turquoise, and white foam accents on a
      gradient blue background. Dynamic and action-oriented feel. 9:16 aspect ratio.

  - name: "incubation-lifecycle"
    topic: "The Incubation Lifecycle: Idea to Funded Product"
    panels: 3
    audience: "incubation teams, startup founders, product leaders"
    style_direction: "startup journey, warm gradient progression"
    prompt: >
      Create a 3-panel infographic about "The Incubation Lifecycle: Idea to Funded Product".
      Panel 1 "Ideation & Validation": problem identification, customer interviews,
      competitive landscape, lean canvas, hypothesis formation, kill criteria.
      Panel 2 "Build & Measure": MVP definition, rapid prototyping, early adopter
      acquisition, key metrics (engagement, retention, NPS), iteration cycles,
      pivot-or-persevere decisions.
      Panel 3 "Scale & Fund": product-market fit signals, growth metrics that
      matter (CAC/LTV, month-over-month growth), pitch deck essentials, funding
      stages (seed to Series A), team scaling, graduation criteria.
      Warm gradient style progressing from seed/earth tones (ideation) to vibrant
      greens (growth) to bold blues (scale). Light background. 9:16 aspect ratio.

  - name: "cicd-pipeline"
    topic: "How a CI/CD Pipeline Works"
    panels: 3
    audience: "software engineers, DevOps teams"
    style_direction: "technical pipeline, dark background with green/blue flow"
    prompt: >
      Create a 3-panel infographic about "How a CI/CD Pipeline Works".
      Panel 1 "Continuous Integration": developer pushes code, automated build
      triggers, unit tests run, linting and static analysis, build artifacts
      created, fast feedback loop (under 10 minutes).
      Panel 2 "Continuous Delivery": artifact promotion, integration tests,
      staging environment deployment, smoke tests, manual approval gate,
      release candidate ready.
      Panel 3 "Continuous Deployment": automated production deploy, canary
      rollout (5% to 25% to 100%), health checks, automated rollback on failure,
      monitoring and alerting, deployment metrics (DORA four keys).
      Technical pipeline style with dark background, green and blue flow arrows
      showing progression, status indicators (pass/fail). 9:16 aspect ratio.

  # ---------------------------------------------------------------------------
  # 4-panel scenarios
  # ---------------------------------------------------------------------------
  - name: "llm-pipeline"
    topic: "The LLM Training Pipeline"
    panels: 4
    audience: "ML engineers, AI researchers"
    style_direction: "dark navy neon, electric blue and cyan accents"
    prompt: >
      Create a 4-panel infographic about "The LLM Training Pipeline".
      Panel 1 "Pre-training": next-token prediction on trillions of tokens,
      self-supervised, thousands of GPUs, costs $2M-$100M+.
      Panel 2 "Supervised Fine-Tuning": 10K-100K instruction-response pairs, human
      expert annotators, task alignment.
      Panel 3 "RLHF & Alignment": human preference ranking, reward model training,
      PPO optimization loop, goal of helpful/harmless/honest.
      Panel 4 "Evaluation & Deployment": benchmarks (MMLU, HumanEval), red-teaming,
      API serving, monitoring, continuous feedback.
      Dark navy neon style with electric blue, cyan, purple accents and amber
      highlights. 9:16 aspect ratio.

  - name: "song-to-spotify"
    topic: "How a Song Goes from Idea to Spotify"
    panels: 4
    audience: "general audience, music creators"
    style_direction: "creative music, warm purple and gold on dark"
    prompt: >
      Create a 4-panel infographic about "How a Song Goes from Idea to Spotify".
      Panel 1 "Songwriting": melody creation, lyric writing, chord progressions,
      demo recording.
      Panel 2 "Recording": studio session, instrument tracking, vocal takes,
      DAW editing.
      Panel 3 "Mixing & Mastering": EQ balancing, compression, spatial effects,
      loudness optimization for streaming.
      Panel 4 "Distribution": digital aggregators (DistroKid, TuneCore), streaming
      platform delivery, royalty splits, playlist placement.
      Creative music style with warm purple and gold palette on a dark background,
      vinyl/waveform visual motifs. 9:16 aspect ratio.

  # ---------------------------------------------------------------------------
  # 5-panel scenarios
  # ---------------------------------------------------------------------------
  - name: "ai-everyday-life"
    topic: "AI in Everyday Life"
    panels: 5
    audience: "general audience, non-technical"
    style_direction: "friendly modern, bright blues and greens on white"
    prompt: >
      Create a 5-panel infographic about "AI in Everyday Life".
      Panel 1 "Recommendations": Netflix, Spotify, shopping algorithms,
      collaborative filtering and content-based matching.
      Panel 2 "Voice Assistants": speech recognition, natural language understanding,
      intent classification, response generation.
      Panel 3 "Navigation": real-time traffic prediction, route optimization, ETA
      estimation, map data fusion.
      Panel 4 "Healthcare": medical imaging analysis, drug discovery acceleration,
      clinical decision support.
      Panel 5 "Creative Tools": image generation, writing assistants, code
      completion, music composition.
      Friendly modern style with bright blues and greens on a white background,
      rounded icons, approachable feel. 9:16 aspect ratio.

  - name: "coffee-bean"
    topic: "The Life of a Coffee Bean"
    panels: 5
    audience: "general audience, food enthusiasts"
    style_direction: "warm earthy, rich browns and cream"
    prompt: >
      Create a 5-panel infographic about "The Life of a Coffee Bean".
      Panel 1 "Growing": coffee belt regions, cherry development on the branch,
      altitude and shade impact on flavor.
      Panel 2 "Harvesting & Processing": hand-picking vs strip-picking, washed vs
      natural vs honey processing methods.
      Panel 3 "Roasting": green bean transformation, Maillard reaction, first crack,
      roast profiles (light/medium/dark).
      Panel 4 "Brewing": grind size spectrum, water temperature, extraction time,
      brew methods (espresso, pour-over, French press).
      Panel 5 "The Cup": flavor wheel, tasting notes (acidity, body, sweetness),
      single-origin vs blend characteristics.
      Warm earthy style with rich browns, cream, and forest greens on a light
      parchment background, illustrated feel. 9:16 aspect ratio.

  # ---------------------------------------------------------------------------
  # 6-panel scenarios
  # ---------------------------------------------------------------------------
  - name: "history-of-internet"
    topic: "History of the Internet"
    panels: 6
    audience: "general audience, tech history enthusiasts"
    style_direction: "timeline with retro-to-modern color progression"
    prompt: >
      Create a 6-panel infographic about "History of the Internet".
      Panel 1 "ARPANET (1960s-70s)": packet switching invention, first 4 nodes,
      military origins.
      Panel 2 "Protocols & Email (1980s)": TCP/IP standardization, SMTP email, DNS
      introduced, NSFNet backbone.
      Panel 3 "The World Wide Web (1990s)": Tim Berners-Lee, HTML/HTTP,
      Mosaic/Netscape browsers, dotcom boom.
      Panel 4 "Web 2.0 (2000s)": social media explosion, user-generated content,
      Ajax/dynamic web, Google/Facebook/YouTube.
      Panel 5 "Mobile & Cloud (2010s)": smartphone revolution, app economy,
      AWS/cloud computing, streaming services.
      Panel 6 "AI & Beyond (2020s)": large language models, edge computing, IoT,
      decentralized web.
      Timeline style with a retro-to-modern color progression, muted greens/ambers
      in early panels transitioning to vibrant blues/purples in later panels.
      9:16 aspect ratio.
```

**Step 2: Verify the YAML is valid**

```bash
cd /Users/gurkaransingh/Desktop/Development/infographic-builder
python -c "import yaml; data = yaml.safe_load(open('eval/scenarios.yaml')); print(f'{len(data[\"scenarios\"])} scenarios loaded'); print([s['name'] for s in data['scenarios']])"
```

Expected: `18 scenarios loaded` and a list of all 18 scenario names.

**Step 3: Commit**

```bash
git add eval/scenarios.yaml && git commit -m "feat: create shared scenarios.yaml with 14 existing + 4 new Microsoft/incubation scenarios"
```

---

## Phase 2: Core Evaluation Logic (Tasks 5–9)

### Task 5: Write tests for score parsing in rubric.py

**Files:**
- Create: `tests/test_rubric.py`

**Context:** We're testing the rubric module's ability to parse the JSON response from OpenAI into a structured result. We'll mock the OpenAI API call in tests -- no real API calls during testing. The rubric module will have two key functions: `build_rubric_prompt(scenario, image_paths)` that constructs the evaluation prompt, and `parse_scores(raw_json_str)` that validates and parses the model's JSON response. We test `parse_scores` first.

**Step 1: Create `tests/test_rubric.py`**

```python
"""Tests for eval/rubric.py -- score parsing and prompt construction."""

import json

import pytest

from eval.rubric import parse_scores, build_rubric_prompt, DIMENSION_WEIGHTS


# ---------------------------------------------------------------------------
# Fixtures: well-formed and malformed evaluator responses
# ---------------------------------------------------------------------------

VALID_RESPONSE = {
    "reasoning": "The infographic shows a clear DNS lookup flow...",
    "scores": {
        "content_accuracy": {
            "score": 4,
            "evidence": "All DNS steps are present and correctly ordered.",
            "improvement": "Could mention DNSSEC.",
        },
        "narrative_structure": {
            "score": 3,
            "evidence": "Clear reading path, logical progression.",
            "improvement": "Transitions between panels could be smoother.",
        },
        "visual_explanation": {
            "score": 4,
            "evidence": "Arrows show flow effectively.",
            "improvement": "Could use spatial layout to show recursion.",
        },
        "typography": {
            "score": 3,
            "evidence": "Most text readable, minor artifacts.",
            "improvement": "Some labels are slightly blurry.",
        },
        "visual_quality": {
            "score": 4,
            "evidence": "Consistent palette, polished look.",
            "improvement": "Minor whitespace imbalance in panel 2.",
        },
    },
    "prompt_fidelity": {
        "score": 5,
        "notes": "Correct topic, panel count, and style direction.",
    },
    "composite_score": 3.75,
    "overall_impression": "A solid, functional DNS explainer.",
    "top_strength": "Visual flow clearly shows the DNS resolution path.",
    "top_weakness": "Minor text rendering artifacts reduce legibility.",
}


# ---------------------------------------------------------------------------
# parse_scores: happy path
# ---------------------------------------------------------------------------


def test_parse_scores_returns_all_dimension_scores():
    """parse_scores extracts a score (int 1-5) for each of the 5 dimensions."""
    result = parse_scores(json.dumps(VALID_RESPONSE))
    assert set(result["scores"].keys()) == {
        "content_accuracy",
        "narrative_structure",
        "visual_explanation",
        "typography",
        "visual_quality",
    }
    for dim in result["scores"].values():
        assert isinstance(dim["score"], int)
        assert 1 <= dim["score"] <= 5


def test_parse_scores_includes_evidence_and_improvement():
    """Each dimension must have 'evidence' and 'improvement' strings."""
    result = parse_scores(json.dumps(VALID_RESPONSE))
    for dim_name, dim in result["scores"].items():
        assert "evidence" in dim, f"Missing 'evidence' in {dim_name}"
        assert "improvement" in dim, f"Missing 'improvement' in {dim_name}"
        assert isinstance(dim["evidence"], str)
        assert isinstance(dim["improvement"], str)


def test_parse_scores_includes_composite():
    """parse_scores must include the composite_score as a float."""
    result = parse_scores(json.dumps(VALID_RESPONSE))
    assert isinstance(result["composite_score"], float)


def test_parse_scores_includes_prompt_fidelity():
    """Prompt fidelity is tracked separately with score and notes."""
    result = parse_scores(json.dumps(VALID_RESPONSE))
    assert "prompt_fidelity" in result
    assert isinstance(result["prompt_fidelity"]["score"], int)


def test_parse_scores_includes_summary_fields():
    """Must include overall_impression, top_strength, top_weakness."""
    result = parse_scores(json.dumps(VALID_RESPONSE))
    assert isinstance(result["overall_impression"], str)
    assert isinstance(result["top_strength"], str)
    assert isinstance(result["top_weakness"], str)


# ---------------------------------------------------------------------------
# parse_scores: recalculates composite from dimension scores
# ---------------------------------------------------------------------------


def test_parse_scores_recalculates_composite():
    """Composite must be recalculated from dimension scores, not trusted from model."""
    result = parse_scores(json.dumps(VALID_RESPONSE))
    expected = (
        4 * 0.20  # content_accuracy
        + 3 * 0.15  # narrative_structure
        + 4 * 0.25  # visual_explanation
        + 3 * 0.20  # typography
        + 4 * 0.20  # visual_quality
    )
    assert result["composite_score"] == pytest.approx(expected, abs=0.01)


# ---------------------------------------------------------------------------
# parse_scores: error handling
# ---------------------------------------------------------------------------


def test_parse_scores_rejects_invalid_json():
    """parse_scores raises ValueError on non-JSON input."""
    with pytest.raises(ValueError, match="Invalid JSON"):
        parse_scores("this is not json")


def test_parse_scores_rejects_missing_dimensions():
    """parse_scores raises ValueError if any dimension is missing."""
    bad = {
        **VALID_RESPONSE,
        "scores": {
            "content_accuracy": VALID_RESPONSE["scores"]["content_accuracy"],
        },
    }
    with pytest.raises(ValueError, match="Missing.*dimension"):
        parse_scores(json.dumps(bad))


def test_parse_scores_rejects_out_of_range_score():
    """Scores outside 1-5 must be rejected."""
    bad = json.loads(json.dumps(VALID_RESPONSE))
    bad["scores"]["content_accuracy"]["score"] = 6
    with pytest.raises(ValueError, match="out of range"):
        parse_scores(json.dumps(bad))


# ---------------------------------------------------------------------------
# DIMENSION_WEIGHTS: must match design doc formula
# ---------------------------------------------------------------------------


def test_dimension_weights_sum_to_one():
    """Weights must sum to 1.0."""
    assert sum(DIMENSION_WEIGHTS.values()) == pytest.approx(1.0)


def test_dimension_weights_match_design():
    """Weights must match the design document formula."""
    assert DIMENSION_WEIGHTS == {
        "content_accuracy": 0.20,
        "narrative_structure": 0.15,
        "visual_explanation": 0.25,
        "typography": 0.20,
        "visual_quality": 0.20,
    }


# ---------------------------------------------------------------------------
# build_rubric_prompt: structure checks
# ---------------------------------------------------------------------------


def test_build_rubric_prompt_contains_all_dimensions():
    """Prompt must mention all 5 dimension names."""
    scenario = {
        "name": "dns",
        "topic": "How DNS Works",
        "panels": 2,
        "audience": "engineers",
    }
    prompt = build_rubric_prompt(scenario, ["panel_1.png", "panel_2.png"])
    for dimension in [
        "Content Accuracy",
        "Narrative Structure",
        "Visual Explanation",
        "Typography",
        "Visual Quality",
    ]:
        assert dimension in prompt, f"Prompt missing dimension: {dimension}"


def test_build_rubric_prompt_contains_scenario_context():
    """Prompt must include the scenario topic and audience."""
    scenario = {
        "name": "dns",
        "topic": "How DNS Works",
        "panels": 2,
        "audience": "engineers",
    }
    prompt = build_rubric_prompt(scenario, ["panel_1.png"])
    assert "How DNS Works" in prompt
    assert "engineers" in prompt


def test_build_rubric_prompt_contains_json_instruction():
    """Prompt must instruct the model to output JSON."""
    scenario = {
        "name": "dns",
        "topic": "How DNS Works",
        "panels": 2,
        "audience": "engineers",
    }
    prompt = build_rubric_prompt(scenario, ["panel_1.png"])
    assert "JSON" in prompt


def test_build_rubric_prompt_contains_chain_of_thought_instruction():
    """Prompt must instruct reasoning before scoring."""
    scenario = {
        "name": "dns",
        "topic": "How DNS Works",
        "panels": 2,
        "audience": "engineers",
    }
    prompt = build_rubric_prompt(scenario, ["panel_1.png"])
    assert "reason" in prompt.lower() or "reasoning" in prompt.lower()


# ---------------------------------------------------------------------------
# build_rubric_prompt: multi-panel evaluation instruction
# ---------------------------------------------------------------------------


def test_build_rubric_prompt_includes_multi_panel_instruction():
    """Multi-panel scenarios must include the cross-panel consistency instruction."""
    scenario = {
        "name": "neural-networks",
        "topic": "How Neural Networks Learn",
        "panels": 3,
        "audience": "ML engineers",
    }
    prompt = build_rubric_prompt(
        scenario, ["panel_1.png", "panel_2.png", "panel_3.png"]
    )
    assert "Multi-Panel Evaluation" in prompt
    assert "cross-panel" in prompt.lower()


def test_build_rubric_prompt_excludes_multi_panel_instruction_for_single_panel():
    """Single-panel scenarios must NOT include the multi-panel instruction."""
    scenario = {
        "name": "mechanical-keyboard",
        "topic": "The Anatomy of a Mechanical Keyboard",
        "panels": 1,
        "audience": "tech enthusiasts",
    }
    prompt = build_rubric_prompt(scenario, ["panel_1.png"])
    assert "Multi-Panel Evaluation" not in prompt
```

**Step 2: Run tests to verify they fail**

```bash
cd /Users/gurkaransingh/Desktop/Development/infographic-builder
pytest tests/test_rubric.py -v 2>&1 | head -30
```

Expected: All tests FAIL with `ModuleNotFoundError: No module named 'eval.rubric'` (the module doesn't exist yet).

**Step 3: Commit**

```bash
git add tests/test_rubric.py && git commit -m "test: add rubric module tests (red phase)"
```

---

### Task 6: Implement eval/rubric.py -- parse_scores and build_rubric_prompt

**Files:**
- Create: `eval/rubric.py`

**Context:** This module has three responsibilities:
1. `DIMENSION_WEIGHTS` -- constant dict with the 5 dimension weights from the design doc
2. `build_rubric_prompt(scenario, image_paths)` -- constructs the full evaluation prompt with all anchors from the design doc
3. `parse_scores(raw_json_str)` -- validates and parses the model's JSON response, recalculates composite
4. `evaluate_image(scenario, image_paths)` -- calls OpenAI vision API with the rubric prompt (tested in integration, not unit tests)

The full rubric prompt is specified in the design document (`docs/plans/2026-03-20-evaluation-harness-design.md`). Copy all the behavioral anchors and AI failure modes from that document into the prompt template.

**Step 1: Create `eval/rubric.py`**

```python
"""Evaluation rubric for AI-generated infographics.

Sends infographic images to OpenAI GPT-4o vision with a structured rubric
prompt and returns parsed quality scores across 5 dimensions.
"""

import base64
import json
import os
from pathlib import Path
from typing import Any


DIMENSION_WEIGHTS: dict[str, float] = {
    "content_accuracy": 0.20,
    "narrative_structure": 0.15,
    "visual_explanation": 0.25,
    "typography": 0.20,
    "visual_quality": 0.20,
}

REQUIRED_DIMENSIONS = set(DIMENSION_WEIGHTS.keys())


def build_rubric_prompt(scenario: dict[str, Any], image_paths: list[str]) -> str:
    """Build the full evaluation prompt with rubric anchors and scenario context.

    Args:
        scenario: Dict with keys: name, topic, panels, audience, style_direction.
        image_paths: List of image file paths being evaluated.

    Returns:
        The complete prompt string to send to the evaluator model.
    """
    panel_desc = (
        f"multi-panel infographic ({scenario['panels']} panels)"
        if scenario["panels"] > 1
        else "single-panel infographic"
    )

    multi_panel_instruction = ""
    if scenario["panels"] > 1:
        multi_panel_instruction = """

## Multi-Panel Evaluation

This is a multi-panel infographic series. In addition to evaluating each panel's individual quality, pay special attention to CROSS-PANEL CONSISTENCY:
- Do all panels share the same icon style and illustration approach?
- Is the color palette consistent across panels (same colors mean the same things)?
- Is typography consistent (same fonts, sizes, weights for equivalent elements)?
- Do panels share consistent spacing rhythm and visual chrome (headers, footers, panel numbering)?
- Does the series feel like a cohesive set, or do panels look like they were designed independently?

Score Dimension 5 (Visual Quality & Consistency) with heavy emphasis on cross-panel coherence. Style drift between panels should significantly lower the score.
"""

    return f"""You are an expert infographic evaluator. You will assess the quality of an AI-generated {panel_desc}.

## Context
- **Topic:** {scenario['topic']}
- **Target audience:** {scenario.get('audience', 'general')}
- **Style direction:** {scenario.get('style_direction', 'not specified')}
- **Panel count:** {scenario['panels']}
- **Images provided:** {len(image_paths)}
{multi_panel_instruction}
## Instructions

First, REASON through your observations about the infographic. Examine each dimension carefully, noting specific evidence. Only AFTER thorough reasoning, assign scores.

## Rubric -- 5 Dimensions (1-5 scale)

### Dimension 1: Content Accuracy (20%)
Does the infographic teach the right things?

| Score | Anchor |
|-------|--------|
| 1 | Major factual errors or critical content missing entirely. A viewer would learn something wrong. |
| 2 | Core concept present but significant errors or gaps. A knowledgeable viewer spots multiple problems. |
| 3 | Core content accurate with minor omissions. Viewer learns the right general picture. |
| 4 | Accurate and appropriately complete for the target audience. No detectable errors. |
| 5 | Comprehensive and precise. Could pass expert review. Appropriate depth -- neither oversimplified nor overwhelming. |

AI failure modes: Hallucinated content (fabricated steps, invented statistics), counting errors (prompt says N steps but infographic shows different count), reversed relationships (arrows pointing wrong direction, cause/effect swapped), contradictory text between sections.

### Dimension 2: Narrative Structure (15%)
Does the explanation build logically with a clear reading path?

| Score | Anchor |
|-------|--------|
| 1 | No discernible reading path. Content feels randomly placed. Viewer can't determine where to start. |
| 2 | Some structure exists but logical flow breaks down -- concepts introduced after they're needed, ambiguous entry point. |
| 3 | Clear reading path with logical progression. Sections are distinguishable. Entry and exit points are identifiable. |
| 4 | Effective progressive disclosure -- simpler concepts precede complex ones. Information chunked into manageable groups. Transitions feel natural. |
| 5 | Masterful sequencing that makes a complex concept feel intuitive. Clear narrative arc. Viewer arrives at understanding feeling it was obvious. |

AI failure modes: Duplicate sections, arbitrary content boundaries between panels, missing transitions between steps.

### Dimension 3: Visual Explanation (25%)
Do the visuals make the concept more understandable than text alone?

| Score | Anchor |
|-------|--------|
| 1 | Visuals are purely decorative. Icons have no meaningful relationship to concepts. This is styled text, not a visual explanation. |
| 2 | Visual encoding attempted but ineffective. Generic clipart next to text, spatial relationships don't reflect conceptual relationships. |
| 3 | Visuals generally support content. Arrows show flow, grouping shows relatedness, icons are recognizable. Adds some value beyond text. |
| 4 | Visual metaphors actively enhance understanding. Relationships encoded visually, not just textually. Viewer grasps the high-level concept from visuals alone. |
| 5 | Visual language deeply integrated with content, creating "aha moments." Complex relationships made intuitive through metaphor or spatial logic. Memorable. |

AI failure modes: Decorative elements that look semantic but aren't, generic iconography, arrows that lead nowhere, spatial relationship errors.

### Dimension 4: Typography & Legibility (20%)
Can you read it, and does the text hierarchy guide attention?

| Score | Anchor |
|-------|--------|
| 1 | Text largely unreadable. Extensive garbling, overlapping elements, or illegible sizing. Infographic is functionally useless. |
| 2 | Some text readable but >25% is garbled, malformed, or illegible. Partial information extractable. |
| 3 | Most text (~80%+) readable with clear hierarchy. Minor rendering artifacts -- occasional garbled word, slightly fuzzy characters. |
| 4 | All text clean and readable. Strong typographic hierarchy guides the eye. Good contrast. No rendering artifacts. |
| 5 | Typography is a design strength. Hierarchy perfectly calibrated. Every label crisp. Text sizing and placement actively guide the reading experience. |

AI failure modes: Character-level garbling, word-level nonsense, overlapping text, inconsistent rendering quality across regions, size hierarchy collapse.

### Dimension 5: Visual Quality & Consistency (20%)
Is it polished, appealing, and visually coherent throughout?

| Score | Anchor |
|-------|--------|
| 1 | Visually chaotic -- clashing colors, mixed styles, no whitespace management. For multi-panel: panels look like different infographics. |
| 2 | Below professional standard. Weak color choices, inconsistent icon styles, unbalanced composition. Dated design patterns: heavy drop shadows, gratuitous gradients, glassmorphism, stock-illustration corporate aesthetic. |
| 3 | Clean and professional enough. Reasonable palette, consistent enough visual language. No major missteps. |
| 4 | Polished and appealing. Harmonious palette, consistent iconography and spacing. Strong visual system throughout. Modern, confident design language. Multi-panel: clearly the same series. |
| 5 | Distinctively beautiful with perfect coherence. Single unified design artifact. Color, composition, and visual rhythm create an aesthetically rewarding experience. Multi-panel: panels indistinguishable in style. |

AI failure modes: Style drift across panels, visual artifacts, style collisions (3D objects on 2D backgrounds), background inconsistency between panels, design era regression.

### Prompt Fidelity (tracked separately)
Did the output match what was requested? Correct topic, scope, style direction, number of panels.

## Required JSON Output

Respond with ONLY valid JSON in this exact format (no markdown fences, no extra text):

{{"reasoning": "<your detailed observations and analysis BEFORE scoring>", "scores": {{"content_accuracy": {{"score": "<1-5>", "evidence": "<specific observations>", "improvement": "<actionable suggestion>"}}, "narrative_structure": {{"score": "<1-5>", "evidence": "<specific observations>", "improvement": "<actionable suggestion>"}}, "visual_explanation": {{"score": "<1-5>", "evidence": "<specific observations>", "improvement": "<actionable suggestion>"}}, "typography": {{"score": "<1-5>", "evidence": "<specific observations>", "improvement": "<actionable suggestion>"}}, "visual_quality": {{"score": "<1-5>", "evidence": "<specific observations>", "improvement": "<actionable suggestion>"}}}}, "prompt_fidelity": {{"score": "<1-5>", "notes": "<how well it matched the request>"}}, "composite_score": "<weighted average as float>", "overall_impression": "<2-3 sentence summary>", "top_strength": "<single strongest aspect>", "top_weakness": "<single most impactful weakness>"}}"""


def parse_scores(raw_json_str: str) -> dict[str, Any]:
    """Parse and validate the evaluator model's JSON response.

    Recalculates the composite score from dimension scores rather than
    trusting the model's calculation.

    Args:
        raw_json_str: Raw JSON string from the evaluator model.

    Returns:
        Validated and normalized result dict.

    Raises:
        ValueError: If JSON is invalid, dimensions are missing, or scores are out of range.
    """
    try:
        data = json.loads(raw_json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from evaluator: {e}") from e

    # Validate all dimensions present
    if "scores" not in data:
        raise ValueError("Missing 'scores' key in evaluator response")

    present = set(data["scores"].keys())
    missing = REQUIRED_DIMENSIONS - present
    if missing:
        raise ValueError(f"Missing dimension(s) in evaluator response: {missing}")

    # Validate score ranges
    for dim_name, dim_data in data["scores"].items():
        score = dim_data.get("score")
        if not isinstance(score, int) or score < 1 or score > 5:
            raise ValueError(
                f"Score for '{dim_name}' is out of range (must be 1-5, got {score})"
            )

    # Recalculate composite from actual dimension scores
    composite = sum(
        data["scores"][dim]["score"] * weight
        for dim, weight in DIMENSION_WEIGHTS.items()
    )

    return {
        "scores": data["scores"],
        "prompt_fidelity": data.get(
            "prompt_fidelity", {"score": 0, "notes": "not provided"}
        ),
        "composite_score": round(composite, 2),
        "overall_impression": data.get("overall_impression", ""),
        "top_strength": data.get("top_strength", ""),
        "top_weakness": data.get("top_weakness", ""),
        "reasoning": data.get("reasoning", ""),
    }


def _encode_image(image_path: str) -> str:
    """Base64-encode an image file for the OpenAI API."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


async def evaluate_image(
    scenario: dict[str, Any],
    image_paths: list[str],
) -> dict[str, Any]:
    """Evaluate infographic image(s) using OpenAI GPT-4o vision.

    Args:
        scenario: Scenario dict with topic, panels, audience, etc.
        image_paths: Paths to the panel images to evaluate.

    Returns:
        Parsed and validated score dict.

    Raises:
        ValueError: If the model response can't be parsed.
        RuntimeError: If the OpenAI API call fails.
    """
    from openai import AsyncOpenAI

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set")

    client = AsyncOpenAI(api_key=api_key)
    prompt = build_rubric_prompt(scenario, image_paths)

    # Build message content: text prompt + image(s)
    content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
    for img_path in image_paths:
        b64 = _encode_image(img_path)
        suffix = Path(img_path).suffix.lstrip(".")
        mime = f"image/{suffix}" if suffix != "jpg" else "image/jpeg"
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{b64}"},
            }
        )

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": content}],
        max_tokens=4096,
        temperature=0.2,
    )

    raw = response.choices[0].message.content
    if not raw:
        raise RuntimeError("Empty response from OpenAI evaluator")

    # Strip markdown fences if the model wraps output in ```json ... ```
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1]  # remove ```json line
    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("```", 1)[0]
    cleaned = cleaned.strip()

    return parse_scores(cleaned)
```

**Step 2: Run the tests**

```bash
cd /Users/gurkaransingh/Desktop/Development/infographic-builder
pytest tests/test_rubric.py -v
```

Expected: All tests PASS.

**Step 3: Run the linter**

```bash
cd /Users/gurkaransingh/Desktop/Development/infographic-builder
ruff check eval/rubric.py && ruff format --check eval/rubric.py
```

Expected: No issues. If there are formatting issues, run `ruff format eval/rubric.py` to fix them.

**Step 4: Commit**

```bash
git add eval/rubric.py && git commit -m "feat: implement rubric module with prompt builder, score parser, and OpenAI vision evaluator"
```

---

### Task 7: Write tests for report.py

**Files:**
- Create: `tests/test_report.py`

**Context:** The report module takes a directory of scored JSON files (one per scenario), aggregates them, and produces a markdown summary. It optionally compares against a previous baseline directory to show trends. We test with fixture data -- no API calls, no filesystem needed (we'll pass dicts directly).

**Step 1: Create `tests/test_report.py`**

```python
"""Tests for eval/report.py -- score aggregation and markdown report generation."""

import pytest

from eval.report import aggregate_scores, generate_markdown_report, interpret_band


# ---------------------------------------------------------------------------
# Fixtures: scored scenario results
# ---------------------------------------------------------------------------

SCENARIO_SCORES = [
    {
        "scenario_name": "dns",
        "scores": {
            "content_accuracy": {"score": 4, "evidence": "...", "improvement": "..."},
            "narrative_structure": {"score": 3, "evidence": "...", "improvement": "..."},
            "visual_explanation": {"score": 4, "evidence": "...", "improvement": "..."},
            "typography": {"score": 3, "evidence": "...", "improvement": "..."},
            "visual_quality": {"score": 4, "evidence": "...", "improvement": "..."},
        },
        "composite_score": 3.75,
        "prompt_fidelity": {"score": 5, "notes": "..."},
        "top_strength": "Clear flow diagram.",
        "top_weakness": "Minor text artifacts.",
        "overall_impression": "Solid DNS explainer.",
        "reasoning": "...",
    },
    {
        "scenario_name": "neural-networks",
        "scores": {
            "content_accuracy": {"score": 3, "evidence": "...", "improvement": "..."},
            "narrative_structure": {"score": 4, "evidence": "...", "improvement": "..."},
            "visual_explanation": {"score": 3, "evidence": "...", "improvement": "..."},
            "typography": {"score": 2, "evidence": "...", "improvement": "..."},
            "visual_quality": {"score": 3, "evidence": "...", "improvement": "..."},
        },
        "composite_score": 2.95,
        "prompt_fidelity": {"score": 4, "notes": "..."},
        "top_strength": "Good logical flow.",
        "top_weakness": "Text garbling in panel 2.",
        "overall_impression": "Decent but legibility hurts it.",
        "reasoning": "...",
    },
]


# ---------------------------------------------------------------------------
# aggregate_scores
# ---------------------------------------------------------------------------


def test_aggregate_scores_computes_mean_composite():
    """Aggregate must compute mean composite across all scenarios."""
    agg = aggregate_scores(SCENARIO_SCORES)
    expected = (3.75 + 2.95) / 2
    assert agg["mean_composite"] == pytest.approx(expected, abs=0.01)


def test_aggregate_scores_computes_dimension_averages():
    """Aggregate must compute per-dimension averages."""
    agg = aggregate_scores(SCENARIO_SCORES)
    assert agg["dimension_averages"]["content_accuracy"] == pytest.approx(3.5)
    assert agg["dimension_averages"]["typography"] == pytest.approx(2.5)


def test_aggregate_scores_includes_scenario_count():
    """Aggregate must report the number of scenarios evaluated."""
    agg = aggregate_scores(SCENARIO_SCORES)
    assert agg["scenario_count"] == 2


def test_aggregate_scores_finds_best_and_worst():
    """Aggregate must identify best and worst scoring scenarios."""
    agg = aggregate_scores(SCENARIO_SCORES)
    assert agg["best_scenario"] == "dns"
    assert agg["worst_scenario"] == "neural-networks"


# ---------------------------------------------------------------------------
# interpret_band
# ---------------------------------------------------------------------------


def test_interpret_band_high_quality():
    assert interpret_band(4.2) == "High quality"


def test_interpret_band_acceptable():
    assert interpret_band(3.5) == "Acceptable"


def test_interpret_band_below_bar():
    assert interpret_band(2.5) == "Below bar"


def test_interpret_band_failed():
    assert interpret_band(1.5) == "Failed"


# ---------------------------------------------------------------------------
# generate_markdown_report: structure checks
# ---------------------------------------------------------------------------


def test_report_contains_composite_scores():
    """Report markdown must include composite scores for each scenario."""
    report = generate_markdown_report(SCENARIO_SCORES)
    assert "3.75" in report
    assert "2.95" in report


def test_report_contains_scenario_names():
    """Report must list each scenario by name."""
    report = generate_markdown_report(SCENARIO_SCORES)
    assert "dns" in report
    assert "neural-networks" in report


def test_report_contains_dimension_averages():
    """Report must include per-dimension averages."""
    report = generate_markdown_report(SCENARIO_SCORES)
    assert "Dimension Averages" in report or "dimension" in report.lower()


def test_report_contains_interpretive_band():
    """Report must show the interpretive band for the overall score."""
    report = generate_markdown_report(SCENARIO_SCORES)
    # Mean composite is 3.35, which is "Acceptable"
    assert "Acceptable" in report


# ---------------------------------------------------------------------------
# generate_markdown_report: baseline comparison
# ---------------------------------------------------------------------------


def test_report_with_baseline_shows_trends():
    """When a baseline is provided, report must show delta indicators."""
    baseline = [
        {
            "scenario_name": "dns",
            "composite_score": 3.0,
            "scores": {
                "content_accuracy": {"score": 3, "evidence": "...", "improvement": "..."},
                "narrative_structure": {"score": 3, "evidence": "...", "improvement": "..."},
                "visual_explanation": {"score": 3, "evidence": "...", "improvement": "..."},
                "typography": {"score": 3, "evidence": "...", "improvement": "..."},
                "visual_quality": {"score": 3, "evidence": "...", "improvement": "..."},
            },
            "prompt_fidelity": {"score": 4, "notes": "..."},
            "top_strength": "...",
            "top_weakness": "...",
            "overall_impression": "...",
            "reasoning": "...",
        },
    ]
    report = generate_markdown_report(SCENARIO_SCORES, baseline=baseline)
    # dns improved from 3.0 to 3.75, report should show positive delta
    assert "+0.75" in report or "improved" in report.lower()


def test_report_without_baseline_omits_trends():
    """Without a baseline, report must not crash and should omit trend data."""
    report = generate_markdown_report(SCENARIO_SCORES)
    assert report  # non-empty
    # Should not contain delta indicators
    assert "vs baseline" not in report.lower() or "no baseline" in report.lower()
```

**Step 2: Run tests to verify they fail**

```bash
cd /Users/gurkaransingh/Desktop/Development/infographic-builder
pytest tests/test_report.py -v 2>&1 | head -20
```

Expected: All tests FAIL with `ModuleNotFoundError: No module named 'eval.report'`.

**Step 3: Commit**

```bash
git add tests/test_report.py && git commit -m "test: add report module tests (red phase)"
```

---

### Task 8: Implement eval/report.py

**Files:**
- Create: `eval/report.py`

**Step 1: Create `eval/report.py`**

```python
"""Report generation for infographic evaluation results.

Aggregates scored JSON results into a markdown summary with per-scenario
scores, composite averages, dimension breakdowns, and optional baseline
comparison for trend tracking.
"""

from typing import Any


def interpret_band(composite: float) -> str:
    """Map a composite score to an interpretive quality band.

    Bands from the design doc:
        4.0 - 5.0  High quality
        3.0 - 3.9  Acceptable
        2.0 - 2.9  Below bar
        1.0 - 1.9  Failed
    """
    if composite >= 4.0:
        return "High quality"
    elif composite >= 3.0:
        return "Acceptable"
    elif composite >= 2.0:
        return "Below bar"
    else:
        return "Failed"


def aggregate_scores(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute aggregate statistics across all scenario results.

    Args:
        results: List of scored scenario dicts, each with 'scenario_name',
                 'composite_score', and 'scores' (per-dimension).

    Returns:
        Dict with mean_composite, dimension_averages, scenario_count,
        best_scenario, worst_scenario.
    """
    if not results:
        return {
            "mean_composite": 0.0,
            "dimension_averages": {},
            "scenario_count": 0,
            "best_scenario": "",
            "worst_scenario": "",
        }

    composites = {r["scenario_name"]: r["composite_score"] for r in results}
    mean_composite = sum(composites.values()) / len(composites)

    # Per-dimension averages
    dimensions = list(results[0]["scores"].keys())
    dimension_averages = {}
    for dim in dimensions:
        scores = [r["scores"][dim]["score"] for r in results]
        dimension_averages[dim] = round(sum(scores) / len(scores), 2)

    best = max(composites, key=composites.get)  # type: ignore[arg-type]
    worst = min(composites, key=composites.get)  # type: ignore[arg-type]

    return {
        "mean_composite": round(mean_composite, 2),
        "dimension_averages": dimension_averages,
        "scenario_count": len(results),
        "best_scenario": best,
        "worst_scenario": worst,
    }


def generate_markdown_report(
    results: list[dict[str, Any]],
    baseline: list[dict[str, Any]] | None = None,
) -> str:
    """Generate a markdown evaluation report.

    Args:
        results: List of scored scenario dicts from the current run.
        baseline: Optional list of scored scenario dicts from a previous run
                  for trend comparison.

    Returns:
        Markdown string with the full report.
    """
    agg = aggregate_scores(results)
    band = interpret_band(agg["mean_composite"])

    # Build baseline lookup for trend comparison
    baseline_lookup: dict[str, float] = {}
    if baseline:
        baseline_lookup = {
            r["scenario_name"]: r["composite_score"] for r in baseline
        }

    lines: list[str] = []
    lines.append("# Infographic Evaluation Report")
    lines.append("")
    lines.append(f"**Scenarios evaluated:** {agg['scenario_count']}")
    lines.append(f"**Mean composite score:** {agg['mean_composite']} -- {band}")
    lines.append(f"**Best scenario:** {agg['best_scenario']}")
    lines.append(f"**Worst scenario:** {agg['worst_scenario']}")
    lines.append("")

    # Dimension Averages
    lines.append("## Dimension Averages")
    lines.append("")
    lines.append("| Dimension | Average | Weight |")
    lines.append("|-----------|---------|--------|")

    weight_labels = {
        "content_accuracy": ("Content Accuracy", "20%"),
        "narrative_structure": ("Narrative Structure", "15%"),
        "visual_explanation": ("Visual Explanation", "25%"),
        "typography": ("Typography & Legibility", "20%"),
        "visual_quality": ("Visual Quality & Consistency", "20%"),
    }

    for dim, avg in agg["dimension_averages"].items():
        label, weight = weight_labels.get(dim, (dim, "?"))
        lines.append(f"| {label} | {avg} | {weight} |")
    lines.append("")

    # Per-scenario breakdown
    lines.append("## Per-Scenario Results")
    lines.append("")

    for result in sorted(
        results, key=lambda r: r["composite_score"], reverse=True
    ):
        name = result["scenario_name"]
        composite = result["composite_score"]
        scenario_band = interpret_band(composite)

        # Trend indicator
        trend = ""
        if baseline_lookup and name in baseline_lookup:
            delta = composite - baseline_lookup[name]
            if delta > 0:
                trend = f" +{delta:.2f} vs baseline"
            elif delta < 0:
                trend = f" {delta:.2f} vs baseline"
            else:
                trend = " unchanged vs baseline"

        lines.append(f"### {name} -- {composite} ({scenario_band}){trend}")
        lines.append("")

        # Dimension scores table
        lines.append("| Dimension | Score | Evidence |")
        lines.append("|-----------|-------|----------|")
        for dim, dim_data in result["scores"].items():
            label = weight_labels.get(dim, (dim, ""))[0]
            lines.append(
                f"| {label} | {dim_data['score']} | {dim_data['evidence']} |"
            )
        lines.append("")

        lines.append(f"**Strength:** {result.get('top_strength', 'N/A')}")
        lines.append(f"**Weakness:** {result.get('top_weakness', 'N/A')}")
        lines.append("")

    return "\n".join(lines)
```

**Step 2: Run the tests**

```bash
cd /Users/gurkaransingh/Desktop/Development/infographic-builder
pytest tests/test_report.py -v
```

Expected: All tests PASS.

**Step 3: Run the linter**

```bash
cd /Users/gurkaransingh/Desktop/Development/infographic-builder
ruff check eval/report.py && ruff format --check eval/report.py
```

Expected: No issues.

**Step 4: Commit**

```bash
git add eval/report.py && git commit -m "feat: implement report module with score aggregation, baseline comparison, and markdown generation"
```

---

### Task 9: Run all tests together to verify nothing is broken

**Files:** None (verification only)

**Step 1: Run the full test suite**

```bash
cd /Users/gurkaransingh/Desktop/Development/infographic-builder
pytest tests/ -v
```

Expected: All tests pass -- both the existing markdown structure tests and the new eval module tests.

**Step 2: Run linting across all eval code**

```bash
cd /Users/gurkaransingh/Desktop/Development/infographic-builder
ruff check eval/ tests/test_rubric.py tests/test_report.py
ruff format --check eval/ tests/test_rubric.py tests/test_report.py
```

Expected: Clean. Fix any issues before proceeding.

---

## Phase 3: Recipe & Integration (Tasks 10–12)

### Task 10: Create a CLI entry point for the evaluator

**Files:**
- Create: `eval/cli.py`
- Create: `eval/__main__.py`

**Context:** The evaluation recipe needs to invoke the Python evaluation and report generation. We create a simple CLI that the recipe's bash steps can call. Two subcommands: `evaluate` (score a single scenario's images) and `report` (aggregate a run directory into summary.md).

**Step 1: Create `eval/cli.py`**

```python
"""CLI entry point for the evaluation harness.

Usage:
    python -m eval evaluate --scenario-file <path> --scenario-name <name> --image-dir <dir> --output <path>
    python -m eval report --run-dir <dir> [--baseline-dir <dir>]
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

import yaml


def _load_scenario(scenario_file: str, scenario_name: str) -> dict:
    """Load a single scenario by name from the scenarios YAML file."""
    with open(scenario_file) as f:
        data = yaml.safe_load(f)
    for s in data["scenarios"]:
        if s["name"] == scenario_name:
            return s
    raise ValueError(f"Scenario '{scenario_name}' not found in {scenario_file}")


def cmd_evaluate(args: argparse.Namespace) -> None:
    """Score a single scenario's images with the rubric evaluator."""
    from eval.rubric import evaluate_image

    scenario = _load_scenario(args.scenario_file, args.scenario_name)
    image_dir = Path(args.image_dir)

    # Find all PNG images in the image directory
    image_paths = sorted(image_dir.glob("*.png"))
    if not image_paths:
        print(f"Error: No PNG images found in {image_dir}", file=sys.stderr)
        sys.exit(1)

    result = asyncio.run(evaluate_image(scenario, [str(p) for p in image_paths]))
    result["scenario_name"] = scenario["name"]

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Scored {scenario['name']}: composite={result['composite_score']}")


def cmd_report(args: argparse.Namespace) -> None:
    """Aggregate scores from a run directory into a markdown report."""
    from eval.report import generate_markdown_report

    run_dir = Path(args.run_dir)

    # Load all score JSON files from the run directory
    results = []
    for score_file in sorted(run_dir.rglob("*_scores.json")):
        with open(score_file) as f:
            results.append(json.load(f))

    if not results:
        print(f"Error: No score files found in {run_dir}", file=sys.stderr)
        sys.exit(1)

    # Load baseline if provided
    baseline = None
    if args.baseline_dir:
        baseline_dir = Path(args.baseline_dir)
        baseline = []
        for score_file in sorted(baseline_dir.rglob("*_scores.json")):
            with open(score_file) as f:
                baseline.append(json.load(f))

    report = generate_markdown_report(results, baseline=baseline)

    summary_path = run_dir / "summary.md"
    with open(summary_path, "w") as f:
        f.write(report)

    print(f"Report written to {summary_path} ({len(results)} scenarios)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Infographic evaluation harness")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # evaluate subcommand
    eval_parser = subparsers.add_parser("evaluate", help="Score a scenario's images")
    eval_parser.add_argument(
        "--scenario-file", required=True, help="Path to scenarios.yaml"
    )
    eval_parser.add_argument(
        "--scenario-name", required=True, help="Scenario name to evaluate"
    )
    eval_parser.add_argument(
        "--image-dir", required=True, help="Directory containing panel PNGs"
    )
    eval_parser.add_argument(
        "--output", required=True, help="Output path for scores JSON"
    )

    # report subcommand
    report_parser = subparsers.add_parser("report", help="Generate summary report")
    report_parser.add_argument(
        "--run-dir", required=True, help="Directory with scored results"
    )
    report_parser.add_argument(
        "--baseline-dir", default=None, help="Previous run directory for comparison"
    )

    args = parser.parse_args()

    if args.command == "evaluate":
        cmd_evaluate(args)
    elif args.command == "report":
        cmd_report(args)


if __name__ == "__main__":
    main()
```

**Step 2: Create `eval/__main__.py`**

Create `eval/__main__.py` so `python -m eval` works:

```python
"""Allow running eval as a module: python -m eval <command>."""

from eval.cli import main

main()
```

**Step 3: Verify the CLI shows help**

```bash
cd /Users/gurkaransingh/Desktop/Development/infographic-builder
python -m eval --help
python -m eval evaluate --help
python -m eval report --help
```

Expected: Each prints usage information without errors.

**Step 4: Commit**

```bash
git add eval/cli.py eval/__main__.py && git commit -m "feat: add CLI entry point for evaluate and report subcommands"
```

---

### Task 11: Create recipes/evaluate.yaml

**Files:**
- Create: `recipes/evaluate.yaml`

**Context:** This is an Amplifier recipe YAML. Refer to the existing recipes (`recipes/generate-sample-gallery.yaml`) for format conventions. The recipe has three stages: generate infographics, evaluate each with OpenAI vision, produce a summary report.

The recipe uses `bash` steps to invoke the Python CLI (`python -m eval evaluate ...` and `python -m eval report ...`) and `agent` steps to delegate infographic generation to `infographic-builder:infographic-builder`.

**Step 1: Create `recipes/evaluate.yaml`**

```yaml
# =============================================================================
# Evaluate Infographic Quality
# =============================================================================
#
# Recipe-driven evaluation pipeline:
#   1. Generate infographics from test scenarios
#   2. Evaluate each with OpenAI GPT-4o vision (rubric scoring)
#   3. Produce a markdown summary report with trends
#
# Prerequisites:
#   - OPENAI_API_KEY environment variable must be set
#   - pip install -e ".[dev]" (for openai + pyyaml)
#
# Usage:
#   amplifier run "execute recipes/evaluate.yaml"
#
# Output:
#   eval-results/<timestamp>/
#     <scenario_name>/
#       panel_*.png
#       <scenario_name>_scores.json
#     summary.md
#
# =============================================================================

name: "evaluate-infographic-quality"
description: "Generate, evaluate, and report on infographic quality across test scenarios"
version: "1.0.0"
tags: ["evaluation", "quality", "rubric", "batch"]

context:
  scenarios_file: "eval/scenarios.yaml"

steps:
  # -------------------------------------------------------------------------
  # Step 1: Create timestamped output directory and load scenarios
  # -------------------------------------------------------------------------
  - id: "setup"
    type: "bash"
    command: |
      TIMESTAMP=$(date +%Y-%m-%d_%H%M%S)
      RUN_DIR="eval-results/${TIMESTAMP}"
      mkdir -p "${RUN_DIR}"
      echo "${RUN_DIR}"
    output: "run_dir"

  - id: "load-scenarios"
    type: "bash"
    command: |
      python -c "
      import yaml, json
      with open('{{scenarios_file}}') as f:
          data = yaml.safe_load(f)
      print(json.dumps(data['scenarios']))
      "
    output: "scenarios"

  # -------------------------------------------------------------------------
  # Step 2: Generate infographics for each scenario
  # -------------------------------------------------------------------------
  - id: "generate-infographics"
    foreach: "{{scenarios}}"
    as: "scenario"
    steps:
      - id: "create-scenario-dir"
        type: "bash"
        command: "mkdir -p {{run_dir}}/{{scenario.name}} && echo 'ready'"
        output: "scenario_dir_status"

      - id: "generate"
        agent: "infographic-builder:infographic-builder"
        prompt: "{{scenario.prompt}} Save all output files to ./{{run_dir}}/{{scenario.name}}/"
        timeout: 1800
        on_error: "continue"

  # -------------------------------------------------------------------------
  # Step 3: Evaluate each generated scenario with OpenAI vision
  # -------------------------------------------------------------------------
  - id: "evaluate-scenarios"
    foreach: "{{scenarios}}"
    as: "scenario"
    type: "bash"
    command: |
      SCENARIO_DIR="{{run_dir}}/{{scenario.name}}"
      if ls "${SCENARIO_DIR}"/*.png 1>/dev/null 2>&1; then
        python -m eval evaluate \
          --scenario-file "{{scenarios_file}}" \
          --scenario-name "{{scenario.name}}" \
          --image-dir "${SCENARIO_DIR}" \
          --output "${SCENARIO_DIR}/{{scenario.name}}_scores.json"
      else
        echo "SKIP: No images found for {{scenario.name}}"
      fi
    on_error: "continue"
    timeout: 120

  # -------------------------------------------------------------------------
  # Step 4: Generate summary report
  # -------------------------------------------------------------------------
  - id: "generate-report"
    type: "bash"
    command: |
      python -m eval report --run-dir "{{run_dir}}"
      echo "Report generated at {{run_dir}}/summary.md"
    output: "report_status"
```

**Step 2: Validate the YAML is parseable**

```bash
cd /Users/gurkaransingh/Desktop/Development/infographic-builder
python -c "import yaml; yaml.safe_load(open('recipes/evaluate.yaml')); print('Valid YAML')"
```

Expected: `Valid YAML`

**Step 3: Commit**

```bash
git add recipes/evaluate.yaml && git commit -m "feat: add evaluation recipe with generate, evaluate, and report stages"
```

---

### Task 12: Run all tests and lint the full eval package

**Files:** None (verification only)

**Step 1: Run the full test suite**

```bash
cd /Users/gurkaransingh/Desktop/Development/infographic-builder
pytest tests/ -v
```

Expected: All tests pass.

**Step 2: Lint and format check all new code**

```bash
cd /Users/gurkaransingh/Desktop/Development/infographic-builder
ruff check eval/ tests/test_rubric.py tests/test_report.py
ruff format --check eval/ tests/test_rubric.py tests/test_report.py
```

Expected: Clean. Fix any issues.

**Step 3: Verify the CLI still works**

```bash
cd /Users/gurkaransingh/Desktop/Development/infographic-builder
python -m eval evaluate --help
python -m eval report --help
```

Expected: Both print help text.

**Step 4: Verify scenario loading works end to end**

```bash
cd /Users/gurkaransingh/Desktop/Development/infographic-builder
python -c "
import yaml
with open('eval/scenarios.yaml') as f:
    data = yaml.safe_load(f)
print(f'Loaded {len(data[\"scenarios\"])} scenarios')
for s in data['scenarios']:
    print(f'  {s[\"name\"]:30s} panels={s[\"panels\"]}  audience={s[\"audience\"][:40]}')
"
```

Expected: Lists all 18 scenarios with their panel counts and audiences.

**Step 5: Final commit if any lint fixes were needed**

```bash
git add -A && git status
# Only commit if there are changes
git diff --cached --quiet || git commit -m "chore: lint and format fixes for eval package"
```
