# PROJ-425 File Manifest

> Generated during project init from the TD-06 plan's `## File Touch Map`.
> Used by `/proj-parallel` for conflict detection. Update if implementation discovers additional files.

## Production code — slimming target

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/ship_instance.py` | Production (rewrite) | Currently 845 LOC. End state: durable state + identity + small pure predicates. Touched in every phase. |

## Production code — existing delegates (extended / become canonical)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/ship_consumable_manager.py` | Production (extend) | Absorbs resource-capacity / consumption / resupply forwarders — Phase 5 Batch 5b. |
| `game/strategy/data/ship_cargo_manager.py` | Production (extend) | Absorbs cargo / carried-vehicle / pod-storage forwarders — **Phase 6** (TD-10-gated). |
| `game/strategy/data/ship_display_formatter.py` | Production (extend) | Absorbs `get_display_id` / `get_status_text` / `get_hp_display` / `get_resource_display` — Phase 5 Batch 5a. |
| `game/strategy/data/ship_instance_bridge.py` | Production (extend) | Absorbs `to_ship` / `update_from_ship` — Phase 5 Batch 5e. |
| `game/strategy/data/ship_instance_serializer.py` | Production (extend) | Absorbs `to_dict` / `from_dict` / `to_json` / `from_json` / `clone` — Phase 5 Batch 5d. |
| `game/strategy/services/ship_instance_write_service.py` | Production (extend) | Absorbs cache-invalidating component toggles and repair / full-repair — Phase 4. |
| `game/strategy/services/component_inspector.py` | Production (extend) | Absorbs `iter_all_components_by_layer` / `get_damaged_components_by_layer` / `get_damaged_component_count` — Phase 2. |

## Production code — optional new modules (created only if extension breaches 500 LOC elsewhere)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/ship_stats_cache.py` | Production (optional new) | Phase 1 — stats calculation + invalidation helper. Created only if no natural existing home. |
| `game/strategy/services/ship_instance_factory.py` | Production (optional new) | Phase 3 — factory body extracted from `ShipInstance.create(...)`. Created only if no natural existing home. |

## Tests — existing modules to extend (Phase 0 + per-phase regression gates)

| File | Type | Notes |
|------|------|-------|
| `tests/unit/strategy/ship_instance/test_convenience_methods.py` | Test (extend) | Phase 0 characterization + Phase 5 regression. |
| `tests/unit/strategy/ship_instance/test_component_toggles.py` | Test (extend) | Phase 0 + Phase 4 (write service migration). |
| `tests/unit/strategy/ship_instance/test_capacity_levels.py` | Test (extend) | Phase 0 + Phase 6 (cargo migration regression). |
| `tests/unit/strategy/ship_instance/test_registries_di.py` | Test (extend) | Phase 0 + Phase 1 (stats cache) + Phase 3 (factory). |
| `tests/unit/strategy/ship_instance/test_ship_instance_bridge.py` | Test (extend) | Phase 0 + Phase 5 Batch 5e. |
| `tests/unit/strategy/ship_instance/test_ship_instance_serializer.py` | Test (extend) | Phase 0 + Phase 5 Batch 5d. |
| `tests/unit/strategy/ship_instance/test_serialization.py` | Test (extend) | Phase 0 + Phase 5 Batch 5d round-trip gate. |
| `tests/unit/strategy/ship_instance/test_cost_queries.py` | Test (extend) | Phase 0 characterization. |
| `tests/unit/strategy/services/test_ship_instance_write_service.py` | Test (extend) | Phase 4 — toggles and repair behavior. |
| `tests/unit/strategy/fleets/test_ship_instance_roundtrip.py` | Test (regression gate) | Phase 5 Batches 5d / 5e. |
| `tests/unit/strategy/fleets/test_ship_instance_components.py` | Test (extend) | Phase 2 — layer inspection moved out. |
| `tests/integration/test_fms_b_e2e.py` | Test (regression gate) | Bridge / serializer regression. |
| `tests/integration/test_fms_c_carrier_ai_launch.py` | Test (regression gate) | Deployable-heavy integration flow — Phase 6 gate. |

## Tests — optional new modules (only if no clean existing home)

| File | Type | Notes |
|------|------|-------|
| `tests/unit/strategy/ship_instance/test_ship_stats_cache.py` | Test (optional new) | Phase 1 — only if `ship_stats_cache.py` is created. |
| `tests/unit/strategy/services/test_ship_instance_factory.py` | Test (optional new) | Phase 3 — only if `ship_instance_factory.py` is created. |

## Caller migration scope (discovered by grep — populated during execution)

Caller files migrated as forwarders are demolished. These will be filled in as each sub-batch runs grep gates:

- Phase 5 Batch 5a (display): `rg -n "get_display_id|get_status_text|get_hp_display|get_resource_display" game tests`
- Phase 5 Batch 5b (consumable): grep for resource-capacity / consumption / resupply call sites.
- Phase 5 Batch 5d (serializer): `rg -n "to_dict\(|from_dict\(|clone\(" game tests`
- Phase 5 Batch 5e (bridge): `rg -n "to_ship\(|update_from_ship\(" game tests`
- Phase 6 / Batch 5c (cargo + deployable, gated on PROJ-431 Phase 1): grep for cargo / carried-vehicle / pod-storage call sites.
- Phase 3 factory shim grep (does not delete callers, only proves the shim is still load-bearing): `rg -n "ShipInstance\.create\(" game tests`
- Phase 6 close gate: `rg -n "ShipInstance\.create\(|\.to_ship\(|\.update_from_ship\(|\.to_dict\(|\.clone\(" game tests`
