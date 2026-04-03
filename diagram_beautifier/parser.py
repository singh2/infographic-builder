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
    if fmt in ("mermaid", "mmd"):
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
    _dot_keywords = frozenset(
        {
            "label",
            "style",
            "color",
            "fontcolor",
            "bgcolor",
            "rank",
            "rankdir",
            "fontname",
            "fontsize",
            "node",
            "edge",
            "graph",
            "digraph",
            "subgraph",
            "compound",
            "newrank",
        }
    )

    # Extract subgraphs
    subgraph_pattern = re.compile(r"subgraph\s+(\w+)\s*\{([^}]*)\}", re.DOTALL)
    for match in subgraph_pattern.finditer(source):
        sg_id = match.group(1)
        sg_body = match.group(2)

        # Extract subgraph label
        label_match = re.search(r'label\s*=\s*"([^"]*)"', sg_body)
        sg_name = label_match.group(1) if label_match else sg_id

        # Extract node IDs declared in this subgraph
        sg_node_ids: list[str] = []
        for node_match in re.finditer(r"^\s*(\w+)\s*[\[;]", sg_body, re.MULTILINE):
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

            edges.append(
                {
                    "from": from_id,
                    "to": to_id,
                    "label": edge_label,
                }
            )

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
