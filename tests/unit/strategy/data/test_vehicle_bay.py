"""PROJ-FMS-A Phase 3: VehicleBay substrate + CarriedVehicle dataclass.

Verifies:
- CarriedVehicle field round-trip via to_dict/from_dict
- VehicleBayAbility instantiates from component data with capacity_mass
- ShipCargoManager.load_vehicle/unload_vehicle bookkeeping is correct
- Planet.staging_yard round-trip preserves CarriedVehicle identity
"""
from __future__ import annotations

import pytest

from game.strategy.data.carried_vehicle import CarriedVehicle
from game.simulation.components.abilities.vehicle_bay import VehicleBayAbility
from game.simulation.components.component_loader import create_component


class TestCarriedVehicleDataclass:
    def _sample(self, mass: float = 25.0) -> CarriedVehicle:
        return CarriedVehicle(
            design_id="qs_fighter",
            design_data={"name": "qs_fighter", "ship_class": "Fighter (Small)"},
            vehicle_type="fighter",
            mass=mass,
            current_hp=80,
        )

    def test_invalid_type_raises(self):
        with pytest.raises(ValueError):
            CarriedVehicle(
                design_id="x", design_data={}, vehicle_type="cruiser",
                mass=1, current_hp=1,
            )

    def test_to_dict_from_dict_roundtrip(self):
        cv = self._sample()
        d = cv.to_dict()
        cv2 = CarriedVehicle.from_dict(d)
        assert cv2.design_id == cv.design_id
        assert cv2.vehicle_type == "fighter"
        assert cv2.mass == cv.mass
        assert cv2.current_hp == cv.current_hp
        assert cv2.design_data == cv.design_data

    # PROJ-431 Phase 1f: ``CarriedVehicle.from_any`` was deleted (its
    # only purpose was bridging the mixed-shape ``carried_items`` list).
    # The previous shape-discrimination tests were a unit test on the
    # discriminator itself. The replacement contract — explicit
    # isinstance + dict-shape probe against ``VALID_VEHICLE_TYPES`` then
    # ``from_dict(...)`` — is exercised by the production sites that
    # adopted it (issuer_adapter, fms_shared, attack_processor) and by
    # the deletion-guard test in ``test_phase_1f_deletion_guard.py``.


class TestVehicleBayAbility:
    def test_instantiates_from_component(self, fresh_registries):
        comp = create_component("vehicle_bay", registries=fresh_registries)
        assert comp is not None
        bays = [a for a in comp.ability_instances if isinstance(a, VehicleBayAbility)]
        assert len(bays) == 1
        assert bays[0].capacity_mass == 250.0
        assert "mine" in bays[0].allowed_types

    def test_accepts_helper(self, fresh_registries):
        comp = create_component("vehicle_bay", registries=fresh_registries)
        bays = [a for a in comp.ability_instances if isinstance(a, VehicleBayAbility)]
        bay = bays[0]
        assert bay.accepts("fighter")
        assert bay.accepts("mine")
        assert not bay.accepts("complex")

    def test_size_mount_scales_capacity_mass(self, fresh_registries):
        """QA-C: VehicleBay.capacity_mass scales linearly with
        ``simple_size_mount`` via the ``bay_capacity_mult`` binding.
        """
        comp_1x = create_component("vehicle_bay", registries=fresh_registries)
        assert comp_1x is not None
        comp_1x.add_modifier("simple_size_mount", 1.0)

        comp_2x = create_component("vehicle_bay", registries=fresh_registries)
        assert comp_2x is not None
        comp_2x.add_modifier("simple_size_mount", 2.0)

        bay_1x = [
            a for a in comp_1x.ability_instances
            if isinstance(a, VehicleBayAbility)
        ][0]
        bay_2x = [
            a for a in comp_2x.ability_instances
            if isinstance(a, VehicleBayAbility)
        ][0]
        assert bay_2x.capacity_mass == bay_1x.capacity_mass * 2.0


class TestShipCargoManagerVehicles:
    """Round-trip a CarriedVehicle through a real ShipInstance bay."""

    def _make_ship_instance(self, fresh_registries):
        """Create a ShipInstance whose design carries one operational
        vehicle bay.

        The bay needs C&C + crew to count as operational, so we wire
        bridge + crew_quarters + life_support + generator alongside it.
        """
        from game.simulation.entities.ship import Ship
        from game.core.constants import LayerType
        from game.strategy.data.ship_instance import ShipInstance

        ship = Ship(
            "Test Ship", 0, 0, (255, 255, 255),
            ship_class="Cruiser", registries=fresh_registries,
        )
        # Wire a minimal-but-operational backbone.
        # QA-C: the test now uses the consolidated ``vehicle_bay`` at
        # its base scale (250 capacity_mass). The prior "_medium" tier
        # is replaced by ``simple_size_mount`` scaling on the same
        # component; size-scaling is covered separately in
        # ``test_size_mount_scales_capacity_mass``.
        for comp_id, layer in (
            ("bridge", LayerType.CORE),
            ("crew_quarters", LayerType.INNER),
            ("life_support", LayerType.INNER),
            ("generator", LayerType.INNER),
            ("vehicle_bay", LayerType.INNER),
        ):
            comp = create_component(comp_id, registries=fresh_registries)
            assert comp is not None, comp_id
            assert ship.add_component(comp, layer), comp_id

        # Pull design dict via ShipSerializer (same path as ShipInstanceBridge).
        from game.simulation.entities.ship_serialization import ShipSerializer
        design_data = ShipSerializer.to_dict(ship)

        inst = ShipInstance(
            instance_id="i1", design_id="test_cruiser",
            name="Test Cruiser", owner_id=0,
            design_data=design_data,
        )
        inst.set_registries(fresh_registries)
        return inst

    def test_load_vehicle_succeeds_within_capacity(self, fresh_registries):
        inst = self._make_ship_instance(fresh_registries)
        cv = CarriedVehicle(
            design_id="qs_fighter",
            design_data={"name": "qs_fighter"},
            vehicle_type="fighter",
            mass=50,
            current_hp=20,
        )
        ok = inst._cargo_mgr.load_vehicle(cv)
        assert ok
        assert len(inst.bay_inventory.bay) == 1
        current, max_mass = inst._cargo_mgr.get_vehicle_bay_capacity()
        assert current == 50
        assert max_mass >= 250  # vehicle_bay base capacity is 250 mass

    def test_load_vehicle_rejects_beyond_capacity(self, fresh_registries):
        inst = self._make_ship_instance(fresh_registries)
        # Try to load 300 mass into a 250-mass bay -> rejected.
        cv = CarriedVehicle(
            design_id="qs_heavy_fighter",
            design_data={"name": "qs_heavy_fighter"},
            vehicle_type="fighter",
            mass=300,
            current_hp=100,
        )
        ok = inst._cargo_mgr.load_vehicle(cv)
        assert ok is False
        assert len(inst.bay_inventory.bay) == 0

    def test_unload_vehicle_returns_original(self, fresh_registries):
        inst = self._make_ship_instance(fresh_registries)
        cv = CarriedVehicle(
            design_id="qs_fighter",
            design_data={"name": "qs_fighter"},
            vehicle_type="fighter",
            mass=50,
            current_hp=33,
        )
        inst._cargo_mgr.load_vehicle(cv)
        popped = inst._cargo_mgr.unload_vehicle(0)
        assert popped.design_id == "qs_fighter"
        assert popped.current_hp == 33
        assert len(inst.bay_inventory.bay) == 0

    def test_get_carried_vehicles_filters_by_type(self, fresh_registries):
        inst = self._make_ship_instance(fresh_registries)
        for vt, name, mass in [
            ("fighter", "f1", 25),
            ("fighter", "f2", 25),
            ("mine", "m1", 5),
            ("satellite", "s1", 50),
        ]:
            cv = CarriedVehicle(
                design_id=name, design_data={"name": name},
                vehicle_type=vt, mass=mass, current_hp=10,
            )
            assert inst._cargo_mgr.load_vehicle(cv)
        fighters = inst._cargo_mgr.get_carried_vehicles_by_type("fighter")
        assert len(fighters) == 2
        mines = inst._cargo_mgr.get_carried_vehicles_by_type("mine")
        assert len(mines) == 1


class TestPlanetStagingYardRoundtrip:
    def test_staging_yard_holds_carried_vehicle_dict(self, fresh_registries):
        from game.strategy.data.planet import Planet, PlanetType
        from game.core.hex_math import HexCoord

        planet = Planet(
            name="Testplanet", location=HexCoord(0, 0),
            orbit_distance=1.0,
            mass=5.97e24, radius=6.371e6, surface_area=5.1e14,
            density=5515.0, surface_gravity=9.81, surface_pressure=101325.0,
            surface_temperature=288.0, surface_water=0.5,
            tectonic_activity=0.5, magnetic_field=1.0,
            planet_type=PlanetType.CONTINENTAL,
        )
        planet.max_staging_mass = 1000.0

        cv = CarriedVehicle(
            design_id="mine_small_design",
            design_data={"name": "mine_small_design"},
            vehicle_type="mine",
            mass=5, current_hp=4,
        )
        ok = planet.add_to_staging_yard(cv.to_dict())
        assert ok
        # PROJ-450 Phase 3: dict input is promoted to a typed
        # ``CarriedVehicle`` on the way in; the public ``staging_yard``
        # property hands out the typed entry directly.
        item = planet.staging_yard[0]
        assert isinstance(item, CarriedVehicle)
        assert item.vehicle_type == "mine"
        assert item.current_hp == 4
