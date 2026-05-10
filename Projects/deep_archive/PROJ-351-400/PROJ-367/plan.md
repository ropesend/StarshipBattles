# PROJ-367: Unified Stat Contributor Extension Surface (typed abilities + registry-as-pipeline)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-367` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-367 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Typed ability classes (PodStorage, MultiplexTracking, VehicleStorage; extend VehicleLaunchAbility) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Built-in Phase-3 contributors as registry entries (collapse two-tier model) | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Typed `StatAccumulator` dataclass (10 scalar + 4 map fields) | Complete | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-05-04 (PROJ-367 closure)
**Active Phase:** All 3 phases complete; ready for audit / user verification.
**Last Action:** Phase 3 committed; sharded suite green; PROJ-360 cross-link backfilled (EXT-07/EXT-11/EXT-13 marked resolved); `docs/02_PATTERNS.md` § 35 rewritten for the unified extension surface.
**Next Action:** User review / audit. The unified extension surface goal is achieved: one registry, typed ability classes, typed StatAccumulator.
**Blockers:** None.

**Commits:**
- Phase 1: `bd473a798` — typed ability classes (closes EXT-07)
- Phase 2: `60e61851d` — built-in contributors as registry entries (closes EXT-11)
- Phase 3: `9a46e7a9d` — typed `StatAccumulator` (closes EXT-13)

## Overview

PROJ-360 decomposed `ShipStatsCalculator` into a `stat_contributors/` package and added `STAT_CONTRIBUTOR_REGISTRY` for extension. The decomposition succeeded; the extension surface did not. PROJ-367 unifies the extension model so every stat-bearing **Phase-3 (per-component, post-`is_operational`) ability** flows through one registry-driven pipeline, with a typed accumulator instead of a raw dict. **Phase 5** helpers (`aggregate_targeting_scores`, `apply_armor_and_repair_scores`, `init_armor_pool`) stay imperative and out-of-scope for this project.

## Goals

- **EXT-07 closed (Phase 1):** `MultiplexTracking`, `VehicleStorage`, `PodStorage` get typed ability classes (`MultiplexTrackingAbility.slots: int`, `VehicleStorageAbility.capacity: int`, `PodStorageAbility.capacity_mass: float`); `VehicleLaunchAbility` is extended with `max_launch_mass: float` to support the existing hangar contributor; `Armor` is consumed exclusively via `has_ability` (marker idiom). Zero `comp.abilities.get(...)` reads remain in `stat_contributors/` and `ship_stats.py:_phase_stats_aggregation`.
- **EXT-11 closed (Phase 2):** Built-in Phase-3 domain functions (`aggregate_propulsion`, `aggregate_defense`, `aggregate_hangar`, `track_multiplex`) are split into per-ability `contribute_*` functions and registered into `STAT_CONTRIBUTOR_REGISTRY` at module import as default entries. Modders register the same way; replacement entries inherit `phase_order=99` (modder default) so they fire after non-replaced built-ins, mirroring today's "skip-built-in-then-modder-runs-last" semantics. The `BUILTIN_HANDLED_ABILITIES` suppression frozenset, `is_builtin_suppressed_for`, and `apply_registered_contributors` are retired. `RegistrationHandle` makes APPEND entries individually addressable.
- **EXT-13 closed (Phase 3):** `acc: Dict[str, Any]` replaced with a `StatAccumulator` `@dataclass` of **10 scalar fields + 4 named map fields = 14 total**. Misspelled scalar/map field names raise `AttributeError` at runtime. Dynamic resource keys (`max_<resource>`, `gen_<resource>`) live inside the `resource_storage` and `resource_generation` map fields, not as top-level scalars.
- All five Phase 3 domains' golden snapshots remain bit-identical through the migration. Pass count grows with new tests; zero regressions.
- A new acceptance test proves that registering a contributor *replaces* the built-in for the same ability without needing a separate suppression mechanism, and that APPEND entries can be individually unregistered without disturbing the default.

## Scope

**In:**
- `game/simulation/components/abilities/markers.py` — add `MultiplexTrackingAbility`, `VehicleStorageAbility`, `PodStorageAbility`. Extend existing `VehicleLaunchAbility` with `max_launch_mass: float`.
- `game/simulation/components/abilities/stat_keys.py` — new `StatKey` entries only if any ability needs stat bindings (current scope: none).
- `game/simulation/components/ability_manager.py` — verify the ability factory routes the new class names; add registration if needed.
- `game/simulation/entities/stat_contributors/registry.py` — add `RegistrationConflictPolicy`, `RegistrationHandle`, `phase_order` field, `iter_for(comp)` helper, `_seed_builtin_contributors()`. Retire `BUILTIN_HANDLED_ABILITIES`, `is_builtin_suppressed_for`, `apply_registered_contributors`. Phase 3: declare `StatAccumulator` dataclass here or in a sibling `accumulator.py` if registry.py would push the 500 LOC ceiling.
- `game/simulation/entities/stat_contributors/{movement,defense,launch,command}.py` — split today's `aggregate_propulsion` / `aggregate_defense` / `aggregate_hangar` / `track_multiplex` into per-ability `contribute_*` functions; migrate dict-access call sites to typed access.
- `game/simulation/entities/ship_stats.py` — Phase 1: migrate `comp.abilities.get("Armor"/"PodStorage")` reads. Phase 2: `_phase_stats_aggregation` becomes a single registry iteration loop. Phase 3: `acc: Dict` → `accumulator: StatAccumulator`; `_aggregate_resource_abilities` writes into `accumulator.resource_storage` / `resource_generation` instead of synthetic dict keys.
- `conftest.py` — verify `reset_stat_contributor_registry` clears AND re-seeds defaults after Phase 2 lands.
- `tests/unit/simulation/components/abilities/test_markers.py` — add unit tests for the new + extended ability classes.
- `tests/unit/simulation/entities/stat_contributors/test_typed_contributor_migration.py` (new) — AST regression locking zero `comp.abilities.get(...)` reads in scope.
- `tests/unit/simulation/entities/stat_contributors/test_registry_pipeline.py` (new) — replacement / append / phase-ordering / handle-based unregister / deprecation-warning tests.
- `tests/unit/simulation/entities/stat_contributors/test_stat_accumulator.py` (new) — 14-field assertion via `dataclasses.fields()`; misspelled-field `AttributeError` test.
- `tests/unit/simulation/entities/stat_contributors/test_registry.py` — migrate to handle-based unregister; remove suppression-frozenset assertions.
- `tests/unit/simulation/entities/test_ship_stats_golden.py` — add carrier + multiplex-equipped designs (closes PROJ-360 review FIND-001 / FIND-005 incidentally).
- `docs/02_PATTERNS.md` § 35 — update extension pattern.
- `Projects/active_projects/PROJ-360/decisions.md` — backfill cross-link: EXT-07/EXT-11/EXT-13 marked resolved.

**Out:**
- `weapons.py` (entirely) — Phase 5 helper, post-physics. Future project required for accumulator-survives-physics-boundary work.
- `aggregate_targeting_scores`, `apply_armor_and_repair_scores`, `init_armor_pool` — Phase 5 helpers, untouched.
- New stat domains beyond the existing five.
- Mod-loading mechanics or hot-reload (registry stays import-time).
- `ship_design_stats.py` and `combat_endurance.py` (separate complexity hotspots called out by PROJ-360 review as future work).
- `ability_stat_registry.py` (combat-side modifier pipeline) — different concern.
- UI changes — `ShipStatsCalculator.calculate(ship)` signature is preserved.

## Key Files

| Component | File Path |
|-----------|-----------|
| Existing stat-contributor registry | `game/simulation/entities/stat_contributors/registry.py` |
| Built-in Phase-3 domains (in scope for split) | `game/simulation/entities/stat_contributors/{movement,defense,launch,command}.py` |
| Built-in Phase-5 helper (out of scope) | `game/simulation/entities/stat_contributors/weapons.py` |
| Calculator | `game/simulation/entities/ship_stats.py` |
| Ability marker classes (target for new typed classes) | `game/simulation/components/abilities/markers.py` |
| Existing typed reference (extend, don't replace) | `game/simulation/components/abilities/markers.py` (`VehicleLaunchAbility`) |
| Ability factory / loader | `game/simulation/components/ability_manager.py` |
| Existing typed reference (read-only) | `game/simulation/components/abilities/propulsion.py` (`CombatPropulsion`) |
| Golden snapshot | `tests/unit/simulation/entities/test_ship_stats_golden.py` + `test_ship_stats_golden_snapshot.json` |
| Existing acceptance test | `tests/unit/simulation/entities/stat_contributors/test_stat_contributor_extension.py` |
| Patterns doc | `docs/02_PATTERNS.md` § 35 |

## Related Documents

- [design.md](design.md) — diagnosis, current vs. target pipeline, alternatives considered, risks
- [decisions.md](decisions.md) — design choices and rejected alternatives (with Codex pressure-test outcomes)
- Codex discussion outcome: `AgentCoordination/Scratchpad/Discussion/20260505T150915Z_proj-367-plan-review/outcome.md` (and the four plan revisions in `plans/`)
- PROJ-360 review extensibility report: `Reviews/results/2026-05-05_073251_code_proj-360-review-shipstatscalculator-domain-decompo_req-req_20260505_073251_b48e74/findings/extensibility_report.md`
- PROJ-360 remediation commit: `79e79d9e5`

## Today's vs. target pipeline (one-line diff)

**Today** (`ship_stats.py:258-269`):
```
_mov.aggregate_propulsion(comp, acc)
_def.aggregate_defense(ship, comp, acc)
_launch.aggregate_hangar(ship, comp)
_cmd.track_multiplex(ship, comp)
apply_registered_contributors(ship, comp, acc)   # gated by BUILTIN_HANDLED_ABILITIES suppression frozenset
```

**Target** (after Phase 2):
```
for entry in STAT_CONTRIBUTOR_REGISTRY.iter_for(comp):
    entry.contributor(ship, comp, accumulator)   # accumulator: StatAccumulator after Phase 3
```

Phase 5 (`ship_stats.py:435-447`) is unchanged.

## Phases

### Phase 1: Typed ability classes [Medium]
**Objective:** Eliminate `comp.abilities.get(...)` raw-dict reads for the five untyped abilities. Each gets a typed class (or, for `Armor`, exclusively `has_ability`). `VehicleLaunchAbility` extended with `max_launch_mass`. Golden snapshot bit-identical.
**Status:** Not Started

See [phase_1_checklist.md](phase_1_checklist.md).

### Phase 2: Built-in Phase-3 contributors as registry entries [Medium]
**Objective:** Register the four Phase-3 domain contributors (`aggregate_propulsion`, `aggregate_defense`, `aggregate_hangar`, `track_multiplex`) split into per-ability `contribute_*` functions, as default `STAT_CONTRIBUTOR_REGISTRY` entries at module import. `_phase_stats_aggregation` becomes a single registry iteration. Retire `BUILTIN_HANDLED_ABILITIES`. Replacement entries inherit `phase_order=99`. `RegistrationHandle` makes APPEND entries individually addressable. Phase 5 helpers untouched. Golden snapshot bit-identical.
**Status:** Not Started

See [phase_2_checklist.md](phase_2_checklist.md).

### Phase 3: Typed `StatAccumulator` dataclass [Medium]
**Objective:** Replace `acc: Dict[str, Any]` with a `StatAccumulator` `@dataclass` of 10 scalar fields + 4 named map fields = 14 total. Misspelled field access raises `AttributeError`. Dynamic resource keys live inside `resource_storage` / `resource_generation` map fields. Golden snapshot bit-identical. `docs/02_PATTERNS.md` § 35 updated.
**Status:** Not Started

See [phase_3_checklist.md](phase_3_checklist.md).

## Verification Checklist

### Project Start (REQUIRED)
- [ ] Read `docs/` foundation docs (01_ARCHITECTURE, 02_PATTERNS, 03_CONVENTIONS)
- [ ] Read PROJ-360 review extensibility report (the source-of-truth findings)
- [ ] Read PROJ-360 remediation commit `79e79d9e5` (current state of `stat_contributors/`)
- [ ] Read Codex discussion outcome at `AgentCoordination/Scratchpad/Discussion/20260505T150915Z_proj-367-plan-review/outcome.md` for the pressure-test rationale
- [ ] Run full test suite: `python Tools/test_sharded/test_sharded.py` — capture baseline pass count

### After Each Phase
- [ ] Run `pytest tests/unit/simulation/entities/ -v` — domain tests pass
- [ ] Run `pytest tests/unit/simulation/components/abilities/ -v` — ability class tests pass
- [ ] Run `python Tools/test_sharded/test_sharded.py` — sharded suite green; pass count grows monotonically
- [ ] Update `Current State` in this plan with handoff context for the next agent

### Final Verification
- [ ] Sharded suite green; pass count ≥ baseline + new tests
- [ ] Golden snapshot at `test_ship_stats_golden.py` matches bit-for-bit (no `--update-snapshot` runs across the project, except Phase 1 Task 1.9 which adds new fixtures; existing 7 designs untouched)
- [ ] Zero `comp.abilities.get(...)` reads in `stat_contributors/` and `ship_stats.py:_phase_stats_aggregation` (AST regression test)
- [ ] `BUILTIN_HANDLED_ABILITIES`, `is_builtin_suppressed_for`, `apply_registered_contributors` are deleted; the symbols are no longer importable
- [ ] `_phase_stats_aggregation` is one iteration loop
- [ ] `StatAccumulator` is a `@dataclass` with exactly 14 fields (verified via `dataclasses.fields()`)
- [ ] `acc[...]` dict-syntax reads/writes are gone from `stat_contributors/` and `ship_stats.py`
- [ ] Acceptance test: registering a contributor for `ShieldProjection` replaces the built-in (no double-count, no suppression frozenset needed)
- [ ] APPEND test: appended entry can be individually unregistered via handle without disturbing the default
- [ ] Combat endurance verified via `ship.resources` (not via accumulator) — `calculate_combat_endurance` outputs match golden snapshot
- [ ] `docs/02_PATTERNS.md` § 35 reflects the unified extension surface
- [ ] PROJ-360 `decisions.md` cross-link backfilled

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All tests passing (sharded suite green)
- [ ] Audit passed (no significant issues)
- [ ] User verified
