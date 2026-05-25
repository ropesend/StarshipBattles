# Stage 4 — Current State

> **Status:** scaffold — not yet filled in. The structure below is a template; future agents should research the codebase and replace each placeholder with concrete findings before this document is treated as authoritative.

> Stage 4's README explicitly says a research system already exists. This document is especially important for Stage 4 — the plan should be an **integration** plan, not a greenfield design.

**As of:** YYYY-MM-DD

## What already exists in the codebase

List the existing research system pieces. Use file paths.

- `<path>` — `<one-line description>`

Particular things to look for:
- Tech data files and the loader.
- `TechNode` / `TechTree` types.
- `ResearchTracker` or equivalent.
- Research service / logic layer.
- Research UI screens / panels.
- Tests covering research.
- Save/load coverage for research state.

## What partially overlaps but doesn't match the planned shape

- `<path>` — overlaps with `<planned concept>`, differs because `<X>`

## What is missing entirely

- `<planned concept>` — no current code

Likely missing pieces (verify):
- Per-empire research state attached to empire objects rather than a singleton.
- RP generation tied to colonies, facilities, population, leaders, or components.
- Research processing in the turn flow.
- Tech → component availability mapping.
- Leveled component family generation.
- Player-package inclusion of research state.
- Research allocation as a typed command consumed by AI and human players alike.

## Hard blockers to the planned design

- `<thing in current code>` — contradicts `<planned rule>`, needs `<resolution>` first

## Naming map

| Planning term | Current code name (if any) | Notes |
|---|---|---|
| Empire research state | | |
| Research generation | | |
| Research allocation | | |
| Tech capability unlocks | | |
| Component family generation | | |
| Research facade / package DTO | | |
| Research AI policy | | |

## How to refresh this document

1. Read the existing research module top-to-bottom.
2. Note where research state is stored (singleton? per-empire? global?).
3. Note where research is currently consumed (UI, turn engine, design system).
4. Update sections above and refresh the "As of" date.
