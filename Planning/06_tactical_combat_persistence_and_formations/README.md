# Stage 6: Tactical Combat Persistence And Formations

## Purpose

Improve tactical combat behavior, fleet AI, formations, and same-turn battlefield continuity.

The specific persistence goal is that if combat occurs again in the same sector during the same strategy turn, surviving or following combat vehicles should begin from appropriate persisted tactical positions rather than being redeployed from scratch.

## Core Principle

Tactical combat should remain connected to the strategy layer without letting simulation internals leak uncontrolled into strategy state.

Persist only the tactical information that strategy needs to resume same-turn combat meaningfully.

## Proposed Concepts

| Concept | Responsibility |
|---|---|
| `TacticalSectorState` | Per-sector, per-turn cache of tactical positions and possibly headings/velocities. |
| `TacticalObjectPose` | Position, heading, velocity, and timestamp for a strategy object in tactical space. |
| `BattleContinuationContext` | Input to battle setup when previous same-turn tactical state exists. |
| `FormationPlan` | Strategy/task-force/squadron formation intent resolved into tactical deployment. |
| `PostBattleTacticalUpdate` | Output that updates same-turn tactical sector state after combat. |

## First Objectives

1. Define which tactical state persists between battles in the same sector and turn.
2. Define when tactical sector state is created, updated, and cleared.
3. Preserve ship/fighter/satellite positions for surviving assets.
4. Decide whether mines, projectiles, wrecks, obstacles, and retreat vectors persist.
5. Improve formation planning at fleet/task-force/squadron level.
6. Improve tactical AI behavior for following, screening, escorting, holding range, and target focus.
7. Add tests for repeated same-sector combat in one strategy turn.
8. Keep replay/debug outputs compatible with the new continuity model.

## Minimal First Version

The first version should persist only:

- Strategy entity ID.
- Tactical position.
- Heading/facing.
- Optional velocity.
- Last updated tick/turn.
- Sector hex.

Clear this state at turn rollover unless a later design explicitly supports multi-turn persistent tactical battlefields.

## Initial Non-Goals

- Full persistent battlefields across many turns.
- Persistent projectiles.
- Persistent wreck/debris simulation.
- Complex terrain/obstacle persistence.
- Major tactical renderer rewrite.
- Perfect fleet AI.

## Design Questions

1. Should tactical state persist only within one strategy turn, or across multiple turns?
2. Should retreating ships preserve exit vectors for later pursuit?
3. Should new arrivals enter from an edge based on strategic movement direction?
4. Should stationary defenses/satellites/mines have fixed tactical anchors?
5. Should fighters launched during combat persist as deployed groups afterward?
6. Should combat AI be allowed to change formations mid-battle?
7. How should tactical state interact with replay verification?
8. Should repeated combat in the same hex use the same battle seed?

## Acceptance Criteria

This stage is ready for implementation projects when there is a documented plan for:

- Per-sector same-turn tactical state.
- Tactical pose persistence.
- State creation/update/clear timing.
- Battle setup using previous tactical state.
- Formation and tactical AI improvement scope.
- Tests for repeated same-sector combat.

## Implementation Project Guidance

Use the existing `Projects/` system for implementation. Suggested project slices:

1. Define tactical sector state DTOs.
2. Store same-turn state in strategy/session layer.
3. Feed existing state into battle-spec compilation.
4. Update state from battle outcomes.
5. Add repeated-combat tests.
6. Improve formation resolver behavior.
7. Improve tactical AI policies and movement behavior.
