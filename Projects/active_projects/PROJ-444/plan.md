# PROJ-444: Post-refactor residue — Data + Facade layer (Bucket A)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-444` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-444 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Tiny one-shot fixes (≤30 LOC each) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Container-substrate residue cleanup | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. PROJ-436 deletion-shim retirement (cross-coupled with PROJ-443) | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. LOC-ceiling extractions (fleet_serde, planet_gen) | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-05-18
**Active Phase:** Planning
**Last Action:** Charter created from comprehensive residue scan ([findings/bucket_a_data_facade_scan.md](findings/bucket_a_data_facade_scan.md), 32 findings)
**Next Action:** User review of scope/phasing, then expand phase checklists from the findings file
**Blockers:** None — but Phase 3 is coupled to PROJ-443 Phase 5b decision (shared 18-file test sweep)

## Overview

Residue cleanup for the **`game/strategy/data/` + `game/strategy/facade/`** layer accumulated across ~22 archived refactors (PROJ-329A, 351A-354B, 416-435) and the in-flight PROJ-436 / PROJ-437. Companion project to PROJ-445 (engine + services residue) and PROJ-446 (UI + core + tests residue) — by design the three projects touch **disjoint file sets** so they can run in parallel without merge conflicts.

The findings come from a layer-scoped automated scan on 2026-05-18 that read every closed project's `decisions.md` / `findings_ledger.md` for deferred items, grepped the layer for `back-compat` / `shim` / `legacy` / `TODO` / `FIXME` markers, and cross-referenced against the 9 entries already in `AgentCoordination/discovered_issues/log.jsonl` (deduplicated, not refiled).

## Goals

- Burn down obsolete back-compat shims and deletion-property clusters left by PROJ-436 Phase 3f/4f when their migration sweeps were intentionally deferred
- Close the small invariant gaps (negative-quantity guards, hardcoded resource IDs, mass-cap proxies) that are the same anti-pattern as `discovered_issues/log.jsonl` entries DI-003/004/005/006 but on adjacent surfaces in this layer
- Bring `ship_instance.py` (839 LOC), `fleet.py` (677 LOC), `planet_gen.py` (610 LOC) toward the 500-LOC ceiling via responsibility-based extraction (fleet_serde.py modeled on planet_serde.py is the obvious win)
- Tighten facade DTO contracts (immutable views, stable catalog-order iteration, typed queue entries) so the facade boundary actually enforces what its docstrings claim
- Replace 7 conditional `pytest.skip` calls in facade/save-load integration tests with deterministic fixtures so RNG-flaky CI never silently passes

## Scope

**In (this project owns these files):**
- All files under `game/strategy/data/`
- All files under `game/strategy/facade/` (slices, DTOs, helpers)
- Tests under `tests/unit/strategy/data/`, `tests/unit/strategy/facade/`
- Tests under `tests/integration/` whose primary subject is a class in the above directories (save_load, facade_integration, etc.)

**Out (PROJ-445 owns these — do NOT touch in this project):**
- `game/strategy/engine/` (production_engine, order_handlers, commands, action_execution_engine, turn_engine, superweapon, etc.)
- `game/strategy/services/` (component_inspector, effect_ability_metadata, replay_store, etc.)
- Tests targeting engine/services

**Out (PROJ-446 owns these — do NOT touch in this project):**
- `game/ui/` (all screens, panels, widgets, dialogs)
- `game/core/protocols/`, `game/core/exceptions.py`
- `tests/static_guards/`, `tests/regression/`, fixtures in `tests/fixtures/`
- Test files targeting UI screens / protocols

**Out (deferred to future projects regardless of layer):**
- PROJ-443 (pytest norecursedirs fix and hidden-test triage) — already chartered
- The `ShipInstance` 839-LOC monolith split itself — finding F-A-007 documents it as a future "ShipInstance shim retirement" project, not in PROJ-444 scope
- DI-006 / DI-007 (already in discovered_issues/log.jsonl) — engine-side fixes belong to PROJ-445

## Findings Summary

Full report: [findings/bucket_a_data_facade_scan.md](findings/bucket_a_data_facade_scan.md) (32 findings)

| Severity | Count | Notes |
|----------|-------|-------|
| High     | 1     | none in this bucket (Bucket B holds the one TypeError-class high) |
| Medium   | 13    | The Container-substrate invariant gaps + PROJ-436 deferred follow-ups |
| Low      | 18    | Polish, stale comments, `# noqa` clean-up |

| Category | Count |
|----------|-------|
| Obsolete-code | 9 |
| Test-inconsistency | 3 |
| Missing-functionality | 5 |
| Polish | 15 |

### Cross-bucket couplings — coordination points and structural joint-phase seams
- **(STRUCTURAL JOINT-PHASE)** **F-A-002 / F-A-003 / F-A-004 / F-A-005 + PROJ-446 F-C-020 (fixture migration)** — Planet + ShipInstance legacy-kwarg constructor wrappers and their @property deletion shims. PROJ-443 Phase 5b retained these citing an 18-file test sweep cost; Codex consult 2026-05-18 indicates the real footprint is larger AND that `planet_serde.py:160-162` is a non-test dependent. **Critical:** PROJ-446's F-C-020 (`tests/fixtures/strategy_entities.py` 3 fixture-site migration) is the unblock — wrapper retirement cannot land cleanly without first migrating the shared fixture module that PROJ-446 owns. Phase 3 of PROJ-444 MUST run as a **stacked PR with PROJ-446** (or one PR spanning both file sets), not as a coordination point. Audit-then-decide step `rg -n "Planet\(.*stockpile=" tests/` should be run BEFORE committing the phase scope.
- **(STRUCTURAL JOINT-PHASE)** **F-A-013 + PROJ-445 F-B-013 (DropPod boundary)** — Codex consult 2026-05-18 verified this is more than coordination. The staging-yard substrate (`Planet._staging_yard: List[Dict[str, Any]]` at `game/strategy/data/planet.py:98, 253-262, 316-322`) is in THIS bucket; the engine-side flatten/inflate call sites are in PROJ-445. The substrate change (typed `Planet._staging_yard: List[CarriedVehicle | DropPod]` + serializer rewrite + `add_to_staging_yard` signature change) starts here; PROJ-445 finishes the call-site adoption. **Requires a stacked PR.** The originally-listed `_ship_container_snapshot` (F-A-013) tightening also rides along.
- **(Coordination)** **F-A-010** — `Fleet.consume_cargo_resource` int-rounds float `amount`. This is the **fix site** for `discovered_issues/log.jsonl` DI-006 (Fleet rounding mismatch). Whichever project closes DI-006 owns this; expected to be PROJ-444 because the actual code change is in data layer. PROJ-445 F-B-019 tightens the Protocol contract docstring alongside.

## Key Files

| Component | File Path | LOC | Why |
|-----------|-----------|-----|-----|
| Container substrate | `game/strategy/data/container.py` | <500 | F-A-001 (BayInventory parallel guards) |
| BayInventory | `game/strategy/data/bay_inventory.py` | <500 | F-A-001 |
| ShipInstance | `game/strategy/data/ship_instance.py` | **839** | F-A-005, F-A-007 (out of phase, tracked for visibility) |
| Planet | `game/strategy/data/planet.py` | 420 | F-A-002, F-A-004 |
| Fleet | `game/strategy/data/fleet.py` | **677** | F-A-008, F-A-010 |
| Empire | `game/strategy/data/empire.py` | <500 | F-A-011, F-A-026 |
| PlanetaryFacility | `game/strategy/data/planetary_facility.py` | <500 | F-A-012 (hardcoded `"fuel"` API) |
| planet_gen | `game/strategy/data/planet_gen.py` | **610** | F-A-009 |
| Stars | `game/strategy/data/stars.py` | <500 | F-A-022 (PROJ-372 Phase 1 shim) |
| Storm | `game/strategy/data/storm.py` | <500 | F-A-024 |
| OrderSerializer | `game/strategy/data/order_serializer.py` | <500 | F-A-020 |
| FleetInfo DTO | `game/strategy/facade/dto/fleet_dto.py` | <500 | F-A-017 |
| PlanetInfo DTO | `game/strategy/facade/dto/planet_dto.py` | <500 | F-A-019 |
| EmpireInfo DTO | `game/strategy/facade/dto/empire_dto.py` | <500 | F-A-018 |
| BuildQueue DTO | `game/strategy/facade/dto/build_queue_dto.py` | <500 | F-A-015, F-A-016 |
| FleetSlice | `game/strategy/facade/slices/fleet_slice.py` | <500 | F-A-013 |
| PlanetSlice | `game/strategy/facade/slices/planet_slice.py` | <500 | F-A-014 |
| CommandDispatch slice | `game/strategy/facade/slices/command_dispatch_slice.py` | <500 | F-A-030 |
| Facade session state | `game/strategy/facade/slices/_facade_state.py` | <500 | F-A-031, F-A-032 |
| Integration tests | `tests/integration/strategy/facade/test_facade_integration.py` | — | F-A-028 (5 conditional skips) |
| Save/load tests | `tests/integration/save_load/test_resupply_persistence.py` | — | F-A-029 |

## Phase Breakdown

### Phase 1 — Tiny one-shot fixes (≤30 LOC each, ~10 findings)
Mechanical, no cross-file dependencies. Each finding is a self-contained PR-able change. Run targeted tests after each:

- F-A-001: Mirror `add_*` non-negative guards on `BayInventory.remove_resource` / `remove_population`
- F-A-006: Fix stale `350 LOC` reference in `planet_serde.py:4`
- F-A-015 + F-A-016: Type `BuildQueueSourceDTO.construction_queue` properly
- F-A-017: Split the `FleetInfo.from_fleet` two-exception narrow catch
- F-A-018: Add `total_resources` to `EmpireInfo`
- F-A-019: Iterate `ResourceCatalog.all_ids()` in `PlanetInfo.stockpile`
- F-A-020: Raise on unknown `type:` in `OrderSerializer._deserialize_target`
- F-A-021: `# noqa: F401` audit on `galaxy.py:10`
- F-A-022: PROJ-372 Phase 1 `StarGenerator` shim retire
- F-A-023, F-A-026, F-A-027: Stale historical comment cleanup
- F-A-024, F-A-025: Legacy save-shape guards delete
- F-A-030: Cache `specs_by_facade_helper()` result
- F-A-031: Add `empire_index` to facade session state
- F-A-032: Rename `stars_cache_new`

### Phase 2 — Container-substrate residue cleanup
Findings tightly coupled to PROJ-436 Container substrate work that shipped Phase 1-12. Each requires a small audit step:

- F-A-012: Replace `PlanetaryFacility.{add,withdraw}_fuel` hardcoded API with generic `add_consumable(resource_id, ...)` iterating `ResourceCatalog.all_ids()`
- F-A-014: Fix `_planet_stockpile_snapshot` mass-cap calculation (multiply by `mass_per_unit`)
- F-A-010 + DI-006: Pick Option A (widen `_resource_agg.unload_cargo_from_fleet` to float) or Option B (round in `has_cargo_resources`). Closes DI-006 in log.jsonl.
- F-A-013 + DI-001: Tighten `_ship_container_snapshot` to the same capacity contract the engine handlers enforce (lands alongside PROJ-445's DI-001 fix)
- F-A-028: Replace the 5 `pytest.skip` calls in facade integration tests with deterministic fixtures
- F-A-029: Same recipe for save_load `test_resupply_persistence.py`

### Phase 3 — PROJ-436 deletion-shim retirement (STACKED PR with PROJ-446, gated on PROJ-443)
Joint audit-then-decide phase. Spans Planet + ShipInstance constructor wrappers AND the PROJ-446-owned shared fixture migration.

- F-A-002: `_planet_init_with_legacy_kwargs` audit. Codex 2026-05-18: real footprint exceeds the original "~15 test files" estimate; also includes `planet_serde.py:160-162` as a non-test dependent.
- F-A-003: `_ship_instance_init_with_legacy_kwargs` audit (PROJ-443 Phase 5b counted 18 files; Codex says count is now larger — verify and decide)
- F-A-004: Planet stockpile / max_stockpile / staging_yard @property shims retire (paired with F-A-002)
- F-A-005: ShipInstance consumable_levels / cargo_contents @property shims retire (paired with F-A-003)
- **(STACKED — PROJ-446-owned)** PROJ-446 F-C-020: Migrate `tests/fixtures/strategy_entities.py` 3 fixture sites off `consumable_levels=` / `cargo_contents=` legacy kwargs. This is the structural unblock for retiring the wrappers — without it the wrapper deletes leave the shared fixture broken across the suite.
- F-A-011: Profile `Empire.resource_pool` walk under late-game save; add cached aggregation only if hot

**Hard gate:** Phase 3 cannot start until:
1. PROJ-443 has settled its Phase 5b decision (or PROJ-444 owner explicitly takes over that scope), AND
2. PROJ-446 confirms F-C-020 is sequenced into the same PR (or a stacked PR ahead of this phase), AND
3. The fresh `rg` audit numbers are in.

Coordinate via decisions.md.

### Phase 4 — LOC-ceiling extractions
Mechanical responsibility-based file splits:

- F-A-008: Extract `Fleet.to_dict` / `Fleet.from_dict` into `fleet_serde.py` (mirrors `planet_serde.py` from PROJ-372). Drops fleet.py by ~140 LOC.
- F-A-009: Split `planet_gen.py` by sub-concern (atmosphere / surface / orbits)
- F-A-007: **Out of scope** — the 839-LOC `ship_instance.py` is documented as a future dedicated project. Track here for visibility only.

## Related Documents

- [design.md](design.md) — Architecture analysis and parallelism contract with PROJ-445/446
- [decisions.md](decisions.md) — Full decisions log including PROJ-443 coordination
- [findings/bucket_a_data_facade_scan.md](findings/bucket_a_data_facade_scan.md) — Source scan, 32 findings with file:line citations
- [`AgentCoordination/Scratchpad/reviews/2026_05_18_post_refactor_residue_review.md`](../../../AgentCoordination/Scratchpad/reviews/2026_05_18_post_refactor_residue_review.md) — Top-level review report (covers all 3 buckets)
- [`AgentCoordination/discovered_issues/log.jsonl`](../../../AgentCoordination/discovered_issues/log.jsonl) — 9 prior entries (DI-001..DI-007); deduplicated against in the scan

## Sibling Projects

| Project | Layer | Findings | High-severity items |
|---------|-------|----------|---------------------|
| PROJ-444 (this) | data + facade | 32 | 1 |
| [PROJ-445](../PROJ-445/plan.md) | engine + services | 22 | 1 (LayMines TypeError) |
| [PROJ-446](../PROJ-446/plan.md) | ui + core + tests | 30 | 0 |

## Verification

- [ ] All phase checklists complete
- [ ] All 32 findings either fixed, deferred-with-rationale, or recategorized
- [ ] Full sharded test suite green (`python Tools/test_sharded/test_sharded.py`)
- [ ] No new entries in `discovered_issues/log.jsonl` during this project (or new entries are real out-of-scope discoveries, not regressions)
- [ ] DI-006 / DI-001 marked resolved in log.jsonl (the cross-coupled engine-side fixes land alongside PROJ-445's Phase 2)
- [ ] Audit passed
- [ ] User verified
