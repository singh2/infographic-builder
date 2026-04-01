# Diagram Beautifier -- Routing Context

## Diagram Input Detection

When the user provides input matching any of these patterns, delegate to
`infographic-builder:diagram-beautifier` instead of `infographic-builder:infographic-builder`:

### File extensions
- `.dot` -- Graphviz source file
- `.mmd` or `.mermaid` -- Mermaid source file
- `.png` -- Existing diagram image (when combined with diagram-beautification intent)

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

### PNG input handling
When a `.png` file is provided, the diagram-beautifier skips the dependency
check and render steps -- the PNG is used directly as the `reference_image_path`
for nano-banana. A `nano-banana analyze` call extracts node/edge labels from the
image to serve as quality review ground truth.

## Routing Rule

If diagram source is detected -> delegate to `infographic-builder:diagram-beautifier`

If natural language topic (no diagram source) -> delegate to `infographic-builder:infographic-builder` (existing behavior, unchanged)

The diagram-beautifier agent handles parsing, rendering, aesthetic selection,
beautification, quality review, and assembly. Pass the user's request as-is.
