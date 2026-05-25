# Stage 4: Research Integration

## Purpose

Integrate the existing research sandbox into the actual strategy game economy, turn engine, empire state, component availability, and ship/colony design systems.

The goal is not just a visible tech tree. The goal is research that changes what an empire can build, design, detect, produce, and field.

## Existing Foundation

The current codebase already has a research system with tech data, tech nodes, a tech tree, research tracker, service logic, UI, tests, and save/load coverage. This stage should integrate and extend that system rather than restart it.

## Core Principle

Research should be empire-specific, turn-processed, and directly connected to gameplay capabilities.

Each empire should have its own research state. Completed research should affect component availability, component level, facility options, sensor capability, weapons, propulsion, construction, economy, and special systems.

## Proposed Concepts

| Concept | Responsibility |
|---|---|
| Empire research state | Per-empire tracker and unlocked tech levels. |
| Research generation | RP produced by colonies, facilities, population, leaders, or special components. |
| Research allocation | Player/AI allocation of RP among available tech nodes. |
| Tech capability unlocks | Mapping from tech levels to game capabilities. |
| Component family generation | Produces leveled component variants from research levels. |
| Research facade/package DTOs | Player-visible research state for UI and future multiplayer. |
| Research AI policy | AI priorities for research allocation. |

## First Objectives

1. Decide where per-empire research state lives.
2. Define how research points are generated.
3. Define how research allocation is represented in player commands/packages.
4. Add research processing to the turn flow.
5. Connect completed tech levels to component/design availability.
6. Define leveled component generation rules.
7. Ensure research state is included in save/load and player turn packages.
8. Ensure AI can allocate research through the same command/package surface as humans.

## Leveled Component Direction

Prefer component families over hand-authored one-off unlocks.

Example:

```text
Tech: Beam Weapons level 5
Component family: Laser Cannon
Available variants:
- Laser Cannon I
- Laser Cannon II
- Laser Cannon III
- Laser Cannon IV
- Laser Cannon V
```

Component stats may be generated from templates:

```text
damage = base_damage * level_multiplier
range = base_range + level_bonus
cost = base_cost * cost_curve(level)
mass = base_mass * mass_curve(level)
```

This should support modding and data-driven balance tuning.

## Initial Non-Goals

- Perfect final tech balance.
- Complete AI research strategy.
- Rewriting the research UI from scratch.
- Locking every possible component behind research immediately.
- Complex espionage or technology theft.
- Multiplayer transport.

## Design Questions

1. Should RP be generated empire-wide, colony-local, or both?
2. Should research allocations be global per empire or split by field/category?
3. Should breakthroughs remain probabilistic or become deterministic progress bars?
4. Should multiplayer/server mode use server-only randomness for research breakthroughs?
5. Should tech levels unlock component variants, scale existing components, or both?
6. Should obsolete components remain buildable?
7. Should research unlock hidden information systems such as improved sensors/scanners?
8. How should mods add new tech fields and component families?

## Acceptance Criteria

This stage is ready for implementation projects when there is a documented plan for:

- Per-empire research state.
- RP generation and allocation.
- Turn-engine integration.
- Component/facility unlocks.
- Leveled component generation.
- Save/load and player package inclusion.
- AI access through the same command model.

## Implementation Project Guidance

Use the existing `Projects/` system for implementation. Suggested project slices:

1. Attach research state to empire and round-trip it.
2. Add RP generation from colonies/facilities.
3. Add research processing phase to the turn engine.
4. Expose research state through facade/player packages.
5. Add command handling for allocation changes.
6. Connect one component family to tech levels as a vertical slice.
7. Expand component/facility unlock mapping.
8. Add AI allocation policy.
