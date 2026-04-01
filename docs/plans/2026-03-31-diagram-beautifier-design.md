# Diagram Beautifier Design

## Goal

Add a dedicated diagram beautifier agent that takes Graphviz (.dot) or Mermaid diagram source files and renders them as beautiful infographic-quality visuals using the existing aesthetic system, preserving the original diagram's topology and labels.

## Background

infographic-builder currently turns natural language topics into polished infographics. It handles layout selection, panel decomposition, style consistency, and quality review — but it always starts from a topic description and builds the visual from scratch.

A common adjacent use case is structured diagrams: users already have a Graphviz or Mermaid definition that captures the exact topology they want (nodes, edges, clusters, labels). What they need is not content creation but **visual transformation** — taking a technically correct but visually plain diagram and rendering it in a compelling aesthetic. This is a different input modality (structured source vs. natural language) with different constraints (preserve existing structure vs. generate structure), which warrants a separate agent rather than overloading the infographic builder.

## Approach

**Render-first architecture with a dedicated agent.** A new `diagram-beautifier` agent sits alongside the existing `infographic-builder` agent. The root session detects whether the input is a diagram source file or a natural language topic and routes accordingly.

The key architectural insight is **render-first**: instead of asking nano-banana to interpret the diagram source and generate a visual from scratch (which loses topological fidelity), the agent first renders the source to a plain PNG using the standard CLI tools (`dot` for Graphviz, `mmdc` for Mermaid), then passes that rendered PNG as `reference_image_path` to nano-banana. The reference image anchors the structure — nano-banana's job is to beautify, not to interpret.

We chose this over:
- **Direct source-to-image generation** — asking nano-banana to read .dot/Mermaid syntax and generate directly. This loses topological fidelity: Gemini would need to parse graph syntax, compute layout, and render — all things that `dot` and `mmdc` already do correctly. The reference image makes structure preservation a visual constraint rather than a language-understanding one.
- **Integrating into the infographic agent** — adding diagram handling as a mode inside the existing agent. The infographic agent's workflow (content analysis → layout selection → decomposition by content density) is fundamentally misaligned with diagram input (fixed structure → decomposition by graph topology). Mixing the two would complicate both paths.

## Architecture

```
User input
  │
  ├─ Natural language topic ──→ infographic-builder (existing, unchanged)
  │
  └─ .dot / Mermaid source ──→ diagram-beautifier (new)
                                  │
                                  ├─ 1. Parse source (nodes, edges, labels, subgraphs)
                                  ├─ 2. Dependency check (dot / mmdc available?)
                                  ├─ 3. Aesthetic selection (shared system, all 6 + freeform)
                                  ├─ 4. Render to plain PNG (dot / mmdc CLI)
                                  ├─ 5. Panel decomposition (by subgraph boundaries)
                                  ├─ 6. Beautify (nano-banana generate with reference PNG)
                                  ├─ 7. Quality review (standard + label fidelity + structural accuracy)
                                  ├─ 8. Assemble (stitch_panels if multi-panel)
                                  └─ 9. Return results
```

The infographic-builder agent is completely unchanged. The diagram-beautifier agent shares the aesthetic system, nano-banana tool, and stitch_panels tool but has its own workflow, decomposition logic, and quality review dimensions.

## Components

### Root Session Routing

The root session (bundle.md or session orchestrator) detects input type and delegates:

- **Diagram source detected**: file with `.dot` or `.mmd`/`.mermaid` extension, or inline content beginning with `digraph`, `graph`, `flowchart`, `sequenceDiagram`, `classDiagram`, `stateDiagram`, `erDiagram`, `gantt`, `pie`, `gitgraph`, or other Mermaid diagram keywords.
- **Natural language detected**: everything else routes to infographic-builder as today.

### Diagram Source Parser

Parses the input source to extract structured metadata used in decomposition and quality review:

**For Graphviz (.dot):**
- Node list with labels (from `label=` attributes or node IDs as implicit labels)
- Edge list (directed/undirected)
- Subgraph/cluster declarations (from `subgraph cluster_*` blocks)
- Total node and edge count

**For Mermaid:**
- Node list with display labels (from `A[Label]`, `B((Label))`, etc.)
- Edge/connection list with optional edge labels
- Subgraph declarations (from `subgraph` blocks)
- Diagram type (flowchart, sequence, class, state, ER, gantt, etc.)
- Total node and edge count

The parser output is a normalized structure used downstream:
```
{
  "format": "dot" | "mermaid",
  "diagram_type": "digraph" | "flowchart" | "sequence" | ...,
  "nodes": [{"id": "A", "label": "Load Balancer"}, ...],
  "edges": [{"from": "A", "to": "B", "label": "HTTP"}, ...],
  "subgraphs": [{"name": "Frontend", "node_ids": ["A", "B"]}, ...],
  "node_count": 12,
  "edge_count": 15
}
```

### Dependency Checker

Before any rendering, verify the required CLI tool is available:

- `.dot` input → check for `dot` (Graphviz) via `which dot`
- Mermaid input → check for `mmdc` (Mermaid CLI) via `which mmdc`

If the tool is unavailable, fail immediately with clear install instructions:

```
Graphviz is required to render .dot diagrams but was not found.

Install with:
  macOS:  brew install graphviz
  Ubuntu: sudo apt-get install graphviz
  Fedora: sudo dnf install graphviz
```

```
Mermaid CLI is required to render Mermaid diagrams but was not found.

Install with:
  npm install -g @mermaid-js/mermaid-cli
```

### Aesthetic Selection (Shared)

The existing aesthetic selection system is reused as-is — same 6 curated aesthetics (Clean Minimalist, Dark Mode Tech, Bold Editorial, Hand-Drawn Sketchnote, Claymation Studio, Lego Brick Builder) plus freeform. No aesthetic narrowing for diagrams: all styles are available. The same in-session UX applies:

```
For this [diagram type] diagram, I'd recommend [Layout observation].

Choose a style, or describe your own:

  1. Clean Minimalist       4. Hand-Drawn Sketchnote
  2. Dark Mode Tech         5. Claymation Studio
  3. Bold Editorial         6. Lego Brick Builder

  Or describe any style — "blueprint", "watercolor",
  "retro pixel art", "neon wireframe" — get creative.
```

If the user specifies a style inline ("beautify this diagram in claymation style"), the two-turn shortcut applies — skip straight to rendering.

### Plain PNG Renderer

Renders the source to a structurally faithful but visually plain PNG:

**Graphviz:**
```bash
dot -Tpng -Gdpi=150 input.dot -o /tmp/diagram_plain.png
```

**Mermaid:**
```bash
mmdc -i input.mmd -o /tmp/diagram_plain.png -w 2048 -H 1536 --scale 2
```

The output resolution should be high enough for nano-banana to clearly see all node labels and edge connections. A minimum of 150 DPI or 2048px on the long edge is targeted.

This plain PNG becomes the `reference_image_path` for nano-banana generation — it anchors the topology so the beautification step preserves structure.

### Panel Decomposition

Panel decomposition for diagrams uses **graph structure**, not content density. This is a fundamental difference from the infographic agent, which decomposes by content density.

**Complexity thresholds:**

| Node count | Subgraphs | Panels | Strategy |
|------------|-----------|--------|----------|
| 1–10       | Any       | 1      | Single panel, entire diagram |
| 11–25      | 0–1       | 1      | Single panel, still manageable |
| 11–25      | 2+        | 2–3    | One panel per major subgraph cluster |
| 26–40      | Any       | 2–4    | Split along subgraph boundaries |
| 40+        | Any       | 3–6    | Split along subgraph boundaries, max 6 |

**Subgraph-driven splitting:**

When the source declares explicit subgraphs/clusters (e.g., `subgraph cluster_frontend { ... }`), those are the natural decomposition boundaries. Each panel covers one or more related subgraphs. Cross-subgraph edges are shown as labeled connection points at panel edges (e.g., an arrow labeled "→ Backend" at the bottom of the Frontend panel).

**No subgraphs declared:**

If the source has high node count but no subgraph declarations, the agent uses topological proximity — groups of densely interconnected nodes form implicit clusters. The agent reasons about this in its planning step rather than running a formal graph partitioning algorithm.

### Beautification (nano-banana generate)

Each panel is generated with three inputs:

1. **`reference_image_path`**: the plain rendered PNG (or the relevant subgraph portion for multi-panel)
2. **Aesthetic template**: the full prompt template from the selected aesthetic (same templates as infographic-builder)
3. **Structural preservation modifier**: an additional prompt directive specific to diagram beautification

The structural preservation modifier is appended to every diagram generation prompt:

```
STRUCTURAL PRESERVATION REQUIREMENTS:
- This is a diagram beautification. The reference image shows the exact topology to preserve.
- Maintain all node positions, connections, and directional flow from the reference image.
- Reproduce every text label EXACTLY as shown — spelling, capitalization, and content must match.
- Preserve the directed/undirected nature of all edges.
- Enhance the visual presentation (colors, shapes, textures, lighting) without altering the structure.
- Node shapes may be stylized to match the aesthetic but must remain visually distinct and readable.
```

**Multi-panel consistency** follows the same reference-image-chaining pattern as infographic-builder:
- Panel 1 is generated first (with the plain PNG as reference), establishing the style anchor.
- Post-Panel 1 style reconciliation is performed (same analyze call as infographic-builder).
- Panels 2–N reference Panel 1 for style consistency AND their own subgraph plain PNG for structural fidelity. Both reference signals are encoded in the prompt — Panel 1's path as `reference_image_path` and the subgraph structure described textually with the structural preservation modifier.

### Quality Review

The diagram beautifier extends the standard 5-dimension quality review with two diagram-specific dimensions:

#### Standard dimensions (shared with infographic-builder):
1. **Content Accuracy** — are the requested elements present?
2. **Layout Quality** — is the structure clear and well-organized?
3. **Visual Clarity** — is text readable, contrast sufficient?
4. **Prompt Fidelity** — does output match the generation prompt?
5. **Aesthetic Fidelity** — does the output match the selected aesthetic?

#### Diagram-specific dimensions (new):

6. **Label Fidelity** — are all text labels from the source diagram accurately reproduced?

   This is the hardest problem. Even with render-first + reference image, Gemini may distort, truncate, or hallucinate node labels. The review extracts all labels from the parsed source (ground truth) and checks each one against the generated output.

   Evaluation prompt addition:
   ```
   LABEL FIDELITY CHECK:
   The source diagram contains these exact labels (ground truth):
   Nodes: {list of all node labels from parser output}
   Edge labels: {list of all edge labels from parser output}

   Check EVERY label in the generated image against this ground truth.
   Are any labels misspelled, truncated, missing, or replaced with
   different text? List each discrepancy.
   Rating: PASS (all labels correct) or NEEDS_REFINEMENT (any label wrong).
   ```

7. **Structural Accuracy** — are all nodes present and are the major connections represented?

   Checks the generated diagram's topology against the parsed source:

   Evaluation prompt addition:
   ```
   STRUCTURAL ACCURACY CHECK:
   The source diagram has {node_count} nodes and {edge_count} connections.
   Major nodes: {list of node labels}
   Key connections: {list of "A → B" edges}

   Verify: Are all major nodes visible in the output? Are the primary
   connection paths represented? Is the directional flow preserved?
   Rating: PASS (topology preserved) or NEEDS_REFINEMENT (nodes/edges missing).
   ```

**Refinement rules** follow the same pattern as infographic-builder: max 1 refinement pass per panel, only if the analysis says NEEDS_REFINEMENT, targeting only the specific issues identified.

### Output Assembly

For multi-panel diagrams, panels are assembled using `stitch_panels` following the same direction-selection logic as infographic-builder:

- Diagrams that show a left-to-right flow (e.g., pipeline, data flow) → `horizontal`
- Diagrams that show a top-to-bottom flow (e.g., hierarchy, sequence) → `vertical`
- 5+ panels → always `vertical`
- When ambiguous → `vertical` (safer default)

Output naming follows the existing convention:
- Single panel: `./infographics/{diagram-name}.png`
- Multi-panel: `./infographics/{diagram-name}_panel_1.png`, etc.
- Combined: `./infographics/{diagram-name}_combined.png`

## Data Flow

```
User provides .dot or Mermaid source
          │
          ▼
   Parse source file
   (extract nodes, edges, labels, subgraphs)
          │
          ▼
   Dependency check
   (is dot / mmdc installed?)
          │
          ├─ NOT FOUND → fail with install instructions
          │
          ▼
   Aesthetic selection
   (present 6 options + freeform, wait for user pick)
          │
          ▼
   Render to plain PNG
   (dot -Tpng / mmdc -o)
          │
          ▼
   Panel decomposition decision
   (node count + subgraph boundaries → 1–6 panels)
          │
          ├─ Single panel path ──────────────────────────────┐
          │                                                  │
          ├─ Multi-panel path                                │
          │   ├─ Split source into subgraph segments         │
          │   └─ Render each segment to separate plain PNG   │
          │                                                  │
          ▼                                                  ▼
   Beautify with nano-banana generate
   (reference_image_path = plain PNG,
    prompt = aesthetic template + structural preservation modifier)
          │
          ├─ Multi-panel: Panel 1 first → reconcile style → Panels 2-N
          │
          ▼
   Quality review
   (standard 5 dimensions + label fidelity + structural accuracy)
          │
          ├─ PASS → accept
          ├─ NEEDS_REFINEMENT → refine prompt, regenerate (max 1 retry)
          │
          ▼
   Assemble (multi-panel only)
   (stitch_panels with direction based on diagram flow)
          │
          ▼
   Return: image path(s) + design rationale + quality review summary
```

## Shared vs. New

| Component | Status | Notes |
|-----------|--------|-------|
| Aesthetic system (all 6 + freeform) | **Shared** | Reused as-is from style-guide.md |
| Aesthetic selection UX | **Shared** | Same 3-turn flow, same two-turn shortcut |
| nano-banana tool (generate, analyze, compare) | **Shared** | Same tool, different prompts |
| stitch_panels tool | **Shared** | Same tool, same direction logic |
| Style prompt templates | **Shared + extended** | Same aesthetic templates with structural preservation modifier appended for diagrams |
| Reference image chaining | **Shared** | Same Panel 1 → reconcile → Panels 2-N pattern |
| Agent instructions/workflow | **New** | Separate agent file at `agents/diagram-beautifier.md` |
| Source parser (nodes/edges/labels/subgraphs) | **New** | Diagram-specific input parsing |
| Dependency checker (dot/mmdc) | **New** | CLI tool availability check |
| Plain PNG rendering step | **New** | The render-first strategy core |
| Panel decomposition logic | **New** | Graph-structure-driven, not content-density-driven |
| Quality review dimensions (label fidelity, structural accuracy) | **New** | Two additional dimensions beyond the standard five |
| Root session routing | **Modified** | Adds diagram detection to existing routing |

## Error Handling

| Condition | Behavior |
|-----------|----------|
| `dot` / `mmdc` not installed | Fail immediately with platform-specific install instructions |
| Source file has syntax errors | Attempt rendering anyway — `dot` and `mmdc` produce their own error messages. Surface the CLI error to the user with the suggestion to fix the source |
| Plain PNG rendering succeeds but produces an empty/tiny image | Warn the user that the source may have issues, show the plain render, and ask whether to proceed |
| Label fidelity check fails (labels distorted) | Refine the generation prompt with explicit label text reinforcement. If still wrong after 1 retry, return with the review notes — label accuracy is the hardest problem and the user may need to accept minor imperfections or try a different aesthetic |
| Structural accuracy check fails (nodes/edges missing) | Refine with stronger structural preservation language. If still wrong after 1 retry, return with review notes |
| Source has 50+ nodes | Warn that very large diagrams may lose detail. Recommend decomposition into subgraph panels. If no subgraphs are declared, suggest the user add explicit subgraph groupings to their source |
| Unsupported Mermaid diagram type | Some Mermaid types (e.g., `gitgraph`, `pie`) may not decompose naturally into panels. Fall back to single-panel treatment and note any limitations |

## Testing Strategy

- **Parser correctness**: Test the source parser against a corpus of .dot and Mermaid files of varying complexity — verify node/edge/label/subgraph extraction is accurate.
- **Dependency checker**: Verify graceful failure messages when `dot`/`mmdc` are absent, and successful detection when present.
- **Render-first fidelity**: Generate plain PNGs from sample diagrams and visually verify they render correctly before beautification.
- **Aesthetic coverage**: Beautify the same sample diagram (e.g., a 10-node architecture diagram) across all 6 aesthetics to verify each produces a visually distinct, stylistically correct result while preserving topology.
- **Label fidelity validation**: Use diagrams with diverse label content (short labels, long labels, labels with special characters, numeric labels) and verify the quality review catches distortions.
- **Structural accuracy validation**: Use diagrams with known topology (specific node count, specific edge paths) and verify the quality review detects missing nodes or broken connections.
- **Panel decomposition**: Test with diagrams of varying complexity and subgraph structure — verify decomposition boundaries align with declared subgraphs and that cross-panel connection points are correctly labeled.
- **Multi-panel consistency**: Generate multi-panel beautified diagrams and verify visual consistency across panels using the cross-panel comparison step.
- **End-to-end**: Beautify a representative .dot and Mermaid file through the full workflow — parse, render, beautify, review, assemble — and verify the output is a coherent, beautiful diagram that preserves the original structure.

## Design Decisions

**Why a separate agent instead of a mode inside infographic-builder?**
The infographic agent's workflow is optimized for natural language → visual creation: content analysis, layout selection from 14 types, decomposition by content density. Diagrams skip all of that — the structure is given, the layout is given, decomposition follows graph topology. Mixing the two paths would add conditional branching throughout the workflow without benefiting either path. A separate agent keeps both clean.

**Why render-first instead of direct source-to-image generation?**
The plain rendered PNG gives nano-banana a visual anchor for the exact topology. Without it, Gemini would need to parse graph syntax, compute a layout algorithm, and render — tasks that `dot` and `mmdc` already do perfectly. The reference image turns "understand and reproduce this graph structure" into "make this image beautiful," which is a much more reliable operation for an image generation model.

**Why all 6 aesthetics with no narrowing?**
The initial instinct might be that playful aesthetics (Claymation, Lego) don't suit technical diagrams. But an architecture diagram rendered as Lego bricks or clay sculptures can be surprisingly effective for presentations, educational content, and making dry technical topics engaging. The user chose the diagram content; let them choose the aesthetic without gatekeeping.

**Why graph-structure decomposition instead of content-density decomposition?**
Infographic decomposition splits by how much content fits in a panel. Diagram decomposition must split along semantic boundaries — a "Frontend" cluster and a "Backend" cluster are natural panel boundaries regardless of how many nodes each contains. Splitting a cluster across panels would break the visual metaphor and require awkward cross-panel edge rendering.

**Why add label fidelity as an explicit review dimension?**
Text rendering is Gemini's weakest point in image generation. For infographics, minor text issues are cosmetic. For diagrams, a misspelled node label ("Loab Balancer" instead of "Load Balancer") is a correctness error. Having the ground truth labels from the source parser enables a precise, automated check that doesn't rely on the model's self-assessment of its own text rendering.

## Open Questions

- **Subgraph rendering for multi-panel decomposition**: when splitting a diagram into panels along subgraph boundaries, should each subgraph be rendered independently to a separate plain PNG (requiring source manipulation to extract subgraphs), or should the full diagram be rendered once and the agent rely on the prompt to focus on the relevant region? Independent rendering is more precise but requires source manipulation; full-render-with-focus is simpler but may produce less accurate structural anchoring.
- **Edge labels in beautified output**: complex diagrams often have labels on edges (e.g., "HTTP/443", "gRPC"). These are harder for Gemini to preserve than node labels. Should edge labels be held to the same fidelity standard as node labels, or should the quality review treat them as best-effort with a lower threshold?
- **Sequence diagrams and non-graph Mermaid types**: Mermaid supports diagram types (sequence, gantt, pie) that don't have a traditional node/edge graph structure. Should these be supported in v1, or scoped out until the core flowchart/graph path is proven?
