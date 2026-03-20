# Style System and Browsable Catalog Design

## Goal

Give infographic-builder a composable style library (layouts × aesthetics) with in-session discovery UX and a browsable catalog website, so users get diverse, high-quality visual treatments without manually engineering prompts.

## Background

infographic-builder currently has 6 layout types, a critic loop, multi-panel mode, and prompt engineering that controls typography, color palette, icon style, orientation, section count, and aspect ratio. Despite this structural control, all infographics come out in "nano-banana house style" — clean flat vector, safe palette. The system controls *content structure* well but doesn't control *visual aesthetic*. Users have no way to get diverse visual treatments without manually engineering prompts.

## Approach

Introduce two independent, composable axes — **layout** (content structure) and **aesthetic** (visual treatment) — rather than a flat style list. This maximizes combinatorial value: any layout can be rendered in any aesthetic. Six deeply-engineered featured aesthetics span the professional-to-playful spectrum, while open-ended freeform input lets users describe any aesthetic they can imagine.

## Architecture

The style system adds a single new concept layer between the user's request and the existing prompt engineering infrastructure:

```
User request
  → Content analysis (recommends layout)
  → Aesthetic selection (user picks or describes)
  → Style brief (layout + aesthetic → full prompt template)
  → Existing prompt engine (output type, orientation, sections, text, style modifier, aspect ratio)
  → nano-banana generation
```

The aesthetic system enhances the existing "style modifier string" with a full curated prompt template instead of a generic phrase. No new user-facing dimensions are introduced — background texture, lighting, mood, and other implementation details stay inside each aesthetic's template.

## Components

### Style Library

Two independent axes that compose freely:

#### 10 Layouts (content structure — system recommends based on content analysis)

| # | Layout | Best For |
|---|--------|----------|
| 1 | Numbered Vertical Flow | How-to, step-by-step |
| 2 | Side-by-Side Comparison | Pros/cons, before/after |
| 3 | Stats with Large Numbers | KPIs, metrics, survey results |
| 4 | Timeline | History, roadmaps, phases |
| 5 | Tree / Pyramid Hierarchy | Org charts, taxonomies, priorities |
| 6 | Circular Flow | Recurring processes, feedback loops |
| 7 | Mind Map *(new)* | Brainstorming, concept relationships |
| 8 | Storyboard Journey *(new)* | Narrative sequences, user journeys |
| 9 | Process Flow Diagram *(new)* | Decision trees, algorithms, logic flows |
| 10 | Long-Form Explainer Panel *(new)* | Deep dives, horizontal banded sections with per-section illustrations |

#### 6 Featured Aesthetics (visual treatment — user chooses or system suggests)

| Aesthetic | Vibe | Internal Prompt Modifiers |
|-----------|------|--------------------------|
| Clean Minimalist | Professional, Swiss design, boardroom-ready | Solid/gradient background, flat even lighting, Helvetica-style type, monochrome flat icons |
| Dark Mode Tech | Developer-native, neon on dark, glassmorphism | Dark slate background, neon glow lighting, monospace fonts, glassmorphism icons |
| Bold Editorial | Wired/Vox magazine, high contrast, commanding | High-contrast color block background, dramatic lighting, massive serif headlines, collage elements |
| Hand-Drawn Sketchnote | Casual, marker-on-notebook, creative | Crumpled graph paper texture, flat lighting, marker doodle type, hand-drawn icons |
| Claymation Studio | Whimsical, tactile, plasticine textures | Cardboard set background, soft studio lighting with realistic shadows, rounded playful type, 3D sculpted plasticine icons |
| Lego Brick Builder | Playful, structural, plastic bricks | Plastic baseplate background, macro photography lighting with depth of field, blocky type embossed on tiles, brick-built icons |

#### Freeform Aesthetics

Users can describe any aesthetic beyond the featured six ("vintage travel poster", "watercolor", "comic book", "pixel art"). The system translates the user's description into reasonable defaults for typography, palette, icon style, and any additional modifiers needed. All structural prompt engineering still applies — only the visual treatment is freeform.

### In-Session UX

A three-turn interaction flow:

**Turn 1** — User request:
> "Create an infographic about how DNS resolution works"

**Turn 2** — System proposes layout + presents aesthetics:

```
For "how DNS resolution works," I'd recommend
Process Flow Diagram.

Choose a style, or describe your own:

  1. Clean Minimalist       4. Hand-Drawn Sketchnote
  2. Dark Mode Tech         5. Claymation Studio
  3. Bold Editorial         6. Lego Brick Builder

  Or describe any style — "professional report",
  "watercolor", "comic book", "retro pixel art",
  "vintage travel poster" — get creative.
```

**Turn 3** — User picks, system generates.

Professional options lead the list. The "describe any style" examples lead with a professional suggestion.

**Shortcut:** If the user specifies a style in their original request ("make a claymation infographic about DNS"), the system skips the proposal and generates directly in two turns.

### Prompt Engineering Per Aesthetic

Each curated aesthetic is a self-contained prompt template that overrides three existing prompt dimensions (typography, palette, icon style) and bakes in whatever additional modifiers it needs (texture, lighting, mood). No new user-facing dimensions are introduced.

The existing prompt engineering infrastructure continues to work unchanged:
- Output type keyword
- Orientation
- Section count
- Text content
- Style modifier string (now receives the full aesthetic template)
- Aspect ratio

### Browsable Catalog Website

A simple static website serving as the out-of-session discovery surface. Users browse this before or between sessions to build their vocabulary of available styles.

**Content focus:** Professional, knowledge-work, tech-audience scenarios.

**Sample scenarios:**

| Scenario | Category |
|----------|----------|
| System architecture overview | Engineering |
| API request lifecycle | Engineering |
| CI/CD pipeline stages | DevOps |
| Quarterly metrics dashboard | Data viz |
| Feature comparison matrix | Product |
| Product roadmap timeline | Product management |
| User research findings synthesis | UX research |
| Customer journey map | UX / Sales |
| Sales pipeline funnel | Sales |
| Sprint retrospective insights | Agile / PM |
| Competitive landscape overview | Strategy / Sales |
| Onboarding flow walkthrough | Process |

Each scenario is rendered across multiple aesthetics so users see how the same content transforms across styles.

**Implementation:** Simple static site, grid layout, filterable by scenario or aesthetic. Built from the existing sample gallery work on the `feat/sample-gallery-recipe` branch.

## Data Flow

1. User submits a topic (and optionally a style preference)
2. System analyzes content → recommends a layout from the 10 available
3. If no style specified, system presents the 6 featured aesthetics + freeform option
4. User selects an aesthetic (featured or freeform description)
5. System assembles a **style brief**: layout template + aesthetic prompt template
6. Style brief feeds into existing prompt engine as an enhanced style modifier string
7. Prompt engine produces the full generation prompt with all dimensions (output type, orientation, sections, text, style modifier, aspect ratio)
8. nano-banana generates the infographic
9. Critic loop evaluates result (including aesthetic fidelity)
10. If multi-panel, style brief propagates to all panels via reference image chaining

## Integration with Existing Features

| Feature | Integration |
|---------|-------------|
| Critic loop | Evaluation rubric expands to assess aesthetic fidelity — "does this actually look like claymation?" becomes part of the criteria |
| Multi-panel mode | Style brief includes full aesthetic specification; all panels share the visual treatment via reference image chaining |
| Combined mode (critic + multi-panel) | Critic checks aesthetic consistency per panel before moving to the next |
| Inline activation | All features compose: "Make a claymation multi-panel infographic about DNS with critic review" activates aesthetic + multi-panel + critic together |

## Error Handling

- **Freeform aesthetic too vague:** System maps the description to sensible defaults across all prompt dimensions; no failure mode, just best-effort interpretation.
- **Aesthetic fidelity miss:** Critic loop catches cases where the output doesn't match the requested aesthetic and triggers a refinement pass.
- **Layout mismatch:** If the system's content-based layout recommendation is overridden by the user, the system respects the override without complaint.

## Testing Strategy

- **Catalog generation:** Render each sample scenario across all 6 featured aesthetics to validate prompt templates produce visually distinct results.
- **Freeform aesthetics:** Test a set of diverse freeform descriptions ("vintage travel poster", "watercolor", "pixel art") to verify the system translates them into coherent prompt modifiers.
- **Critic loop integration:** Verify the expanded evaluation rubric catches aesthetic mismatches (e.g., a "claymation" request that produces flat vector output).
- **Multi-panel consistency:** Generate multi-panel infographics in each aesthetic and verify visual consistency across panels.
- **Composability:** Test combined activation (aesthetic + multi-panel + critic) to verify all features compose correctly.
- **Two-turn shortcut:** Verify that specifying a style in the original request skips the proposal turn.

## Design Decisions

**Why two independent axes (layout × aesthetic) instead of a flat style list?**
Some styles are clearly structures (mind map, storyboard, process flow — they determine information architecture). Others are clearly visual treatments (claymation, Lego, sketchnote — they change how it looks, not how information is organized). Making them independent means any layout can be rendered in any aesthetic, maximizing combinatorial value.

**Why 6 featured aesthetics instead of more?**
The six span the professional-to-playful spectrum (Clean Minimalist and Dark Mode Tech for professional, Bold Editorial for commanding, Sketchnote for casual, Claymation and Lego for delight). Plus users can describe any aesthetic they want — the featured six are curated starting points, not a closed set.

**Why not surface background texture, mood, and lighting as user-facing dimensions?**
These are implementation details inside each aesthetic's prompt template. Surfacing them adds complexity without user value. The user picks "Claymation" and gets realistic shadows on cardboard — they don't need to know that's a "lighting" choice.

**Why propose styles before generating instead of using smart defaults?**
The user wants discovery — users can't know what's available unless the system presents options. The style proposal adds one lightweight turn (a quick pick) but enables users to discover aesthetics they wouldn't have thought to request. Users who already know what they want can specify it in their original message and skip the proposal entirely.

## Open Questions

None — design is validated and ready for implementation.
