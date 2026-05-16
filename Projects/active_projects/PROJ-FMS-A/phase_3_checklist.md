# PROJ-FMS-A Phase 3: VehicleBay substrate + carried_items generalisation

> See [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md) for full design context.

**Goal:** Generalise the existing drop-pod `carried_items` machinery so ships can store design-backed vehicles (with per-instance HP state) in a typed bay. Reuses `Planet.staging_yard` for the planet-side equivalent. **No launch behavior yet** — that lands in PROJ-FMS-B/C/D.

## Tasks

### CarriedVehicle dataclass
- [ ] Add a `CarriedVehicle` dataclass (or `TypedDict`) somewhere accessible to both `ShipInstance` and `Planet`. Fields:
  - `design_id: str`
  - `design_data: Dict[str, Any]` — full design snapshot for cold reconstruction
  - `vehicle_type: str` — `"mine" | "fighter" | "satellite"`
  - `mass: int`
  - `current_hp: int` — per-instance HP for fighters/satellites; ignored for mines (one-way)
  - `component_states: Optional[Dict[str, ComponentState]]` — optional per-instance damage; reuses existing `ComponentState` from [`ship_instance.py`](../../../game/strategy/data/ship_instance.py)

### VehicleBayAbility
- [ ] Add `VehicleBayAbility` in a new file under [`game/simulation/components/abilities/`](../../../game/simulation/components/abilities/). `AbilityLayer.STRATEGIC`. Additive `capacity_mass: int` per instance. Inputs from component data: `capacity_mass`, optional `allowed_types: List[str]` (defaults to all three).
- [ ] Register in [`abilities/__init__.py`](../../../game/simulation/components/abilities/__init__.py).
- [ ] Add `bay_capacity_mass` and `bay_current_mass` to ship stat aggregation (alongside other STRATEGIC stats). New stat contributor under [`game/simulation/entities/stat_contributors/`](../../../game/simulation/entities/stat_contributors/), mirroring [`launch.py:29-61`](../../../game/simulation/entities/stat_contributors/launch.py#L29).
- [ ] Add a couple of bay components to [`data/components.json`](../../../data/components.json) at multiple tiers — e.g., `vehicle_bay_small`, `vehicle_bay_medium`, `vehicle_bay_large` — with mass and capacity values. Allowed on `Ship` vehicle types.

### ShipInstance generalisation
- [ ] At [`ship_instance.py:135-136`](../../../game/strategy/data/ship_instance.py#L135), keep `carried_items: List[Dict[str, Any]]` for backwards compatibility but document that entries can be either drop-pod-shaped or `CarriedVehicle`-shaped. Prefer migrating to a typed `List[CarriedVehicle]` if the change is contained; otherwise add a parallel `carried_vehicles: List[CarriedVehicle]` field.
- [ ] Add helpers: `get_carried_vehicles() -> List[CarriedVehicle]`, `get_carried_vehicles_by_type(vehicle_type: str)`, `get_carried_vehicle_mass() -> int`.

### ShipCargoManager
- [ ] Extend [`game/strategy/data/ship_cargo_manager.py`](../../../game/strategy/data/ship_cargo_manager.py) with:
  - `load_vehicle(ship: ShipInstance, vehicle: CarriedVehicle) -> bool` — returns False if bay capacity exceeded.
  - `unload_vehicle(ship: ShipInstance, vehicle_index: int) -> CarriedVehicle` — pops and returns.
  - `get_vehicle_bay_capacity(ship: ShipInstance) -> Tuple[int, int]` — `(current_mass, max_mass)`.
- [ ] Existing resource-cargo helpers stay untouched.

### Planet.staging_yard
- [ ] Verify [`game/strategy/data/planet.py`](../../../game/strategy/data/planet.py) `staging_yard` shape can hold `CarriedVehicle`-shaped entries. Generalise if needed.
- [ ] Extend [`transfer_branches.py:128-281`](../../../game/strategy/engine/order_handlers/transfer_branches.py#L128) so the staging-transfer order can move generic carried vehicles between ship bays and planet staging.
- [ ] Update [`transfer_view_model.py:264-303`](../../../game/ui/screens/transfer_view_model.py#L264) to render generic carried-vehicle rows.

### DTO updates
- [ ] [`fleet_dto.py:96-100,187-218`](../../../game/strategy/facade/dto/fleet_dto.py#L96) — extend FleetInfo carried-items summaries to break down by vehicle type (mine/fighter/satellite) with counts.

### Tests
- [ ] Load a fighter design, instantiate a `CarriedVehicle`, load into a ship with a `VehicleBay` — capacity bookkeeping correct.
- [ ] Load beyond capacity → returns False.
- [ ] Unload → returns the original `CarriedVehicle` with HP preserved.
- [ ] Transfer to planet staging and back; design integrity preserved through a round-trip.
- [ ] Serialize a ship with carried vehicles, deserialize, verify identity preserved.

## Verification
- `python Tools/test_sharded/test_sharded.py`
- `pytest tests/unit/strategy/data/ -k 'cargo or bay'`

## Exit criteria
- Ships can carry mine/fighter/satellite designs as bay cargo with per-instance HP.
- Planet staging can hold the same.
- Transfer between ship bay and planet staging works.
- All existing drop-pod tests still pass (backwards compatible).
