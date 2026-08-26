# Infographic Builder

You have access to visual generation via the
`infographic-builder:infographic-builder` agent — it turns topics, documents,
and codebases into designed, publication-ready visuals using Gemini image
generation.

## When to Use

- User asks for a generated visual of any kind — "create an infographic",
  "show me a diagram of...", "visualize...", "summarize this as a visual",
  "make it visual". The word "infographic" is not required.
- User hands over an artifact and wants it made visual — a codebase, git
  history, release notes, test output, issue list, postmortem, meeting
  transcript, strategy doc, spreadsheet, or itinerary.
- User asks for styling, panel count, or orientation on a visual they want
  produced ("claymation", "dark mode tech", "lego diorama", "3-panel").

## How to Use

Delegate the request as-is. The agent selects the layout (process flow,
comparison, timeline, hierarchy, flowchart, funnel, matrix, Venn, mind map,
journey, and more), proposes aesthetics, decomposes into panels, and runs its
own quality review. It is fully self-contained — no file reading, research, or
preparation is needed before delegating.

    delegate(agent="infographic-builder:infographic-builder",
             instruction="<the user's request, verbatim>")

## Prerequisites

`GOOGLE_API_KEY` must be set (Gemini image generation via nano-banana).
