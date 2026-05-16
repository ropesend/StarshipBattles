"""PROJ-FMS-D audit Fix 2 — per-bay typed capacity allocation.

Codex's mid-project PROJ-FMS-D audit identified that the shipped
:class:`game.strategy.data.ship_cargo_manager.ShipCargoManager` enforced
typed-bay filtering as a ship-wide UNION:

  * :meth:`_allowed_vehicle_types` unions every active
    :class:`VehicleBayAbility`'s ``allowed_types``.
  * :meth:`can_accept_vehicle` only checks the aggregate
    ``bay_capacity_mass`` from the cached design stats.
  * :meth:`load_vehicle` appends without recording which bay accepted
    the vehicle.

Effect: a carrier with one fighter-only bay (capacity 250) plus one
satellite-only bay (capacity 800) accepted 1050 mass of fighters because
the ship-wide allowed-types union accepted fighters and the aggregate
capacity check covered the total. The fighter-only / satellite-only
separation existed in the bay component data (PROJ-FMS-D Phase 1) but
the cargo manager never enforced it per-bay.

These tests pin the corrected per-bay behaviour.
"""
from __future__ import annotations

import pytest

from game.core.constants import LayerType
from game.simulation.components.component_loader import create_component
from game.simulation.entities.ship import Ship
from game.strategy.data.carried_vehicle import CarriedVehicle
from game.strategy.data.ship_instance import ShipInstance


def _ship_instance_from(layers_components, fresh_registries) -> ShipInstance:
    """Build a real ShipInstance whose design has the listed components.

    ``layers_components`` is a list of ``(component_id, LayerType)`` pairs.
    A minimal-but-operational backbone is always added so the bay is
    considered active.
    """
    ship = Ship(
        "Test Ship", 0, 0, (255, 255, 255),
        ship_class="Cruiser", registries=fresh_registries,
    )
    # Operational backbone.
    backbone = [
        ("bridge", LayerType.CORE),
        ("crew_quarters", LayerType.INNER),
        ("life_support", LayerType.INNER),
        ("generator", LayerType.INNER),
    ]
    for comp_id, layer in backbone + list(layers_components):
        comp = create_component(comp_id, registries=fresh_registries)
        assert comp is not None, comp_id
        assert ship.add_component(comp, layer), comp_id

    from game.simulation.entities.ship_serialization import ShipSerializer
    design_data = ShipSerializer.to_dict(ship)

    inst = ShipInstance(
        instance_id="carrier_1", design_id="test_carrier",
        name="Test Carrier", owner_id=0,
        design_data=design_data,
    )
    inst.set_registries(fresh_registries)
    return inst


def _fighter(mass: float = 100.0) -> CarriedVehicle:
    return CarriedVehicle(
        design_id="fighter_alpha",
        design_data={"name": "fighter_alpha"},
        vehicle_type="fighter",
        mass=mass, current_hp=50,
    )


def _satellite(mass: float = 100.0) -> CarriedVehicle:
    return CarriedVehicle(
        design_id="sat_alpha",
        design_data={"name": "sat_alpha"},
        vehicle_type="satellite",
        mass=mass, current_hp=50,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestMixedBayCarrier:
    """Per-bay allocation enforcement on a fighter-only + satellite-only
    mixed-bay carrier."""

    def _mixed_bay_carrier(self, fresh_registries) -> ShipInstance:
        # ``fighter_bay_small`` -> 250 fighter-only, ``satellite_bay_small`` -> 300 satellite-only.
        return _ship_instance_from(
            [
                ("fighter_bay_small", LayerType.INNER),
                ("satellite_bay_small", LayerType.INNER),
            ],
            fresh_registries,
        )

    def test_fighter_only_bay_does_not_accept_satellite_within_its_capacity(
        self, fresh_registries
    ):
        """A satellite must NOT consume fighter-only bay capacity.

        Pre-fix bug: the ship-wide union accepted satellite (because the
        satellite_bay_small accepts it) and the aggregate capacity check
        covered the sum (250 + 300 = 550). After consuming the satellite
        bay (300), a 250-mass satellite would have been loaded into the
        "free" fighter-only bay space. The corrected behaviour rejects
        the second satellite: the satellite bay is full, the fighter
        bay rejects the type.
        """
        inst = self._mixed_bay_carrier(fresh_registries)
        # Load a 250-mass satellite — fits in the satellite bay (300).
        assert inst._cargo_mgr.load_vehicle(_satellite(mass=250.0))
        # Load a 200-mass satellite — would need 200 free in a
        # satellite-accepting bay. Satellite bay has 50 free; fighter
        # bay has 250 free but cannot accept satellites. Must reject.
        ok = inst._cargo_mgr.load_vehicle(_satellite(mass=200.0))
        assert ok is False, (
            "Audit Fix 2: satellite must NOT consume fighter-only bay "
            "capacity even though aggregate ship capacity has room. "
            "The current behaviour (union+aggregate) wrongly accepts."
        )

    def test_satellite_only_bay_does_not_accept_fighter_within_its_capacity(
        self, fresh_registries
    ):
        """Symmetric: fighters must NOT consume satellite-only bay capacity."""
        inst = self._mixed_bay_carrier(fresh_registries)
        # Fill the fighter bay (250).
        assert inst._cargo_mgr.load_vehicle(_fighter(mass=250.0))
        # 200-mass fighter cannot use the satellite bay's 300 capacity.
        ok = inst._cargo_mgr.load_vehicle(_fighter(mass=200.0))
        assert ok is False, (
            "Audit Fix 2: fighter must NOT consume satellite-only bay "
            "capacity even though aggregate ship capacity has room."
        )

    def test_each_type_fills_its_own_bay_independently(self, fresh_registries):
        """Fighter and satellite bays accept their own types up to capacity."""
        inst = self._mixed_bay_carrier(fresh_registries)
        # Load right up to fighter-bay capacity.
        assert inst._cargo_mgr.load_vehicle(_fighter(mass=200.0))
        assert inst._cargo_mgr.load_vehicle(_fighter(mass=50.0))
        # Now no more fighters fit.
        assert inst._cargo_mgr.load_vehicle(_fighter(mass=1.0)) is False
        # But satellites still load up to their bay's capacity.
        assert inst._cargo_mgr.load_vehicle(_satellite(mass=300.0))
        assert inst._cargo_mgr.load_vehicle(_satellite(mass=1.0)) is False

    def test_unload_returns_capacity_to_the_correct_bay(self, fresh_registries):
        """After unloading a fighter, the fighter bay regains capacity."""
        inst = self._mixed_bay_carrier(fresh_registries)
        assert inst._cargo_mgr.load_vehicle(_fighter(mass=250.0))
        assert inst._cargo_mgr.load_vehicle(_satellite(mass=300.0))
        # Both bays full.
        assert inst._cargo_mgr.load_vehicle(_fighter(mass=1.0)) is False
        assert inst._cargo_mgr.load_vehicle(_satellite(mass=1.0)) is False
        # Unload the fighter. Fighter bay should have 250 free again.
        inst._cargo_mgr.unload_vehicle(0)
        assert inst._cargo_mgr.load_vehicle(_fighter(mass=200.0))
        # Satellite bay is still full.
        assert inst._cargo_mgr.load_vehicle(_satellite(mass=1.0)) is False


class TestUniversalBay:
    """The universal vehicle_bay_* path keeps working — both types share
    the same bay with a single pool of capacity."""

    def test_universal_bay_accepts_both_types_to_aggregate_cap(
        self, fresh_registries
    ):
        # vehicle_bay_medium = capacity_mass 750, allowed = [mine, fighter, satellite].
        inst = _ship_instance_from(
            [("vehicle_bay_medium", LayerType.INNER)],
            fresh_registries,
        )
        assert inst._cargo_mgr.load_vehicle(_fighter(mass=400.0))
        assert inst._cargo_mgr.load_vehicle(_satellite(mass=300.0))
        # 50 free in the universal bay.
        assert inst._cargo_mgr.load_vehicle(_fighter(mass=60.0)) is False
        assert inst._cargo_mgr.load_vehicle(_satellite(mass=50.0))


class TestSingleTypedBay:
    """Single-bay carriers still gate by type correctly."""

    def test_fighter_only_carrier_rejects_satellite(self, fresh_registries):
        inst = _ship_instance_from(
            [("fighter_bay_small", LayerType.INNER)],
            fresh_registries,
        )
        assert inst._cargo_mgr.load_vehicle(_fighter(mass=200.0))
        assert inst._cargo_mgr.load_vehicle(_satellite(mass=1.0)) is False
