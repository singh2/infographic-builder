# Diagram Beautifier Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a dedicated `diagram-beautifier` agent that takes Graphviz (.dot) or Mermaid diagram source and renders them as beautiful infographic-quality visuals using the existing aesthetic system, preserving original topology and labels.

**Architecture:** A render-first approach: parse the diagram source to extract nodes/edges/labels/subgraphs, render the source to a plain PNG via CLI tools (`dot`/`mmdc`), then pass that PNG as `reference_image_path` to nano-banana `generate` for beautification. A new `diagram-beautifier` agent sits alongside the existing `infographic-builder` agent, sharing the aesthetic system, nano-banana tool, and stitch_panels tool but with its own workflow, decomposition logic, and quality review dimensions. The root session routing is updated to detect diagram input and delegate accordingly.

**Tech Stack:** Python 3.11+, pytest, Graphviz (`dot` CLI), Mermaid CLI (`mmdc`), nano-banana tool, stitch_panels tool

**Design Document:** `docs/plans/2026-03-31-diagram-beautifier-design.md`

---

## Important Context for Implementer

### Project Structure

```
infographic-builder/
  agents/infographic-builder.md       # Existing agent (Markdown + YAML frontmatter)
  behaviors/infographic.yaml          # Existing behavior YAML wiring tools + agents + context
  bundle.md                           # Root bundle (YAML frontmatter + Markdown body)
  context/infographic-awareness.md    # Existing routing context for root session
  docs/style-guide.md                 # Shared aesthetic system (6 aesthetics + freeform)
  tests/                              # All tests (flat, no subdirectories)
  tests/helpers.py                    # Shared test helpers (read_guide(), read_agent())
  pyproject.toml                      # pythonpath = [".", "tests"]
```

### Testing Conventions

- All tests live in `tests/` (flat directory, no nesting)
- Tests import from `helpers.py` which provides file path constants and read helpers
- Tests read Markdown/YAML files and assert structural properties (headings present, sections in order, keywords present)
- Python modules (like `eval/`) use standard `pytest` with `from __future__ import annotations`
- `pyproject.toml` sets `pythonpath = [".", "tests"]` so `from helpers import ...` works
- Run with: `python -m pytest tests/ -v`

### Agent Markdown Structure

Agent files use YAML frontmatter with `meta:` block (name, model_role, description with examples) followed by Markdown body with workflow steps. See `agents/infographic-builder.md` for the exact pattern.

### Behavior YAML Structure

`behaviors/infographic.yaml` wires context includes, tool modules, and agent includes. The new agent must be added to both the `agents.include` list and the `context.include` list.

### Python Source Files

New Python modules for the diagram beautifier (parser, dependency checker, decomposition, etc.) go in a new `diagram_beautifier/` package at the project root, following the same pattern as the existing `eval/` package.

---

## Task 1: Source Parser

**Files:**
- Create: `diagram_beautifier/__init__.py`
- Create: `diagram_beautifier/parser.py`
- Create: `tests/test_diagram_parser.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_diagram_parser.py`:

```python
"""Tests for diagram_beautifier/parser.py -- diagram source parser."""

from __future__ import annotations

import pytest

from diagram_beautifier.parser import parse_diagram_source


# ---------------------------------------------------------------------------
# Graphviz (.dot) parsing
# ---------------------------------------------------------------------------

SIMPLE_DIGRAPH = """\
digraph G {
    A [label="Load Balancer"]
    B [label="Web Server"]
    C [label="Database"]
    A -> B [label="HTTP"]
    B -> C [label="SQL"]
}
"""

DOT_WITH_SUBGRAPHS = """\
digraph architecture {
    subgraph cluster_frontend {
        label="Frontend"
        A [label="React App"]
        B [label="CDN"]
    }
    subgraph cluster_backend {
        label="Backend"
        C [label="API Server"]
        D [label="Worker"]
    }
    A -> C
    B -> A
    C -> D
}
"""

DOT_IMPLICIT_LABELS = """\
digraph G {
    server -> database
    database -> cache
}
"""

UNDIRECTED_GRAPH = """\
graph G {
    A [label="Node 1"]
    B [label="Node 2"]
    A -- B
}
"""


def test_parse_dot_simple_digraph_format() -> None:
    """Parser identifies .dot format and digraph type."""
    result = parse_diagram_source(SIMPLE_DIGRAPH, "dot")
    assert result["format"] == "dot"
    assert result["diagram_type"] == "digraph"


def test_parse_dot_simple_digraph_nodes() -> None:
    """Parser extracts all 3 nodes with their labels."""
    result = parse_diagram_source(SIMPLE_DIGRAPH, "dot")
    labels = {n["label"] for n in result["nodes"]}
    assert labels == {"Load Balancer", "Web Server", "Database"}
    assert result["node_count"] == 3


def test_parse_dot_simple_digraph_edges() -> None:
    """Parser extracts edges with labels."""
    result = parse_diagram_source(SIMPLE_DIGRAPH, "dot")
    assert result["edge_count"] == 2
    edge_labels = {e.get("label") for e in result["edges"] if e.get("label")}
    assert "HTTP" in edge_labels
    assert "SQL" in edge_labels


def test_parse_dot_subgraphs() -> None:
    """Parser extracts subgraph declarations with their node IDs."""
    result = parse_diagram_source(DOT_WITH_SUBGRAPHS, "dot")
    assert len(result["subgraphs"]) == 2
    names = {sg["name"] for sg in result["subgraphs"]}
    assert "Frontend" in names or "cluster_frontend" in names


def test_parse_dot_implicit_labels() -> None:
    """When no label= attribute, node ID is used as label."""
    result = parse_diagram_source(DOT_IMPLICIT_LABELS, "dot")
    labels = {n["label"] for n in result["nodes"]}
    assert "server" in labels
    assert "database" in labels
    assert "cache" in labels


def test_parse_dot_undirected_graph() -> None:
    """Parser handles undirected 'graph' (not 'digraph')."""
    result = parse_diagram_source(UNDIRECTED_GRAPH, "dot")
    assert result["diagram_type"] == "graph"
    assert result["node_count"] == 2
    assert result["edge_count"] == 1


# ---------------------------------------------------------------------------
# Mermaid parsing
# ---------------------------------------------------------------------------

SIMPLE_FLOWCHART = """\
flowchart TD
    A[Load Balancer] --> B[Web Server]
    B --> C[Database]
    B --> D[Cache]
"""

MERMAID_WITH_SUBGRAPHS = """\
flowchart TD
    subgraph Frontend
        A[React App]
        B[CDN]
    end
    subgraph Backend
        C[API Server]
        D[Worker]
    end
    A --> C
    B --> A
"""

MERMAID_EDGE_LABELS = """\
flowchart LR
    A[Client] -->|HTTP| B[Server]
    B -->|SQL| C[DB]
"""


def test_parse_mermaid_flowchart_format() -> None:
    """Parser identifies mermaid format and flowchart type."""
    result = parse_diagram_source(SIMPLE_FLOWCHART, "mermaid")
    assert result["format"] == "mermaid"
    assert result["diagram_type"] == "flowchart"


def test_parse_mermaid_flowchart_nodes() -> None:
    """Parser extracts nodes with display labels from bracket syntax."""
    result = parse_diagram_source(SIMPLE_FLOWCHART, "mermaid")
    labels = {n["label"] for n in result["nodes"]}
    assert "Load Balancer" in labels
    assert "Web Server" in labels
    assert "Database" in labels
    assert "Cache" in labels
    assert result["node_count"] == 4


def test_parse_mermaid_flowchart_edges() -> None:
    """Parser extracts edges from --> syntax."""
    result = parse_diagram_source(SIMPLE_FLOWCHART, "mermaid")
    assert result["edge_count"] == 3


def test_parse_mermaid_subgraphs() -> None:
    """Parser extracts subgraph blocks."""
    result = parse_diagram_source(MERMAID_WITH_SUBGRAPHS, "mermaid")
    assert len(result["subgraphs"]) == 2
    names = {sg["name"] for sg in result["subgraphs"]}
    assert "Frontend" in names
    assert "Backend" in names


def test_parse_mermaid_edge_labels() -> None:
    """Parser extracts edge labels from |label| syntax."""
    result = parse_diagram_source(MERMAID_EDGE_LABELS, "mermaid")
    edge_labels = {e.get("label") for e in result["edges"] if e.get("label")}
    assert "HTTP" in edge_labels
    assert "SQL" in edge_labels


# ---------------------------------------------------------------------------
# Raw source preservation
# ---------------------------------------------------------------------------


def test_parse_preserves_raw_source() -> None:
    """Parser includes the original source text in the result."""
    result = parse_diagram_source(SIMPLE_DIGRAPH, "dot")
    assert result["raw_source"] == SIMPLE_DIGRAPH
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_diagram_parser.py -v
```

Expected: FAIL -- `ModuleNotFoundError: No module named 'diagram_beautifier'`

- [ ] **Step 3: Write the implementation**

Create `diagram_beautifier/__init__.py`:

```python
"""Diagram beautifier -- parse, render, and beautify Graphviz/Mermaid diagrams."""
```

Create `diagram_beautifier/parser.py`:

```python
"""Parse Graphviz (.dot) and Mermaid diagram sources into a normalized structure.

The parser extracts nodes, edges, labels, and subgraphs from diagram source text.
The output is used downstream for panel decomposition and quality review.
"""

from __future__ import annotations

import re
from typing import Any


def parse_diagram_source(source: str, fmt: str) -> dict[str, Any]:
    """Parse diagram source into a normalized structure.

    Args:
        source: The diagram source text.
        fmt: Format identifier -- ``"dot"`` for Graphviz or ``"mermaid"`` for Mermaid.

    Returns:
        A dict with keys: ``format``, ``diagram_type``, ``nodes``, ``edges``,
        ``subgraphs``, ``node_count``, ``edge_count``, ``raw_source``.
    """
    if fmt == "dot":
        return _parse_dot(source)
    if fmt == "mermaid":
        return _parse_mermaid(source)
    raise ValueError(f"Unsupported format: {fmt!r}")


# ---------------------------------------------------------------------------
# Graphviz (.dot) parser
# ---------------------------------------------------------------------------


def _parse_dot(source: str) -> dict[str, Any]:
    """Parse a Graphviz .dot source."""
    # Determine graph type
    if re.search(r"\bdigraph\b", source):
        diagram_type = "digraph"
    else:
        diagram_type = "graph"

    nodes: list[dict[str, str]] = []
    edges: list[dict[str, str | None]] = []
    subgraphs: list[dict[str, Any]] = []
    seen_node_ids: set[str] = set()

    # Keywords that should not be treated as node IDs
    _dot_keywords = frozenset({
        "label", "style", "color", "fontcolor", "bgcolor", "rank",
        "rankdir", "fontname", "fontsize", "node", "edge", "graph",
        "digraph", "subgraph", "compound", "newrank",
    })

    # Extract subgraphs
    subgraph_pattern = re.compile(
        r"subgraph\s+(\w+)\s*\{([^}]*)\}", re.DOTALL
    )
    for match in subgraph_pattern.finditer(source):
        sg_id = match.group(1)
        sg_body = match.group(2)

        # Extract subgraph label
        label_match = re.search(r'label\s*=\s*"([^"]*)"', sg_body)
        sg_name = label_match.group(1) if label_match else sg_id

        # Extract node IDs declared in this subgraph
        sg_node_ids: list[str] = []
        for node_match in re.finditer(
            r"^\s*(\w+)\s*[\[;]", sg_body, re.MULTILINE
        ):
            node_id = node_match.group(1)
            if node_id not in _dot_keywords:
                sg_node_ids.append(node_id)

        subgraphs.append({"name": sg_name, "node_ids": sg_node_ids})

    # Extract nodes with explicit labels
    node_pattern = re.compile(
        r"^\s*(\w+)\s*\[([^\]]*label\s*=\s*\"([^\"]*)\"[^\]]*)\]",
        re.MULTILINE,
    )
    for match in node_pattern.finditer(source):
        node_id = match.group(1)
        label = match.group(3)
        if node_id not in _dot_keywords:
            nodes.append({"id": node_id, "label": label})
            seen_node_ids.add(node_id)

    # Extract edges: A -> B or A -- B, with optional labels
    edge_pattern = re.compile(
        r"(\w+)\s*(-[->])\s*(\w+)(?:\s*\[([^\]]*)\])?", re.MULTILINE
    )
    for match in edge_pattern.finditer(source):
        from_id = match.group(1)
        to_id = match.group(3)
        attrs = match.group(4) or ""

        edge_label = None
        label_match = re.search(r'label\s*=\s*"([^"]*)"', attrs)
        if label_match:
            edge_label = label_match.group(1)

        edges.append({"from": from_id, "to": to_id, "label": edge_label})

        # Add nodes discovered only in edges (implicit labels = node ID)
        for nid in (from_id, to_id):
            if nid not in seen_node_ids:
                nodes.append({"id": nid, "label": nid})
                seen_node_ids.add(nid)

    return {
        "format": "dot",
        "diagram_type": diagram_type,
        "nodes": nodes,
        "edges": edges,
        "subgraphs": subgraphs,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "raw_source": source,
    }


# ---------------------------------------------------------------------------
# Mermaid parser
# ---------------------------------------------------------------------------


def _parse_mermaid(source: str) -> dict[str, Any]:
    """Parse a Mermaid diagram source."""
    lines = source.strip().splitlines()
    first_line = lines[0].strip() if lines else ""

    # Determine diagram type from first line
    diagram_type = first_line.split()[0] if first_line else "flowchart"

    nodes: list[dict[str, str]] = []
    edges: list[dict[str, str | None]] = []
    subgraphs: list[dict[str, Any]] = []
    seen_node_ids: set[str] = set()

    # Track current subgraph context
    current_subgraph: dict[str, Any] | None = None

    for line in lines[1:]:
        stripped = line.strip()

        # Subgraph start
        sg_match = re.match(r"subgraph\s+(.+)", stripped)
        if sg_match:
            current_subgraph = {
                "name": sg_match.group(1).strip(),
                "node_ids": [],
            }
            continue

        # Subgraph end
        if stripped == "end" and current_subgraph is not None:
            subgraphs.append(current_subgraph)
            current_subgraph = None
            continue

        # Edge with optional label: A -->|label| B or A --> B
        edge_match = re.match(
            r"(\w+)(?:\[[^\]]*\])?\s*--+>(?:\|([^|]*)\|)?\s*(\w+)(?:\[([^\]]*)\])?",
            stripped,
        )
        if edge_match:
            from_id = edge_match.group(1)
            edge_label = edge_match.group(2)
            to_id = edge_match.group(3)

            edges.append({
                "from": from_id,
                "to": to_id,
                "label": edge_label,
            })

            # Extract node labels from bracket syntax in the edge line
            for node_def in re.finditer(r"(\w+)\[([^\]]*)\]", stripped):
                nid = node_def.group(1)
                nlabel = node_def.group(2)
                if nid not in seen_node_ids:
                    nodes.append({"id": nid, "label": nlabel})
                    seen_node_ids.add(nid)
                    if current_subgraph is not None:
                        current_subgraph["node_ids"].append(nid)

            # Add nodes without bracket labels (implicit)
            for nid in (from_id, to_id):
                if nid not in seen_node_ids:
                    nodes.append({"id": nid, "label": nid})
                    seen_node_ids.add(nid)
                    if current_subgraph is not None:
                        current_subgraph["node_ids"].append(nid)

            continue

        # Standalone node definition: A[Label]
        node_match = re.match(r"(\w+)\[([^\]]*)\]", stripped)
        if node_match:
            nid = node_match.group(1)
            nlabel = node_match.group(2)
            if nid not in seen_node_ids:
                nodes.append({"id": nid, "label": nlabel})
                seen_node_ids.add(nid)
                if current_subgraph is not None:
                    current_subgraph["node_ids"].append(nid)

    return {
        "format": "mermaid",
        "diagram_type": diagram_type,
        "nodes": nodes,
        "edges": edges,
        "subgraphs": subgraphs,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "raw_source": source,
    }
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_diagram_parser.py -v
```

Expected: All 14 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add diagram_beautifier/__init__.py diagram_beautifier/parser.py tests/test_diagram_parser.py && git commit -m "feat(diagram): add source parser for Graphviz and Mermaid diagrams"
```

---

## Task 2: Dependency Checker

**Files:**
- Create: `diagram_beautifier/deps.py`
- Create: `tests/test_diagram_deps.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_diagram_deps.py`:

```python
"""Tests for diagram_beautifier/deps.py -- CLI dependency checker."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from diagram_beautifier.deps import check_dependency, DependencyError


# ---------------------------------------------------------------------------
# Successful detection
# ---------------------------------------------------------------------------


def test_check_dependency_dot_found() -> None:
    """check_dependency returns the path when dot is found."""
    with patch("shutil.which", return_value="/usr/local/bin/dot"):
        result = check_dependency("dot")
    assert result == "/usr/local/bin/dot"


def test_check_dependency_mmdc_found() -> None:
    """check_dependency returns the path when mmdc is found."""
    with patch("shutil.which", return_value="/usr/local/bin/mmdc"):
        result = check_dependency("mermaid")
    assert result == "/usr/local/bin/mmdc"


# ---------------------------------------------------------------------------
# Missing dependency errors
# ---------------------------------------------------------------------------


def test_check_dependency_dot_missing_raises() -> None:
    """check_dependency raises DependencyError with install instructions for dot."""
    with patch("shutil.which", return_value=None):
        with pytest.raises(DependencyError, match="brew install graphviz"):
            check_dependency("dot")


def test_check_dependency_mmdc_missing_raises() -> None:
    """check_dependency raises DependencyError with install instructions for mmdc."""
    with patch("shutil.which", return_value=None):
        with pytest.raises(DependencyError, match="mermaid-cli"):
            check_dependency("mermaid")


def test_check_dependency_dot_error_includes_platform_instructions() -> None:
    """DependencyError for dot includes macOS, Ubuntu, and Fedora install lines."""
    with patch("shutil.which", return_value=None):
        with pytest.raises(DependencyError) as exc_info:
            check_dependency("dot")
    message = str(exc_info.value)
    assert "brew install graphviz" in message
    assert "apt-get install graphviz" in message
    assert "dnf install graphviz" in message


def test_check_dependency_unknown_format_raises() -> None:
    """check_dependency raises ValueError for unknown format."""
    with pytest.raises(ValueError, match="Unsupported format"):
        check_dependency("svg")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_diagram_deps.py -v
```

Expected: FAIL -- `ModuleNotFoundError: No module named 'diagram_beautifier.deps'`

- [ ] **Step 3: Write the implementation**

Create `diagram_beautifier/deps.py`:

```python
"""Check for required CLI tools (dot for Graphviz, mmdc for Mermaid).

Fails immediately with clear, platform-specific install instructions
if a required tool is not found on PATH.
"""

from __future__ import annotations

import shutil


class DependencyError(RuntimeError):
    """Raised when a required CLI tool is not installed."""


_GRAPHVIZ_INSTALL = """\
Graphviz is required to render .dot diagrams but was not found.

Install with:
  macOS:  brew install graphviz
  Ubuntu: sudo apt-get install graphviz
  Fedora: sudo dnf install graphviz"""

_MERMAID_INSTALL = """\
Mermaid CLI is required to render Mermaid diagrams but was not found.

Install with:
  npm install -g @mermaid-js/mermaid-cli"""


def check_dependency(fmt: str) -> str:
    """Verify the required CLI tool is available for the given format.

    Args:
        fmt: ``"dot"`` for Graphviz or ``"mermaid"`` for Mermaid.

    Returns:
        The absolute path to the CLI tool.

    Raises:
        DependencyError: If the tool is not found on PATH.
        ValueError: If *fmt* is not a supported format.
    """
    if fmt == "dot":
        path = shutil.which("dot")
        if path is None:
            raise DependencyError(_GRAPHVIZ_INSTALL)
        return path

    if fmt == "mermaid":
        path = shutil.which("mmdc")
        if path is None:
            raise DependencyError(_MERMAID_INSTALL)
        return path

    raise ValueError(f"Unsupported format: {fmt!r}")
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_diagram_deps.py -v
```

Expected: All 6 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add diagram_beautifier/deps.py tests/test_diagram_deps.py && git commit -m "feat(diagram): add dependency checker for dot and mmdc CLI tools"
```

---

## Task 3: Plain PNG Renderer

**Files:**
- Create: `diagram_beautifier/renderer.py`
- Create: `tests/test_diagram_renderer.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_diagram_renderer.py`:

```python
"""Tests for diagram_beautifier/renderer.py -- plain PNG rendering via CLI tools."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from diagram_beautifier.renderer import render_plain_png, RenderError


# ---------------------------------------------------------------------------
# Graphviz rendering
# ---------------------------------------------------------------------------

DOT_SOURCE = """\
digraph G {
    A [label="Hello"]
    B [label="World"]
    A -> B
}
"""


def test_render_dot_calls_subprocess_correctly(tmp_path: Path) -> None:
    """render_plain_png calls dot with correct arguments."""
    source_file = tmp_path / "test.dot"
    source_file.write_text(DOT_SOURCE)
    output_path = tmp_path / "output.png"

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stderr = ""

    with patch("subprocess.run", return_value=mock_result) as mock_run:
        render_plain_png(str(source_file), "dot", str(output_path))

    mock_run.assert_called_once()
    call_args = mock_run.call_args[0][0]
    assert call_args[0] == "dot"
    assert "-Tpng" in call_args
    assert "-Gdpi=150" in call_args
    assert str(source_file) in call_args


def test_render_dot_failure_raises(tmp_path: Path) -> None:
    """render_plain_png raises RenderError when dot fails."""
    source_file = tmp_path / "bad.dot"
    source_file.write_text("not valid dot")
    output_path = tmp_path / "output.png"

    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stderr = "Error: syntax error"

    with patch("subprocess.run", return_value=mock_result):
        with pytest.raises(RenderError, match="syntax error"):
            render_plain_png(str(source_file), "dot", str(output_path))


# ---------------------------------------------------------------------------
# Mermaid rendering
# ---------------------------------------------------------------------------

MERMAID_SOURCE = """\
flowchart TD
    A[Hello] --> B[World]
"""


def test_render_mermaid_calls_subprocess_correctly(tmp_path: Path) -> None:
    """render_plain_png calls mmdc with correct arguments."""
    source_file = tmp_path / "test.mmd"
    source_file.write_text(MERMAID_SOURCE)
    output_path = tmp_path / "output.png"

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stderr = ""

    with patch("subprocess.run", return_value=mock_result) as mock_run:
        render_plain_png(str(source_file), "mermaid", str(output_path))

    mock_run.assert_called_once()
    call_args = mock_run.call_args[0][0]
    assert call_args[0] == "mmdc"
    assert "-i" in call_args


# ---------------------------------------------------------------------------
# Source string rendering (no file on disk)
# ---------------------------------------------------------------------------


def test_render_from_source_string_creates_temp_file(tmp_path: Path) -> None:
    """render_plain_png can accept source text directly and writes a temp file."""
    output_path = tmp_path / "output.png"

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stderr = ""

    with patch("subprocess.run", return_value=mock_result):
        render_plain_png(
            DOT_SOURCE, "dot", str(output_path), is_source_text=True
        )
    # Should not raise
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_diagram_renderer.py -v
```

Expected: FAIL -- `ModuleNotFoundError: No module named 'diagram_beautifier.renderer'`

- [ ] **Step 3: Write the implementation**

Create `diagram_beautifier/renderer.py`:

```python
"""Render diagram source to a plain PNG using CLI tools.

Graphviz sources are rendered via ``dot -Tpng``.
Mermaid sources are rendered via ``mmdc -o``.
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


class RenderError(RuntimeError):
    """Raised when the CLI rendering tool fails."""


def render_plain_png(
    source_or_path: str,
    fmt: str,
    output_path: str,
    *,
    is_source_text: bool = False,
) -> str:
    """Render diagram source to a plain PNG.

    Args:
        source_or_path: Either a file path to the diagram source, or the
            source text itself (when *is_source_text* is True).
        fmt: ``"dot"`` for Graphviz or ``"mermaid"`` for Mermaid.
        output_path: Where to write the output PNG.
        is_source_text: If True, *source_or_path* is treated as source text
            and a temporary file is created for the CLI tool.

    Returns:
        The *output_path* on success.

    Raises:
        RenderError: If the CLI tool exits with a non-zero return code.
        ValueError: If *fmt* is not supported.
    """
    if is_source_text:
        suffix = ".dot" if fmt == "dot" else ".mmd"
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=suffix, delete=False
        )
        tmp.write(source_or_path)
        tmp.close()
        source_path = tmp.name
    else:
        source_path = source_or_path

    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    if fmt == "dot":
        cmd = [
            "dot",
            "-Tpng",
            "-Gdpi=150",
            source_path,
            "-o",
            output_path,
        ]
    elif fmt == "mermaid":
        cmd = [
            "mmdc",
            "-i",
            source_path,
            "-o",
            output_path,
            "-w",
            "2048",
            "-H",
            "1536",
            "--scale",
            "2",
        ]
    else:
        raise ValueError(f"Unsupported format: {fmt!r}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RenderError(
            f"{cmd[0]} exited with code {result.returncode}: {result.stderr}"
        )

    return output_path
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_diagram_renderer.py -v
```

Expected: All 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add diagram_beautifier/renderer.py tests/test_diagram_renderer.py && git commit -m "feat(diagram): add plain PNG renderer for dot and mmdc CLI tools"
```

---

## Task 4: Panel Decomposition

**Files:**
- Create: `diagram_beautifier/decompose.py`
- Create: `tests/test_diagram_decompose.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_diagram_decompose.py`:

```python
"""Tests for diagram_beautifier/decompose.py -- panel decomposition logic."""

from __future__ import annotations

from diagram_beautifier.decompose import decide_panels


# ---------------------------------------------------------------------------
# Single-panel cases
# ---------------------------------------------------------------------------


def test_small_diagram_single_panel() -> None:
    """<=10 nodes always produces 1 panel regardless of subgraphs."""
    result = decide_panels(node_count=8, subgraphs=[
        {"name": "A", "node_ids": ["1", "2", "3", "4"]},
        {"name": "B", "node_ids": ["5", "6", "7", "8"]},
    ])
    assert result["panel_count"] == 1
    assert result["strategy"] == "single"


def test_medium_diagram_no_subgraphs_single_panel() -> None:
    """11-25 nodes with 0-1 subgraphs produces 1 panel."""
    result = decide_panels(node_count=20, subgraphs=[])
    assert result["panel_count"] == 1
    assert result["strategy"] == "single"


def test_medium_diagram_one_subgraph_single_panel() -> None:
    """11-25 nodes with exactly 1 subgraph produces 1 panel."""
    result = decide_panels(node_count=15, subgraphs=[
        {"name": "Main", "node_ids": [str(i) for i in range(15)]},
    ])
    assert result["panel_count"] == 1
    assert result["strategy"] == "single"


# ---------------------------------------------------------------------------
# Multi-panel cases
# ---------------------------------------------------------------------------


def test_medium_diagram_multiple_subgraphs_splits() -> None:
    """11-25 nodes with 2+ subgraphs splits into multiple panels."""
    result = decide_panels(node_count=20, subgraphs=[
        {"name": "Frontend", "node_ids": [str(i) for i in range(10)]},
        {"name": "Backend", "node_ids": [str(i) for i in range(10, 20)]},
    ])
    assert result["panel_count"] >= 2
    assert result["strategy"] == "subgraph_split"


def test_large_diagram_splits() -> None:
    """26-40 nodes always splits."""
    result = decide_panels(node_count=30, subgraphs=[
        {"name": "A", "node_ids": [str(i) for i in range(15)]},
        {"name": "B", "node_ids": [str(i) for i in range(15, 30)]},
    ])
    assert result["panel_count"] >= 2
    assert result["strategy"] == "subgraph_split"


def test_very_large_diagram_splits_max_6() -> None:
    """40+ nodes splits into max 6 panels."""
    result = decide_panels(node_count=80, subgraphs=[
        {"name": f"Group{i}", "node_ids": [str(j) for j in range(i * 10, (i + 1) * 10)]}
        for i in range(8)
    ])
    assert result["panel_count"] >= 3
    assert result["panel_count"] <= 6


def test_large_diagram_no_subgraphs_suggests_single() -> None:
    """26+ nodes with no subgraphs falls back to single with a warning."""
    result = decide_panels(node_count=35, subgraphs=[])
    # Without subgraph boundaries, decomposition cannot split meaningfully
    assert result["panel_count"] == 1
    assert result["strategy"] == "single"
    assert result.get("warning") is not None


# ---------------------------------------------------------------------------
# Panel assignments
# ---------------------------------------------------------------------------


def test_panel_assignments_cover_all_subgraphs() -> None:
    """Each subgraph is assigned to a panel."""
    result = decide_panels(node_count=30, subgraphs=[
        {"name": "Frontend", "node_ids": ["A", "B", "C"]},
        {"name": "Backend", "node_ids": ["D", "E", "F"]},
        {"name": "Database", "node_ids": ["G", "H", "I"]},
    ])
    assigned_subgraphs = set()
    for panel in result["panels"]:
        for sg_name in panel["subgraph_names"]:
            assigned_subgraphs.add(sg_name)
    assert assigned_subgraphs == {"Frontend", "Backend", "Database"}
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_diagram_decompose.py -v
```

Expected: FAIL -- `ModuleNotFoundError: No module named 'diagram_beautifier.decompose'`

- [ ] **Step 3: Write the implementation**

Create `diagram_beautifier/decompose.py`:

```python
"""Panel decomposition for diagrams based on graph structure.

Uses node count and subgraph boundaries to decide single vs. multi-panel
layout. This is fundamentally different from infographic decomposition
(which uses content density) -- diagrams split along semantic boundaries.
"""

from __future__ import annotations

from typing import Any


def decide_panels(
    node_count: int,
    subgraphs: list[dict[str, Any]],
) -> dict[str, Any]:
    """Decide panel decomposition based on node count and subgraph structure.

    Thresholds:
        - 1-10 nodes: always single panel
        - 11-25 nodes, 0-1 subgraphs: single panel
        - 11-25 nodes, 2+ subgraphs: split by subgraph (2-3 panels)
        - 26-40 nodes: split by subgraph (2-4 panels)
        - 40+ nodes: split by subgraph (3-6 panels, max 6)

    Args:
        node_count: Total number of nodes in the diagram.
        subgraphs: List of subgraph dicts with ``name`` and ``node_ids``.

    Returns:
        Dict with ``panel_count``, ``strategy``, ``panels`` (list of panel
        assignments), and optional ``warning``.
    """
    num_subgraphs = len(subgraphs)

    # Small diagrams: always single panel
    if node_count <= 10:
        return _single_panel_result(subgraphs)

    # Medium diagrams: split only if 2+ subgraphs
    if node_count <= 25:
        if num_subgraphs <= 1:
            return _single_panel_result(subgraphs)
        return _split_by_subgraphs(subgraphs, max_panels=3)

    # Large diagrams: split if subgraphs available
    if num_subgraphs == 0:
        return {
            "panel_count": 1,
            "strategy": "single",
            "panels": [{"panel_number": 1, "subgraph_names": []}],
            "warning": (
                f"Diagram has {node_count} nodes but no subgraph declarations. "
                "Consider adding explicit subgraph groupings to your source "
                "for better multi-panel decomposition."
            ),
        }

    if node_count <= 40:
        return _split_by_subgraphs(subgraphs, max_panels=4)

    # Very large diagrams
    return _split_by_subgraphs(subgraphs, max_panels=6)


def _single_panel_result(
    subgraphs: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build a single-panel result."""
    sg_names = [sg["name"] for sg in subgraphs]
    return {
        "panel_count": 1,
        "strategy": "single",
        "panels": [{"panel_number": 1, "subgraph_names": sg_names}],
    }


def _split_by_subgraphs(
    subgraphs: list[dict[str, Any]],
    max_panels: int,
) -> dict[str, Any]:
    """Split subgraphs across panels, merging small groups as needed."""
    if len(subgraphs) <= max_panels:
        # Each subgraph gets its own panel
        panels = [
            {"panel_number": i + 1, "subgraph_names": [sg["name"]]}
            for i, sg in enumerate(subgraphs)
        ]
    else:
        # More subgraphs than max panels -- merge adjacent subgraphs
        panels = []
        per_panel = len(subgraphs) / max_panels
        current: list[str] = []
        for i, sg in enumerate(subgraphs):
            current.append(sg["name"])
            if len(current) >= per_panel and len(panels) < max_panels - 1:
                panels.append({
                    "panel_number": len(panels) + 1,
                    "subgraph_names": current,
                })
                current = []
        # Last panel gets remaining subgraphs
        if current:
            panels.append({
                "panel_number": len(panels) + 1,
                "subgraph_names": current,
            })

    return {
        "panel_count": len(panels),
        "strategy": "subgraph_split",
        "panels": panels,
    }
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_diagram_decompose.py -v
```

Expected: All 8 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add diagram_beautifier/decompose.py tests/test_diagram_decompose.py && git commit -m "feat(diagram): add panel decomposition by graph structure"
```

---

## Task 5: Beautification Prompt Builder

**Files:**
- Create: `diagram_beautifier/prompt.py`
- Create: `tests/test_diagram_prompt.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_diagram_prompt.py`:

```python
"""Tests for diagram_beautifier/prompt.py -- beautification prompt builder."""

from __future__ import annotations

from diagram_beautifier.prompt import (
    build_beautify_prompt,
    STRUCTURAL_PRESERVATION_MODIFIER,
)


# ---------------------------------------------------------------------------
# Structural preservation modifier
# ---------------------------------------------------------------------------


def test_structural_modifier_mentions_topology() -> None:
    """The modifier mentions preserving topology from the reference image."""
    lower = STRUCTURAL_PRESERVATION_MODIFIER.lower()
    assert (
        "topology" in lower
        or "node positions" in lower
        or "exact topology" in lower
    )


def test_structural_modifier_mentions_labels() -> None:
    """The modifier mentions reproducing text labels exactly."""
    assert "label" in STRUCTURAL_PRESERVATION_MODIFIER.lower()


def test_structural_modifier_mentions_connections() -> None:
    """The modifier mentions preserving connections/edges."""
    lower = STRUCTURAL_PRESERVATION_MODIFIER.lower()
    assert "connection" in lower or "edge" in lower


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------


def test_build_beautify_prompt_includes_aesthetic_template() -> None:
    """The built prompt includes the aesthetic template text."""
    prompt = build_beautify_prompt(
        aesthetic_template="Claymation Studio style with soft lighting",
        diagram_type="digraph",
        node_labels=["Load Balancer", "Web Server"],
        edge_labels=["HTTP"],
    )
    assert "Claymation Studio" in prompt


def test_build_beautify_prompt_includes_structural_modifier() -> None:
    """The built prompt includes the structural preservation modifier."""
    prompt = build_beautify_prompt(
        aesthetic_template="Clean Minimalist style",
        diagram_type="flowchart",
        node_labels=["A", "B"],
        edge_labels=[],
    )
    assert "STRUCTURAL PRESERVATION" in prompt


def test_build_beautify_prompt_lists_node_labels() -> None:
    """The prompt includes all node labels for text rendering accuracy."""
    prompt = build_beautify_prompt(
        aesthetic_template="Dark Mode Tech",
        diagram_type="digraph",
        node_labels=["Load Balancer", "API Gateway", "Database"],
        edge_labels=["gRPC"],
    )
    assert "Load Balancer" in prompt
    assert "API Gateway" in prompt
    assert "Database" in prompt


def test_build_beautify_prompt_lists_edge_labels() -> None:
    """The prompt includes edge labels when provided."""
    prompt = build_beautify_prompt(
        aesthetic_template="Clean Minimalist",
        diagram_type="digraph",
        node_labels=["A", "B"],
        edge_labels=["HTTP/443", "gRPC"],
    )
    assert "HTTP/443" in prompt
    assert "gRPC" in prompt


def test_build_beautify_prompt_mentions_diagram_type() -> None:
    """The prompt mentions the diagram type for context."""
    prompt = build_beautify_prompt(
        aesthetic_template="Bold Editorial",
        diagram_type="flowchart",
        node_labels=["Start", "End"],
        edge_labels=[],
    )
    assert "flowchart" in prompt.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_diagram_prompt.py -v
```

Expected: FAIL -- `ModuleNotFoundError: No module named 'diagram_beautifier.prompt'`

- [ ] **Step 3: Write the implementation**

Create `diagram_beautifier/prompt.py`:

```python
"""Build nano-banana generate prompts for diagram beautification.

Combines the selected aesthetic template with a structural preservation
modifier to ensure nano-banana enhances visual treatment without altering
diagram topology or labels.
"""

from __future__ import annotations

STRUCTURAL_PRESERVATION_MODIFIER = """\
STRUCTURAL PRESERVATION REQUIREMENTS:
- This is a diagram beautification. The reference image shows the exact topology to preserve.
- Maintain all node positions, connections, and directional flow from the reference image.
- Reproduce every text label EXACTLY as shown -- spelling, capitalization, and content must match.
- Preserve the directed/undirected nature of all edges.
- Enhance the visual presentation (colors, shapes, textures, lighting) without altering the structure.
- Node shapes may be stylized to match the aesthetic but must remain visually distinct and readable."""


def build_beautify_prompt(
    aesthetic_template: str,
    diagram_type: str,
    node_labels: list[str],
    edge_labels: list[str],
) -> str:
    """Build a nano-banana generate prompt for diagram beautification.

    Args:
        aesthetic_template: The full aesthetic prompt template text
            (e.g., from the Style Guide aesthetic section).
        diagram_type: The diagram type (``"digraph"``, ``"flowchart"``, etc.).
        node_labels: All node labels from the parsed source (ground truth).
        edge_labels: All edge labels from the parsed source (ground truth).

    Returns:
        A complete generation prompt string.
    """
    lines: list[str] = [
        f"Beautify this {diagram_type} diagram as a polished, publication-ready visual.",
        "",
        "AESTHETIC STYLE:",
        aesthetic_template,
        "",
        STRUCTURAL_PRESERVATION_MODIFIER,
        "",
        "EXACT TEXT LABELS TO REPRODUCE:",
        f"Node labels: {', '.join(node_labels)}",
    ]

    if edge_labels:
        lines.append(f"Edge labels: {', '.join(edge_labels)}")

    lines += [
        "",
        "Render every label listed above with precise spelling. Do not omit, "
        "truncate, or paraphrase any label.",
    ]

    return "\n".join(lines)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_diagram_prompt.py -v
```

Expected: All 8 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add diagram_beautifier/prompt.py tests/test_diagram_prompt.py && git commit -m "feat(diagram): add beautification prompt builder with structural preservation"
```

---

## Task 6: Label Fidelity + Structural Accuracy Review Prompts

**Files:**
- Create: `diagram_beautifier/review.py`
- Create: `tests/test_diagram_review.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_diagram_review.py`:

```python
"""Tests for diagram_beautifier/review.py -- quality review prompt builders."""

from __future__ import annotations

from diagram_beautifier.review import (
    build_label_fidelity_prompt,
    build_structural_accuracy_prompt,
)


# ---------------------------------------------------------------------------
# Label fidelity prompt
# ---------------------------------------------------------------------------


def test_label_fidelity_prompt_includes_all_node_labels() -> None:
    """The label fidelity prompt lists all node labels as ground truth."""
    prompt = build_label_fidelity_prompt(
        node_labels=["Load Balancer", "Web Server", "Database"],
        edge_labels=["HTTP", "SQL"],
    )
    assert "Load Balancer" in prompt
    assert "Web Server" in prompt
    assert "Database" in prompt


def test_label_fidelity_prompt_includes_edge_labels() -> None:
    """The label fidelity prompt lists all edge labels as ground truth."""
    prompt = build_label_fidelity_prompt(
        node_labels=["A", "B"],
        edge_labels=["HTTP/443", "gRPC"],
    )
    assert "HTTP/443" in prompt
    assert "gRPC" in prompt


def test_label_fidelity_prompt_mentions_ground_truth() -> None:
    """The prompt uses 'ground truth' language for the label list."""
    prompt = build_label_fidelity_prompt(
        node_labels=["A"], edge_labels=[]
    )
    assert "ground truth" in prompt.lower()


def test_label_fidelity_prompt_asks_for_pass_or_needs_refinement() -> None:
    """The prompt asks for PASS or NEEDS_REFINEMENT rating."""
    prompt = build_label_fidelity_prompt(
        node_labels=["A"], edge_labels=[]
    )
    assert "PASS" in prompt
    assert "NEEDS_REFINEMENT" in prompt


# ---------------------------------------------------------------------------
# Structural accuracy prompt
# ---------------------------------------------------------------------------


def test_structural_accuracy_prompt_includes_node_count() -> None:
    """The structural accuracy prompt includes node count."""
    prompt = build_structural_accuracy_prompt(
        node_count=12,
        edge_count=15,
        node_labels=["A", "B", "C"],
        edge_pairs=[("A", "B"), ("B", "C")],
    )
    assert "12" in prompt


def test_structural_accuracy_prompt_includes_edge_count() -> None:
    """The structural accuracy prompt includes edge count."""
    prompt = build_structural_accuracy_prompt(
        node_count=12,
        edge_count=15,
        node_labels=["A", "B", "C"],
        edge_pairs=[("A", "B"), ("B", "C")],
    )
    assert "15" in prompt


def test_structural_accuracy_prompt_lists_major_nodes() -> None:
    """The structural accuracy prompt lists major node labels."""
    prompt = build_structural_accuracy_prompt(
        node_count=5,
        edge_count=4,
        node_labels=["Load Balancer", "API Gateway", "Database"],
        edge_pairs=[("Load Balancer", "API Gateway")],
    )
    assert "Load Balancer" in prompt
    assert "API Gateway" in prompt
    assert "Database" in prompt


def test_structural_accuracy_prompt_lists_key_connections() -> None:
    """The structural accuracy prompt lists key edge pairs."""
    prompt = build_structural_accuracy_prompt(
        node_count=3,
        edge_count=2,
        node_labels=["A", "B", "C"],
        edge_pairs=[("A", "B"), ("B", "C")],
    )
    # Should contain arrow notation like "A -> B"
    assert "A" in prompt and "B" in prompt


def test_structural_accuracy_prompt_asks_for_rating() -> None:
    """The structural accuracy prompt asks for PASS or NEEDS_REFINEMENT."""
    prompt = build_structural_accuracy_prompt(
        node_count=3,
        edge_count=2,
        node_labels=["A", "B"],
        edge_pairs=[("A", "B")],
    )
    assert "PASS" in prompt
    assert "NEEDS_REFINEMENT" in prompt
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_diagram_review.py -v
```

Expected: FAIL -- `ModuleNotFoundError: No module named 'diagram_beautifier.review'`

- [ ] **Step 3: Write the implementation**

Create `diagram_beautifier/review.py`:

```python
"""Quality review prompt builders for diagram-specific dimensions.

Extends the standard 5-dimension quality review with:
- Label Fidelity: verifies all text labels from source are accurately reproduced
- Structural Accuracy: verifies node count and major connections are represented
"""

from __future__ import annotations


def build_label_fidelity_prompt(
    node_labels: list[str],
    edge_labels: list[str],
) -> str:
    """Build a nano-banana analyze prompt for label fidelity checking.

    Args:
        node_labels: All node labels from the parsed source (ground truth).
        edge_labels: All edge labels from the parsed source (ground truth).

    Returns:
        An evaluation prompt string for nano-banana analyze.
    """
    lines: list[str] = [
        "LABEL FIDELITY CHECK:",
        "",
        "The source diagram contains these exact labels (ground truth):",
        f"Nodes: {', '.join(node_labels)}",
    ]

    if edge_labels:
        lines.append(f"Edge labels: {', '.join(edge_labels)}")

    lines += [
        "",
        "Check EVERY label in the generated image against this ground truth.",
        "Are any labels misspelled, truncated, missing, or replaced with "
        "different text? List each discrepancy.",
        "",
        "Rating: PASS (all labels correct) or NEEDS_REFINEMENT (any label wrong).",
    ]

    return "\n".join(lines)


def build_structural_accuracy_prompt(
    node_count: int,
    edge_count: int,
    node_labels: list[str],
    edge_pairs: list[tuple[str, str]],
) -> str:
    """Build a nano-banana analyze prompt for structural accuracy checking.

    Args:
        node_count: Total node count from the parsed source.
        edge_count: Total edge count from the parsed source.
        node_labels: All node labels (for listing major nodes).
        edge_pairs: List of (from_label, to_label) tuples for key connections.

    Returns:
        An evaluation prompt string for nano-banana analyze.
    """
    connections = "\n".join(
        f"  {src} \u2192 {dst}" for src, dst in edge_pairs
    )

    lines: list[str] = [
        "STRUCTURAL ACCURACY CHECK:",
        "",
        f"The source diagram has {node_count} nodes and {edge_count} connections.",
        f"Major nodes: {', '.join(node_labels)}",
        "Key connections:",
        connections,
        "",
        "Verify: Are all major nodes visible in the output? Are the primary "
        "connection paths represented? Is the directional flow preserved?",
        "",
        "Rating: PASS (topology preserved) or NEEDS_REFINEMENT (nodes/edges missing).",
    ]

    return "\n".join(lines)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_diagram_review.py -v
```

Expected: All 9 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add diagram_beautifier/review.py tests/test_diagram_review.py && git commit -m "feat(diagram): add label fidelity and structural accuracy review prompts"
```

---

## Task 7: diagram-beautifier Agent

**Files:**
- Create: `agents/diagram-beautifier.md`
- Create: `tests/test_diagram_beautifier_agent.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_diagram_beautifier_agent.py`:

```python
"""Tests for agents/diagram-beautifier.md structure and correctness.

Validates the agent file has the correct YAML frontmatter and Markdown
workflow structure matching the project's agent conventions.
"""

from pathlib import Path

AGENT_FILE = Path(__file__).parent.parent / "agents" / "diagram-beautifier.md"


def _read_agent() -> str:
    return AGENT_FILE.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# File existence and frontmatter
# ---------------------------------------------------------------------------


def test_agent_file_exists() -> None:
    """agents/diagram-beautifier.md must exist."""
    assert AGENT_FILE.exists(), f"Agent file not found: {AGENT_FILE}"


def test_agent_has_yaml_frontmatter() -> None:
    """Agent file must start with YAML frontmatter (--- delimiters)."""
    content = _read_agent()
    assert content.startswith("---"), "Agent file must start with '---' frontmatter"
    # Must have closing frontmatter delimiter
    second_delimiter = content.index("---", 3)
    assert second_delimiter > 3, "Must have closing '---' frontmatter delimiter"


def test_agent_frontmatter_has_meta_name() -> None:
    """Frontmatter must contain meta.name: diagram-beautifier."""
    content = _read_agent()
    frontmatter_end = content.index("---", 3)
    frontmatter = content[:frontmatter_end]
    assert "name: diagram-beautifier" in frontmatter


def test_agent_frontmatter_has_model_role() -> None:
    """Frontmatter must contain model_role with image-gen."""
    content = _read_agent()
    frontmatter_end = content.index("---", 3)
    frontmatter = content[:frontmatter_end]
    assert "image-gen" in frontmatter


# ---------------------------------------------------------------------------
# Workflow steps: 9-step pipeline
# ---------------------------------------------------------------------------


def test_workflow_has_9_steps() -> None:
    """Agent workflow must contain 9 numbered steps."""
    content = _read_agent()
    for n in range(1, 10):
        assert f"{n}. **" in content or f"{n}." in content, (
            f"Step {n} not found in agents/diagram-beautifier.md"
        )


def test_workflow_step_order() -> None:
    """Key workflow steps appear in the correct order."""
    content = _read_agent()
    keywords_in_order = [
        "parse",           # Step 1: Parse source
        "dependency",      # Step 2: Dependency check
        "aesthetic",       # Step 3: Aesthetic selection
        "render",          # Step 4: Render to plain PNG
        "decompos",        # Step 5: Panel decomposition
        "beautif",         # Step 6: Beautify
        "review",          # Step 7: Quality review
        "assembl",         # Step 8: Assemble
        "return",          # Step 9: Return results
    ]
    lower = content.lower()
    last_pos = -1
    for keyword in keywords_in_order:
        pos = lower.find(keyword)
        assert pos != -1, f"Keyword '{keyword}' not found in agent"
        assert pos > last_pos, (
            f"Keyword '{keyword}' (pos {pos}) should appear after "
            f"previous keyword (pos {last_pos})"
        )
        last_pos = pos


# ---------------------------------------------------------------------------
# Diagram-specific content
# ---------------------------------------------------------------------------


def test_agent_mentions_render_first() -> None:
    """Agent must describe the render-first architecture."""
    content = _read_agent()
    lower = content.lower()
    assert "render" in lower and "reference" in lower, (
        "Agent must describe render-first approach using reference image"
    )


def test_agent_mentions_structural_preservation() -> None:
    """Agent must mention structural preservation in beautification."""
    content = _read_agent()
    lower = content.lower()
    assert "structural preservation" in lower or "preserve" in lower


def test_agent_mentions_label_fidelity() -> None:
    """Agent must mention label fidelity as a review dimension."""
    content = _read_agent()
    lower = content.lower()
    assert "label fidelity" in lower


def test_agent_mentions_nano_banana() -> None:
    """Agent must reference nano-banana tool."""
    content = _read_agent()
    assert "nano-banana" in content


def test_agent_mentions_stitch_panels() -> None:
    """Agent must reference stitch_panels for multi-panel assembly."""
    content = _read_agent()
    assert "stitch_panels" in content


def test_agent_references_style_guide() -> None:
    """Agent must reference the shared style guide."""
    content = _read_agent()
    assert "style-guide" in content or "style guide" in content.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_diagram_beautifier_agent.py -v
```

Expected: FAIL -- `FileNotFoundError` or `AssertionError: Agent file not found`

- [ ] **Step 3: Write the agent file**

Create `agents/diagram-beautifier.md` with the following complete content:

```markdown
---
meta:
  name: diagram-beautifier
  model_role: [image-gen, creative, general]
  description: |
    Expert diagram beautifier that takes Graphviz (.dot) or Mermaid diagram
    source files and renders them as beautiful infographic-quality visuals
    using the existing aesthetic system, preserving the original diagram's
    topology and labels. Uses a render-first architecture: renders plain PNG
    via CLI tools, then beautifies with nano-banana using the rendered image
    as a structural reference.

    **Authoritative on:** diagram beautification, Graphviz rendering, Mermaid
    rendering, graph visualization, topology-preserving visual transformation

    **MUST be used for:**
    - Any request to beautify, style, or enhance a .dot or Mermaid diagram
    - Requests that provide diagram source (digraph, graph, flowchart, etc.)
    - Requests mentioning diagram files (.dot, .mmd, .mermaid extensions)

    <example>
    user: 'Beautify this architecture diagram in claymation style' (with .dot file)
    assistant: 'I'll delegate to diagram-beautifier to render and beautify this diagram.'
    <commentary>
    Diagram source input with beautification intent triggers diagram-beautifier.
    </commentary>
    </example>

    <example>
    user: 'Make this flowchart look professional' (with Mermaid source)
    assistant: 'I'll use diagram-beautifier to transform this Mermaid diagram.'
    <commentary>
    Mermaid source with visual enhancement intent routes to diagram-beautifier.
    </commentary>
    </example>
---

# Diagram Beautifier

You are an expert diagram beautifier with image generation capabilities via the
`nano-banana` tool (`generate` and `analyze` operations) and panel assembly via
the `stitch_panels` tool. You transform structurally correct but visually plain
diagrams into polished, publication-ready visuals.

**Execution model:** You run as a sub-session. Parse the diagram, verify
dependencies, render a plain reference PNG, then beautify using nano-banana
*(unless aesthetic selection is required -- see Step 3)*.

## Design Knowledge

For aesthetic templates, prompt engineering patterns, and evaluation criteria,
see the shared Style Guide:

@infographic-builder:docs/style-guide.md

## Operating Principles

1. **Render first, beautify second** -- always render the source to a plain PNG
   as the structural anchor before any beautification
2. **Preserve topology** -- node positions, connections, labels, and directional
   flow must be maintained exactly
3. **Explain your choices** -- describe the aesthetic applied and any
   decomposition decisions
4. **Iterate if given feedback** -- treat follow-up messages as refinement requests

## Workflow

1. **Parse the source**: Extract nodes, edges, labels, and subgraphs from the
   Graphviz (.dot) or Mermaid input. Determine the diagram format and type.
   Use `diagram_beautifier.parser.parse_diagram_source()` to produce the
   normalized structure: nodes, edges, subgraphs, node_count, edge_count.

2. **Dependency check**: Verify the required CLI tool is available.
   - `.dot` input -> check for `dot` (Graphviz) via `which dot`
   - Mermaid input -> check for `mmdc` (Mermaid CLI) via `which mmdc`

   If the tool is unavailable, fail immediately with clear install instructions:
   - Graphviz: `brew install graphviz` (macOS), `apt-get install graphviz` (Ubuntu)
   - Mermaid CLI: `npm install -g @mermaid-js/mermaid-cli`

3. **Aesthetic selection**: Before beautifying, guide the user to a visual style.
   Reuse the shared aesthetic system from the Style Guide -- all 6 curated
   aesthetics plus freeform are available.

   **Check for inline style specification.** If the user already described an
   aesthetic (e.g., "beautify in claymation style"), skip to step 4. This is
   the **two-turn shortcut**.

   **If no style was specified**, present the options and halt:

   ```
   For this [diagram type] diagram, I'd recommend [observation about layout].

   Choose a style, or describe your own:

     1. Clean Minimalist       4. Hand-Drawn Sketchnote
     2. Dark Mode Tech         5. Claymation Studio
     3. Bold Editorial         6. Lego Brick Builder

     Or describe any style -- "blueprint", "watercolor",
     "retro pixel art", "neon wireframe" -- get creative.
   ```

   **Then stop and wait for the user's selection.**

4. **Render to plain PNG**: Render the source to a structurally faithful but
   visually plain PNG using the appropriate CLI tool:
   - Graphviz: `dot -Tpng -Gdpi=150 input.dot -o /tmp/diagram_plain.png`
   - Mermaid: `mmdc -i input.mmd -o /tmp/diagram_plain.png -w 2048 -H 1536 --scale 2`

   This plain PNG becomes the `reference_image_path` for nano-banana generation.

5. **Panel decomposition**: Based on node count and subgraph structure, decide
   single vs. multi-panel layout:
   - 1-10 nodes: single panel
   - 11-25 nodes, 0-1 subgraphs: single panel
   - 11-25 nodes, 2+ subgraphs: split by subgraph (2-3 panels)
   - 26-40 nodes: split by subgraph (2-4 panels)
   - 40+ nodes: split by subgraph (3-6 panels, max 6)

   Use `diagram_beautifier.decompose.decide_panels()` for the decision.

6. **Beautify**: Generate beautified image(s) via `nano-banana generate`:

   **Single-panel path:**
   - Use `reference_image_path` = plain rendered PNG
   - Prompt = aesthetic template + structural preservation modifier
   - Include all node/edge labels in the prompt for text accuracy

   **Multi-panel path:**
   - Panel 1 generated first with plain PNG as reference (style anchor)
   - Call `nano-banana analyze` on Panel 1 for style reconciliation
   - Panels 2-N reference Panel 1 for style consistency AND their own
     subgraph structure via the structural preservation modifier

7. **Quality review**: Analyze each panel using `nano-banana analyze` with:
   - Standard 5 dimensions (content accuracy, layout quality, visual clarity,
     prompt fidelity, aesthetic fidelity)
   - **Label fidelity** -- check all text labels against source ground truth
   - **Structural accuracy** -- verify node count and major connections

   Max 1 refinement pass per panel, targeting only specific issues identified.

8. **Assemble** (multi-panel only): Call `stitch_panels` to combine panels.
   Choose direction based on diagram flow:
   - Left-to-right flow (pipeline, data flow) -> `horizontal`
   - Top-to-bottom flow (hierarchy, sequence) -> `vertical`
   - 5+ panels -> always `vertical`
   - Ambiguous -> `vertical` (safer default)

   Output naming: `./infographics/{name}_panel_N.png` and
   `./infographics/{name}_combined.png`

9. **Return results**: image path(s) + design rationale + quality review summary
   (including label fidelity and structural accuracy results) + suggestions for
   next steps

## Using nano-banana generate

| Parameter | Required | Description |
|-----------|----------|-------------|
| `operation` | yes | Always `"generate"` |
| `prompt` | yes | Aesthetic template + structural preservation modifier |
| `output_path` | yes | Where to save the image |
| `reference_image_path` | **yes** | Plain rendered PNG (structural anchor) |

## Using nano-banana analyze

| Parameter | Required | Description |
|-----------|----------|-------------|
| `operation` | yes | Always `"analyze"` |
| `prompt` | yes | Evaluation criteria (standard + label fidelity + structural accuracy) |
| `image_path` | yes | Path to the beautified image to evaluate |

## Using stitch_panels

| Parameter | Required | Description |
|-----------|----------|-------------|
| `panel_paths` | yes | Ordered list of PNG file paths to combine |
| `output_path` | yes | File path for the combined output PNG |
| `direction` | **yes** | `"vertical"` or `"horizontal"` -- always specify explicitly |

## Output Contract

Your response MUST include:
- The generated image path(s) (or a clear error if generation failed)
- A brief design rationale (2-4 sentences)
- Quality review summary (standard dimensions + label fidelity + structural accuracy)
- Suggested next steps

---

@foundation:context/shared/common-agent-base.md
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_diagram_beautifier_agent.py -v
```

Expected: All 13 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add agents/diagram-beautifier.md tests/test_diagram_beautifier_agent.py && git commit -m "feat(diagram): add diagram-beautifier agent with 9-step workflow"
```

---

## Task 8: Wire Agent into Behavior YAML

**Files:**
- Create: `context/diagram-beautifier-awareness.md`
- Modify: `behaviors/infographic.yaml`
- Create: `tests/test_diagram_wiring.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_diagram_wiring.py`:

```python
"""Tests for diagram-beautifier wiring into the behavior YAML and context."""

from pathlib import Path

import yaml

BEHAVIOR_FILE = Path(__file__).parent.parent / "behaviors" / "infographic.yaml"
AWARENESS_FILE = (
    Path(__file__).parent.parent / "context" / "diagram-beautifier-awareness.md"
)


# ---------------------------------------------------------------------------
# Behavior YAML wiring
# ---------------------------------------------------------------------------


def test_behavior_yaml_includes_diagram_beautifier_agent() -> None:
    """behaviors/infographic.yaml must include the diagram-beautifier agent."""
    content = BEHAVIOR_FILE.read_text(encoding="utf-8")
    data = yaml.safe_load(content)
    agent_includes = data.get("agents", {}).get("include", [])
    agent_refs = [
        ref if isinstance(ref, str) else str(ref) for ref in agent_includes
    ]
    assert any("diagram-beautifier" in ref for ref in agent_refs), (
        f"diagram-beautifier agent not found in agents.include: {agent_refs}"
    )


def test_behavior_yaml_includes_diagram_context() -> None:
    """behaviors/infographic.yaml must include diagram-beautifier-awareness context."""
    content = BEHAVIOR_FILE.read_text(encoding="utf-8")
    data = yaml.safe_load(content)
    context_includes = data.get("context", {}).get("include", [])
    context_refs = [
        ref if isinstance(ref, str) else str(ref) for ref in context_includes
    ]
    assert any("diagram-beautifier" in ref for ref in context_refs), (
        f"diagram-beautifier context not found in context.include: {context_refs}"
    )


# ---------------------------------------------------------------------------
# Awareness context file
# ---------------------------------------------------------------------------


def test_diagram_awareness_file_exists() -> None:
    """context/diagram-beautifier-awareness.md must exist."""
    assert AWARENESS_FILE.exists(), f"File not found: {AWARENESS_FILE}"


def test_diagram_awareness_mentions_dot_extension() -> None:
    """Awareness context must mention .dot file detection."""
    content = AWARENESS_FILE.read_text(encoding="utf-8")
    assert ".dot" in content


def test_diagram_awareness_mentions_mermaid_keywords() -> None:
    """Awareness context must mention Mermaid diagram keywords."""
    content = AWARENESS_FILE.read_text(encoding="utf-8")
    lower = content.lower()
    assert "flowchart" in lower or "mermaid" in lower


def test_diagram_awareness_mentions_delegation() -> None:
    """Awareness context must instruct delegation to diagram-beautifier."""
    content = AWARENESS_FILE.read_text(encoding="utf-8")
    assert "diagram-beautifier" in content
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_diagram_wiring.py -v
```

Expected: FAIL -- `AssertionError: diagram-beautifier agent not found in agents.include`

- [ ] **Step 3: Create the awareness context file**

Create `context/diagram-beautifier-awareness.md`:

```markdown
# Diagram Beautifier -- Routing Context

## Diagram Input Detection

When the user provides input matching any of these patterns, delegate to
`infographic-builder:diagram-beautifier` instead of `infographic-builder:infographic-builder`:

### File extensions
- `.dot` -- Graphviz source file
- `.mmd` or `.mermaid` -- Mermaid source file

### Inline source patterns
Detect diagram source when the user's message contains text beginning with:
- `digraph` or `graph {` -- Graphviz directed/undirected graph
- `flowchart` -- Mermaid flowchart
- `sequenceDiagram` -- Mermaid sequence diagram
- `classDiagram` -- Mermaid class diagram
- `stateDiagram` -- Mermaid state diagram
- `erDiagram` -- Mermaid ER diagram
- `graph TD` or `graph LR` -- Mermaid graph with direction

### Intent keywords
- "beautify this diagram", "make this diagram pretty", "style this graph"
- Any request combining a diagram source with visual enhancement intent

## Routing Rule

If diagram source is detected -> delegate to `infographic-builder:diagram-beautifier`

If natural language topic (no diagram source) -> delegate to `infographic-builder:infographic-builder` (existing behavior, unchanged)

The diagram-beautifier agent handles parsing, rendering, aesthetic selection,
beautification, quality review, and assembly. Pass the user's request as-is.
```

- [ ] **Step 4: Update the behavior YAML**

Modify `behaviors/infographic.yaml`. The current file is:

```yaml
bundle:
  name: infographic-behavior
  version: 0.1.0
  description: Infographic design capability -- image generation via nano-banana, designer agent, awareness context

context:
  include:
    - infographic-builder:context/infographic-awareness.md

tools:
  - module: tool-nano-banana
    source: git+https://github.com/kenotron-ms/amplifier-module-tool-nano-banana@main
  - module: tool-stitch-panels
    source: ../modules/tool-stitch-panels

agents:
  include:
    - infographic-builder:infographic-builder
```

Add the new agent and context entries. Change the `context.include` section to:

```yaml
context:
  include:
    - infographic-builder:context/infographic-awareness.md
    - infographic-builder:context/diagram-beautifier-awareness.md
```

Change the `agents.include` section to:

```yaml
agents:
  include:
    - infographic-builder:infographic-builder
    - infographic-builder:diagram-beautifier
```

The complete updated file should be:

```yaml
bundle:
  name: infographic-behavior
  version: 0.1.0
  description: Infographic design capability -- image generation via nano-banana, designer agent, awareness context

context:
  include:
    - infographic-builder:context/infographic-awareness.md
    - infographic-builder:context/diagram-beautifier-awareness.md

tools:
  - module: tool-nano-banana
    source: git+https://github.com/kenotron-ms/amplifier-module-tool-nano-banana@main
  - module: tool-stitch-panels
    source: ../modules/tool-stitch-panels

agents:
  include:
    - infographic-builder:infographic-builder
    - infographic-builder:diagram-beautifier
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
python -m pytest tests/test_diagram_wiring.py -v
```

Expected: All 6 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add context/diagram-beautifier-awareness.md behaviors/infographic.yaml tests/test_diagram_wiring.py && git commit -m "feat(diagram): wire diagram-beautifier agent into behavior YAML and add routing context"
```

---

## Task 9: Root Routing Updates

**Files:**
- Modify: `bundle.md`
- Modify: `context/infographic-awareness.md`
- Create: `tests/test_diagram_routing.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_diagram_routing.py`:

```python
"""Tests for root routing updates to detect diagram input and delegate."""

from pathlib import Path

BUNDLE_FILE = Path(__file__).parent.parent / "bundle.md"
AWARENESS_FILE = Path(__file__).parent.parent / "context" / "infographic-awareness.md"


# ---------------------------------------------------------------------------
# bundle.md updates
# ---------------------------------------------------------------------------


def test_bundle_references_diagram_awareness() -> None:
    """bundle.md must reference the diagram-beautifier-awareness context."""
    content = BUNDLE_FILE.read_text(encoding="utf-8")
    assert "diagram-beautifier-awareness" in content


# ---------------------------------------------------------------------------
# infographic-awareness.md updates
# ---------------------------------------------------------------------------


def test_infographic_awareness_mentions_diagram_detection() -> None:
    """infographic-awareness.md must describe diagram input detection."""
    content = AWARENESS_FILE.read_text(encoding="utf-8")
    lower = content.lower()
    assert "diagram" in lower, (
        "infographic-awareness.md must mention diagram input detection"
    )


def test_infographic_awareness_mentions_dot_pattern() -> None:
    """infographic-awareness.md must mention .dot detection pattern."""
    content = AWARENESS_FILE.read_text(encoding="utf-8")
    assert ".dot" in content


def test_infographic_awareness_mentions_mermaid_pattern() -> None:
    """infographic-awareness.md must mention Mermaid detection patterns."""
    content = AWARENESS_FILE.read_text(encoding="utf-8")
    lower = content.lower()
    assert "flowchart" in lower or "mermaid" in lower


def test_infographic_awareness_mentions_digraph_pattern() -> None:
    """infographic-awareness.md must mention digraph detection pattern."""
    content = AWARENESS_FILE.read_text(encoding="utf-8")
    assert "digraph" in content


def test_infographic_awareness_routes_diagrams_to_beautifier() -> None:
    """infographic-awareness.md must route diagrams to diagram-beautifier."""
    content = AWARENESS_FILE.read_text(encoding="utf-8")
    assert "diagram-beautifier" in content


def test_infographic_awareness_preserves_existing_delegation() -> None:
    """infographic-awareness.md must still delegate non-diagram requests to infographic-builder."""
    content = AWARENESS_FILE.read_text(encoding="utf-8")
    assert "infographic-builder" in content
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_diagram_routing.py -v
```

Expected: FAIL -- `AssertionError: infographic-awareness.md must mention diagram input detection` (the existing file does not mention diagrams)

- [ ] **Step 3: Update bundle.md**

Modify `bundle.md` to add the diagram-beautifier-awareness context reference. The current file is:

```markdown
---
bundle:
  name: infographic-builder
  version: 0.1.0
  description: AI-powered infographic design with image generation via nano-banana

  includes:
    - bundle: git+https://github.com/microsoft/amplifier-foundation@main
    - bundle: infographic-builder:behaviors/infographic
---

# Infographic Builder

@infographic-builder:context/infographic-awareness.md

---

@foundation:context/shared/common-system-base.md
```

Change it to:

```markdown
---
bundle:
  name: infographic-builder
  version: 0.1.0
  description: AI-powered infographic design with image generation via nano-banana

  includes:
    - bundle: git+https://github.com/microsoft/amplifier-foundation@main
    - bundle: infographic-builder:behaviors/infographic
---

# Infographic Builder

@infographic-builder:context/infographic-awareness.md

@infographic-builder:context/diagram-beautifier-awareness.md

---

@foundation:context/shared/common-system-base.md
```

The only change is adding the `@infographic-builder:context/diagram-beautifier-awareness.md` line after the existing awareness context reference.

- [ ] **Step 4: Update context/infographic-awareness.md**

Modify `context/infographic-awareness.md` to add diagram detection to the routing logic. The existing file ends with the `## Prerequisites` section. Insert a new section **before** `## Prerequisites` (after `## How to Delegate`) that describes diagram routing.

Add the following text between the end of the `## How to Delegate` section (after the paragraph starting "The agent automatically handles:") and the `## Prerequisites` section:

```markdown

## Diagram Input Detection

**Before delegating, check if the input is diagram source.** If any of these
patterns are present, delegate to `infographic-builder:diagram-beautifier`
instead of `infographic-builder:infographic-builder`:

- **File extensions:** `.dot`, `.mmd`, `.mermaid`
- **Inline source patterns:** Input text starting with `digraph`, `graph {`,
  `flowchart`, `sequenceDiagram`, `classDiagram`, `stateDiagram`, `erDiagram`,
  `graph TD`, `graph LR`
- **Intent keywords:** "beautify this diagram", "make this diagram pretty",
  "style this graph", or any combination of diagram source + visual enhancement

**Routing rule:**
- Diagram source detected -> delegate to `infographic-builder:diagram-beautifier`
- Natural language topic (no diagram source) -> delegate to `infographic-builder:infographic-builder`
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
python -m pytest tests/test_diagram_routing.py -v
```

Expected: All 7 tests PASS.

- [ ] **Step 6: Run the full test suite to verify no regressions**

```bash
python -m pytest tests/ -v
```

Expected: All existing tests PASS alongside all new tests. No regressions in `test_infographic_builder.py` or any other existing test files.

- [ ] **Step 7: Commit**

```bash
git add bundle.md context/infographic-awareness.md tests/test_diagram_routing.py && git commit -m "feat(diagram): update root routing to detect diagram input and delegate to diagram-beautifier"
```

---

## Summary

| Task | Component | Tests | Files |
|------|-----------|-------|-------|
| 1 | Source parser (dot + Mermaid) | 14 | `diagram_beautifier/__init__.py`, `diagram_beautifier/parser.py`, `tests/test_diagram_parser.py` |
| 2 | Dependency checker (dot/mmdc) | 6 | `diagram_beautifier/deps.py`, `tests/test_diagram_deps.py` |
| 3 | Plain PNG renderer | 4 | `diagram_beautifier/renderer.py`, `tests/test_diagram_renderer.py` |
| 4 | Panel decomposition | 8 | `diagram_beautifier/decompose.py`, `tests/test_diagram_decompose.py` |
| 5 | Beautification prompt builder | 8 | `diagram_beautifier/prompt.py`, `tests/test_diagram_prompt.py` |
| 6 | Label fidelity + structural accuracy review | 9 | `diagram_beautifier/review.py`, `tests/test_diagram_review.py` |
| 7 | diagram-beautifier agent (9-step workflow) | 13 | `agents/diagram-beautifier.md`, `tests/test_diagram_beautifier_agent.py` |
| 8 | Behavior YAML wiring + awareness context | 6 | `context/diagram-beautifier-awareness.md`, `behaviors/infographic.yaml`, `tests/test_diagram_wiring.py` |
| 9 | Root routing (bundle.md + infographic-awareness) | 7 | `bundle.md`, `context/infographic-awareness.md`, `tests/test_diagram_routing.py` |
| **Total** | **6 Python modules + 1 agent + 2 context files + 2 modified files** | **75** | **9 new + 2 modified** |
