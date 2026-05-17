# PROJ-FMS-A Phase 3: VehicleBay substrate + carried_items generalisation

> See [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md) for full design context.

**Goal:** Generalise the existing drop-pod `carried_items` machinery so ships can store design-backed vehicles (with per-instance HP state) in a typed bay. Reuses `Planet.staging_yard` for the planet-side equivalent. **No launch behavior yet** — that lands in PROJ-FMS-B/C/D.

## Tasks

### CarriedVehicle dataclass
- [x] Add a `CarriedVehicle` dataclass (or `TypedDict`) somewhere accessible to both `ShipInstance` and `Planet`. Fields:
  - `design_id: str`
  - `design_data: Dict[str, Any]` — full design snapshot for cold reconstruction
  - `vehicle_type: str` — `"mine" | "fighter" | "satellite"`
  - `mass: int`
  - `current_hp: int` — per-instance HP for fighters/satellites; ignored for mines (one-way)
  - `component_states: Optional[Dict[str, ComponentState]]` — optional per-instance damage; reuses existing `ComponentState` from [`ship_instance.py`](../../../game/strategy/data/ship_instance.py)

### VehicleBayAbility
- [x] Add `VehicleBayAbility` in a new file under [`game/simulation/components/abilities/`](../../../game/simulation/components/abilities/). `AbilityLayer.STRATEGIC`. Additive `capacity_mass: int` per instance. Inputs from component data: `capacity_mass`, optional `allowed_types: List[str]` (defaults to all three).
- [x] Register in [`abilities/__init__.py`](../../../game/simulation/components/abilities/__init__.py).
- [x] Add `bay_capacity_mass` to ship stat aggregation (alongside other STRATEGIC stats). New stat contributor under [`game/simulation/entities/stat_contributors/`](../../../game/simulation/entities/stat_contributors/), mirroring [`launch.py:29-61`](../../../game/simulation/entities/stat_contributors/launch.py#L29).
    - *Audit fix pass (2026-05-16):* `bay_current_mass` is intentionally NOT a design-time stat — it depends on runtime `ShipInstance.carried_items` contents. Exposed as a strategy-layer property `ShipInstance.bay_current_mass` that delegates to `ShipCargoManager.get_vehicle_bay_capacity()`. The dead `ship.bay_current_mass = 0.0` reset on the simulation Ship was removed.
- [x] Add a couple of bay components to [`data/components.json`](../../../data/components.json) at multiple tiers — e.g., `vehicle_bay_small`, `vehicle_bay_medium`, `vehicle_bay_large` — with mass and capacity values. Allowed on `Ship` vehicle types. **(Superseded by Round 4 Obs C — the per-tier components were consolidated to a single `vehicle_bay` whose capacity scales via the `simple_size_mount` modifier and the new `bay_capacity_mult` stat key. See `PROJ-FMS-shared/design.md` Round 4 status update.)**

### ShipInstance generalisation
- [x] At [`ship_instance.py:135-136`](../../../game/strategy/data/ship_instance.py#L135), keep `carried_items: List[Dict[str, Any]]` for backwards compatibility but document that entries can be either drop-pod-shaped or `CarriedVehicle`-shaped. Prefer migrating to a typed `List[CarriedVehicle]` if the change is contained; otherwise add a parallel `carried_vehicles: List[CarriedVehicle]` field.
- [x] Add helpers: `get_carried_vehicles() -> List[CarriedVehicle]`, `get_carried_vehicles_by_type(vehicle_type: str)`, `get_carried_vehicle_mass() -> int`.

### ShipCargoManager
- [x] Extend [`game/strategy/data/ship_cargo_manager.py`](../../../game/strategy/data/ship_cargo_manager.py) with:
  - `load_vehicle(ship: ShipInstance, vehicle: CarriedVehicle) -> bool` — returns False if bay capacity exceeded.
  - `unload_vehicle(ship: ShipInstance, vehicle_index: int) -> CarriedVehicle` — pops and returns.
  - `get_vehicle_bay_capacity(ship: ShipInstance) -> Tuple[int, int]` — `(current_mass, max_mass)`.
- [x] Existing resource-cargo helpers stay untouched.

### Planet.staging_yard
- [x] Verify [`game/strategy/data/planet.py`](../../../game/strategy/data/planet.py) `staging_yard` shape can hold `CarriedVehicle`-shaped entries. Generalise if needed.
- [x] Extend [`transfer_branches.py:128-281`](../../../game/strategy/engine/order_handlers/transfer_branches.py#L128) so the staging-transfer order can move generic carried vehicles between ship bays and planet staging.
- [x] Update [`transfer_view_model.py:264-303`](../../../game/ui/screens/transfer_view_model.py#L264) to render generic carried-vehicle rows.

### DTO updates
- [x] [`fleet_dto.py:96-100,187-218`](../../../game/strategy/facade/dto/fleet_dto.py#L96) — extend FleetInfo carried-items summaries to break down by vehicle type (mine/fighter/satellite) with counts.

### Tests
- [x] Load a fighter design, instantiate a `CarriedVehicle`, load into a ship with a `VehicleBay` — capacity bookkeeping correct.
- [x] Load beyond capacity → returns False.
- [x] Unload → returns the original `CarriedVehicle` with HP preserved.
- [x] Transfer to planet staging and back; design integrity preserved through a round-trip.
- [x] Serialize a ship with carried vehicles, deserialize, verify identity preserved.
    - *Audit fix pass (2026-05-16):* explicit serializer round-trip test added at `tests/unit/strategy/data/test_fms_a_audit_fixes.py::TestCarriedVehicleSerializerRoundtrip` (mixes CarriedVehicle + drop-pod entries; verifies HP and `design_data` survive).

## Verification
- `python Tools/test_sharded/test_sharded.py`
- `pytest tests/unit/strategy/data/ -k 'cargo or bay'`

## Exit criteria
- Ships can carry mine/fighter/satellite designs as bay cargo with per-instance HP.
- Planet staging can hold the same.
- Transfer between ship bay and planet staging works.
- All existing drop-pod tests still pass (backwards compatible).
