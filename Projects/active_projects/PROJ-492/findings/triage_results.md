# PROJ-492 Phase 2 Triage Results

Each of the 37 consumer files was inspected and classified A/B/C/D per
[design.md](../design.md). The canonical signature is:

```python
def _make_mock_fleet(
    fleet_id: int = 1,
    owner_id: int = 1,
    location=None,
    speed: float = 5,
    **overrides,
):
    fleet = MagicMock()
    fleet.id = fleet_id
    fleet.owner_id = owner_id
    fleet.location = location
    fleet.speed = float(speed)
    fleet.ships = [MagicMock()]
    fleet.task_forces = []
    fleet.orders = []
    for attr, value in overrides.items():
        setattr(fleet, attr, value)
    return fleet
```

## Summary of categories

| Category | Action | Files |
|----------|--------|-------|
| A — identical signature | delete local, import canonical | 0 |
| B — canonical-superset | delete local, import canonical | 1 |
| C — divergent (rewrite callsites) | rewrite call sites, delete local | 0 |
| D — semantically different (rename) | rename local helper to `_make_<purpose>_fleet` (or similar) | 36 |

The canonical helper is intentionally a *minimal* MagicMock-based fleet (id,
owner_id, location, speed, ships=[one MagicMock], task_forces=[], orders=[]).
Almost every consumer either builds a *real* `Fleet` instance (typed test) or
configures specific protocol surfaces (cargo `resources.*`, `capabilities.*`,
`get_combat_capable_ships`, custom `__str__`, drop-pod state, etc.). Force-merging
them into the canonical would obscure intent and force extensive
test-rewrites, which the design explicitly rejects.

## Per-file classifications

### tests/unit/strategy/validation/test_transfer_drop_pod.py — Category D
- Local: `_make_fleet(pod_capacity=2000.0, pod_mass_used=0.0)`
- Builds a fleet with `resources.get_fleet_pod_capacity` / `pod_mass_used` magic-method returns. Drop-pod specific.
- Action: rename to `_make_drop_pod_fleet`.

### tests/integration/strategy/test_three_empire_battle.py — Category B
- Local: `_make_fleet(fleet_id, owner_id, location, speed=5)`
- Body sets the canonical attrs; only difference is canonical sets `orders=[]` (extra is harmless) and uses `float(speed)`.
- Action: delete local, import canonical, update call sites to pass `fleet_id`, `owner_id`, `location` (positional or kw to match canonical names).

### tests/unit/strategy/combat/test_battle_assembly_third_party_mines.py — Category D
- Local: `_make_fleet(fleet_id, owner_id, location, ships)` with `MagicMock(spec_set=[...])` and explicit `ships` parameter.
- `spec_set` constraint is critical (battle assembly compiler reads exactly these fields). Canonical does not use `spec_set`.
- Action: rename to `_make_combat_fleet`.

### tests/unit/strategy/combat/test_battle_assembly.py — Category D
- Local: `_make_fleet(fleet_id, owner_id, *, ships=())` with `spec_set` constraint.
- Same rationale as above.
- Action: rename to `_make_combat_fleet`.

### tests/integration/strategy/test_replay_capture_e2e.py — Category D
- Local: `_make_fleet(fleet_id, ships)` mock with `task_forces=[]`, ships forwarded, HexCoord-zero location.
- Action: rename to `_make_replay_fleet`.

### tests/integration/strategy/test_fleet_registration_lifecycle.py — Category D
- Local builds a *real* `Fleet` with `make_mock_ship_instance` ships. Real Fleet, not MagicMock.
- Action: rename to `_make_real_fleet`.

### tests/unit/strategy/adapters/test_simulation_adapter_registry_threading.py — Category D
- Local: `_make_fleet(fleet_id, ships)` — assigns ships directly.
- Action: rename to `_make_adapter_fleet`.

### tests/unit/strategy/adapters/test_simulation_adapter.py — Category D
- Same shape as the registry-threading file. Rename to `_make_adapter_fleet`.

### tests/unit/strategy/test_fleet_speed_calculator.py — Category D
- Local: `_make_mock_fleet(ships)` — also stubs `get_ship_instances`.
- Action: rename to `_make_speed_calc_fleet`.

### tests/unit/strategy/data/test_construction_queue_paused_persistence.py — Category D
- Local returns a *real* `Fleet`.
- Action: rename to `_make_real_fleet`.

### tests/unit/strategy/data/test_fleet_cargo_resources.py — Category D
- Local builds a real `Fleet` and appends ships.
- Action: rename to `_make_real_fleet`.

### tests/unit/strategy/fleet/test_fleet_pursuer_tracker.py — Category D
- Local: `make_fleet(fleet_id, location=None)` returns real `Fleet`.
- Action: rename to `_make_pursuer_fleet`.

### tests/unit/strategy/fleet_navigation/test_service_edge_cases.py — Category D
- Local: `_make_mock_fleet(*, location, path, orders, speed, can_use_warp, current_order)` stubs `capabilities.can_use_warp` and optional `get_current_order`.
- Action: rename to `_make_navigation_fleet`.

### tests/unit/strategy/data/test_order_serializer.py — Category D
- Local nested inside a test method, sets `fleet.fleets = []` for empire-like behavior.
- Action: rename to `_make_order_serializer_fleet`.

### tests/unit/strategy/facade/test_strategy_session_facade.py — Category D
- Three local helpers (instance methods); each sets multiple facade-specific stubs.
- Action: rename to `_make_facade_fleet` (all three).

### tests/unit/strategy/engine/test_action_execution_engine_gaps.py — Category D
- Local builds a real `Fleet`.
- Action: rename to `_make_real_fleet`.

### tests/unit/strategy/engine/test_conflict_round_budget.py — Category D
- Local is already a thin wrapper around canonical, but adds `orders=list(orders) if orders else []` semantic via overrides.
- Action: rename to `_make_conflict_round_fleet`.

### tests/unit/strategy/engine/test_action_execution_engine.py — Category D
- Local builds a real `Fleet` with defaults.
- Action: rename to `_make_real_fleet`.

### tests/unit/strategy/engine/test_environmental_hazard_engine.py — Category D
- Local: `_make_fleet(*, fleet_id=1, location=_UNSET, combat_ships=None)` with sentinel.
- Stubs `get_combat_capable_ships`.
- Action: rename to `_make_hazard_fleet`.

### tests/unit/strategy/engine/test_multi_pod_colonization.py — Category D
- Local: `_make_fleet(ships, orders=None)`.
- Action: rename to `_make_pod_colo_fleet`.

### tests/unit/strategy/engine/handlers/test_order_queue_handlers.py — Category D
- Local builds real `Fleet` with `component_registry={}`.
- Action: rename to `_make_real_fleet`.

### tests/unit/strategy/engine/test_issuer_adapter.py — Category D
- Local builds real `Fleet` + appends carrier ship.
- Action: rename to `_make_real_fleet`.

### tests/unit/strategy/engine/handlers/test_movement_handlers.py — Category D
- Local builds real `Fleet` and assigns `_capabilities` SimpleNamespace.
- Action: rename to `_make_real_fleet`.

### tests/unit/strategy/services/test_fleet_cargo_projector.py — Category D
- Local mock with `resources.get_fleet_cargo_*` stubs.
- Action: rename to `_make_cargo_projector_fleet`.

### tests/unit/strategy/engine/test_fleet_transfer_extended.py — Category D
- Local mock with multiple cargo-resource stubs.
- Action: rename to `_make_cargo_transfer_fleet`.

### tests/unit/strategy/engine/order_handlers/conftest.py — Category D
- Local: `make_fleet()` — pytest fixture returning a memoized real Fleet.
- Action: rename to `make_real_fleet_fixture` (fixture name).

### tests/unit/strategy/engine/test_pod_transfer.py — Category D
- Trivial mock with `fleet.ships = ships`.
- Action: rename to `_make_pod_transfer_fleet`.

### tests/unit/strategy/engine/test_resupply_engine.py — Category D
- Local: `_make_mock_fleet(owner_id, location, ships)` returns minimal MagicMock.
- Action: rename to `_make_resupply_fleet`.

### tests/unit/strategy/engine/test_staging_yard_operations.py — Category D
- Local: trivial mock with `ships=ships or []`.
- Action: rename to `_make_staging_fleet`.

### tests/unit/strategy/engine/test_superweapon_event_payloads.py — Category D
- Local builds `MagicMock(spec=Fleet)`, with `loc` default and orders=[].
- Action: rename to `_make_superweapon_fleet`.

### tests/unit/strategy/engine/test_superweapon_order_pop_matrix.py — Category D
- Identical to event_payloads. Rename to `_make_superweapon_fleet`.

### tests/unit/strategy/engine/test_transfer_handler_fleet_to_fleet.py — Category D
- Local with `resources.get_fleet_cargo_*` stubs + `add_order` lambda.
- Action: rename to `_make_transfer_handler_fleet`.

### tests/unit/strategy/services/test_fleet_navigation_mutual_pursuit.py — Category D
- Local stubs `capabilities.can_use_warp` and `get_current_order`.
- Action: rename to `_make_pursuit_fleet`.

### tests/unit/ui/screens/battle_setup/test_fleet_hierarchy_editor.py — Category D
- Local: `_make_fleet()` builds real `Fleet(1, 0, HexCoord(0, 0))`.
- Action: rename to `_make_real_fleet`.

### tests/unit/ui/screens/test_fleet_detail_fmt.py — Category D
- Local: `_make_mock_fleet(...)` with `resources.fuel_endurance` stub and custom `__str__`.
- Action: rename to `_make_detail_fmt_fleet`.

### tests/unit/ui/screens/test_build_queue_screen_lifecycle.py — Category D
- Local: `_make_fleet(fleet_id, hex_coord, name)` with `has_space_shipyard` + `construction_queue` stubs.
- Action: rename to `_make_build_queue_fleet`.

### tests/unit/ui/screens/test_fleet_menu_items.py — Category D
- Local builds a `SimpleNamespace` (not a Fleet/MagicMock) with capabilities for menu-item assertions.
- Action: rename to `_make_menu_fleet`.

## Excluded-list verification (manifest.md "Excluded from Phase 2")

Re-confirmed via grep `def _make_fleet[a-zA-Z_]` — none of the following match the
exact `_make_fleet` / `make_fleet` / `_make_mock_fleet` pattern. All are
correctly excluded:

| File | Sibling helper |
|------|----------------|
| tests/integration/strategy/test_economy_e2e.py | `_make_fleet_with_ship` |
| tests/unit/strategy/engine/test_conflict_resolution_event_replay.py | `_make_fleet_pair` |
| tests/unit/strategy/engine/test_minefield_resolver.py | `_make_fleet_at` |
| tests/unit/strategy/engine/test_production_normalisation.py | `_make_fleet_with_bay` |
| tests/unit/strategy/engine/test_transfer_order.py | `make_fleet_with_cargo_ship` (sibling) |
| tests/unit/strategy/data/test_build_queue_source.py | `_make_fleet_with_yard`, `_make_fleet_without_yard` |
| tests/unit/strategy/data/test_fleet_consume_cargo_symmetry.py | `_make_fleet_with_cargo` |
| tests/unit/strategy/production_engine/test_paused_queue.py | `_make_fleet_with_yard` |
| tests/unit/ui/panels/test_build_queue_controller.py | `_make_fleet_controller_with_galaxy` |
| tests/unit/ui/screens/test_fleet_report_window.py | `_make_fleet_mock`, `_make_fleet_report_window` |
| tests/unit/ui/screens/test_strategy_screen.py | `make_fleet_ops` (nested method) |
| tests/fixtures/strategy_screen_composition.py | (no `def _make_fleet*` definitions found in this file) |
