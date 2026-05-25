# Stage 1: Information Boundary And Fog Of War

## Purpose

Create a clean separation between the authoritative game state and the information each empire is allowed to know. This stage is the foundation for fog of war, fair computer players, server-authoritative multiplayer, and secure player turn packages.

The immediate goal is not polished fog rendering. The immediate goal is a correct information model.

## Core Principle

A fleet, planet, colony, warp point, storm, minefield, fighter wing, or satellite constellation does not have one universal visibility value. Visibility is observer-relative. Each empire may know a different amount about the same object.

The authoritative session owns the truth. Each empire owns an intelligence/memory view of that truth.

## Proposed Concepts

| Concept | Responsibility |
|---|---|
| `VisibilityLevel` | Defines how much detail an observer has: unknown, remembered, contact, identified, detailed, etc. |
| `SensorProfile` | Describes what an object can detect, at what range, and to what detail. |
| `DetectabilityProfile` | Describes how easy an object is to detect: signature, stealth, object class, emissions, size. |
| `EmpireIntelState` | Per-empire memory of previously seen objects, last known positions, last seen turn/tick, and stale details. |
| `VisibilityResolver` | Computes current live visibility from sensor sources and object detectability. |
| `IntelSnapshot` | Player-facing DTO containing only visible and remembered information. |
| `GhostContact` | Memory record for something no longer currently visible but previously detected. |

## Suggested Visibility Bands

| Level | Meaning | Example |
|---|---|---|
| `UNKNOWN` | No knowledge. | Unexplored planet/warp point/fleet. |
| `REMEMBERED` | Last known information only. | Fleet last seen at hex X on turn 12. |
| `CONTACT` | Something is currently detected, but details are limited. | Unknown fleet contact. |
| `IDENTIFIED` | Basic identity known. | Enemy fleet name/owner and rough class. |
| `DETAILED` | Strong scan. | Composition, colony details, defenses, cargo, or component-level info. |

Stars are the special case: star positions should be visible across the galaxy. The open design question is whether spectral class, name, system radius, or star image are also globally visible.

## Relationship To Stage 2.5 Developer Cheat And Test Control Plane

Stage 2.5 adds privileged debug visibility controls such as global omniscience, per-empire omniscience, reveal-system, reveal-galaxy, reveal-contact, and reset-intel commands.

Those controls must not be implemented as UI-side hidden-state access. They should alter server-built player packages or Stage 1 intel/visibility state through the authoritative session.

Stage 1 should therefore preserve a clean distinction between:

```text
Normal player-visible package mode
  Uses regular visibility and intel rules.

Debug global omniscient package mode
  Server packages full authoritative visibility for debug use.

Debug per-empire omniscient package mode
  Server packages full visibility for selected empires only.
```

Required Stage 1 support for Stage 2.5:

- Omniscient view must be reversible.
- Global omniscience and per-empire omniscience must be independently toggleable.
- Turning omniscience off must restore normal fog/intel package behavior.
- The UI should never receive hidden raw truth in normal package mode.
- Debug package modes should be explicit and should not become the default player package path.

## First Objectives

1. Define the vocabulary and DTO shape for player-visible information.
2. Add per-empire intel/memory state without changing UI behavior yet.
3. Add sensor profiles to colonies, fleets, units, and relevant deployed groups.
4. Add detectability/signature profiles to objects that can be discovered.
5. Create a pure visibility resolver that can be tested without UI.
6. Add player-specific snapshots that show different results for different empires.
7. Add stale memory/ghost contacts for fleets, planets, and other detected objects.
8. Gradually route strategy UI reads through player-visible DTOs rather than raw game state.
9. Keep a future debug package mode seam available for Stage 2.5 omniscient and reveal controls.

## Initial Non-Goals

- Fancy fog rendering.
- Stealth/counter-stealth balance.
- Espionage.
- Sensor jamming.
- Cloaking.
- Network transport.
- Full AI exploitation of fog.
- Stage 2.5 cheat command implementation.

## Design Questions

1. How many visibility bands are needed for the first implementation?
2. Should memory records degrade over time, or remain until refreshed?
3. Should fleet ghost positions become uncertain after several turns?
4. Should planets, colonies, and warp points remain permanently remembered once discovered?
5. Should combat reveal all participants to all combatants, or only objects detected by combat sensors?
6. Should sensor range be hex distance only, or modified by storms, nebulae, stealth, emissions, and object size?
7. Should debug omniscience be represented as a package-building mode, a visibility resolver override, or a separate debug snapshot builder?

## Acceptance Criteria

This stage is ready for implementation projects when there is a documented visibility model, per-empire intel plan, current-contact/ghost-contact plan, sensor/detectability plan, and a test strategy proving two empires can receive different views of the same galaxy.

The design should also leave an explicit seam for Stage 2.5 debug visibility modes without weakening normal hidden-information guarantees.

## Implementation Project Guidance

Use the existing `Projects/` system for implementation. Suggested project slices: DTOs, sensor/detectability profiles, per-empire intel state, visibility resolver, facade read namespace, one UI conversion path, then broader strategy-map conversion.
