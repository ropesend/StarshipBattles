# Stage 1 — Current State

> **Status:** scaffold — not yet filled in. The structure below is a template; future agents should research the codebase and replace each placeholder with concrete findings before this document is treated as authoritative.

> Goal of this document: ground the Stage 1 plan in the actual codebase so implementation projects start from reality, not abstraction. Update the "as of" date whenever this file is refreshed.

**As of:** YYYY-MM-DD

## What already exists in the codebase

List existing modules that already partially implement Stage 1 concepts. Use file paths.

- `<path>` — `<one-line description of what it covers>`

## What partially overlaps but doesn't match the planned shape

List existing code that touches a Stage 1 concept but with a different shape than the plan. Note the mismatch so an implementation project knows whether to adapt or replace.

- `<path>` — overlaps with `<planned concept>`, differs because `<X>`

## What is missing entirely

List Stage 1 concepts with no current code representation.

- `<planned concept>` — no current code

## Hard blockers to the planned design

List existing code or data that would actively contradict the Stage 1 plan and must be changed first.

- `<thing in current code>` — contradicts `<planned rule>`, needs `<resolution>` before Stage 1 implementation can proceed

## Naming map

| Planning term | Current code name (if any) | Notes |
|---|---|---|
| `VisibilityLevel` | | |
| `SensorProfile` | | |
| `DetectabilityProfile` | | |
| `EmpireIntelState` | | |
| `VisibilityResolver` | | |
| `IntelSnapshot` | | |
| `GhostContact` | | |
| `SectorContact` | | |
| `ShipContact` | | |

## How to refresh this document

1. Grep the codebase for each term in the naming map and for related synonyms.
2. Walk the relevant top-level packages (likely `game/strategy/`, `game/ui/`, `game/services/`) and identify modules that touch visibility, intel, sensors, scanners, or fog-of-war.
3. Update each section above with concrete file paths and one-line descriptions.
4. Update the "As of" date and remove the scaffold status banner once the document reflects reality.
