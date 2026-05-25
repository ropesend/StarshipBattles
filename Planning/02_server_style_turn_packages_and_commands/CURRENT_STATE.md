# Stage 2 — Current State

> **Status:** scaffold — not yet filled in. The structure below is a template; future agents should research the codebase and replace each placeholder with concrete findings before this document is treated as authoritative.

> Goal of this document: ground the Stage 2 plan in the actual codebase so implementation projects start from reality, not abstraction. Update the "as of" date whenever this file is refreshed.

**As of:** YYYY-MM-DD

## What already exists in the codebase

List existing modules that already partially implement Stage 2 concepts. Use file paths.

- `<path>` — `<one-line description>`

Particular things to look for:
- An existing `GameSession`-shaped object (anything that owns the authoritative game state).
- Any code that already builds per-empire views or filtered snapshots.
- Any command/order/intent object pattern, even informal.
- The current turn-resolution entry point.
- Where the UI currently mutates game state directly (this is the "existing leak surface" Stage 2 is trying to close).

## What partially overlaps but doesn't match the planned shape

- `<path>` — overlaps with `<planned concept>`, differs because `<X>`

## What is missing entirely

- `<planned concept>` — no current code

## Hard blockers to the planned design

- `<thing in current code>` — contradicts `<planned rule>`, needs `<resolution>` before Stage 2 implementation can proceed

Specifically check for:
- UI code that holds long-lived references to live game objects.
- Code that passes Python object references where stable IDs would be required.
- Hidden global mutable game state that would need to be eliminated.

## Naming map

| Planning term | Current code name (if any) | Notes |
|---|---|---|
| `PlayerTurnPackage` | | |
| `OrdersSubmission` | | |
| `CommandBatch` | | |
| `CommandValidationContext` | | |
| `CommandValidationResult` | | |
| `TurnResolutionReport` | | |
| `PlayerEventPackage` | | |
| `GameSession` (authoritative) | | |

## Candidate first-vertical-slice command

Once the above is filled in, note which existing object would be easiest to wrap as the first stable-ID command target (e.g., fleet rename, research allocation). See the expansion notes for the analysis.

- Candidate: `<command>` — supported by existing code at `<path>`

## How to refresh this document

1. Grep for each term in the naming map.
2. Identify the current turn-resolution pipeline end-to-end.
3. Identify the UI ↔ game-state coupling that Stage 2 will need to break.
4. Update each section above with concrete file paths and one-line descriptions.
5. Update the "As of" date and remove the scaffold banner once the document reflects reality.
