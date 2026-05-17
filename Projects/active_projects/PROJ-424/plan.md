# PROJ-424: Order metadata convergence (TD-03)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-424` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-424 [phase]` before stopping
> - Update Current State with specific handoff context

**Execution Protocol:** 03c-phase-aware-execution

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 0. Preflight + remaining-consumer inventory | Complete | [phase_0_checklist.md](phase_0_checklist.md) |
| 1. Explicit `planet_fms` metadata + registry derivation | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Add `OrderMetadataView` (lazy, cycle-safe) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Migrate snapshot consumer (`action_time_resolver.py`) | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Migrate remaining production consumers | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Delete duplicated constants + `fleet.py` re-exports | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Docs convergence + final grep gate | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-05-17
**Active Phase:** Phase 1
**Last Action:** Phase 0 baseline captured — reader counts confirmed; manifest is a superset of test imports; 40 (not 41) `@command_spec` decorators total but the 5 FMS handlers are unambiguous
**Next Action:** Start Phase 1 by writing the failing `test_exactly_five_specs_carry_planet_fms_subcategory` + `test_planet_fms_action_order_types_derivation_matches_constant` tests
**Blockers:** None

## Overview
Five distinct truth surfaces in the strategy layer encode overlapping order metadata: the 41-DTO command catalog, `CommandRegistry`, three hardcoded frozensets in `order_types.py` (`MOVEMENT_ORDER_TYPES`, `ACTION_ORDER_TYPES`, `PLANET_ACTION_ORDER_TYPES`), a fourth hardcoded frozenset `PLANET_FMS_ACTION_ORDER_TYPES`, and the import-time-frozen `ORDER_TO_ABILITY_MAP` snapshot in `action_time_resolver.py`. The frozensets are pinned hardcoded because runtime derivation from `CommandRegistry` would trigger an import cycle through the order handlers. The contract test pins equality at test time but does nothing about runtime drift if `command_registry.register(..., replace=True)` is called after import.

This project converges all five surfaces onto a single cycle-safe, lazy `OrderMetadataView` that imports `command_registry` only inside its `_registry()` method and seeds the registry on first read. The view becomes the only metadata read path used by engines and services; the duplicated frozensets and the import-time snapshot are deleted after consumers migrate; and the five FMS handlers gain an explicit `subcategories={"planet_fms"}` tag so the FMS derivation is data-driven rather than hardcoded.

## Goals
- Add `OrderMetadataView` at `game/strategy/engine/commands/order_metadata_view.py` as a live, lazy reader over `command_registry`. Lazy import inside `_registry()` breaks the import cycle.
- Tag the five FMS handler command specs (`lay_mines`, `launch_fighters`, `launch_satellites`, `recover_fighters`, `recover_satellites`) with `subcategories=frozenset({"planet_fms"})`. Derive `planet_fms_action_order_types()` from the tag, not from a handler-name list.
- Replace the import-time `ORDER_TO_ABILITY_MAP` snapshot in `action_time_resolver.py` with a call-time read of `order_metadata.order_to_ability_map`.
- Migrate the 8 production consumers (engines + services) off the duplicated `order_types.py` frozensets and the `fleet.py` re-exports onto `order_metadata`.
- Delete `MOVEMENT_ORDER_TYPES`, `ACTION_ORDER_TYPES`, `PLANET_ACTION_ORDER_TYPES`, `PLANET_FMS_ACTION_ORDER_TYPES`, and the `fleet.py` re-exports after all consumers are migrated. No compatibility aliases.
- Update `docs/systems/orders_system.md`, `docs/04_SERVICES.md`, and `docs/systems/satellites.md` to describe `order_metadata` as the single read path; remove instructions telling contributors to edit frozensets manually.
- Add `test_order_metadata_view.py` with explicit lazy-import + replace-overlay coverage, and `test_order_types_no_duplicated_metadata.py` as the final guard.

## Scope
**In:** add `order_metadata_view.py`; tag five FMS command specs and add `CommandRegistry.planet_fms_action_order_types()`; migrate `action_time_resolver.py` off `ORDER_TO_ABILITY_MAP` and the duplicated frozensets; migrate remaining 8 production consumers onto `order_metadata`; delete the four duplicated frozensets in `order_types.py` and the re-exports in `fleet.py`; update 3 docs pages; add 2 new test modules; update 7 existing test modules to assert against the view.

**Out:** relocating the 41-DTO catalog in `game/strategy/engine/commands/__init__.py`; introducing caching or invalidation in `OrderMetadataView`; eliminating `command_registry.register(..., replace=True)`; module-level compatibility aliases in `order_types.py`; touching `CommandSpec` semantics or `CommandRegistry` mutator semantics beyond adding the FMS derivation method; ability-metadata convergence (that is TD-07 / PROJ-429, which mirrors this pattern but builds a registry rather than a view).

## Dependencies
Hard predecessors: none. Soft predecessors: none. **This is a HARD predecessor of PROJ-429 (TD-07).** PROJ-429 must wait for this project to complete. TD-07 mirrors this lazy-view pattern for ability metadata (though TD-07 builds a registry rather than a view — see [TD-07 plan](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-07_ability_metadata_unification.md) for the shape rationale). See [EXECUTION_ORDER.md](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/EXECUTION_ORDER.md) §"Recommended Linear Order #3" and "Phase Gate #4".

Independent of TD-01, TD-02, TD-08. The facade already reads live registry state; this plan narrows the metadata path only.

## Key Files

### New production file
| Component | File Path | Type |
|-----------|-----------|------|
| Live lazy metadata view | `game/strategy/engine/commands/order_metadata_view.py` | Production (new) |

### Production files to edit
| Component | File Path | Type |
|-----------|-----------|------|
| Command spec registry | `game/strategy/engine/commands/registry.py` | Production |
| Duplicated frozensets (delete in Phase 5) | `game/strategy/data/order_types.py` | Production |
| Re-exports (delete in Phase 5) | `game/strategy/data/fleet.py` | Production |
| Import-time snapshot owner | `game/strategy/services/action_time_resolver.py` | Production |
| Action engine consumer | `game/strategy/engine/action_execution_engine.py` | Production |
| Fleet movement engine consumer | `game/strategy/engine/fleet_movement_engine.py` | Production |
| Planet action engine consumer | `game/strategy/engine/planet_action_engine.py` | Production |
| Fleet navigation service consumer | `game/strategy/services/fleet_navigation_service.py` | Production |
| Fleet path projection consumer | `game/strategy/services/fleet_path_projection.py` | Production |
| Cargo transfer service consumer | `game/strategy/services/cargo_transfer_service.py` | Production |

### FMS handler files to tag (Phase 1)
| File Path | Type |
|-----------|------|
| `game/strategy/engine/handlers/lay_mines.py` | Production |
| `game/strategy/engine/handlers/launch_fighters.py` | Production |
| `game/strategy/engine/handlers/launch_satellites.py` | Production |
| `game/strategy/engine/handlers/recover_fighters.py` | Production |
| `game/strategy/engine/handlers/recover_satellites.py` | Production |

### New tests
| File Path | Type |
|-----------|------|
| `tests/unit/strategy/engine/commands/test_order_metadata_view.py` | Test (new) |
| `tests/unit/strategy/data/test_order_types_no_duplicated_metadata.py` | Test (new) |

### Existing tests to update
| File Path | Type |
|-----------|------|
| `tests/unit/strategy/engine/test_command_specs_contract.py` | Test |
| `tests/unit/strategy/engine/test_command_registry_contract.py` | Test |
| `tests/unit/strategy/engine/test_command_registry_thirdparty.py` | Test |
| `tests/unit/strategy/data/test_order_types_characterization.py` | Test |
| `tests/unit/strategy/services/test_action_time_resolver.py` | Test |
| `tests/unit/strategy/fleet_movement_engine/test_characterization.py` | Test |
| `tests/unit/strategy/engine/order_handlers/test_handler_registry_completeness.py` | Test |
| `tests/unit/strategy/test_fleet_order_processor.py` | Test |

### Docs to update (Phase 6)
| File Path | Type |
|-----------|------|
| `docs/systems/orders_system.md` | Docs |
| `docs/04_SERVICES.md` | Docs |
| `docs/systems/satellites.md` | Docs |

Full enumeration lives in [manifest.md](manifest.md).

## Phases

### Phase 0: Preflight + remaining-consumer inventory
Run the two `rg` commands from the TD-03 Executor Guardrails to capture the current consumer inventory and confirm `PLANET_FMS_ACTION_ORDER_TYPES` still has exactly one production consumer (`action_execution_engine.py`). Record every test file that imports the duplicated constants directly so Phase 4/5 know what to update. No production edits in this phase.

### Phase 1: Explicit `planet_fms` metadata + registry derivation
Write the failing tests first: `test_planet_fms_action_order_types_derivation_matches_constant` and `test_exactly_five_specs_carry_planet_fms_subcategory`. Add `subcategories=frozenset({"planet_fms"})` to the five FMS `@command_spec(...)` declarations. Add `CommandRegistry.planet_fms_action_order_types()` deriving from the `subcategories` tag (not from handler paths or a hardcoded order-name list). Update `test_command_specs_contract.py` to assert the derivation.

### Phase 2: Add `OrderMetadataView` (lazy, cycle-safe)
Write the failing tests first: `test_view_movement_matches_registry`, `test_view_action_matches_registry`, `test_view_planet_action_matches_registry`, `test_view_planet_fms_matches_registry`, `test_view_order_to_ability_matches_registry`, `test_view_is_lazy_at_import_time`, `test_view_reflects_replace_overlay`. Create `order_metadata_view.py` exposing `OrderMetadataView` and a module-level `order_metadata` singleton. The `_registry()` staticmethod imports `command_registry` + `seed_default_commands` lazily and calls `seed_default_commands` on empty. No caching, no invalidation. Consumers are not migrated yet.

### Phase 3: Migrate `action_time_resolver.py` (snapshot consumer)
Most dangerous stale-snapshot first. Write the failing test `test_resolve_action_time_reflects_registry_replace` and update the contract test to assert against `order_metadata.order_to_ability_map`. Delete `_build_order_to_ability_map` and the module-level `ORDER_TO_ABILITY_MAP`. Replace `MOVEMENT_ORDER_TYPES` / `PLANET_ACTION_ORDER_TYPES` imports with `order_metadata`. `resolve_action_time(...)` reads `order_metadata.order_to_ability_map` at call time.

### Phase 4: Migrate remaining production consumers
Migrate `action_execution_engine.py`, `fleet_movement_engine.py`, `planet_action_engine.py`, `fleet_navigation_service.py`, `fleet_path_projection.py`, and `cargo_transfer_service.py` from duplicated constant imports to `from game.strategy.engine.commands.order_metadata_view import order_metadata`. Update related characterization/contract tests. Do NOT touch `order_types.py` constants yet — production is cleaned first.

### Phase 5: Delete duplicated constants + `fleet.py` re-exports
Write the failing tests `test_order_types_module_no_longer_exports_metadata_constants` and `test_fleet_module_no_longer_re_exports_metadata_constants`. Delete `MOVEMENT_ORDER_TYPES`, `ACTION_ORDER_TYPES`, `PLANET_ACTION_ORDER_TYPES`, `PLANET_FMS_ACTION_ORDER_TYPES` from `order_types.py`. Delete the `fleet.py` re-exports. Update any remaining tests still importing the constants. No compatibility aliases. Full sharded suite must pass at this boundary.

### Phase 6: Docs convergence + final grep gate
Update `docs/systems/orders_system.md`, `docs/04_SERVICES.md`, `docs/systems/satellites.md` to reference `order_metadata` as the single read path. Remove guidance that tells contributors to edit `ORDER_TO_ABILITY_MAP` or frozensets manually. Document the `planet_fms` subcategory and the lazy-view cycle break. Final grep over `game`, `docs`, `tests`: only `registry.py` derivation methods and `order_metadata_view.py` should match the duplicated-constant names. Full sharded suite green.

## Related Documents
- [TD-03 source plan](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-03_order_metadata_convergence.md) — canonical specification (verification findings, cycle analysis, consumer inventory, per-phase exit criteria, risks)
- [Strategy tech-debt EXECUTION_ORDER.md](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/EXECUTION_ORDER.md) — execution order and phase gates
- [TD-07 source plan](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-07_ability_metadata_unification.md) — the downstream consumer of this work (PROJ-429)
- [design.md](design.md) — `OrderMetadataView` class contract, cycle analysis, duplicated-frozenset inventory
- [decisions.md](decisions.md) — full decisions log
- [manifest.md](manifest.md) — enumerated file touch list

## Verification
Acceptance criteria from the TD-03 plan:
- [ ] `game/strategy/engine/commands/order_metadata_view.py` exists and imports the registry only inside `_registry()`.
- [ ] The five FMS handler specs carry `subcategories=frozenset({"planet_fms"})`.
- [ ] `CommandRegistry` exposes `planet_fms_action_order_types()` derived from the `subcategories` tag.
- [ ] `game/strategy/services/action_time_resolver.py` has no `ORDER_TO_ABILITY_MAP`.
- [ ] `game/strategy/data/order_types.py` exports no metadata frozensets.
- [ ] `game/strategy/data/fleet.py` no longer re-exports order-metadata constants.
- [ ] Production consumers read metadata through `order_metadata`.
- [ ] `tests/unit/strategy/engine/commands/test_order_metadata_view.py` exists and passes (including `test_view_is_lazy_at_import_time` and `test_view_reflects_replace_overlay`).
- [ ] `tests/unit/strategy/data/test_order_types_no_duplicated_metadata.py` exists and passes.
- [ ] `python Tools/test_sharded/test_sharded.py` passes after Phase 5 and again after Phase 6.
- [ ] Docs no longer instruct contributors to edit `ORDER_TO_ABILITY_MAP` or the duplicated frozensets manually.
