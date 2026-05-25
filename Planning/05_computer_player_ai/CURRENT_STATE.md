# Stage 5 — Current State

> **Status:** scaffold — not yet filled in. The structure below is a template; future agents should research the codebase and replace each placeholder with concrete findings before this document is treated as authoritative.

**As of:** YYYY-MM-DD

## What already exists in the codebase

List existing AI code by layer (tactical, operational, strategic). Use file paths.

### Tactical AI

- `<path>` — `<one-line description>`

### Operational / strategic AI

- `<path>` — `<one-line description>`

### Personality / difficulty / policy

- `<path>` — `<one-line description>`

## What partially overlaps but doesn't match the planned shape

- `<path>` — overlaps with `<planned concept>`, differs because `<X>`

Specifically check: does current AI consume raw authoritative game state, or does it already go through any kind of view / package? Most likely raw — note that explicitly.

## What is missing entirely

- `<planned concept>` — no current code

## Hard blockers to the planned design

Stage 5's core principle is "fair AI uses the same fog-limited package humans get." Audit:

- Does current AI read hidden enemy information?
- Does current AI mutate authoritative state directly instead of emitting commands?
- Does current AI depend on Python object identity in ways that would break across save/load?

List each as a blocker with the path.

## Dependency check

Stage 5 depends on Stages 1, 2, 2.5, and partially 4. Note status:

- Stage 1 (`IntelSnapshot`, intel state): `<status>`
- Stage 2 (`PlayerTurnPackage`, `OrdersSubmission`): `<status>`
- Stage 2.5 (AI debug controls via admin commands): `<status>`
- Stage 4 (research as command): `<status>`

## Naming map

| Planning term | Current code name (if any) | Notes |
|---|---|---|
| AI input package | | |
| AI command-batch output | | |
| Strategic AI controller | | |
| Operational AI controller | | |
| Tactical AI controller | | |
| Personality / policy profile | | |

## How to refresh this document

1. Walk every AI-related module.
2. Note which read paths touch hidden information.
3. Note which write paths bypass a command/order surface.
4. Update sections above and refresh the "As of" date.
