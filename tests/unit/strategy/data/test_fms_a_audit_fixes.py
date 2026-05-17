"""PROJ-FMS-A audit fix-pass regression tests.

Covers four codex audit fixes:

- Fix 1 (P1): ``TransferValidator`` admits ``cargo_type="vehicle"``.
- Fix 2 (P2): ``ShipInstance.get_pod_storage_used`` excludes
  ``CarriedVehicle``-shaped entries; ``bay_current_mass`` only counts
  vehicles (no cross-bleed with drop pods).
- Fix 3 (P2): ``FleetCapabilityCalculator`` returns ``False`` for
  warp/build on non-``fleet`` ``group_kind``.
- Fix 4 (P2): ``ShipInstanceSerializer`` round-trips ``CarriedVehicle``
  entries with HP and design_data intact.
"""
from __future__ import annotations

import pytest

from game.core.hex_math import HexCoord
from game.simulation.components.component_loader import create_component
from game.core.constants import LayerType
from game.strategy.data.carried_vehicle import CarriedVehicle
from game.strategy.data.fleet import Fleet
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
from game.strategy.data.ship_instance import ShipInstance
from game.strategy.data.ship_instance_serializer import ShipInstanceSerializer
from game.strategy.validation.transfer_validator import TransferValidator


# ---------------------------------------------------------------------------
# Fix 1: TransferValidator admits "vehicle"
# ---------------------------------------------------------------------------


class TestTransferValidatorAcceptsVehicleCargoType:
    def test_vehicle_in_valid_cargo_types(self):
        assert "vehicle" in TransferValidator.VALID_CARGO_TYPES

    def test_invalid_cargo_type_still_rejected(self, fresh_registries):
        # Use a dummy fleet/target — both real objects so protocol checks pass.
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
        # Use any target; INVALID_CARGO_TYPE fires before location checks.
        result = TransferValidator.validate(
            galaxy=None, fleet=fleet, target=fleet,
            cargo_type="not_a_real_cargo", direction="load", amount=1,
            skip_location_check=True,
        )
        assert not result.is_valid
        assert result.error_code == "INVALID_CARGO_TYPE"


# ---------------------------------------------------------------------------
# Fix 2: Pod-storage bleed regression
# ---------------------------------------------------------------------------


def _make_bay_ship_instance(fresh_registries) -> ShipInstance:
    """Build a ShipInstance whose design carries a working VehicleBay."""
    from game.simulation.entities.ship import Ship
    from game.simulation.entities.ship_serialization import ShipSerializer

    ship = Ship(
        "Audit Cruiser", 0, 0, (255, 255, 255),
        ship_class="Cruiser", registries=fresh_registries,
    )
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
    design_data = ShipSerializer.to_dict(ship)
    inst = ShipInstance(
        instance_id="audit_i1", design_id="audit_cruiser",
        name="Audit Cruiser", owner_id=0,
        design_data=design_data,
    )
    inst.set_registries(fresh_registries)
    return inst


class TestPodStorageBleedRegression:
    def test_pod_storage_used_ignores_vehicle_entries(self, fresh_registries):
        inst = _make_bay_ship_instance(fresh_registries)
        # Two drop pods + three fighter CarriedVehicles in carried_items.
        # Drop pods: untyped dicts with mass only.
        inst.carried_items.append({"name": "pod_a", "mass": 7.0})
        inst.carried_items.append({"name": "pod_b", "mass": 11.0})
        for i in range(3):
            cv = CarriedVehicle(
                design_id=f"fighter_{i}",
                design_data={"name": f"fighter_{i}"},
                vehicle_type="fighter",
                mass=25.0, current_hp=80,
            )
            inst.carried_items.append(cv.to_dict())

        # Drop-pod side sees only 7+11=18.
        assert inst.get_pod_storage_used() == pytest.approx(18.0)
        # Bay side sees only 3*25=75.
        assert inst.bay_current_mass == pytest.approx(75.0)

    def test_bay_current_mass_is_zero_with_only_drop_pods(self, fresh_registries):
        inst = _make_bay_ship_instance(fresh_registries)
        inst.carried_items.append({"name": "pod_x", "mass": 50.0})
        assert inst.bay_current_mass == pytest.approx(0.0)
        assert inst.get_pod_storage_used() == pytest.approx(50.0)


# ---------------------------------------------------------------------------
# Fix 3: Capability calculator gates on group_kind
# ---------------------------------------------------------------------------


class TestCapabilityCalculatorOnRealFleet:
    """PROJ-431 Phase 3: Fleet.group_kind is GONE. Every Fleet is a real
    fleet — :meth:`FleetCapabilityCalculator._is_real_fleet` is a
    degenerate no-op that always returns True. The previous "non-fleet
    group_kind kills warp/build" surface is replaced structurally: a
    :class:`FighterWing` / :class:`SatelliteConstellation` /
    :class:`MineGroup` is not a Fleet at all, so it cannot reach this
    calculator.
    """

    def test_real_fleet_is_a_real_fleet(self):
        f = Fleet(fleet_id=102, owner_id=0, location=HexCoord(0, 0))
        calc = FleetCapabilityCalculator(f, component_registry={})
        assert calc._is_real_fleet() is True


# ---------------------------------------------------------------------------
# Fix 4: CarriedVehicle serializer round-trip
# ---------------------------------------------------------------------------


class TestCarriedVehicleSerializerRoundtrip:
    def test_ship_instance_round_trip_preserves_carried_vehicles(self, fresh_registries):
        inst = _make_bay_ship_instance(fresh_registries)
        cv_a = CarriedVehicle(
            design_id="qs_fighter",
            design_data={"name": "qs_fighter", "ship_class": "Fighter (Small)"},
            vehicle_type="fighter", mass=40.0, current_hp=55,
        )
        cv_b = CarriedVehicle(
            design_id="qs_mine_small",
            design_data={"name": "qs_mine_small", "ship_class": "Mine (Small)"},
            vehicle_type="mine", mass=5.0, current_hp=12,
        )
        assert inst._cargo_mgr.load_vehicle(cv_a)
        assert inst._cargo_mgr.load_vehicle(cv_b)
        # Also throw in a drop-pod-shaped entry so we can confirm both
        # shapes survive the round trip. PROJ-431 Phase 1f: pods live in
        # the typed ``bay_inventory.pods`` slot directly.
        from game.strategy.data.bay_inventory import DropPod
        inst.bay_inventory.pods.append(DropPod(
            design_id="pod_a", design_data={}, mass=13.0,
            payload={"name": "pod_a"},
        ))

        data = ShipInstanceSerializer.to_dict(inst)
        restored = ShipInstanceSerializer.from_dict(data)
        restored.set_registries(fresh_registries)

        carried = restored.get_carried_vehicles()
        assert len(carried) == 2
        # Order is not guaranteed; compare by design_id.
        by_id = {cv.design_id: cv for cv in carried}
        assert by_id["qs_fighter"].current_hp == 55
        assert by_id["qs_fighter"].mass == pytest.approx(40.0)
        assert by_id["qs_fighter"].design_data == cv_a.design_data
        assert by_id["qs_mine_small"].vehicle_type == "mine"
        assert by_id["qs_mine_small"].current_hp == 12
        # Drop-pod entry survived too. PROJ-431 Phase 1f: pods live in
        # the typed ``bay_inventory.pods`` slot, distinct from vehicles
        # in ``.bay``; ``carried_items`` is the legacy projection. Probe
        # the typed slot directly.
        assert any(
            pod.payload.get("name") == "pod_a" or pod.design_id == "pod_a"
            for pod in restored.bay_inventory.pods
        )
