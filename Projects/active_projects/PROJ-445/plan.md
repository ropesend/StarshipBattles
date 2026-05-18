# PROJ-445: Post-refactor residue — Engine + Services layer (Bucket B)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-445` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-445 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. **F-B-001 LayMines TypeError fix** (urgent — single high-severity finding) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Engine boundary tightening (DI-001/006/007 fix sites + transfer_branches private slots) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Annotation + ratchet test polish | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. OrderProcessor PROJ-368 facade unwinding (F-B-017/018) | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-05-18
**Active Phase:** Planning
**Last Action:** Charter created from comprehensive residue scan ([findings/bucket_b_engine_services_scan.md](findings/bucket_b_engine_services_scan.md), 22 findings)
**Next Action:** **PHASE 1 PRIORITY** — fix F-B-001 (LayMinesOrderHandler signature drift will TypeError on any planet-issued LAY_MINES order). Three-line change; no reason to wait.
**Blockers:** None

## Overview

Residue cleanup for the **`game/strategy/engine/` + `game/strategy/services/`** layer accumulated across ~22 archived refactors. Companion project to PROJ-444 (data + facade) and PROJ-446 (UI + core + tests) — by design the three projects touch **disjoint file sets** so they can run in parallel without merge conflicts.

**The most consequential finding in the entire 84-issue review lives in this bucket:** F-B-001 — `LayMinesOrderHandler.execute_for_issuer` is missing the `registries` kwarg that PROJ-438 Phase 6 unconditionally passes. Any planet-issued LAY_MINES order ticked through `ActionExecutionEngine._process_planet_action_tick` will raise `TypeError`. No behavioral test covers the path (compounded by DI-2026-05-18-001's documented planet-FMS coverage gap), and the PROJ-438 Phase 6 removal of the `try/except TypeError` reach-in fallback turned a silent skip into a hard failure. Phase 1 is just this one fix plus the parametrized planet-FMS dispatch test.

## Goals

- **(Phase 1, urgent)** Resolve the LayMines TypeError before it ships into a user-facing release
- Close out the engine-side fix sites for `discovered_issues/log.jsonl` entries DI-001 (fleet-to-fleet pod/vehicle transfer silent no-op), DI-002 (CommandRegistry.serializer_codec_for ambiguity), DI-007 (ProductionEngine ignore-bool)
- Sweep the PROJ-368 / PROJ-438 partial-migration residue: facade-side reshape of `OrderExecutionResult` into legacy typed result dataclasses (F-B-017 — rewritten per Codex 2026-05-18; handler signatures themselves already match the Protocol, the residue is the facade compensation), `OrderExecutionResult` legacy fields (F-B-018), `ship._cargo_mgr` private-slot reaches from transfer_branches (F-B-003)
- Retire the two service-layer re-export shims (`effect_ability_metadata.py`, `component_inspector.py`) that PROJ-429 and PROJ-433 left in place for caller-migration deferral
- Add the parametrized planet-FMS engine-mediated dispatch test that PROJ-438 Phase 10 deferred (the F-B-022 + DI-001 + F-B-001 parametrize-over-all-5-handlers test, not just launch + recovery)
- Polish: 6 missing return annotations on public engine accessors, 1 stale `IProductionResourceSource` docstring, 1 `# type: ignore` masking a real annotation gap

## Scope

**In (this project owns these files):**
- All files under `game/strategy/engine/` including `order_handlers/`, `commands/`, `handlers/`, `superweapon_handlers/`
- All files under `game/strategy/services/`
- Tests under `tests/unit/strategy/engine/`, `tests/unit/strategy/services/`
- Tests under `tests/integration/` whose primary subject is an engine/services class (test_fms_planet_*, etc.)

**Out (PROJ-444 owns these — do NOT touch in this project):**
- `game/strategy/data/` (containers, fleets, planets, ship_instance, empire, etc.)
- `game/strategy/facade/` (DTOs, slices)
- Save/load tests, facade integration tests

**Out (PROJ-446 owns these — do NOT touch in this project):**
- `game/ui/` (all UI)
- `game/core/protocols/`, `game/core/exceptions.py`
- Static guards, regression snapshots, shared test fixtures

**Out (deferred to future projects regardless of layer):**
- PROJ-443 (pytest norecursedirs fix) — already chartered
- The broader `_process_planet_action_tick` E2E coverage push that DI-001 captures — this project adds the LAY_MINES-specific test slice but the full Phase 10 scaffolding (1 empire, 1 owned planet, queued order, deployed groups) is its own project

## Findings Summary

Full report: [findings/bucket_b_engine_services_scan.md](findings/bucket_b_engine_services_scan.md) (22 findings)

| Severity | Count | Notes |
|----------|-------|-------|
| High     | 1     | **F-B-001** — LayMines TypeError waiting to happen |
| Medium   | 5     | F-B-002 (staging-yard direct mutation), F-B-013 (DropPod flatten boundary — joint-phase with PROJ-444), F-B-017 (facade-side legacy result reshape — rewritten r2), F-B-019 (Protocol contract gap), F-B-022 (LayMines dispatch coverage) |
| Low      | 16    | Polish, narrow private-slot reaches, stale docstrings |

(The bucket-report summary stated `high 2` — body inspection confirms 1 high and 5 medium; the report summary undercount is cosmetic.)

| Category | Count |
|----------|-------|
| Obsolete-code | 4 |
| Test-inconsistency | 3 |
| Missing-functionality | 2 |
| Polish | 13 |

### Cross-bucket couplings — three coordination points, two structural joint-phase seams
- **(Coordination)** **F-B-001 + F-B-022 + DI-2026-05-18-001** — All three coalesce on the planet-FMS engine-mediated dispatch path. The fix (F-B-001) is tiny; the test (F-B-022) parametrizes the Phase-10 scaffold DI-001 already scoped. **This project closes F-B-001 unilaterally in Phase 1.** The parametrized test in Phase 1 also closes part of DI-001.
- **(Coordination)** **F-B-019 + DI-2026-05-18-006 + DI-2026-05-18-007** — Affordability-vs-consumption contract. F-B-019 tightens the `IProductionResourceSource` Protocol docstring; PROJ-444's F-A-010 owns the actual `Fleet.consume_cargo_resource` fix site. Land together in Phase 2.
- **(Coordination)** **F-B-002 + F-B-003 + PROJ-444's F-A-007** — `transfer_branches.py` private-slot reaches into `ship._cargo_mgr`. The fix adds public delegators on `ShipInstance`; PROJ-444 owns ShipInstance, this project owns the call sites. Coordinate in Phase 2.
- **(STRUCTURAL JOINT-PHASE)** **F-B-013 + DI-2026-05-18-001 (transfer) + PROJ-444 Planet substrate** — Codex consult 2026-05-18 verified this is NOT mere coordination. The symptom is in `engine/transfer_branches.py` (this bucket) but the root cause — `Planet._staging_yard: List[Dict[str, Any]]` + `Planet.add_to_staging_yard(dict)` — lives in PROJ-444's `game/strategy/data/planet.py:98, 253-262, 316-322`. The field rename + serializer migration starts in PROJ-444; the call-site adoption finishes here. **Requires a stacked PR (or one PR spanning both bucket file sets). Do NOT attempt independently from either side.**
- **(Coordination, but verify framing first)** **F-B-017 + F-B-018** — Codex consult 2026-05-18 refuted the original "signature mismatch on `execute_action_order`" framing. The three concrete handlers (`JoinFleetHandler`, `ColonizeHandler`, `TransferHandler`) already accept the full 5-kwarg shape with defaults. The real residue is the facade-side reshape of `OrderExecutionResult` back into the pre-PROJ-368 typed result dataclasses (`JoinFleetResult`, `ColonizeResult`, `TransferResult`). Cleanup theme intact; rationale revised in the findings file.

## Key Files

| Component | File Path | Findings |
|-----------|-----------|----------|
| LayMines handler | `game/strategy/engine/order_handlers/lay_mines.py` | **F-B-001 (high)** |
| Transfer branches | `game/strategy/engine/order_handlers/transfer_branches.py` | F-B-002, F-B-003, F-B-013, DI-2026-05-18-001 |
| OrderHandler base | `game/strategy/engine/order_handlers/base.py` | F-B-017, F-B-018 |
| ActionExecutionEngine | `game/strategy/engine/action_execution_engine.py` | F-B-022, DI-2026-05-18-001 |
| OrderProcessor | `game/strategy/engine/order_processor.py` | F-B-007, F-B-017 |
| ProductionEngine | `game/strategy/engine/production_engine.py` | F-B-015, F-B-019 |
| CommandRegistry | `game/strategy/engine/commands/registry.py` | F-B-020, DI-2026-05-18-002 |
| TurnEngine | `game/strategy/engine/turn_engine.py` | F-B-010 |
| Superweapon processor | `game/strategy/engine/superweapon_order_processor.py` | F-B-006, F-B-008, F-B-014 |
| Close warp point | `game/strategy/engine/superweapon_handlers/close_warp_point.py` | F-B-014 |
| Conflict modifier | `game/strategy/engine/conflict_modifier_collection.py` | F-B-016 |
| FMS shared | `game/strategy/engine/handlers/fms_shared.py` | F-B-009 |
| Effect ability shim | `game/strategy/services/effect_ability_metadata.py` | F-B-004 (retire entire module) |
| Component inspector shim | `game/strategy/services/component_inspector.py` | F-B-005 (retire entire module) |
| Replay store | `game/strategy/services/replay_store.py` | F-B-021 |
| Mutator accessors | `game/strategy/engine/harvesting_engine.py`, `atmosphere_engine.py`, `planet_modifier_effect_engine.py`, `production_spawner.py` | F-B-011 |
| Superweapon test | `tests/unit/strategy/services/test_superweapon_registry_contract.py` | F-B-012 |
| Planet-FMS tests | `tests/integration/test_fms_planet_*.py` (+ new LAY_MINES) | F-B-022 |

## Phase Breakdown

### Phase 1 — F-B-001 LayMines TypeError fix + ratchet parity-gap closure (HIGH-SEVERITY, do this first)

Scope: 3-line production fix + 1 new integration test + parity-gap fix in the existing contract ratchet.

- F-B-001: Add `registries: Any = None` to `LayMinesOrderHandler.execute_for_issuer` (mirror `recover_fighters.py:107-120`). Accept and ignore.
- F-B-022 (partial): Add `tests/integration/test_fms_planet_lay_mines.py` parametrized across the 5 entries in `command_registry.planet_fms_action_order_types()`. This is the LAY_MINES slice of the broader DI-2026-05-18-001 scaffold.
- F-B-020 (companion): Add `test_planet_fms_subcategory_tag_spelling_or_set_size` ratchet asserting `len(planet_fms_action_order_types()) == 5` and the set equals the declared OrderTypes. Catches typos like `"planet-fms"` / `"plnaet_fms"`.
- **Codex-discovered parity gap (2026-05-18):** Extend `tests/unit/strategy/engine/test_issuer_execution_contract.py:36-65` (the existing PROJ-438 contract ratchet) to assert the 5-kwarg `execute_for_issuer` signature for `LayMinesOrderHandler` AND `LaunchSatellitesOrderHandler`. Both were silently omitted from the original ratchet, which is exactly how F-B-001's drift slipped through PROJ-438's audit. **Adding these two cases is the test that would have caught F-B-001 prophylactically; without it, the next handler added in the same shape will drift again.**

**Acceptance:** Sharded tests green. The new LAY_MINES dispatch test fails before the F-B-001 fix and passes after. The extended contract ratchet covers all 5 planet-FMS handlers (3 already covered + 2 new: LayMines, LaunchSatellites). Subcategory-tag ratchet locks the planet-FMS surface at 5 entries.

### Phase 2 — Engine boundary tightening (closes 3 DI log entries)

- F-B-002: `planet.staging_yard.append(removed)` → `planet.add_to_staging_yard(removed)` at `transfer_branches.py:365` (rollback path uses capacity-checked API)
- F-B-003 + DI-2026-05-18-001 (fleet-to-fleet): Add public `ship.can_carry_pod` / `ship.load_vehicle` / `ship.unload_vehicle` delegators (coordinated with PROJ-444); migrate `transfer_branches.py` 6 call sites off `ship._cargo_mgr`. Then add the missing fleet-to-fleet drop_pod/vehicle dispatch branch in `_dispatch_fleet_to_fleet` (DI-001 fix proper).
- F-B-013: Typed `staging_yard_typed: List[CarriedVehicle | DropPod]` on Planet (PROJ-444 coordination) — eliminates the flatten/inflate round-trip. Keep this scoped to engine-side adoption; PROJ-444 owns the actual Planet field rename.
- F-B-014: Audit + delete the pre-PROJ-228 plain-string CLOSE_WARP_POINT target form (`_parse_close_target` string branch, special-case at `superweapon_order_processor.py:222`)
- F-B-019 + DI-2026-05-18-007: Tighten `IProductionResourceSource.production_consume_resource` Protocol docstring contract. Add a ratchet test that asserts each concrete implementer's `production_consume_resource` returns True whenever `production_has_resources` does.
- DI-2026-05-18-002: Harden `CommandRegistry.serializer_codec_for` to raise on multi-spec ambiguity (precondition for any future `Order.to_dict` dispatch through it)

### Phase 3 — Annotation + ratchet test polish (tiny, mechanical)

- F-B-006: Annotate `_get_system_at_hex`, drop `# type: ignore`
- F-B-007 + F-B-008: Type `event_bus` parameters on engine __init__s
- F-B-009: Annotate `resolve_requested` return as `int | ValidationResult`
- F-B-010: Annotate `TurnEngine.planet_modifier_effect_engine`
- F-B-011: Annotate 4 `_get_*_mutator` accessors as `-> Any`
- F-B-012: Delete the two dead `try / except ImportError → pytest.skip` guards in `test_superweapon_registry_contract.py`
- F-B-015: Update stale `_cargo_contents` reference in `IProductionResourceSource` docstring → `ShipCargoManager`
- F-B-016: Drop "Phase 7 deletes the legacy path" stale docstring in `conflict_modifier_collection.py`
- F-B-021: Annotate `ReplayStore._iter_replay_files` return

### Phase 4 — Service-layer shim retirement + PROJ-368 facade unwinding

- F-B-004: Sweep `effect_ability_metadata.py`'s 2 callers → `ability_metadata.py`. Delete the 131-LOC shim module.
- F-B-005: Sweep ~50 callers off `component_inspector.py` → `component_abilities.py` / `component_layers.py`. Delete the 67-LOC re-export module.
- F-B-017: Audit `process_join_fleet` / `process_colonize` / `process_transfer` characterization callers; migrate them to read `OrderExecutionResult` directly; narrow the `IOrderHandler` Protocol.
- F-B-018: Once F-B-017 is settled, delete the 5 legacy-field attributes on `OrderExecutionResult`.

## Related Documents

- [design.md](design.md) — Architecture analysis and parallelism contract with PROJ-444/446
- [decisions.md](decisions.md) — Full decisions log
- [findings/bucket_b_engine_services_scan.md](findings/bucket_b_engine_services_scan.md) — Source scan, 22 findings with file:line citations
- [`AgentCoordination/Scratchpad/reviews/2026_05_18_post_refactor_residue_review.md`](../../../AgentCoordination/Scratchpad/reviews/2026_05_18_post_refactor_residue_review.md) — Top-level review report (covers all 3 buckets)
- [`AgentCoordination/discovered_issues/log.jsonl`](../../../AgentCoordination/discovered_issues/log.jsonl) — 9 prior entries (DI-001..DI-007); 5 of them have fix sites in this project

## Sibling Projects

| Project | Layer | Findings | High-severity items |
|---------|-------|----------|---------------------|
| [PROJ-444](../PROJ-444/plan.md) | data + facade | 32 | 0 |
| PROJ-445 (this) | engine + services | 22 | **1 (F-B-001 LayMines)** |
| [PROJ-446](../PROJ-446/plan.md) | ui + core + tests | 30 | 0 |

## Verification

- [ ] All phase checklists complete
- [ ] F-B-001 fixed and the new LAY_MINES dispatch test passes
- [ ] DI-001 (transfer + planet-FMS), DI-002, DI-006 (protocol-side), DI-007 closed in `discovered_issues/log.jsonl`
- [ ] Full sharded test suite green (`python Tools/test_sharded/test_sharded.py`)
- [ ] Component-inspector shim deleted, all callers migrated (no `from game.strategy.services.component_inspector import` remains in `git grep`)
- [ ] Effect-ability-metadata shim deleted
- [ ] No new `discovered_issues/log.jsonl` entries flagged against engine/services during this project (or new entries are real out-of-scope discoveries)
- [ ] Audit passed
- [ ] User verified
