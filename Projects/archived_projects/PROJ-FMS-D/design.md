# PROJ-FMS-D Design — Satellites slice

This project's slice of the shared design. **See [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md) for the canonical, end-to-end design.** Only PROJ-FMS-D-specific notes go here.

## In scope
- `StrategicSatelliteLaunchAbility` and `TacticalSatelliteLaunchAbility` behavior.
- `RecoverSatellitesAbility` strategic action.
- Stationary tactical AI variant.
- Bay separation: satellite-only bays vs fighter-only bays vs universal bays.
- End-of-battle reboard extension to handle satellites alongside fighters.

## Out of scope
- Sensor / fog-of-war system — satellites are excellent sensor platforms but the existing sensor model is C&C-gated and pre-fog-of-war. Sensor work is a separate future project.

## Key risks
- **Bay separation design**: a single `VehicleBayAbility` with type filtering is more flexible than splitting into `FighterBay` / `SatelliteBay` / `MineBay`, but it requires the type filter to be honored everywhere (load, unload, recovery). The split-class approach is more explicit but adds component count. Phase 1 decides.
- **Stationary AI vs broken AI**: the existing AI controller has stationary satellite behavior referenced at [`controller.py:361-363`](../../../game/ai/controller.py#L361). Make sure the new `SatelliteAIController` doesn't accidentally inherit movement code.
- **End-of-battle reboard generalisation**: PROJ-FMS-C Phase 3 implemented reboard for fighters. Extending to satellites without a refactor could lead to duplicate logic. Lean: generalise the hook to iterate `launched_in_battle_id`-tagged vehicles of either type with type-appropriate bay matching, rather than copy-pasting.
- **Cross-type isolation**: a fighter recovery ability MUST NOT recover satellites and vice versa, otherwise the separate-ability-gate design intent collapses. Test explicitly.

## Decisions deferred to implementation (PROJ-FMS-D)
- Bay separation mechanism (filter vs split).
- Satellite spawn position pattern in tactical combat.
- Whether to retro-tag existing fighter bay components with `allowed_types: ["fighter"]` or leave them untyped (= universal).
