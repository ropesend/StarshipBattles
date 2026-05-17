# TD-06: Slim `ShipInstance` to durable state plus identity API

**Status:** VERIFIED
**Source report:** `Reviews/results/2026-05-16_strategy-layer-tech-debt-review/report.md` section TD-06
**Primary file under review:** `game/strategy/data/ship_instance.py`

---

## Verification Summary

This problem is real and has worsened.

Validated facts:
- `game/strategy/data/ship_instance.py` is still far over the project file-size target.
- The class still contains a large forwarder wall to delegates that already exist elsewhere.
- The heaviest remaining in-class concerns are:
  - the `create(...)` factory path;
  - stats caching and DI-sensitive stat calculation;
  - component/layer inspection for UI-style views;
  - write operations such as component toggles and repair.

Important current-state detail for execution:
- the write-service code and the live `ShipInstance` fields do not use the same manager attribute names everywhere, so a weak LLM must not assume `_cargo_manager` / `_consumable_manager` exist on real `ShipInstance` instances without checking and standardizing that first.

---

## End State

The plan is done when all of the following are true:
- `ShipInstance` primarily holds durable state, identity helpers, and small pure predicates.
- large behavior blocks move to existing delegates or focused helpers;
- the broad forwarder wall is removed in batches, not in one risky sweep;
- caller code uses delegates/services directly instead of going through redundant one-line wrappers;
- the file is materially smaller and easier to extend without cross-layer leakage.

Target shape for `ShipInstance`:
- identity and durable fields;
- `__hash__`, `__eq__`, `__repr__`;
- small read-only properties such as `design_name`, `hull_class`, `effective_role`;
- minimal pure predicates such as `is_damaged` and `is_combat_capable`;
- optional thin shims only while callers are still being migrated.

---

## Weak-LLM Guardrails

- Use the existing test package `tests/unit/strategy/ship_instance/` first; do not invent a parallel test layout unless there is no natural existing home.
- Do not remove `ShipInstance.create`, `to_dict`, `from_dict`, `to_ship`, or similar entry points until grep proves their callers were migrated.
- Do not remove `_cached_stats` in the same phase that extracts stat-calculation logic. Move logic first, storage second.
- Prefer extending the existing `game/strategy/services/component_inspector.py` before creating a second inspector module. Only split if file-size limits force it.
- Standardize manager/accessor naming before migrating callers through the write service. Do not guess which manager attribute names are canonical.
- Treat deployable/cargo forwarders as a separate sub-batch because TD-10 overlaps there directly.

---

## File Touch Map

Core code files:
- `game/strategy/data/ship_instance.py`
- `game/strategy/data/ship_instance_bridge.py`
- `game/strategy/data/ship_instance_serializer.py`
- `game/strategy/data/ship_display_formatter.py`
- `game/strategy/data/ship_cargo_manager.py`
- `game/strategy/data/ship_consumable_manager.py`
- `game/strategy/services/ship_instance_write_service.py`
- `game/strategy/services/component_inspector.py`
- optional new `game/strategy/services/ship_instance_factory.py`
- optional new `game/strategy/data/ship_stats_cache.py`

Existing tests to extend first:
- `tests/unit/strategy/ship_instance/test_convenience_methods.py`
- `tests/unit/strategy/ship_instance/test_component_toggles.py`
- `tests/unit/strategy/ship_instance/test_capacity_levels.py`
- `tests/unit/strategy/ship_instance/test_registries_di.py`
- `tests/unit/strategy/ship_instance/test_ship_instance_bridge.py`
- `tests/unit/strategy/ship_instance/test_ship_instance_serializer.py`
- `tests/unit/strategy/ship_instance/test_serialization.py`
- `tests/unit/strategy/ship_instance/test_cost_queries.py`
- `tests/unit/strategy/services/test_ship_instance_write_service.py`
- `tests/unit/strategy/fleets/test_ship_instance_roundtrip.py`
- `tests/unit/strategy/fleets/test_ship_instance_components.py`
- `tests/integration/test_fms_b_e2e.py`
- `tests/integration/test_fms_c_carrier_ai_launch.py`

Optional new tests if there is no clean existing home:
- `tests/unit/strategy/ship_instance/test_ship_stats_cache.py`
- `tests/unit/strategy/services/test_ship_instance_factory.py`

---

## Phased Remediation Plan

### Phase 0 - Freeze current behavior using existing test surfaces

Before extracting anything, add or tighten tests for:
- `create(...)` behavior;
- stats-cache hit, miss, and invalidation behavior;
- component-toggle invalidation behavior;
- bridge and serializer round-trips;
- resource, cargo, and display convenience behavior that will later be migrated away.

Preferred test homes:
- `tests/unit/strategy/ship_instance/test_convenience_methods.py`
- `tests/unit/strategy/ship_instance/test_component_toggles.py`
- `tests/unit/strategy/ship_instance/test_registries_di.py`
- `tests/unit/strategy/ship_instance/test_ship_instance_bridge.py`
- `tests/unit/strategy/ship_instance/test_ship_instance_serializer.py`

Do not create a large new characterization file when the repo already has focused test modules for these concerns.

### Phase 1 - Extract stats-calculation logic before changing storage

Touch list:
- optional new `game/strategy/data/ship_stats_cache.py`
- `game/strategy/data/ship_instance.py`
- `tests/unit/strategy/ship_instance/test_registries_di.py`
- optional new `tests/unit/strategy/ship_instance/test_ship_stats_cache.py`

Execution rules:
- first move calculation and invalidation behavior into a helper/service;
- keep `_cached_stats` temporarily if that makes the move smaller and safer;
- only after the helper is proven should you consider moving cache storage off the entity.

Required behavior to keep:
- missing registries still fail in the same way;
- cache invalidation after relevant state changes still works;
- callers do not need to change in this phase.

### Phase 2 - Move component/layer inspection out of `ShipInstance`

Touch list:
- `game/strategy/services/component_inspector.py`
- `game/strategy/data/ship_instance.py`
- `tests/unit/strategy/fleets/test_ship_instance_components.py`
- any UI or formatter tests that directly rely on component-layer views

Preferred implementation:
- extend `game/strategy/services/component_inspector.py` with ship-instance-specific helpers;
- only create a new inspector module if extending the existing one would clearly violate the 500-LOC limit.

Move these behaviors out:
- `iter_all_components_by_layer`
- `get_damaged_components_by_layer`
- `get_damaged_component_count`
- helper logic that joins design layers with `ComponentState`

Do not move them into UI code.

### Phase 3 - Extract the factory path and keep a thin shim

Touch list:
- optional new `game/strategy/services/ship_instance_factory.py`
- `game/strategy/data/ship_instance.py`
- `tests/unit/strategy/services/test_ship_instance_factory.py`
- `tests/unit/strategy/ship_instance/test_registries_di.py`

Scope:
- move the body of `ShipInstance.create(...)` to a factory/helper;
- move `_build_full_hp_components_from_design(...)` with it;
- leave `ShipInstance.create(...)` as a thin shim until callers are migrated.

This phase should not migrate every call site yet.

Required grep before the phase ends:

```bash
rg -n "ShipInstance\.create\(" game tests
```

The shim stays until a later caller-migration batch removes or empties that result set.

### Phase 4 - Move write behavior onto `ShipInstanceWriteService` and standardize manager names

Touch list:
- `game/strategy/services/ship_instance_write_service.py`
- `game/strategy/data/ship_instance.py`
- `tests/unit/strategy/services/test_ship_instance_write_service.py`
- `tests/unit/strategy/ship_instance/test_component_toggles.py`

Required prep inside this phase:
- verify the canonical manager/accessor names on `ShipInstance`;
- make the write service and entity agree on those names before caller migration.

Required behavior moves:
- cache-invalidating component toggles;
- repair/full-repair logic;
- any remaining direct-write helpers that are not identity-level behavior.

Do not leave cache invalidation split across old entity methods and new service methods.

### Phase 5 - Remove forwarders in controlled sub-batches

Do not attempt this as one giant edit. Use sub-batches with grep and focused tests between them.

#### Batch 5a - Display forwarders

Forwarders:
- `get_display_id`
- `get_status_text`
- `get_hp_display`
- `get_resource_display`

Caller migration target:
- `ShipDisplayFormatter`

#### Batch 5b - Resource/consumable forwarders

Forwarders:
- resource-capacity queries
- resource-consumption helpers
- resupply helpers

Caller migration target:
- `ShipConsumableManager` or a stable accessor to it

#### Batch 5c - Cargo and capacity forwarders

Forwarders:
- cargo queries and mutators
- carried-vehicle queries
- pod-storage helpers

Caller migration target:
- `ShipCargoManager`

Important overlap:
- this is the sub-batch that directly overlaps TD-10.

#### Batch 5d - Serializer forwarders

Forwarders:
- `to_dict`
- `from_dict`
- `to_json`
- `from_json`
- `clone`

Caller migration target:
- `ShipInstanceSerializer`

#### Batch 5e - Bridge forwarders

Forwarders:
- `to_ship`
- `update_from_ship`

Caller migration target:
- `ShipInstanceBridge`

For every sub-batch:
1. grep for live callers;
2. add or update one focused failing test for the new direct-call path;
3. migrate callers;
4. remove only the forwarders covered by that sub-batch;
5. rerun focused tests before moving to the next batch.

Useful grep patterns:

```bash
rg -n "get_display_id|get_status_text|get_hp_display|get_resource_display" game tests
rg -n "to_ship\(|update_from_ship\(" game tests
rg -n "to_dict\(|from_dict\(|clone\(" game tests
```

### Phase 6 - Final trim and cleanup

Goals:
- shrink `ship_instance.py` as far as practical after caller migration;
- keep only durable state, identity helpers, and small pure predicates;
- delete obsolete shims only after grep shows no live callers remain.

Final grep gates:

```bash
rg -n "ShipInstance\.create\(|\.to_ship\(|\.update_from_ship\(|\.to_dict\(|\.clone\(" game tests
```

If any high-value entry point still has many live callers, leave it as a thin shim and document that explicitly instead of forcing a risky all-callers migration.

---

## Test Strategy

Focused suites by concern:

```bash
pytest tests/unit/strategy/ship_instance/ -x
pytest tests/unit/strategy/services/test_ship_instance_write_service.py -x
pytest tests/unit/strategy/fleets/test_ship_instance_roundtrip.py tests/unit/strategy/fleets/test_ship_instance_components.py -x
pytest tests/integration/test_fms_b_e2e.py tests/integration/test_fms_c_carrier_ai_launch.py -x
```

Only after focused suites are green:

```bash
python Tools/test_sharded/test_sharded.py
```

Minimum behavior that must stay locked:
- serializer round-trips;
- bridge conversion round-trips;
- stats-cache invalidation after state changes;
- cargo/resource semantics;
- deployable-heavy integration flows that still depend on `ShipInstance`.

---

## Risks And Mitigations

| Risk | Mitigation |
|---|---|
| A weak LLM removes shims before migrating callers. | Add grep gates to each removal phase and allow thin shims to remain temporarily. |
| Cache invalidation breaks silently while logic moves to helpers. | Extract calculation logic before changing storage, and centralize toggle/repair invalidation in the write service. |
| A second ship-inspector module duplicates existing service logic. | Prefer extending `component_inspector.py`; split only if size limits require it. |
| Manager naming drift causes write-service bugs. | Standardize live attribute/accessor names in Phase 4 before broader caller migration. |
| Cargo/deployable changes conflict with TD-10. | Treat cargo/deployable forwarders as their own batch and sequence them with TD-10. |

---

## Ordering Constraints

Hard ordering constraints:
- None for Phases 0 through 4.
- Only Batch 5c should be treated as TD-10-sensitive.

Soft ordering notes:
- TD-10 should land before or together with Batch 5c if possible.
- TD-02 is helpful if a session-level services container is introduced, but TD-06 does not require TD-02 to start.
- TD-05 does not require TD-06 first. TD-05 can keep using `ShipInstance.create(...)` or a shim while this plan is in progress.

Effect on `EXECUTION_ORDER.md`:
- Remove any hard `TD-06 -> TD-05` dependency.
- Keep only the narrower note that TD-10 affects the cargo/deployable forwarder batch inside TD-06.

---

## Acceptance Criteria

- [ ] `ShipInstance` is materially smaller and no longer owns its largest helper blocks.
- [ ] Stats-calculation logic no longer lives inline in `ShipInstance`.
- [ ] Component/layer inspection no longer lives inline in `ShipInstance`.
- [ ] Direct write behavior is centralized through `ShipInstanceWriteService` or an equivalent single write path.
- [ ] Removed forwarders have had their callers migrated in bounded batches.
- [ ] Serializer and bridge round-trips are still green.
- [ ] Focused ship-instance, fleet, and FMS integration suites are green before the sharded run.
- [ ] `python Tools/test_sharded/test_sharded.py` is green.

---

## Out Of Scope

- Redesigning deployable substrate semantics beyond the TD-10 overlap noted above.
- Save-format changes unrelated to this slimming effort.
- UI/facade redesign not directly required by caller migration.
