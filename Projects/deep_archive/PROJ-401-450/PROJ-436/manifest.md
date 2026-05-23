# PROJ-436 File Manifest

> Generated during charter creation from the converged design at `AgentCoordination/Scratchpad/Discussion/20260517T230029Z_post-435-project-creation/plans/post_435_project_set_r001.md` and `AgentCoordination/Scratchpad/reports/unified_container_design_sketch.md`. Updated as implementation discovers additional files.

## Files

### Production — added (Phase 0)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/container.py` | Production (new) | `ContainableKind` enum, `Containable` abstract base, `ContainerPolicy` dataclass, `Container` class with three slices (`resources: Dict[str, float]`, `items: List[ItemRef]`, `population: Dict[str, int]`), mass-cap accounting, `accepts()` / `add()` / `remove()` / `contents()` ops. Save/load round-trip via `to_dict()` / `from_dict()`. Estimate ~400-500 LOC. |
| `game/strategy/data/containable.py` | Production (new) | `ItemRef` dataclass for items-slice identity (design_id + optional damage/state); resource and population entries store as primitive dict keys. `Containable.mass_per_unit` resolves through the existing `ResourceCatalog` (Core layer) for resources, through species/race JSONs for population, and through design metadata for items. |

### Production — modified (Phase 0)

| File | Type | Notes |
|------|------|-------|
| `game/core/resources.py` | Production | **Extend `ResourceDefinition` dataclass with `mass_per_unit: float = 1.0`.** Add `ResourceCatalog.get_mass_per_unit(resource_id) -> float` convenience accessor (raises on unknown). Update `ResourceCatalog.from_data` / `from_json` parsers to read the new field. Keep the immutable-dataclass + frozen-typing contract. This is the single source of truth for mass-per-unit; no parallel strategy-local registry is introduced. |
| `data/resources.json` | Data (modified, existing canonical file) | **Add `mass_per_unit` to each of the 8 existing entries.** Values: metals 0.01, organics 0.01, vapors 0.001, radioactives 0.005, exotics 0.001, fuel 0.0001, ammo 0.001, energy 1.0 (per user directive). Existing fields (`id`, `name`, `description`, `display_group`, `has_quality`) unchanged. Populations carry mass per-species on the existing race JSONs under `data/races/`, defaulting to 0.1 per individual when absent. |

### Production — added (Phase 1)

| File | Type | Notes |
|------|------|-------|
| `game/simulation/components/abilities/container.py` | Production (new) | Single `Container` ability replacing the three current storage abilities. JSON shape: `{capacity_mass: <float>, allowed_kinds: [<kind>], allowed_type_ids: [<id> or null]}`. |

### Production — modified (Phase 1)

| File | Type | Notes |
|------|------|-------|
| `game/simulation/components/abilities/cargo.py` | Production | `CargoStorage` becomes a legacy parser that compiles to `Container` internally; existing data-file shapes (`{cargo_type, capacity}`) continue to load. No runtime behavior change yet. |
| `game/simulation/components/abilities/resources.py` | Production | `ResourceStorage` becomes a legacy parser that compiles to `Container` internally. `ResourceGeneration` and `ResourceConsumption` UNCHANGED — they stay separate per user direction. |
| Existing component classes wired through ability registry | Production | Ability-registry registration extended for `Container`. |

### Production — modified (Phase 2)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/bay_inventory.py` | Production | Widen `BayInventory` from `{pods: List[DropPod], vehicles: List[CarriedVehicle]}` to a full `Container` with three slices. Existing `pods` / `vehicles` accessors become views over `container.items`. Mass accounting unified. |
| `game/strategy/engine/order_handlers/launch_fighters.py` | Production | Source items via `container.remove()` instead of `bay.pop()`. |
| `game/strategy/engine/order_handlers/launch_satellites.py` | Production | Same. |
| `game/strategy/engine/order_handlers/lay_mines.py` | Production | Same. |
| `game/strategy/engine/order_handlers/recover_fighters.py` | Production | Push recovered items via `container.add()`. |
| `game/strategy/engine/order_handlers/recover_satellites.py` | Production | Same. |
| `game/strategy/services/mine_group_service.py` | Production | Consume widened container API. |

### Production — modified (Phase 3)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/ship_instance.py` | Production | Delete `cargo_contents: Dict[str, int]` and `consumable_levels: Dict[str, float]` dataclass fields. Replace with per-component `Container` access. |
| `game/strategy/data/ship_cargo_manager.py` | Production | All reads/writes through `Container.get_resource()` / `Container.add_resource()` etc. PROJ-431 1f migration pattern. |
| `game/strategy/data/ship_consumable_manager.py` | Production | Same. |
| `game/strategy/data/ship_instance_bridge.py` | Production | Decoupled bridge reads from container. |
| `game/strategy/data/ship_display_formatter.py` | Production | UI display reads from container. |
| `game/strategy/data/ship_instance_serializer.py` | Production | Round-trip via container; legacy `cargo_contents` / `consumable_levels` serialization deleted at final-cutover commit. Saves are disposable per CLAUDE.md. |

### Production — modified (Phase 4)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/planet.py` | Production | Delete `stockpile: Dict[str, float]`, `max_stockpile: Dict[str, float]`, `staging_yard: List[Dict[str, Any]]` dataclass fields. Replace with per-facility-component `Container` access. `add_to_stockpile` / `consume_from_stockpile` / `has_stockpile` / `get_stockpile` / `add_to_staging_yard` / `remove_from_staging_yard` / `get_staging_yard_mass` rewrite around `Container` ops. |
| `game/strategy/data/planetary_facility.py` | Production | `consumable_levels: Dict[str, float]` per Phase 0 decision: either folds into facility-local Container or stays as facility internal state. |
| Planet serializer + relevant production engine consumers | Production | Round-trip via Container. |

### Production — modified (Phase 5)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/empire.py` | Production | **DONE (5f).** Deleted `_fleet_resource_pool: Dict[str, float]` durable state, `Empire.add_resources`, `Empire.consume_resources`, and the `resource_pool` property setter. `resource_pool` is a pure aggregation over `self.colonies[*].stockpile` (Phase 0 D2 default — no caching). `to_dict` drops the legacy `resource_pool` key; `from_dict` ignores it on pre-Phase-5 saves. The "fleet construction resources move into ship/fleet containers" framing in the original Phase 5 plan was aspirational — production code never read fleet cargo through `Empire.resource_pool`; fleet construction reads `Fleet.has_cargo_resources` / `Fleet.consume_cargo_resource` directly in `ProductionEngine`. |
| `game/strategy/engine/production_engine.py` | Production | **DONE (5f).** Dead `else` fallback branches (`empire.has_resources` / `empire.consume_resources` / `empire.resource_pool.get(...)`) replaced with explicit `ValueError`. Every production caller passes a Planet or a Fleet; the fallback was unreachable. The `if planet / elif fleet` branching itself stays for Phase 8. |
| `game/strategy/engine/empire_economy_calculator.py` | Production | **No-op for Phase 5.** Reads `empire.resource_pool.copy()` (line 168) — tolerates the new pure-aggregate semantics unchanged. Treasury "Total In Storage" now reports colony-stockpile totals only (matches what the pre-Phase-5 implementation reported in practice, because `_fleet_resource_pool` was never populated by production code). |
| `game/strategy/services/empire_write_service.py` | Production | **No-op for Phase 5.** Docstring updated to drop the `_fleet_resource_pool` mutation surface from the listed responsibilities. |

### Production — modified (Phase 6)

| File | Type | Notes |
|------|------|-------|
| `game/core/protocols/strategy_domain.py` | Production | Redesign `IEmpire.resource_pool` / `IEmpire.max_storage` around the new Container contract (lines 64-72). |
| `game/strategy/data/galaxy_protocols.py` | Production | Consolidate `IStockpileHolder` / `IStagingYardHolder` (lines 130-180) around `Container`. The two protocols may collapse to one. |
| `game/ui/panels/build_queue_controller.py` | Production | Build-queue UI `context_type` cleanup at lines 483-513. Reads via typed Container queries. |
| Other UI consumers of the deprecated protocol methods | Production | Migrate to the new Container API. |

### Production — modified (Phase 7)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/validation/transfer_validator.py` | Production | **Delete `VALID_CARGO_TYPES` (lines 16-25).** Validation through `Container.accepts()` + resource/species/design registries. `_validate_cargo_type` check at lines 72-76 collapses to `source.accepts(containable) and dest.accepts(containable)`. |
| `game/ui/screens/transfer_view_model.py` | Production | **Delete `RESOURCE_TYPES` + `RESOURCE_DISPLAY_NAMES` hardcoded lists (lines 26-35).** Iterate `ResourceCatalog.all_ids()` (Core-layer single source of truth). `RESOURCE_DISPLAY_NAMES` collapses to `ResourceDefinition.name` lookup. |
| `game/ui/screens/transfer_dialog.py` | Production | Re-export site at lines 39-43 deleted. |
| `game/strategy/engine/order_handlers/transfer_branches.py` | Production | Branches consume Container API. |

### Production — modified (Phase 8)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/engine/production_engine.py` | Production | **Delete `context_type` branching at lines 503-521, 549, 606-615.** Production reads inputs and writes outputs through Container protocol — context_type is no longer a routing signal. |

### Production — modified (Phase 9)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/ship_instance.py` | Production | **Delete `_CarriedItemsProxy` class + the `carried_items` property** (currently lines 92-95 + 371-396). Production code path no longer needs it. |
| Test fixtures referencing `_CarriedItemsProxy` / `ship.carried_items` | Test | Audit + rewrite to typed Container API. |

### Tests — added

| File | Type | Notes |
|------|------|-------|
| `tests/unit/strategy/data/test_container.py` | Test (new) | Phase 0. Container ops, mass accounting, policy filtering, three-slice round-trip, content-policy rejection. |
| `tests/unit/strategy/data/test_containable.py` | Test (new) | Phase 0. `Containable` variants, mass-per-unit lookup via existing `ResourceCatalog`. |
| `tests/unit/core/test_resource_catalog_mass_per_unit.py` | Test (new) | Phase 0. Tests for the extended `ResourceCatalog.get_mass_per_unit()` and the new field on `ResourceDefinition`. Lives under `tests/unit/core/` because the catalog is Core-layer. |
| `tests/unit/simulation/components/abilities/test_container_ability.py` | Test (new) | Phase 1. Container ability parser parity with `ResourceStorage` / `CargoStorage` / `VehicleBay`. |
| `tests/unit/strategy/data/test_bay_inventory_widened.py` | Test (new) | Phase 2. Widened BayInventory three-slice behavior; backward-compatible `pods` / `vehicles` accessors still work. |
| `tests/integration/test_ship_resource_migration.py` | Test (new) | Phase 3. End-to-end ship resource production / consumption through unified Container. |
| `tests/integration/test_planet_storage_migration.py` | Test (new) | Phase 4. End-to-end planet stockpile + staging yard through unified Container. |
| `tests/integration/test_empire_resource_aggregation.py` | Test (new) | **DONE (5g).** `Empire.resource_pool` pure-aggregation contract across colony stockpiles. 14 tests in 3 classes: aggregation walk + snapshot semantics, `has_resources`/`get_resource` routing, save-shape contract incl. legacy-key drop. Landed as the Phase 5g verified-finding remediation after Codex flagged its absence in the post-5f consult. |
| `tests/static_guards/test_no_legacy_storage_fields.py` | Test (new) | Phases 3/4/5 gates. AST assertion that no `cargo_contents`, `consumable_levels`, `stockpile`, `max_stockpile`, `staging_yard`, `_fleet_resource_pool` fields exist on the targeted dataclasses. |
| `tests/static_guards/test_no_legacy_protocol_names.py` | Test (new) | Phase 6 gate. AST assertion against the old protocol method names. |
| `tests/integration/test_transfer_container_validation.py` | Test (new) | Phase 7. Transfer flow through `Container.accepts()` end-to-end. |
| `tests/integration/test_production_engine_container_unified.py` | Test (new) | Phase 8. ProductionEngine source/dest through Container. |
| `tests/static_guards/test_no_carried_items_proxy.py` | Test (new) | Phase 9 gate. AST assertion that `_CarriedItemsProxy` class and `carried_items` attribute are gone. |

### Tests — modified

Many existing tests across `tests/unit/strategy/data/`, `tests/integration/`, `tests/integration/strategy/`, and `tests/static_guards/` will need updates as fields migrate. Enumerated phase-by-phase in each phase checklist.

### Docs — modified (Phase 10)

| File | Type | Notes |
|------|------|-------|
| `docs/systems/resource_system.md` | Doc | Rewrite around the unified Container. Drop references to `VALID_CARGO_TYPES`. |
| `docs/systems/production_system.md` | Doc | Update for ProductionEngine consuming Container protocol. |
| `docs/systems/strategy_layer.md` | Doc | Update storage/inventory section. |
| `docs/01_ARCHITECTURE.md` | Doc | If it describes the old storage abstractions, update. |
| `docs/02_PATTERNS.md` | Doc | Add/update Container pattern entry. |
| Other docs flagged during Phase 10 audit | Doc | Anything touching the migrated surfaces. |
