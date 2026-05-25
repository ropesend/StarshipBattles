# Stage 6 — Current State

> **Status:** scaffold — not yet filled in. The structure below is a template; future agents should research the codebase and replace each placeholder with concrete findings before this document is treated as authoritative.

**As of:** YYYY-MM-DD

## What already exists in the codebase

List the existing tactical combat, formation, battle setup, and battle outcome modules. Use file paths.

- `<path>` — `<one-line description>`

Particular things to look for:
- Battle screen / tactical renderer.
- Battle spec / setup builder.
- Battle outcome / report objects.
- Formation logic (if any).
- Same-turn / same-sector continuation logic (this is the main new thing Stage 6 adds — likely absent today).
- Tactical AI for movement, targeting, screening, retreat.
- Replay / battle-state persistence for debugging.

## What partially overlaps but doesn't match the planned shape

- `<path>` — overlaps with `<planned concept>`, differs because `<X>`

## What is missing entirely

- `<planned concept>` — no current code

Likely missing pieces (verify):
- `TacticalSectorState` — per-sector, per-turn cache of poses.
- `TacticalObjectPose` — position, heading, velocity, timestamp.
- `BattleContinuationContext` — input to battle setup when prior same-turn state exists.
- `FormationPlan` — fleet/task-force/squadron formation intent.
- `PostBattleTacticalUpdate` — write-back after combat.

## Hard blockers to the planned design

- `<thing in current code>` — contradicts `<planned rule>`, needs `<resolution>` first

Specifically check: does the current battle setup assume "fresh deployment from scratch every battle"? If so, the assumption is everywhere and Stage 6 has to thread continuation through carefully.

## Naming map

| Planning term | Current code name (if any) | Notes |
|---|---|---|
| `TacticalSectorState` | | |
| `TacticalObjectPose` | | |
| `BattleContinuationContext` | | |
| `FormationPlan` | | |
| `PostBattleTacticalUpdate` | | |

## How to refresh this document

1. Walk the battle / tactical modules end-to-end.
2. Note the battle setup pipeline: where do ships get their initial positions today?
3. Note the post-battle pipeline: where do survivors return to the strategy layer?
4. Update sections above and refresh the "As of" date.
