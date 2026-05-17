# PROJ-425: ShipInstance slimming (TD-06)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-425` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-425 [phase]` before stopping
> - Update Current State with specific handoff context

**Execution Protocol:** 03c-phase-aware-execution

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 0. Characterization — freeze current behavior using existing test surfaces | Complete | [phase_0_checklist.md](phase_0_checklist.md) |
| 1. Extract stats-calculation logic before changing storage | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Move component/layer inspection out of `ShipInstance` | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Extract the factory path and keep a thin shim | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Move write behavior onto `ShipInstanceWriteService` + standardize manager names | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Demolish display / consumable / serializer / bridge forwarders (batches 5a/5b/5d/5e) | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. **Cargo + deployable forwarder demolition (batch 5c)** — **Blocked by:** PROJ-431 Phase 1 (typed `bay_inventory`) | Blocked | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-05-17
**Active Phase:** Phase 4 (write behavior consolidation + manager-name standardization)
**Last Action:** Phase 3 complete — created `game/strategy/services/ship_instance_factory.py` (166 LOC) with `ShipInstanceFactory.create` + `build_full_hp_components_from_design`. `ShipInstance.create` is now a thin shim. Grep gate: 33 callers across game+tests; shim stays. Fixed broken import in `tests/unit/strategy/test_ship_instance_damage.py`. `ship_instance.py` 629 LOC (-93 this phase; -216 cumulative). 4557 strategy unit tests pass.
**Next Action:** Phase 4 — rename entity manager fields to `_cargo_manager` / `_consumable_manager` (reconcile with write service), move component-toggle and repair logic onto `ShipInstanceWriteService`.
**Blockers:** None for Phases 0–5. Phase 6 is blocked until [PROJ-431](../PROJ-431/plan.md) Phase 1 lands typed `bay_inventory`.

## Overview
`game/strategy/data/ship_instance.py` is 845 LOC — well past the 500-LOC project ceiling — and is mostly a wall of one-line forwarders to delegate classes that already exist (`ShipConsumableManager`, `ShipCargoManager`, `ShipDisplayFormatter`, `ShipInstanceBridge`, `ShipInstanceSerializer`, `ShipInstanceWriteService`). Three substantive in-class blocks remain — the stats cache + registry-DI calculation path, the component-introspection helpers, and the `create(...)` factory — and they all want to move out before the forwarders are demolished. This project executes the six-phase TDD extraction in TD-06, slimming `ShipInstance` toward "durable state + identity + small pure predicates" without breaking any caller.

## Goals
- Reduce `ShipInstance` to durable state, identity helpers (`__hash__`/`__eq__`/`__repr__`), small read-only properties (`design_name`, `hull_class`, `effective_role`), and minimal pure predicates (`is_damaged`, `is_combat_capable`).
- Move the stats-calculation + cache-invalidation logic, the component-by-layer inspection block, and the `create(...)` factory body out of the entity into focused services/helpers — without changing call-site behavior in the same phase that moves the logic.
- Demolish the forwarder wall in **sub-batches with grep gates between them** (display → consumable → serializer → bridge → cargo/deployable), migrating callers to the canonical delegate before deleting the wrapper.
- Standardize manager/accessor names on `ShipInstance` before the write service and entity start cross-referring (Phase 4 prep).
- End the project with `ship_instance.py` materially under 500 LOC and no high-value entry point (`create`, `to_dict`, `from_dict`, `to_ship`, `clone`) deleted ahead of caller migration.

## Scope
**In:** `game/strategy/data/ship_instance.py` slimming; extension of existing delegate classes (`ShipConsumableManager`, `ShipCargoManager`, `ShipDisplayFormatter`, `ShipInstanceBridge`, `ShipInstanceSerializer`); extension of `ShipInstanceWriteService` and `component_inspector.py`; optional new helpers (`ship_stats_cache.py`, `ship_instance_factory.py`) **only if** extending existing modules would push them over the 500-LOC ceiling; caller migration in `game/` and `tests/` per the grep-driven sub-batches; tightening of the existing tests under `tests/unit/strategy/ship_instance/`, `tests/unit/strategy/services/`, and `tests/unit/strategy/fleets/`.

**Out:** Save-format changes unrelated to slimming; UI/facade redesign not directly required by caller migration; deployable-substrate redesign (that is PROJ-431 / TD-10's job — this project's Phase 6 just demolishes the now-redundant forwarders once the substrate work has landed); renaming `ShipInstance.create` or other public entry points without grep-proven caller migration; introducing a parallel "old + new" stats-cache path (per AGENTS.md root-cause rule).

## Dependencies
Hard predecessors: none.

**Phase gate with PROJ-431 (TD-10):** Phases 0–4 may run immediately. The final cargo/deployable forwarder-demolition phase (Phase 6 of this project, corresponding to TD-06 Batch 5c) is **blocked** until [PROJ-431 (TD-10) Phase 1](../PROJ-431/plan.md) has landed the typed `bay_inventory` substrate. The TD-06 source plan's `## Ordering Constraints` section codifies this gate explicitly ("Only Batch 5c should be treated as TD-10-sensitive"), and [EXECUTION_ORDER.md](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/EXECUTION_ORDER.md) §"Recommended Linear Order" lists the deferred cargo/deployable cleanup as step 11 — the deferred tail of TD-06 that runs only after TD-10 Phase 1 is complete.

Soft predecessors: none. TD-05 (PROJ-426 production/persistence split) does not block this work and can keep using `ShipInstance.create(...)` or the shim while TD-06 progresses.

## Key Files
| Component | File Path | Type |
|-----------|-----------|------|
| Slimming target | [`game/strategy/data/ship_instance.py`](../../../game/strategy/data/ship_instance.py) | Production (rewrite, currently 845 LOC) |
| Consumable delegate (existing) | [`game/strategy/data/ship_consumable_manager.py`](../../../game/strategy/data/ship_consumable_manager.py) | Production (extend / become canonical) |
| Cargo delegate (existing) | [`game/strategy/data/ship_cargo_manager.py`](../../../game/strategy/data/ship_cargo_manager.py) | Production (extend / become canonical — Phase 6) |
| Display delegate (existing) | [`game/strategy/data/ship_display_formatter.py`](../../../game/strategy/data/ship_display_formatter.py) | Production (extend / become canonical) |
| Bridge delegate (existing) | [`game/strategy/data/ship_instance_bridge.py`](../../../game/strategy/data/ship_instance_bridge.py) | Production (extend / become canonical) |
| Serializer delegate (existing) | [`game/strategy/data/ship_instance_serializer.py`](../../../game/strategy/data/ship_instance_serializer.py) | Production (extend / become canonical) |
| Write service (existing) | [`game/strategy/services/ship_instance_write_service.py`](../../../game/strategy/services/ship_instance_write_service.py) | Production (extend with toggles/repair — Phase 4) |
| Component inspector (existing) | [`game/strategy/services/component_inspector.py`](../../../game/strategy/services/component_inspector.py) | Production (extend with layer inspection — Phase 2) |
| Stats cache helper | `game/strategy/data/ship_stats_cache.py` | Production (optional new — Phase 1) |
| Factory helper | `game/strategy/services/ship_instance_factory.py` | Production (optional new — Phase 3) |
| Characterization tests (existing) | `tests/unit/strategy/ship_instance/` | Test (extend in Phase 0) |
| Write-service tests | `tests/unit/strategy/services/test_ship_instance_write_service.py` | Test (extend in Phase 4) |
| Fleet round-trip tests | `tests/unit/strategy/fleets/test_ship_instance_roundtrip.py`, `test_ship_instance_components.py` | Test (regression gate) |
| FMS integration regression | `tests/integration/test_fms_b_e2e.py`, `tests/integration/test_fms_c_carrier_ai_launch.py` | Test (regression gate) |

Full enumeration of touched files (production + tests + docs) lives in [manifest.md](manifest.md).

## Phases

### Phase 0: Characterization — freeze current behavior using existing test surfaces
Read TD-06 + the foundation docs (`docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`). Audit the existing test homes in `tests/unit/strategy/ship_instance/` and confirm coverage gaps for: `create(...)` factory behavior, stats-cache hit/miss/invalidation, component-toggle invalidation, bridge round-trip, serializer round-trip, and the resource/cargo/display convenience helpers that will later be migrated away. Tighten or extend those tests **in their existing files** — do not invent a parallel characterization layout. Verify all targeted tests pass on `main` to establish the regression baseline. Confirm the live `ShipInstance` attribute names for cargo/consumable managers via grep (`_cargo_manager`, `_consumable_manager`, etc.) so Phase 4 can standardize without guessing.

### Phase 1: Extract stats-calculation logic before changing storage
Move the stats-calculation + cache-invalidation logic into a helper (extend an existing module if natural; otherwise add `game/strategy/data/ship_stats_cache.py`). **Keep `_cached_stats` on `ShipInstance` for this phase** — move logic first, storage second. Required behavior preserved: missing-registry failures still surface in the same way; cache invalidation after relevant state changes still works; no caller changes required. The Phase 0 stats-cache test must remain green.

### Phase 2: Move component/layer inspection out of `ShipInstance`
Extend [`game/strategy/services/component_inspector.py`](../../../game/strategy/services/component_inspector.py) with the ship-instance-specific helpers `iter_all_components_by_layer`, `get_damaged_components_by_layer`, `get_damaged_component_count`, and the helper logic that joins design layers with `ComponentState`. Only create a second inspector module if extending the existing one would clearly violate the 500-LOC limit. Do **not** move this logic into UI code. Update `tests/unit/strategy/fleets/test_ship_instance_components.py` and any UI/formatter tests that asserted layer views.

### Phase 3: Extract the factory path and keep a thin shim
Move the body of `ShipInstance.create(...)` (and `_build_full_hp_components_from_design(...)`) into a factory/helper (extend an existing service if natural; otherwise add `game/strategy/services/ship_instance_factory.py`). **Leave `ShipInstance.create(...)` as a thin shim** that delegates to the new factory — this phase does not migrate every call site yet. Required grep before phase close: `rg -n "ShipInstance\.create\(" game tests` — the shim stays as long as that result set is non-empty.

### Phase 4: Move write behavior onto `ShipInstanceWriteService` + standardize manager names
Prep: verify canonical manager/accessor names on `ShipInstance` (per Phase 0 grep notes) and make the write service and entity agree on those names **before** any broader caller migration. Then move cache-invalidating component toggles, repair / full-repair logic, and any remaining direct-write helpers that are not identity-level behavior onto [`ShipInstanceWriteService`](../../../game/strategy/services/ship_instance_write_service.py). Acceptance: cache invalidation is centralized in the write service — not split across old entity methods and new service methods. Update `test_ship_instance_write_service.py` and `test_component_toggles.py`.

### Phase 5: Demolish display / consumable / serializer / bridge forwarders (batches 5a / 5b / 5d / 5e)
Demolish the four TD-10-independent forwarder sub-batches **sequentially, with grep gates between them**:
- **5a Display** — `get_display_id`, `get_status_text`, `get_hp_display`, `get_resource_display` → `ShipDisplayFormatter`.
- **5b Consumable** — resource-capacity queries, resource-consumption helpers, resupply helpers → `ShipConsumableManager` (or a stable accessor to it).
- **5d Serializer** — `to_dict`, `from_dict`, `to_json`, `from_json`, `clone` → `ShipInstanceSerializer`.
- **5e Bridge** — `to_ship`, `update_from_ship` → `ShipInstanceBridge`.

For each sub-batch: grep for live callers; add or update one focused failing test for the new direct-call path; migrate callers; remove only the forwarders covered by that sub-batch; rerun focused tests before moving to the next. **Skip Batch 5c here — it is Phase 6.**

### Phase 6: Cargo + deployable forwarder demolition (TD-06 Batch 5c) — gated by PROJ-431 Phase 1
**Blocked by:** [PROJ-431 (TD-10) Phase 1](../PROJ-431/plan.md) — typed `bay_inventory` substrate must land first. Do **not** start this phase until PROJ-431 Phase 1 is merged.

When unblocked: demolish the cargo/deployable forwarders (cargo queries and mutators, carried-vehicle queries, pod-storage helpers) and migrate their callers to `ShipCargoManager` (or the stable accessor to it post-TD-10). Same sub-batch discipline as Phase 5: grep → failing test for the new direct-call path → migrate callers → remove forwarders → focused tests → next slice. Final grep gate before phase close: `rg -n "ShipInstance\.create\(|\.to_ship\(|\.update_from_ship\(|\.to_dict\(|\.clone\(" game tests` — if any high-value entry point still has many live callers, leave it as a documented thin shim rather than forcing a risky all-callers migration.

## Related Documents
- [TD-06 source plan](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-06_ship_instance_slimming.md) — canonical specification (verification findings, file touch map, six-phase TDD extraction, risks, acceptance criteria)
- [Strategy tech-debt EXECUTION_ORDER.md](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/EXECUTION_ORDER.md) — confirms TD-06 Phases 0–4 may start immediately and codifies the cargo/deployable cleanup as the deferred tail (step 11) after TD-10 Phase 1
- [PROJ-431 (TD-10) deployable substrate redesign](../PROJ-431/plan.md) — the cross-project phase gate that releases Phase 6 of this plan
- [design.md](design.md) — distilled responsibility inventory, current state, risk register
- [decisions.md](decisions.md) — full decisions log
- [manifest.md](manifest.md) — enumerated file touch list
- [findings_ledger.md](findings_ledger.md) — running findings ledger per the 03c protocol

## Verification
Acceptance criteria from the TD-06 plan:
- [ ] `ShipInstance` is materially smaller and no longer owns its largest helper blocks.
- [ ] Stats-calculation logic no longer lives inline in `ShipInstance`.
- [ ] Component/layer inspection no longer lives inline in `ShipInstance`.
- [ ] Direct write behavior is centralized through `ShipInstanceWriteService` (or an equivalent single write path).
- [ ] Removed forwarders have had their callers migrated in bounded batches.
- [ ] Serializer and bridge round-trips are still green.
- [ ] Focused ship-instance, fleet, and FMS integration suites are green before the sharded run.
- [ ] `python Tools/test_sharded/test_sharded.py` is green.
- [ ] `ShipInstance.create`, `to_dict`, `from_dict`, `to_ship`, `clone` were not deleted ahead of grep-proven caller migration (per Weak-LLM Guardrails).
- [ ] PROJ-431 Phase 1 landed before any code in Phase 6 of this project touched `main`.
