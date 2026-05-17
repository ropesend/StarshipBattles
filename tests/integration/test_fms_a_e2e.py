"""PROJ-FMS-A Phase 5: end-to-end rollup of Phases 1-4.

Pure-Python integration test (no rendering, no save/load round-trip
beyond what's needed for fleet group_kind serialisation). Covers:

  - Designing a mine with Warhead + Hull + SmallTargetingSensor validates.
  - Designing a fighter with Warhead validates (ramming is universal
    after QA 2026-05-16 Obs 1b — no ``RamTarget`` ability gate).
  - Designing a capital ship with VehicleBay + Strategic launch +
    Recover abilities validates.
  - All eight Phase-5 skeleton abilities instantiate cleanly from
    component data and are discoverable via the ABILITY_REGISTRY.
  - Reserved OrderType enum values are present.
  - Mine class total_defense_score reflects signature_bonus.
  - Fleet group_kind discriminator + can_strategic_move invariant.
"""
from __future__ import annotations

import pytest

from game.core.constants import LayerType
from game.core.hex_math import HexCoord
from game.simulation.entities.ship import Ship
from game.simulation.components.abilities import (
    ABILITY_REGISTRY,
    BeamWeaponAbility,
    LaserheadAbility,
    RecoverFightersAbility,
    RecoverSatellitesAbility,
    StrategicFighterLaunchAbility,
    StrategicMineLayerAbility,
    StrategicSatelliteLaunchAbility,
    TacticalFighterLaunchAbility,
    TacticalMineLayerAbility,
    TacticalSatelliteLaunchAbility,
    VehicleBayAbility,
    WarheadAbility,
)
from game.simulation.components.component_loader import create_component
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import OrderType


def _add(ship, comp_id, layer, fresh_registries):
    comp = create_component(comp_id, registries=fresh_registries)
    assert comp is not None, comp_id
    assert ship.add_component(comp, layer), f"{comp_id} -> {layer.name}"
    return comp


class TestPhase1DataValidationE2E:
    def test_mine_design_validates(self, fresh_registries):
        mine = Ship(
            "MineProto", 0, 0, (255, 255, 255),
            ship_class="Mine (Medium)", registries=fresh_registries,
        )
        _add(mine, "hull_mine_medium", LayerType.CORE, fresh_registries)
        _add(mine, "warhead", LayerType.CORE, fresh_registries)
        _add(mine, "small_targeting_sensor", LayerType.CORE, fresh_registries)
        # All three components placed within Mine_Standard CORE whitelist.
        assert len(mine.layers[LayerType.CORE].components) >= 3

    def test_fighter_with_warhead_validates(self, fresh_registries):
        """QA 2026-05-16 Obs 1b: ramming is a universal tactical
        action — a kamikaze fighter only needs a warhead. The previous
        ``ram_target_module`` component was deleted alongside the
        gate."""
        fighter = Ship(
            "RammerProto", 0, 0, (255, 255, 255),
            ship_class="Fighter (Medium)", registries=fresh_registries,
        )
        _add(fighter, "warhead", LayerType.CORE, fresh_registries)
        assert len(fighter.layers[LayerType.CORE].components) >= 1


class TestPhase5AbilitySkeletons:
    def test_all_eight_skeletons_registered(self):
        for key, expected_class in [
            ("StrategicMineLayer", StrategicMineLayerAbility),
            ("StrategicFighterLaunch", StrategicFighterLaunchAbility),
            ("StrategicSatelliteLaunch", StrategicSatelliteLaunchAbility),
            ("TacticalMineLayer", TacticalMineLayerAbility),
            ("TacticalFighterLaunch", TacticalFighterLaunchAbility),
            ("TacticalSatelliteLaunch", TacticalSatelliteLaunchAbility),
            ("RecoverFighters", RecoverFightersAbility),
            ("RecoverSatellites", RecoverSatellitesAbility),
        ]:
            assert ABILITY_REGISTRY[key] is expected_class

    def test_fighter_launch_bay_instantiates(self, fresh_registries):
        comp = create_component(
            "fighter_launch_bay", registries=fresh_registries,
        )
        assert comp is not None
        # QA-C: collocated launch + recovery on a single component.
        strat = comp.get_abilities("StrategicFighterLaunch")
        tact = comp.get_abilities("TacticalFighterLaunch")
        rec = comp.get_abilities("RecoverFighters")
        assert strat and tact and rec
        assert isinstance(strat[0], StrategicFighterLaunchAbility)
        assert isinstance(tact[0], TacticalFighterLaunchAbility)
        assert isinstance(rec[0], RecoverFightersAbility)
        assert strat[0].capacity_per_action == 4
        assert strat[0].cycle_time == 15.0
        assert tact[0].launch_rate_tons_per_sec == 8.0
        assert rec[0].recovery_per_action == 4

    def test_mine_deployer_instantiates(self, fresh_registries):
        comp = create_component("mine_deployer", registries=fresh_registries)
        assert comp is not None
        assert comp.get_abilities("StrategicMineLayer")
        assert comp.get_abilities("TacticalMineLayer")

    def test_satellite_launch_bay_instantiates(self, fresh_registries):
        comp = create_component(
            "satellite_launch_bay", registries=fresh_registries,
        )
        assert comp is not None
        assert comp.get_abilities("StrategicSatelliteLaunch")
        assert comp.get_abilities("TacticalSatelliteLaunch")
        # QA-C: satellite_launch_bay also bundles RecoverSatellites.
        rec = comp.get_abilities("RecoverSatellites")
        assert rec
        assert rec[0].recovery_per_action == 2


class TestOrderTypeReservations:
    def test_reserved_enum_values_exist(self):
        for name in (
            "LAY_MINES",
            "LAUNCH_FIGHTERS",
            "LAUNCH_SATELLITES",
            "RECOVER_FIGHTERS",
            "RECOVER_SATELLITES",
        ):
            assert hasattr(OrderType, name), name


class TestFleetGroupKindIntegration:
    def test_group_kind_rejects_move_at_validation_time(self):
        """Programmatic check — the actual rejection runs through
        BaseCommandHandler._reject_if_non_fleet_group; here we just
        verify can_strategic_move is wired."""
        for kind in ("fighter_group", "satellite_group", "mine_group"):
            f = Fleet(
                fleet_id=1, owner_id=0, location=HexCoord(0, 0),
                group_kind=kind,
            )
            assert not f.can_strategic_move

    def test_signature_bonus_visible_on_mine_class(self, fresh_registries):
        mine = Ship(
            "M", 0, 0, (255, 255, 255),
            ship_class="Mine (Heavy)", registries=fresh_registries,
        )
        mine.recalculate_stats()
        assert mine.signature_bonus > 0


class TestLaserheadFamilyDetection:
    def test_laserhead_is_beam_weapon_ability_subclass(self, fresh_registries):
        """Critical wiring — beam family detection at weapon_registry.py
        relies on isinstance(ability, BeamWeaponAbility)."""
        comp = create_component("laserhead", registries=fresh_registries)
        assert comp is not None
        lasers = comp.get_abilities("Laserhead")
        assert lasers
        assert isinstance(lasers[0], BeamWeaponAbility)


# ---------------------------------------------------------------------------
# PROJ-FMS-A audit fix pass: end-to-end TransferHandler with cargo_type="vehicle"
# ---------------------------------------------------------------------------


def _make_bay_ship_instance(fresh_registries):
    """Construct a ShipInstance whose design has an operational VehicleBay."""
    from game.simulation.entities.ship_serialization import ShipSerializer
    from game.strategy.data.ship_instance import ShipInstance

    ship = Ship(
        "FMS-A Cruiser", 0, 0, (255, 255, 255),
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
        instance_id="fms_a_i1", design_id="fms_a_cruiser",
        name="FMS-A Cruiser", owner_id=0,
        design_data=design_data,
    )
    inst.set_registries(fresh_registries)
    return inst


def _make_planet_with_staging():
    from game.strategy.data.planet import Planet, PlanetType

    planet = Planet(
        name="StagingTestworld", location=HexCoord(0, 0),
        orbit_distance=1.0,
        mass=5.97e24, radius=6.371e6, surface_area=5.1e14,
        density=5515.0, surface_gravity=9.81, surface_pressure=101325.0,
        surface_temperature=288.0, surface_water=0.5,
        tectonic_activity=0.5, magnetic_field=1.0,
        planet_type=PlanetType.CONTINENTAL,
        owner_id=0,
    )
    planet.max_staging_mass = 10000.0
    return planet


class TestTransferHandlerVehicleE2E:
    """End-to-end coverage of ``cargo_type="vehicle"`` through TransferHandler.

    Exercises Fix 1 of the PROJ-FMS-A audit fix pass: the
    ``TransferValidator`` now admits ``"vehicle"`` and the
    ``_dispatch_carried_vehicle_*`` branches actually run.
    """

    def _build_environment(self, fresh_registries):
        from unittest.mock import MagicMock
        from game.strategy.data.carried_vehicle import CarriedVehicle

        planet = _make_planet_with_staging()
        inst = _make_bay_ship_instance(fresh_registries)
        fleet = Fleet(fleet_id=42, owner_id=0, location=HexCoord(0, 0))
        fleet.add_ship(inst)

        # Pre-stage a fighter in the planet staging yard for the LOAD test.
        cv = CarriedVehicle(
            design_id="qs_fighter",
            design_data={"name": "qs_fighter", "ship_class": "Fighter (Small)"},
            vehicle_type="fighter",
            mass=40.0, current_hp=77,
        )
        planet.add_to_staging_yard(cv.to_dict())

        # Minimal galaxy stub that resolves the planet and reports the
        # fleet co-located with it (skip_location_check=True will bypass
        # most of the path, but is_planet() still needs a non-fleet target).
        galaxy = MagicMock()
        galaxy.get_planet_by_id.return_value = planet
        empire = MagicMock()
        empire.id = 0

        return fleet, inst, planet, galaxy, empire, cv

    def test_load_vehicle_end_to_end(self, fresh_registries):
        from game.strategy.data.order_types import Order, OrderType
        from game.strategy.engine.order_handlers.transfer import TransferHandler

        fleet, inst, planet, galaxy, empire, _cv = self._build_environment(
            fresh_registries
        )
        fleet.add_order(
            Order(
                OrderType.TRANSFER,
                {
                    "direction": "load",
                    "cargo_type": "vehicle",
                    "amount": 1,
                    "planet_id": planet.id,
                    "species_id": "qs_fighter",  # design_id discriminator
                },
            )
        )

        handler = TransferHandler()
        result = handler.execute_action_order(fleet, empire, galaxy)
        assert result.success is True
        # Vehicle moved from staging to ship bay.
        assert len(planet.staging_yard) == 0
        carried = inst.get_carried_vehicles()
        assert len(carried) == 1
        assert carried[0].design_id == "qs_fighter"
        assert carried[0].current_hp == 77
        # Bay current mass reflects the loaded vehicle.
        assert inst.bay_current_mass == pytest.approx(40.0)

    def test_unload_vehicle_end_to_end(self, fresh_registries):
        from game.strategy.data.carried_vehicle import CarriedVehicle
        from game.strategy.data.order_types import Order, OrderType
        from game.strategy.engine.order_handlers.transfer import TransferHandler

        fleet, inst, planet, galaxy, empire, _ = self._build_environment(
            fresh_registries
        )
        # Pre-load the ship instead — and clear the planet staging.
        planet.staging_yard.clear()
        mine = CarriedVehicle(
            design_id="qs_mine_small",
            design_data={"name": "qs_mine_small", "ship_class": "Mine (Small)"},
            vehicle_type="mine", mass=5.0, current_hp=3,
        )
        assert inst._cargo_mgr.load_vehicle(mine)
        assert len(inst.get_carried_vehicles()) == 1

        fleet.add_order(
            Order(
                OrderType.TRANSFER,
                {
                    "direction": "unload",
                    "cargo_type": "vehicle",
                    "amount": 1,
                    "planet_id": planet.id,
                    "species_id": "qs_mine_small",
                },
            )
        )

        handler = TransferHandler()
        result = handler.execute_action_order(fleet, empire, galaxy)
        assert result.success is True
        assert len(inst.get_carried_vehicles()) == 0
        # Round-trip: mine entry now lives in the planet staging yard.
        assert len(planet.staging_yard) == 1
        from game.strategy.data.carried_vehicle import CarriedVehicle as CV
        # PROJ-431 Phase 1f: from_any deleted; the staging-yard entry is
        # a dict produced by ``CarriedVehicle.to_dict()`` so use the
        # typed deserialiser directly.
        yard_item = planet.staging_yard[0]
        assert isinstance(yard_item, dict)
        restored = CV.from_dict(yard_item)
        assert restored.design_id == "qs_mine_small"
        assert restored.current_hp == 3
