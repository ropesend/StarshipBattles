# PROJ-436: Unified Storage Substrate and Container Unification

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-436` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-436 [phase]` before stopping
> - Update Current State with specific handoff context

**Execution Protocol:** 03c-phase-aware-execution

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 0. Container substrate + design decisions | Complete | [phase_0_checklist.md](phase_0_checklist.md) |
| 1. Component ability convergence (`Container` parser) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. `ShipInstance.bay_inventory` widening to full Container | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. `ShipInstance.cargo_contents` + `consumable_levels` migration | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. `Planet.stockpile` + `max_stockpile` + `staging_yard` migration | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. `Empire._fleet_resource_pool` deletion + `resource_pool` semantics | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Protocol churn + build-queue/UI `context_type` cleanup | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. `TransferValidator` / resource-list deletion | Not Started | [phase_7_checklist.md](phase_7_checklist.md) |
| 8. `ProductionEngine.context_type` deletion | Not Started | [phase_8_checklist.md](phase_8_checklist.md) |
| 9. `_CarriedItemsProxy` final cutover | Not Started | [phase_9_checklist.md](phase_9_checklist.md) |
| 10. Doc refresh | Not Started | [phase_10_checklist.md](phase_10_checklist.md) |
| 11. Codex consult + verified-finding remediation | Not Started | [phase_11_checklist.md](phase_11_checklist.md) |

## Current State
**Last Updated:** 2026-05-18
**Active Phase:** Phase 3 (ShipInstance cargo_contents + consumable_levels migration)
**Last Action:** Phase 2 COMPLETE. Widened `BayInventory` from 2 typed slots (`bay`, `pods`) to 4 typed slots adding `resources: Dict[str, float]` and `population: Dict[str, int]` with full mass accounting unified via `total_mass()`. New API: `add_resource()` / `remove_resource()` / `get_resource()` / `add_population()` / `remove_population()` / `get_population()` / `total_resource_mass()` / `total_population_mass()` / `container_view()`. Backward-compatible: existing PROJ-431 tests still green; legacy round-trip (saves predating Phase 2) works. 30 focused widening tests + 8 existing PROJ-431 bay_inventory tests = 38 green. Sharded suite: 21169/21169 green (unchanged because the directory is hidden — see norecursedirs finding below). Direct `tests/unit/strategy/data/` run reduced failures from 91 → 65 (PROJ-431-flagged `test_cargo_tracking.py` issues remain pre-existing, unrelated to PROJ-436).

**Discovery — `pytest.ini` `norecursedirs = ... data ...`:** the `data` token in `norecursedirs` matches `tests/unit/strategy/data/` as well as the intended top-level `data/` directory. Every test in `tests/unit/strategy/data/` (1575 tests including PROJ-431's BayInventory tests, PROJ-436 Phase 0 container tests, etc.) is silently hidden from the sharded suite. Pre-existing — predates PROJ-436. Recommend fixing in a separate small project: switch from `norecursedirs = ... data ...` to using `--ignore=data` in addopts so only the top-level `data/` directory is excluded. Documented in `decisions.md`. Until fixed, focused tests for Phase 2+ are run via direct path invocation in addition to the sharded suite.

**Next Action:** Phase 3 — migrate `ShipInstance.cargo_contents` + `consumable_levels` to per-component Container projections; sweep callers per PROJ-431 sub-phase model; final cutover deletes the legacy fields.
**Blockers:** None.

## Overview
Replace the post-435 fragmented storage model with one mass-based `Container` abstraction shared across resources, constructed items, and population. Today three separate component abilities (`ResourceStorage`, `CargoStorage`, `VehicleBay`) plus eight entity-level storage fields (`Planet.stockpile` / `max_stockpile` / `staging_yard`, `ShipInstance.cargo_contents` / `consumable_levels` / `bay_inventory`, `Empire._fleet_resource_pool` / `resource_pool`) plus a hardcoded `TransferValidator.VALID_CARGO_TYPES` whitelist plus `ProductionEngine.context_type` branching all encode the same domain concept three different ways. The redesign collapses them into one `Container(capacity_mass, policy, resources, items, population)` with three internal slices, mass-based capacity, and policy-driven content type filtering.

## Goals
- Replace `ResourceStorage` + `CargoStorage` + `VehicleBay` with one `Container` ability that the engine reads through one interface.
- Unify ship/planet/empire storage fields into per-component `Container` instances sourced from operational components.
- Mass-based capacity throughout, with per-resource `mass_per_unit` added as a field on the existing `ResourceDefinition` in `game/core/resources.py` and populated by extending the existing canonical `data/resources.json` (energy = 1.0, population = 0.1 per individual, others first-pass guesses). The strategy/UI layers consume mass-per-unit through the existing `ResourceCatalog` API — no parallel strategy-local resource registry.
- Three internal slices (A2 model): `resources: Dict[str, float]`, `items: List[ItemRef]`, `population: Dict[str, int]`. Item identity preserved for damaged units; healthy uniform-design items may be compressed.
- Delete `TransferValidator.VALID_CARGO_TYPES` hardcoded whitelist; validation becomes `Container.accepts()` against registries.
- Delete `transfer_view_model.RESOURCE_TYPES` hardcoded list in favor of registry-driven UI iteration.
- Delete `Empire._fleet_resource_pool` durable state; `Empire.resource_pool` becomes a pure aggregation query.
- Delete `ProductionEngine.context_type` branching (3 sites); production reads from any `Container` matching the input/output policy.
- Consolidate the `IStockpileHolder` / `IStagingYardHolder` / `IEmpire.resource_pool` / `IEmpire.max_storage` protocol surface around the new `Container` contract.
- Delete `_CarriedItemsProxy` test-only shim once production tests no longer need the legacy `carried_items` access pattern.
- Every phase boundary leaves the game runnable/savable/loadable; substrate-then-sweep-per-PROJ-431-model with new-as-projection-over-legacy direction.

## Scope
**In:** new `Container` / `Containable` / `ContainerPolicy` / `ContainableKind` substrate; extension of existing `game/core/resources.py:ResourceDefinition` to carry `mass_per_unit` and extension of existing canonical `data/resources.json` with that field on every entry; migration of `ResourceStorage` / `CargoStorage` / `VehicleBay` ability parsers; widening of `BayInventory` to full Container; migration of all eight legacy storage fields (`Planet.stockpile` / `max_stockpile` / `staging_yard`, `ShipInstance.cargo_contents` / `consumable_levels`, `Empire._fleet_resource_pool` / `resource_pool`, `PlanetaryFacility.consumable_levels`); deletion of `TransferValidator.VALID_CARGO_TYPES` + `transfer_view_model.RESOURCE_TYPES`; deletion of `ProductionEngine.context_type` branching; redesign of `IEmpire.resource_pool` / `IEmpire.max_storage` / `IStockpileHolder` / `IStagingYardHolder` protocols; build-queue UI `context_type` cleanup; `_CarriedItemsProxy` deletion; doc refresh; end-of-project Codex consult and verified-finding remediation.

**Out:** transfer UI rewrite beyond the minimum adapter needed to keep the current dialog functional (deferred to PROJ-437); temporal scheduler / 100-tick model changes; the 5 retained `ShipInstance` entry-point thin shims (`create`, `to_dict`, `clone`, `to_ship`, `update_from_ship`) — kept per Weak-LLM Guardrail #1; `Empire.is_eliminated()` semantics resolution (product question, separate ticket); order/command lifecycle changes (residual already absorbed by PROJ-424 + PROJ-429); component balance / mass-per-unit tuning beyond first-pass values; launch/recovery ability changes (storage stays separate from launch/recovery per user direction); life support ability changes (stays separate from Container per user direction); resource generation / consumption ability changes (stay separate from Container per user direction).

## Dependencies
**No hard predecessor.** The full PROJ-422..PROJ-435 prerequisite tranche is complete per `Projects/active_projects/PROJ-435/findings/Completion Repot`. Baseline tests: 21132/21132 green at 2026-05-17.

**Soft adjacency: PROJ-437 (Container-Aware Transfer UI).** PROJ-437 starts after PROJ-436 Phase 7 (TransferValidator deletion) so the unified `Container.accepts()` API is stable. Earlier phases of PROJ-437 (Phase 0 read-the-API, Phase 1 source-destination browsing prototype) may run during PROJ-436 Phase 6-8 if the API surface stabilizes.

**No worktrees** per user standing preference. Serial execution in the main checkout.

## Key Files
| Component | File Path |
|-----------|-----------|
| `Container` / `Containable` / policy substrate (new) | `game/strategy/data/container.py` |
| `ResourceDefinition.mass_per_unit` (extended) | `game/core/resources.py` |
| Mass-per-unit data (existing file, extended) | `data/resources.json` |
| Replaces 3 storage abilities | `game/simulation/components/abilities/cargo.py`, `game/simulation/components/abilities/resources.py`, `game/simulation/components/abilities/vehicle_bay.py` (consolidated) |
| `ShipInstance` storage migration | `game/strategy/data/ship_instance.py`, `bay_inventory.py`, `ship_cargo_manager.py`, `ship_consumable_manager.py` |
| `Planet` storage migration | `game/strategy/data/planet.py` |
| `Empire` pool deletion | `game/strategy/data/empire.py` |
| Protocol churn | `game/core/protocols/strategy_domain.py`, `game/strategy/data/galaxy_protocols.py` |
| `TransferValidator` deletion | `game/strategy/validation/transfer_validator.py` |
| `ProductionEngine` cleanup | `game/strategy/engine/production_engine.py` |
| `_CarriedItemsProxy` deletion | `game/strategy/data/ship_instance.py` (proxy lives at lines ~371-396) |
| Build-queue UI cleanup | `game/ui/panels/build_queue_controller.py` |

Full enumeration in [manifest.md](manifest.md).

## Phases

### Phase 0: Container substrate + design decisions
Land `Container`, `Containable`, `ContainerPolicy`, `ContainableKind`. Extend existing `game/core/resources.py:ResourceDefinition` to carry `mass_per_unit: float`; extend existing canonical `data/resources.json` with `mass_per_unit` on every entry. The strategy/UI layers consume mass-per-unit through the existing `ResourceCatalog` API — no parallel strategy-local resource registry. No callers migrated. Resolve the three deferred design decisions carried forward from the discussion: (a) `PlanetaryFacility.consumable_levels` fold-in scope; (b) `Empire.resource_pool` query-vs-cached; (c) non-fixed `mass_per_unit` initial values. **Checkpoint:** unit tests for Container ops, extended `ResourceCatalog.get_mass_per_unit()`, mass-aware accept/add/remove validation.

### Phase 1: Component ability convergence
Add `Container` ability parser. Keep `ResourceStorage` / `CargoStorage` / `VehicleBay` as legacy parsers that compile to `Container` internally — the runtime layer reads the unified shape. **Checkpoint:** parser parity tests; existing `component_definitions` tests stay green; no behavior change.

### Phase 2: `ShipInstance.bay_inventory` widening
Extend `BayInventory` (already typed + mass-based per PROJ-431) from `{pods, vehicles}` to a full `Container` with three slices. Migrate fighter / satellite / mine launch-recovery handlers to source items from the widened container. Launch / recovery abilities stay separate from `Container` per user direction. **Checkpoint:** existing FMS tests stay green; new tests for fighter/sat/mine storage round-trip through the widened container.

### Phase 3: `ShipInstance.cargo_contents` + `consumable_levels` migration
Both legacy `Dict[str, float|int]` fields become projections over per-component `Container`s on operational ResourceStorage / CargoStorage components. Sweep callers in PROJ-431 sub-phase style: ShipCargoManager → ShipConsumableManager → ShipInstanceBridge → ShipDisplayFormatter → serializer → final-cutover commit deletes the legacy fields. **Checkpoint:** save/load round-trip parity test; grep gate for both legacy field names returns zero in `game/`.

### Phase 4: `Planet.stockpile` + `max_stockpile` + `staging_yard` migration
Planet stockpile becomes one or more `Container`s sourced from planetary facility components with the `Container` ability (`staging_yard_small`, `metals_silo_…`, etc.). `staging_yard` (already mass-aware) folds into a `Container` with `allowed_kinds={ITEM}`. Sweep callers. Final-cutover commit deletes all three legacy fields. **Checkpoint:** save/load parity; grep gate; production-engine smoke tests stay green; planet-detail UI smoke test.

### Phase 5: `Empire._fleet_resource_pool` deletion + `resource_pool` semantics
Delete `Empire._fleet_resource_pool` durable state. Fleet construction resources move into per-fleet/per-ship `Container`s. `Empire.resource_pool` becomes a pure aggregation query that walks all containers in the empire's planets + fleets + ships and sums by `resource_id`. Decide cached-vs-pure here per Phase 0 deferred decision. Migrate all read sites (build-queue projector, empire economy projector, treasury panel). **Checkpoint:** empire economy projection tests; build-queue tests; grep gate for `_fleet_resource_pool`.

### Phase 6: Protocol churn + build-queue/UI `context_type` cleanup
Redesign the public protocol surface: `IEmpire.resource_pool` / `IEmpire.max_storage` at [game/core/protocols/strategy_domain.py:64-72](game/core/protocols/strategy_domain.py#L64-L72) become container-aware reads; `IStockpileHolder` / `IStagingYardHolder` at [game/strategy/data/galaxy_protocols.py:130-180](game/strategy/data/galaxy_protocols.py#L130-L180) consolidate around `Container`. Build-queue controller `context_type` reads at [game/ui/panels/build_queue_controller.py:483-513](game/ui/panels/build_queue_controller.py#L483-L513) move to typed Container queries. **Checkpoint:** static guard tests prove the old protocol method names are gone; UI smoke tests; build-queue integration tests stay green.

### Phase 7: `TransferValidator.VALID_CARGO_TYPES` deletion + UI registry
Delete the hardcoded whitelist at [game/strategy/validation/transfer_validator.py:16-25](game/strategy/validation/transfer_validator.py#L16-L25). Transfer flow consults `Container.accepts()` + resource registry + species registry + design registry. Delete `transfer_view_model.RESOURCE_TYPES` hardcoded list at [game/ui/screens/transfer_view_model.py:26-33](game/ui/screens/transfer_view_model.py#L26-L33); UI iterates the resource registry. **Checkpoint:** transfer integration tests + existing transfer UI tests stay green; grep gate.

### Phase 8: `ProductionEngine.context_type` deletion
Delete the 3 branch sites at [game/strategy/engine/production_engine.py:516,549,606](game/strategy/engine/production_engine.py#L516). ProductionEngine reads from any `Container` whose policy accepts the inputs and writes to any `Container` whose policy accepts the output. Production capability stays an ability on the surrounding component, not part of the container model. **Checkpoint:** production engine integration tests; smoke test of planet build queue + fleet construction.

### Phase 9: `_CarriedItemsProxy` final cutover
Delete the test-only `_CarriedItemsProxy` shim at `game/strategy/data/ship_instance.py:371-396` and all the `_CarriedItemsProxy`-touching test fixtures. By this point production code no longer references `carried_items` at all, and tests can rewrite to the typed `bay_inventory` / `container` API. **Checkpoint:** AST guard tests confirm `_CarriedItemsProxy` is gone; grep gate for `_CarriedItemsProxy` returns zero across `game/` + `tests/`.

### Phase 10: Doc refresh
Update `docs/systems/resource_system.md`, `docs/systems/production_system.md`, `docs/systems/strategy_layer.md`, plus any drift from PROJ-431/434/435 around `carried_items`, `DesignLibrary`, `SaveGameService` replay wiring that this project touched. **Checkpoint:** doc-sync grep checks pass; manual review of touched-doc sections.

### Phase 11: Codex consult + verified-finding remediation
Per the standing end-of-project workflow: run a Codex consult on the landed work. For each finding, verify against current code (do not trust the consult's word). Verified findings become added phases (12+, 13+, …) per the workflow rule. Unverified or out-of-scope findings logged in `decisions.md`. **Checkpoint:** consult round-trip complete; remediation phases (if any) RED→GREEN tested.

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (sharded suite green at each phase boundary)
- [ ] Audit passed
- [ ] User verified
