# PROJ-428: Phase registry hooks (TD-04)

**Execution Protocol:** 03c-phase-aware-execution

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-428` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-428 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status

| Phase | Name | Status | Checklist |
|-------|------|--------|-----------|
| 0 | Freeze the real contract with red tests | Complete | [phase_0_checklist.md](phase_0_checklist.md) |
| 1 | Move planet-modifier engine resolution onto `TurnEngine` | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2 | Move small hook logic onto named `TurnEngine` methods | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3 | Extract the movement-only collaborator | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4 | Add a registry-purity guard | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5 | Validate and document | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State

**Last Updated:** 2026-05-17
**Active Phase:** 1 — Move planet-modifier engine resolution onto `TurnEngine`
**Last Action:** Phase 0 characterization tests added (env-event hook, booster-dirty selective flip, fleet pruning after minefield kill); hook lookup goes through `DEFAULT_TICK_PHASE_LIST` so tests survive relocation.
**Next Action:** Phase 1 — lazy property + descriptor lambda + delete `_resolve_planet_modifier_effects`.
**Blockers:** None

## Overview

`game/strategy/engine/turn_phase_registry.py` is meant to be a declarative
descriptor module, but it currently hosts six behavior-bearing helpers and
constructs gameplay engines (`PlanetModifierEffectEngine`, `MinefieldResolver`)
from inside the module. The worst offender, `_derive_moved_fleet_ids`, runs
movement diffing, `_booster_dirty` propagation, minefield resolution, and
fleet pruning. This project relocates that behavior to `TurnEngine` (or a
single movement-specific collaborator) so the registry can become pure data.

## Goals

- Restore `turn_phase_registry.py` to descriptors, dataclasses, and constants only.
- Move planet-modifier engine resolution to a `TurnEngine` lazy property.
- Move small per-hook logic onto named `TurnEngine` methods.
- Extract movement-specific snapshot/diff/minefield/pruning work into a single
  `MovementPhaseCollaborator` owned by `TurnEngine`.
- Add an AST/registry-purity guard test that prevents future drift.
- Preserve `DEFAULT_TICK_PHASE_LIST`, `DEFAULT_END_OF_TURN_PHASE_LIST`,
  `TURN PERF` output, `last_environmental_events`, `_booster_dirty`, and the
  `MinefieldResolver` call contract (`registries=engine._registries`).

## Scope

**In:**
- `game/strategy/engine/turn_phase_registry.py` — hook removal, lambda repointing
- `game/strategy/engine/turn_engine.py` — lazy property + named methods + collaborator wiring
- Optional new `game/strategy/engine/movement_phase_collaborator.py`
- Tests under `tests/unit/strategy/turn_engine/` and `tests/unit/strategy/engine/`
- Targeted integration tests `tests/integration/test_fms_b_e2e.py` and
  `tests/integration/test_fms_b_statistical_balance.py`
- Optional doc touch in `docs/systems/strategy_layer.md` if it describes hook placement

**Out:**
- Renaming phase keys or timing buckets
- Adding a new strategy engine interface (explicitly forbidden by TD-04 guardrails)
- Adding a new `TurnEngineConfig` field unless an existing failing test forces it
- Changing the phase order or moving minefield resolution to a different phase
- Modifying `MinefieldResolver`'s public surface
- Wider strategy-layer refactors covered by TD-09/TD-10

## Dependencies

- **Hard predecessors:** none. The TD-04 plan explicitly states
  "Hard ordering constraints: None."
- **Soft predecessors:** [PROJ-422](../PROJ-422/plan.md) (TD-09 engine
  interface split). PROJ-422 helps but is not required — TD-04 Phase 1 uses a
  lazy property on `TurnEngine` instead of adding a new ABC, so the engine
  interface monolith does not block this work.
- TD-10 (deployable substrate redesign) is also a soft preference, not a
  blocker. The new collaborator can keep using the current `MinefieldResolver`
  until TD-10 changes that subsystem.

## Key Files

| Component | File Path |
|-----------|-----------|
| Registry under refactor | `game/strategy/engine/turn_phase_registry.py` |
| Primary consumer | `game/strategy/engine/turn_engine.py` |
| New collaborator (Phase 3) | `game/strategy/engine/movement_phase_collaborator.py` |
| Planet modifier engine | `game/strategy/engine/planet_modifier_effect_engine.py` |
| Minefield resolver | `game/strategy/engine/minefield_resolver.py` |
| Descriptor tests | `tests/unit/strategy/turn_engine/test_tick_phase_descriptors.py` |
| Tick list golden | `tests/unit/strategy/turn_engine/test_default_tick_phase_list.py` |
| End-of-turn list golden | `tests/unit/strategy/turn_engine/test_default_end_of_turn_phase_list.py` |
| Movement diff test | `tests/unit/strategy/turn_engine/test_turn_engine_phase_320_movement_diff.py` |
| Lazy-property tests | `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py` |
| Engine config test | `tests/unit/strategy/engine/test_turn_engine_config.py` |
| Lazy-fallback guard | `tests/unit/strategy/engine/test_no_lazy_fallback_init.py` |
| FMS-B integration | `tests/integration/test_fms_b_e2e.py`, `tests/integration/test_fms_b_statistical_balance.py` |
| Optional new purity guard | `tests/unit/strategy/turn_engine/test_turn_phase_registry_purity.py` |
| Optional new collaborator tests | `tests/unit/strategy/turn_engine/test_movement_phase_collaborator.py` |

## Phases

### Phase 0: Freeze the real contract with red tests
Add failing / characterization tests for `last_environmental_events`,
`move_queue`/`pre_movement_locations` snapshotting, `moved_fleet_ids`,
`_booster_dirty` flips, the `MinefieldResolver.resolve_minefield_entry`
call contract, and fleet-pruning after minefield damage. No production
code changes.

### Phase 1: Move planet-modifier engine resolution onto `TurnEngine`
Introduce `TurnEngine.planet_modifier_effect_engine` lazy property.
Repoint the descriptor resolver to
`lambda e: e.planet_modifier_effect_engine.process_modifier_effects_tick`.
Delete `_resolve_planet_modifier_effects` from the registry. Do NOT add a
new `TurnEngineConfig` field.

### Phase 2: Move small hook logic onto named `TurnEngine` methods
Add named methods for the tick-1 pre-harvesting log, the tick-1 post-production
log, and env-event accumulation. Repoint hooks at those methods. Delete the
three small registry helpers.

### Phase 3: Extract the movement-only collaborator
Introduce `MovementPhaseCollaborator` with `snapshot_before(ctx, result)` and
`resolve_after(engine, ctx)`. Internally split `_diff_moved_fleets`,
`_mark_boosters_dirty`, `_resolve_minefields`, `_prune_destroyed_fleet_contents`.
Wire `movement_calc` / `movement_apply` hooks to it. Preserve the existing
broad-catch around minefield resolution and the `registries=engine._registries`
call contract. Delete `_capture_move_queue` and `_derive_moved_fleet_ids`.

### Phase 4: Add a registry-purity guard
Add an AST-driven test that enforces: no module-level functions in
`turn_phase_registry.py`, no gameplay engine imports, descriptor order and
keys unchanged.

### Phase 5: Validate and document
Run focused turn-engine + FMS-B suites, then the full sharded suite. Update
`docs/systems/strategy_layer.md` only if it explicitly describes hook
placement or registry ownership.

## Related Documents

- Source TD plan: [TD-04 phase registry hooks](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-04_phase_registry_hooks.md)
- Execution order: [EXECUTION_ORDER.md](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/EXECUTION_ORDER.md)
- Design rationale: [design.md](design.md)
- Decisions log: [decisions.md](decisions.md)
- File manifest: [manifest.md](manifest.md)
- Findings ledger: [findings_ledger.md](findings_ledger.md)

## Verification

- [ ] `turn_phase_registry.py` defines no module-level behavior functions.
- [ ] `turn_phase_registry.py` imports no gameplay engine classes
      (`PlanetModifierEffectEngine`, `MinefieldResolver`, etc.).
- [ ] `DEFAULT_TICK_PHASE_LIST` and `DEFAULT_END_OF_TURN_PHASE_LIST` keep the
      same phase keys, order, and timing buckets.
- [ ] `TURN PERF` output format is unchanged.
- [ ] `TurnEngine.last_environmental_events` behavior is unchanged.
- [ ] `_booster_dirty` behavior is unchanged.
- [ ] Minefield resolution still runs after movement and before combat with
      `registries=engine._registries`.
- [ ] Fleets emptied by minefield damage are pruned exactly as before.
- [ ] Registry-purity AST guard is in place.
- [ ] Focused turn-engine + FMS-B suites are green.
- [ ] `python Tools/test_sharded/test_sharded.py` is green.
- [ ] All phase checklists complete.
- [ ] Audit passed.
- [ ] User verified.
