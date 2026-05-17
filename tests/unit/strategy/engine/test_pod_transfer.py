"""Tests for drop pod transfer between staging yard and ship carried_items.

Phase 3: Pods are transferred via the TRANSFER order with cargo_type='drop_pod'.
Load: planet.staging_yard -> ship.bay_inventory.pods
Unload: ship.bay_inventory.pods -> planet.staging_yard

PROJ-431 Phase 1d: the ``_make_ship`` helper now mirrors the typed
:class:`BayInventory` substrate the dispatch branches consume. It
projects ``carried_items`` into a typed view at construction time and
on every ``set_bay_inventory(...)`` write-through, so legacy assertions
on ``ship.carried_items`` keep working.
"""
from unittest.mock import MagicMock, patch
from game.strategy.data.bay_inventory import BayInventory, DropPod
from game.strategy.engine.order_handlers.transfer import TransferHandler


def _pod_dict_to_typed(d) -> DropPod:
    if isinstance(d, DropPod):
        return d
    if not isinstance(d, dict):
        return DropPod(design_id="", design_data={}, mass=0.0, payload={})
    return DropPod(
        design_id=str(d.get("design_id", "")),
        design_data=dict(d.get("design_data", {})),
        mass=float(d.get("mass", 0.0)),
        payload={
            k: v for k, v in d.items()
            if k not in {"design_id", "design_data", "mass"}
        },
    )


def _bi_from_carried(items) -> BayInventory:
    return BayInventory(bay=[], pods=[_pod_dict_to_typed(i) for i in items])


def _make_planet(staging_items=None):
    planet = MagicMock()
    planet.staging_yard = list(staging_items or [])
    planet.max_staging_mass = 10000.0
    planet.name = "TestPlanet"

    def remove_from_staging_yard(index):
        if 0 <= index < len(planet.staging_yard):
            return planet.staging_yard.pop(index)
        return None
    planet.remove_from_staging_yard = remove_from_staging_yard

    def add_to_staging_yard(item):
        mass = item.get('mass', 0.0)
        current = sum(i.get('mass', 0.0) for i in planet.staging_yard)
        if planet.max_staging_mass > 0 and current + mass > planet.max_staging_mass:
            return False
        planet.staging_yard.append(item)
        return True
    planet.add_to_staging_yard = add_to_staging_yard

    return planet


def _make_ship(carried_items=None, pod_capacity=2000.0):
    ship = MagicMock()
    ship.carried_items = list(carried_items or [])
    ship.bay_inventory = _bi_from_carried(ship.carried_items)

    # PROJ-425 Phase 6: pod-storage helpers live on ``_cargo_mgr``,
    # not on ``ShipInstance`` directly.
    def _get_pod_storage_used() -> float:
        return sum(i.get('mass', 0.0) for i in ship.carried_items)

    def _can_carry_pod(mass: float) -> bool:
        return (
            pod_capacity > 0
            and _get_pod_storage_used() + mass <= pod_capacity
        )

    cargo_mgr = MagicMock()
    cargo_mgr.get_pod_storage_capacity = MagicMock(return_value=pod_capacity)
    cargo_mgr.get_pod_storage_used = _get_pod_storage_used
    cargo_mgr.can_carry_pod = _can_carry_pod
    ship._cargo_mgr = cargo_mgr

    def _set_bay_inventory(bi: BayInventory) -> None:
        ship.bay_inventory = bi
        ship.carried_items = []
        for cv in bi.bay:
            ship.carried_items.append(cv.to_dict())
        for p in bi.pods:
            entry = {
                "design_id": p.design_id,
                "design_data": p.design_data,
                "mass": p.mass,
            }
            entry.update(p.payload)
            ship.carried_items.append(entry)

    ship.set_bay_inventory = _set_bay_inventory
    return ship


def _make_fleet(ships):
    fleet = MagicMock()
    fleet.ships = ships
    return fleet


def _pod_item(name="Colony Pod", mass=500.0):
    return {'vehicle_type': 'drop_pod', 'name': name, 'mass': mass, 'design_id': 'colony_pod'}


class TestLoadPodFromStagingYard:
    """Test loading pods from planet staging yard to fleet ships."""

    def test_load_single_pod(self):
        planet = _make_planet([_pod_item()])
        ship = _make_ship(pod_capacity=2000.0)
        fleet = _make_fleet([ship])

        proc = TransferHandler()
        loaded = proc._dispatch_drop_pod_load(fleet, planet, amount=1)

        assert loaded == 1
        assert len(ship.carried_items) == 1
        assert len(planet.staging_yard) == 0

    def test_load_all_pods(self):
        planet = _make_planet([_pod_item(), _pod_item(), _pod_item()])
        ship = _make_ship(pod_capacity=2000.0)
        fleet = _make_fleet([ship])

        proc = TransferHandler()
        loaded = proc._dispatch_drop_pod_load(fleet, planet, amount=0)

        assert loaded == 3
        assert len(ship.carried_items) == 3
        assert len(planet.staging_yard) == 0

    def test_load_respects_ship_capacity(self):
        planet = _make_planet([_pod_item(mass=500), _pod_item(mass=500), _pod_item(mass=500)])
        ship = _make_ship(pod_capacity=1000.0)  # Can only fit 2
        fleet = _make_fleet([ship])

        proc = TransferHandler()
        loaded = proc._dispatch_drop_pod_load(fleet, planet, amount=0)

        assert loaded == 2
        assert len(ship.carried_items) == 2
        assert len(planet.staging_yard) == 1

    def test_load_by_name(self):
        planet = _make_planet([
            _pod_item("Small Pod", mass=500),
            _pod_item("Large Pod", mass=2000),
        ])
        ship = _make_ship(pod_capacity=5000.0)
        fleet = _make_fleet([ship])

        proc = TransferHandler()
        loaded = proc._dispatch_drop_pod_load(fleet, planet, pod_name="Small Pod", amount=1)

        assert loaded == 1
        assert ship.carried_items[0]['name'] == "Small Pod"
        assert len(planet.staging_yard) == 1
        assert planet.staging_yard[0]['name'] == "Large Pod"

    def test_load_no_capacity(self):
        planet = _make_planet([_pod_item()])
        ship = _make_ship(pod_capacity=0.0)
        fleet = _make_fleet([ship])

        proc = TransferHandler()
        loaded = proc._dispatch_drop_pod_load(fleet, planet, amount=1)

        assert loaded == 0
        assert len(planet.staging_yard) == 1

    def test_load_distributes_across_ships(self):
        planet = _make_planet([_pod_item(mass=500), _pod_item(mass=500), _pod_item(mass=500)])
        ship1 = _make_ship(pod_capacity=1000.0)  # Fits 2
        ship2 = _make_ship(pod_capacity=1000.0)  # Fits 2
        fleet = _make_fleet([ship1, ship2])

        proc = TransferHandler()
        loaded = proc._dispatch_drop_pod_load(fleet, planet, amount=0)

        assert loaded == 3
        assert len(ship1.carried_items) == 2
        assert len(ship2.carried_items) == 1


class TestUnloadPodToStagingYard:
    """Test unloading pods from fleet ships to planet staging yard."""

    def test_unload_single_pod(self):
        pod = _pod_item()
        ship = _make_ship(carried_items=[pod])
        fleet = _make_fleet([ship])
        planet = _make_planet()

        proc = TransferHandler()
        unloaded = proc._dispatch_drop_pod_unload(fleet, planet, amount=1)

        assert unloaded == 1
        assert len(ship.carried_items) == 0
        assert len(planet.staging_yard) == 1

    def test_unload_all_pods(self):
        ship = _make_ship(carried_items=[_pod_item(), _pod_item()])
        fleet = _make_fleet([ship])
        planet = _make_planet()

        proc = TransferHandler()
        unloaded = proc._dispatch_drop_pod_unload(fleet, planet, amount=0)

        assert unloaded == 2
        assert len(ship.carried_items) == 0
        assert len(planet.staging_yard) == 2

    def test_unload_by_name(self):
        ship = _make_ship(carried_items=[
            _pod_item("Small Pod", mass=500),
            _pod_item("Large Pod", mass=2000),
        ])
        fleet = _make_fleet([ship])
        planet = _make_planet()

        proc = TransferHandler()
        unloaded = proc._dispatch_drop_pod_unload(fleet, planet, pod_name="Large Pod", amount=1)

        assert unloaded == 1
        assert len(ship.carried_items) == 1
        assert ship.carried_items[0]['name'] == "Small Pod"
        assert planet.staging_yard[0]['name'] == "Large Pod"

    def test_unload_respects_staging_capacity(self):
        ship = _make_ship(carried_items=[_pod_item(mass=500), _pod_item(mass=500)])
        fleet = _make_fleet([ship])
        planet = _make_planet()
        planet.max_staging_mass = 500.0  # Only fits 1

        proc = TransferHandler()
        unloaded = proc._dispatch_drop_pod_unload(fleet, planet, amount=0)

        assert unloaded == 1
        assert len(ship.carried_items) == 1
        assert len(planet.staging_yard) == 1
