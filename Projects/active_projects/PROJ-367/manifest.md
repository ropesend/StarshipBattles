# PROJ-367 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.
>
> **This file reflects the post-Codex-consensus state** (r002 + r003 + r004 corrections merged).

## Files modified or created

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `game/simulation/components/abilities/markers.py` | Production (modify) | 1 | Add `MultiplexTrackingAbility` (`slots: int`), `VehicleStorageAbility` (`capacity: int`), `PodStorageAbility` (`capacity_mass: float`). Extend existing `VehicleLaunchAbility` with `max_launch_mass: float`. |
| `game/simulation/components/abilities/stat_keys.py` | Production (modify) | 1 | New `StatKey` entries only if any new ability needs stat bindings (current scope: none expected). |
| `game/simulation/components/ability_manager.py` | Production (modify) | 1 | Verify factory routes new class names; add registration if needed. |
| `game/simulation/entities/stat_contributors/launch.py` | Production (modify) | 1, 2 | Phase 1: migrate `comp.abilities.get("VehicleLaunch", {})` and `comp.abilities.get("VehicleStorage", 0)` to typed access. Phase 2: split `aggregate_hangar` into per-ability `contribute_*` functions; delete `aggregate_hangar` wrapper. |
| `game/simulation/entities/stat_contributors/command.py` | Production (modify) | 1, 2 | Phase 1: migrate `comp.abilities.get("MultiplexTracking", 0)` to typed access. Phase 2: split `track_multiplex` into per-ability `contribute_*` functions; delete `track_multiplex` wrapper. |
| `game/simulation/entities/stat_contributors/defense.py` | Production (modify) | 1, 2 | Phase 1: migrate `Armor` to `has_ability`. Phase 2: split `aggregate_defense` into per-ability `contribute_*` functions; delete `aggregate_defense` wrapper. |
| `game/simulation/entities/stat_contributors/movement.py` | Production (modify) | 2 | Phase 2: split `aggregate_propulsion` into per-ability `contribute_*` functions; delete `aggregate_propulsion` wrapper. |
| `game/simulation/entities/stat_contributors/weapons.py` | Production (untouched) | — | **Phase 5 helper, post-physics — out-of-scope for PROJ-367.** Future project required for accumulator-survives-physics-boundary work. |
| `game/simulation/entities/stat_contributors/registry.py` | Production (modify) | 2, 3 | Phase 2: add `RegistrationConflictPolicy`, `RegistrationHandle`, `phase_order` field, `iter_for(comp)` helper, `_seed_builtin_contributors()`. Retire `BUILTIN_HANDLED_ABILITIES`, `is_builtin_suppressed_for`, `apply_registered_contributors`. Phase 3: declare `StatAccumulator` dataclass here OR in a sibling `accumulator.py` if registry.py would push the 500 LOC ceiling. |
| `game/simulation/entities/stat_contributors/accumulator.py` | Production (new — optional) | 3 | Sibling module for `StatAccumulator` dataclass if `registry.py` would push 500 LOC. Decide at implementation time. |
| `game/simulation/entities/stat_contributors/__init__.py` | Production (modify) | 2 | Seed default contributors at module import via `_seed_builtin_contributors()`. Update `__all__`. |
| `game/simulation/entities/stat_contributors/_builtins.py` | Production (new — optional) | 2 | Dedicated module for default-seed function if `__init__.py` would grow too large. Decide at implementation time. |
| `game/simulation/entities/ship_stats.py` | Production (modify) | 1, 2, 3 | Phase 1: migrate `comp.abilities.get("Armor"/"PodStorage")` reads at lines 201, 207, 315. Phase 2: `_phase_stats_aggregation` (Phase 3 path, lines 258-269) becomes a single registry iteration loop. Phase 3: `acc: Dict` → `accumulator: StatAccumulator`; `_aggregate_resource_abilities` writes into `accumulator.resource_storage` / `resource_generation`. **Phase 5 path (lines 433-447) untouched.** |
| `conftest.py` | Test (verify) | 2 | Verify `reset_stat_contributor_registry` re-seeds defaults after reset (not just clears). Likely no change if Task 2.4 lands the seeding correctly inside the helper. |
| `tests/unit/simulation/components/abilities/test_markers.py` | Test (modify or new) | 1 | Add unit tests for `MultiplexTrackingAbility`, `VehicleStorageAbility`, `PodStorageAbility` (parse + recalculate + UI rows). Add tests for `VehicleLaunchAbility.max_launch_mass`. |
| `tests/unit/simulation/entities/stat_contributors/test_typed_contributor_migration.py` | Test (new) | 1 | AST regression: zero `comp.abilities.get(...)` reads in `stat_contributors/` and `ship_stats.py:_phase_stats_aggregation` path. |
| `tests/unit/simulation/entities/stat_contributors/test_registry_pipeline.py` | Test (new) | 2 | Replacement test (`REPLACE_WARN`/`SILENT`), append test (`APPEND`), error test (`ERROR`), phase-ordering test, REPLACE_WARN-emits-log test, handle-based unregister tests, `CannotUnregisterDefaultError` test, `DeprecationWarning` test for `_by_name` shim. |
| `tests/unit/simulation/entities/stat_contributors/test_stat_accumulator.py` | Test (new) | 3 | `dataclasses.fields(StatAccumulator)` returns exactly 14; misspelled-field `AttributeError` test; default values verified. |
| `tests/unit/simulation/entities/stat_contributors/test_registry.py` | Test (modify) | 2 | Migrate to handle-based unregister (Task 2.7a). Remove suppression-frozenset assertions. Update double-registration assertions for new policy semantics. |
| `tests/unit/simulation/entities/test_ship_stats_golden.py` | Test (modify) | 1 | Add carrier design + multiplex-equipped design fixtures (closes PROJ-360 FIND-001 / FIND-005). |
| `tests/unit/simulation/entities/test_ship_stats_golden_snapshot.json` | Test (modify) | 1 | Auto-regenerated when new fixtures added; bit-identical for existing 7 designs. |
| `Projects/active_projects/PROJ-360/decisions.md` | Project doc (modify) | 3 | Backfill cross-link: EXT-07/EXT-11/EXT-13 marked resolved by PROJ-367 commit `<sha>`. |
| `docs/02_PATTERNS.md` | Documentation (modify) | 3 | § 35 updated to describe the unified extension surface (one registry, one typed accumulator, one mutation contract). Update `> **Last verified:**` blockquote. |
