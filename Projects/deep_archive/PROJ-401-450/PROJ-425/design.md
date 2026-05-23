# PROJ-425: Design Document — ShipInstance Slimming (TD-06)

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to [decisions.md](decisions.md).

## Verification findings (from TD-06 plan)

- `game/strategy/data/ship_instance.py` is **845 LOC** today, well past the 500-LOC project ceiling.
- Roughly **~50 thin one-line forwarders** delegate to helper classes that already exist elsewhere in `game/strategy/data/` and `game/strategy/services/`.
- The forwarder wall has worsened since the original review, not improved.
- The **heaviest remaining in-class concerns** (the parts that are *not* forwarders) are three substantive blocks plus one factory:
  1. **Stats cache + DI-sensitive stat calculation.** The entity holds `_cached_stats` and runs registry-dependent calculation inline.
  2. **Component / layer introspection.** Methods such as `iter_all_components_by_layer`, `get_damaged_components_by_layer`, `get_damaged_component_count` join the design's layer structure with `ComponentState` instances and produce UI-style views from inside the entity.
  3. **The `create(...)` factory path** — together with `_build_full_hp_components_from_design(...)`. Construction logic lives on the class it constructs.
  4. **Cache-invalidating writes** — component toggles and repair / full-repair logic mutate state *and* invalidate `_cached_stats` from inside the entity.
- **Manager/accessor naming is inconsistent.** The write-service code and the live `ShipInstance` fields do not use the same manager attribute names everywhere. A weak LLM must not assume `_cargo_manager` / `_consumable_manager` exist on real `ShipInstance` instances without checking and standardizing that first. (TD-06 Verification Summary explicitly calls this out.)

## Responsibility inventory — what `ShipInstance` is doing today

| Responsibility | Belongs on `ShipInstance`? | Today's owner | Target owner |
|---|---|---|---|
| Durable state fields (instance id, design ref, ownership, hp, ammo, etc.) | Yes | `ShipInstance` | `ShipInstance` (unchanged) |
| `__hash__` / `__eq__` / `__repr__` | Yes | `ShipInstance` | `ShipInstance` (unchanged) |
| Identity properties (`design_name`, `hull_class`, `effective_role`) | Yes | `ShipInstance` | `ShipInstance` (unchanged) |
| Pure predicates (`is_damaged`, `is_combat_capable`) | Yes | `ShipInstance` | `ShipInstance` (unchanged) |
| Stats calculation + cache + invalidation | **No** | `ShipInstance` (inline) | New helper (`ship_stats_cache.py`) or existing stats path — Phase 1 |
| Component / layer introspection | **No** | `ShipInstance` (inline) | `component_inspector.py` (extend) — Phase 2 |
| Factory (`create`, `_build_full_hp_components_from_design`) | **No** | `ShipInstance.create` (inline body) | New `ship_instance_factory.py` — Phase 3 (with shim) |
| Cache-invalidating component toggles + repair | **No** | `ShipInstance` (inline) | `ShipInstanceWriteService` — Phase 4 |
| Display helpers (`get_display_id`, `get_status_text`, `get_hp_display`, `get_resource_display`) | **No (forwarders)** | `ShipInstance` (1-line wrappers) | `ShipDisplayFormatter` (already exists) — Phase 5 Batch 5a |
| Resource / consumable queries + resupply helpers | **No (forwarders)** | `ShipInstance` (1-line wrappers) | `ShipConsumableManager` (already exists) — Phase 5 Batch 5b |
| Cargo / carried-vehicle / pod-storage helpers | **No (forwarders)** | `ShipInstance` (1-line wrappers) | `ShipCargoManager` (already exists) — Phase 6 (TD-10-gated) |
| `to_dict` / `from_dict` / `to_json` / `from_json` / `clone` | **No (forwarders)** | `ShipInstance` (1-line wrappers) | `ShipInstanceSerializer` (already exists) — Phase 5 Batch 5d |
| `to_ship` / `update_from_ship` | **No (forwarders)** | `ShipInstance` (1-line wrappers) | `ShipInstanceBridge` (already exists) — Phase 5 Batch 5e |

## Existing healthy delegates — already in the tree, just under-used

The good news: TD-06 is mostly a **migration / demolition** project, not a "design a new architecture" project. The delegates already exist and are healthy. The goal is to remove the redundant forwarder layer on `ShipInstance`, not to design new collaborators from scratch.

| Delegate | File | Purpose |
|---|---|---|
| `ShipConsumableManager` | [`game/strategy/data/ship_consumable_manager.py`](../../../game/strategy/data/ship_consumable_manager.py) | Resource-capacity, consumption, and resupply behavior |
| `ShipCargoManager` | [`game/strategy/data/ship_cargo_manager.py`](../../../game/strategy/data/ship_cargo_manager.py) | Cargo / carried-vehicle / pod-storage queries and mutators |
| `ShipDisplayFormatter` | [`game/strategy/data/ship_display_formatter.py`](../../../game/strategy/data/ship_display_formatter.py) | `display_id` / `status_text` / `hp_display` / `resource_display` formatters |
| `ShipInstanceBridge` | [`game/strategy/data/ship_instance_bridge.py`](../../../game/strategy/data/ship_instance_bridge.py) | `ShipInstance` ↔ `Ship` (battle layer) conversion |
| `ShipInstanceSerializer` | [`game/strategy/data/ship_instance_serializer.py`](../../../game/strategy/data/ship_instance_serializer.py) | dict / json serialization + `clone` |
| `ShipInstanceWriteService` | [`game/strategy/services/ship_instance_write_service.py`](../../../game/strategy/services/ship_instance_write_service.py) | Centralized write path (will absorb toggles + repair in Phase 4) |

## The three substantive non-forwarder offenders

These are the only meaningful *logic* that needs to *move* (rather than be forwarded out of existence). Each gets its own phase.

### 1. Stats cache + registry-DI calculation — Phase 1
- Inline `_cached_stats` storage on the entity.
- Inline calculation path that needs registry-style DI.
- TD-06's Weak-LLM Guardrail #2: *"Do not remove `_cached_stats` in the same phase that extracts stat-calculation logic. Move logic first, storage second."*
- Plan: extract calculation + invalidation into a helper. Keep `_cached_stats` on the entity through Phase 1. Only consider moving the cache storage off the entity *after* the helper is proven.

### 2. Component / layer introspection — Phase 2
- `iter_all_components_by_layer`, `get_damaged_components_by_layer`, `get_damaged_component_count`, plus the helper logic that joins design layers with `ComponentState`.
- TD-06's Weak-LLM Guardrail #4: *"Prefer extending the existing `game/strategy/services/component_inspector.py` before creating a second inspector module. Only split if file-size limits force it."*
- Plan: extend `component_inspector.py` (current LOC is comfortably under the ceiling). Only split if extension would breach 500 LOC there.

### 3. `ShipInstance.create(...)` factory — Phase 3
- Construction logic on the class being constructed; pulls in `_build_full_hp_components_from_design(...)`.
- TD-06's Weak-LLM Guardrail #1: *"Do not remove `ShipInstance.create`, `to_dict`, `from_dict`, `to_ship`, or similar entry points until grep proves their callers were migrated."*
- Plan: extract the body to a factory helper. **Keep `ShipInstance.create(...)` as a thin shim** that delegates to the factory. Caller migration is *not* a Phase 3 goal — the shim stays until a later batch empties `rg -n "ShipInstance\.create\(" game tests`.

## Cross-project phase gate — PROJ-431 (TD-10)

The cargo / carried-vehicle / pod-storage forwarders (TD-06 Batch 5c) overlap directly with [PROJ-431 (TD-10) deployable substrate redesign](../PROJ-431/plan.md). Demolishing those forwarders before PROJ-431 lands the typed `bay_inventory` substrate would force this project to either:

- migrate callers to today's untyped accessor (then re-migrate them in PROJ-431), or
- preemptively design the typed substrate inside TD-06's scope (out of scope).

Neither is acceptable. The resolution is the **phase gate**: TD-06 Phases 0–4 (plus Phase 5 batches 5a / 5b / 5d / 5e) run unblocked. **Phase 6 (Batch 5c) is blocked until PROJ-431 Phase 1 has landed typed `bay_inventory`.** The TD-06 source plan's `## Ordering Constraints` section codifies this ("Only Batch 5c should be treated as TD-10-sensitive"), and [EXECUTION_ORDER.md](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/EXECUTION_ORDER.md) lists "Return to TD-06 if cargo/deployable forwarder cleanup still remains" as step 11 — the deferred tail of TD-06 that runs only after TD-10 Phase 1.

The `## Dependencies` section of [plan.md](plan.md) and `phase_6_checklist.md`'s `**Depends on:**` line both surface this gate. `phase_state.json` records the in-project predecessor only (`phase_5`), because cross-project predecessors are not first-class in `phase_state` — the gate is enforced by the checklist and by the project-status row marked `Blocked` until PROJ-431 Phase 1 merges.

## Risk register

| Risk | Mitigation |
|---|---|
| A weak LLM removes shims before migrating callers (`ShipInstance.create`, `to_dict`, `to_ship`, `clone`). | TD-06 Weak-LLM Guardrail #1 + grep gates required at every phase that touches a forwarder. Shims may remain temporarily and be documented. |
| Cache invalidation breaks silently while logic moves to helpers (Phase 1 → Phase 4). | TD-06 Guardrail #2: extract calculation *before* changing storage. Centralize toggle/repair invalidation in the write service (Phase 4) so it is not split across old entity methods and new service methods. |
| A second component-inspector module duplicates existing service logic. | Prefer extending [`component_inspector.py`](../../../game/strategy/services/component_inspector.py); split only if 500-LOC limit forces it. |
| Manager naming drift causes write-service bugs in Phase 4. | Standardize live attribute/accessor names in Phase 4 prep (and confirm during Phase 0 grep) *before* broader caller migration. Do not guess. |
| Cargo/deployable changes conflict with TD-10 / PROJ-431. | Phase gate — Phase 6 blocked until PROJ-431 Phase 1 lands typed `bay_inventory`. Recorded in plan.md, design.md (this section), and phase_6_checklist.md. |
| Big-bang demolition of the forwarder wall. | Forwarders demolished in sub-batches (5a → 5b → 5d → 5e → 5c) with grep + focused tests between each sub-batch — never in one sweep. |

## Out of scope

- Save-format changes unrelated to slimming.
- UI / facade redesign not directly required by caller migration.
- Renaming or removing high-value entry points without grep-proven caller migration (`ShipInstance.create`, `to_dict`, `from_dict`, `to_ship`, `clone`).
- The PROJ-431 / TD-10 deployable substrate redesign itself — this project only consumes the typed `bay_inventory` PROJ-431 produces, in Phase 6.
