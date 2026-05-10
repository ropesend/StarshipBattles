# PROJ-335 — File Manifest

## Production files in scope (read-only)

| File | LOC | Notes |
|---|---:|---|
| `game/strategy/data/planetary_facility.py` | 214 | Dataclass + activation, queue, fuel; legacy fallbacks. |
| `game/strategy/data/species_population.py` | 43 | Trivial dataclass; possibly already covered. |
| `game/strategy/data/squadron.py` | 102 | `FleetHierarchyNode` subclass; spatial behavior fields. |
| `game/strategy/data/order_types.py` | 166 | `OrderType` enum, three frozensets, `Order` with 10-branch `to_dict`. |
| `game/strategy/data/group_policy_registry.py` | 108 | JSON-loaded registry with three policy axes. |

## Files out of scope but adjacent

- `game/strategy/data/fleet_hierarchy.py` — parent class of `Squadron`. Covered
  by `tests/unit/strategy/data/test_fleet_hierarchy.py`; do not re-test.
- `game/strategy/data/task_force.py` — sibling of `Squadron`; not in this batch.
- `game/strategy/data/component_activation_state.py` — collaborator of
  `PlanetaryFacility.set_activation_state`; characterized indirectly via the
  facility round-trip but not tested standalone here.

## Existing tests that overlap

Read these first during Phase 1 before writing anything new:

| Existing test file | Covers |
|---|---|
| `tests/unit/strategy/data/test_facility_activation.py` | Component on/off, activation state. |
| `tests/unit/strategy/data/test_facility_construction_queue.py` | Construction queue mutation. |
| `tests/unit/strategy/data/test_facility_resource_tracking.py` | Fuel storage, withdraw, overflow. |
| `tests/unit/strategy/data/test_population_model.py` (`TestSpeciesPopulation`) | Possibly the full surface of `species_population.py`. |
| `tests/unit/strategy/data/test_fleet_hierarchy.py` | `FleetHierarchyNode` parent class. |
| `tests/unit/strategy/data/test_superweapon_orders.py` | Specific `Order` serialization for superweapon paths. |
| `tests/unit/strategy/data/test_fleet_order_resolution.py` | `Order` serialization for fleet orders. |

## New test files to create

One per production file, modulo the species_population skip:

| New test file | Production file | Conditional |
|---|---|---|
| `tests/unit/strategy/data/test_planetary_facility_characterization.py` | `planetary_facility.py` | Always. |
| `tests/unit/strategy/data/test_species_population_characterization.py` | `species_population.py` | Only if existing class doesn't cover the surface (~30% probability). |
| `tests/unit/strategy/data/test_squadron_characterization.py` | `squadron.py` | Always (no existing direct coverage). |
| `tests/unit/strategy/data/test_order_types_characterization.py` | `order_types.py` | Always. |
| `tests/unit/strategy/data/test_group_policy_registry_characterization.py` | `group_policy_registry.py` | Always (no existing coverage). |
