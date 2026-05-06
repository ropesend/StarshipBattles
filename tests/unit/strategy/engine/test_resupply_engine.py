"""
Tests for ResupplyEngine - fuel generation at planetary facilities.

PROJ-74 Phase 3: TDD tests for ResupplyEngine.process_fuel_generation().
Covers strict DI, fuel generation, max storage capping, non-operational
facilities, and facilities without synthesizers.
"""
import pytest
from unittest.mock import MagicMock

from game.strategy.data.planet import PlanetaryFacility
from game.strategy.engine.resupply_engine import ResupplyEngine, ResupplyEvent
from game.core.exceptions import ValidationException


# ===========================================================================
# Fixtures / Helpers
# ===========================================================================

def _make_mock_registries(fuel_tank_amount: float = 500.0, fuel_gen_amount: float = 300.0):
    """Create mock registries with fuel_tank and fuel_synthesizer components."""
    registries = MagicMock()

    fuel_tank_comp = MagicMock()
    fuel_tank_comp.abilities = {
        "ResourceStorage": [{"resource": "fuel", "amount": fuel_tank_amount}],
    }

    fuel_synth_comp = MagicMock()
    fuel_synth_comp.abilities = {
        "ResourceGeneration": [{"resource": "fuel", "amount": fuel_gen_amount}],
    }

    energy_gen_comp = MagicMock()
    energy_gen_comp.abilities = {
        "ResourceGeneration": [{"resource": "energy", "amount": 50}],
    }

    def get_component(comp_id):
        if comp_id == "fuel_tank":
            return fuel_tank_comp
        if comp_id == "fuel_synthesizer":
            return fuel_synth_comp
        if comp_id == "energy_generator":
            return energy_gen_comp
        return None

    registries.components.get = get_component
    return registries


def _make_fuel_facility(
    instance_id: str = "fuel-001",
    fuel_storage_amount: float = 500.0,
    has_synthesizer: bool = True,
    is_operational: bool = True,
    consumable_levels: dict = None,
) -> PlanetaryFacility:
    """Create a facility with fuel tank and optional fuel synthesizer."""
    components = []
    if has_synthesizer:
        components.append({"id": "fuel_synthesizer"})
    components.append({"id": "fuel_tank"})
    facility = PlanetaryFacility(
        instance_id=instance_id,
        design_id="fuel_depot",
        name="Fuel Depot",
        design_data={"layers": {"hull": components}},
        is_operational=is_operational,
    )
    if consumable_levels is not None:
        facility.consumable_levels = consumable_levels.copy()
    return facility


def _make_energy_facility(instance_id: str = "energy-001") -> PlanetaryFacility:
    """Create a facility with energy generator only (no fuel synthesizer)."""
    return PlanetaryFacility(
        instance_id=instance_id,
        design_id="power_plant",
        name="Power Plant",
        design_data={"layers": {"hull": [{"id": "energy_generator"}]}},
        is_operational=True,
    )


def _make_colony(facilities=None):
    """Create a mock colony (Planet) with facilities."""
    colony = MagicMock()
    colony.facilities = facilities or []
    colony.name = "Test Colony"
    return colony


def _make_empire(colonies=None):
    """Create a mock empire with colonies."""
    empire = MagicMock()
    empire.colonies = colonies or []
    empire.id = 0
    return empire


# ===========================================================================
# Task 3.1: Strict DI
# ===========================================================================

class TestResupplyEngineDI:
    """ResupplyEngine must enforce strict dependency injection."""

    def test_engine_requires_registries_strict_di(self):
        """ResupplyEngine must raise ValidationException if registries is None."""
        with pytest.raises(ValidationException):
            ResupplyEngine(registries=None)

    def test_engine_accepts_valid_registries(self):
        """ResupplyEngine should accept valid registries."""
        registries = _make_mock_registries()
        engine = ResupplyEngine(registries=registries)
        assert engine is not None


# ===========================================================================
# Task 3.1: Fuel Generation Tests
# ===========================================================================

class TestProcessFuelGeneration:
    """Tests for ResupplyEngine.process_fuel_generation()."""

    def test_process_fuel_generation_adds_to_facility(self):
        """Fuel generation should add fuel to facility's consumable_levels."""
        registries = _make_mock_registries(fuel_gen_amount=300.0)
        engine = ResupplyEngine(registries=registries)

        facility = _make_fuel_facility(consumable_levels={"fuel": 0.0})
        colony = _make_colony(facilities=[facility])
        empire = _make_empire(colonies=[colony])

        events = engine.process_fuel_generation(tick=1, empires=[empire])

        # 300 fuel/turn spread over 100 ticks = 3.0 per tick
        assert facility.consumable_levels["fuel"] == pytest.approx(3.0)
        assert len(events) == 1
        assert events[0].fuel_generated == pytest.approx(3.0)
        assert events[0].facility_name == "Fuel Depot"

    def test_generation_accumulates_over_ticks(self):
        """Fuel should accumulate across multiple ticks."""
        registries = _make_mock_registries(fuel_gen_amount=300.0)
        engine = ResupplyEngine(registries=registries)

        facility = _make_fuel_facility(consumable_levels={"fuel": 0.0})
        colony = _make_colony(facilities=[facility])
        empire = _make_empire(colonies=[colony])

        # Process 10 ticks
        for tick in range(1, 11):
            engine.process_fuel_generation(tick=tick, empires=[empire])

        # 3.0 per tick * 10 ticks = 30.0
        assert facility.consumable_levels["fuel"] == pytest.approx(30.0)

    def test_generation_respects_max_storage(self):
        """Fuel generation should not exceed facility max storage capacity."""
        registries = _make_mock_registries(fuel_tank_amount=500.0, fuel_gen_amount=300.0)
        engine = ResupplyEngine(registries=registries)

        # Start nearly full
        facility = _make_fuel_facility(consumable_levels={"fuel": 499.0})
        colony = _make_colony(facilities=[facility])
        empire = _make_empire(colonies=[colony])

        events = engine.process_fuel_generation(tick=1, empires=[empire])

        # Should cap at 500.0 (max), not 502.0
        assert facility.consumable_levels["fuel"] == pytest.approx(500.0)
        assert events[0].fuel_generated == pytest.approx(1.0)

    def test_non_operational_facility_no_generation(self):
        """Non-operational facilities should not generate fuel."""
        registries = _make_mock_registries()
        engine = ResupplyEngine(registries=registries)

        facility = _make_fuel_facility(is_operational=False, consumable_levels={"fuel": 0.0})
        colony = _make_colony(facilities=[facility])
        empire = _make_empire(colonies=[colony])

        events = engine.process_fuel_generation(tick=1, empires=[empire])

        assert facility.consumable_levels["fuel"] == 0.0
        assert len(events) == 0

    def test_facility_without_synthesizer_no_generation(self):
        """Facilities without fuel synthesizer should not generate fuel."""
        registries = _make_mock_registries()
        engine = ResupplyEngine(registries=registries)

        # Facility with fuel tank but no synthesizer
        facility = _make_fuel_facility(has_synthesizer=False, consumable_levels={"fuel": 100.0})
        colony = _make_colony(facilities=[facility])
        empire = _make_empire(colonies=[colony])

        events = engine.process_fuel_generation(tick=1, empires=[empire])

        assert facility.consumable_levels["fuel"] == 100.0  # Unchanged
        assert len(events) == 0

    def test_energy_generator_does_not_produce_fuel(self):
        """Facility with energy generator (not fuel) should not produce fuel."""
        registries = _make_mock_registries()
        engine = ResupplyEngine(registries=registries)

        facility = _make_energy_facility()
        colony = _make_colony(facilities=[facility])
        empire = _make_empire(colonies=[colony])

        events = engine.process_fuel_generation(tick=1, empires=[empire])

        assert len(events) == 0

    def test_multiple_empires_multiple_facilities(self):
        """Fuel generation processes all empires and all facilities."""
        registries = _make_mock_registries(fuel_gen_amount=200.0)
        engine = ResupplyEngine(registries=registries)

        f1 = _make_fuel_facility(instance_id="f1", consumable_levels={"fuel": 0.0})
        f2 = _make_fuel_facility(instance_id="f2", consumable_levels={"fuel": 0.0})
        colony1 = _make_colony(facilities=[f1])
        colony2 = _make_colony(facilities=[f2])
        empire1 = _make_empire(colonies=[colony1])
        empire2 = _make_empire(colonies=[colony2])

        events = engine.process_fuel_generation(tick=1, empires=[empire1, empire2])

        # Each facility gets 200/100 = 2.0 per tick
        assert f1.consumable_levels["fuel"] == pytest.approx(2.0)
        assert f2.consumable_levels["fuel"] == pytest.approx(2.0)
        assert len(events) == 2

    def test_facility_already_full_no_generation(self):
        """No fuel added when facility is already at max capacity."""
        registries = _make_mock_registries(fuel_tank_amount=500.0, fuel_gen_amount=300.0)
        engine = ResupplyEngine(registries=registries)

        facility = _make_fuel_facility(consumable_levels={"fuel": 500.0})
        colony = _make_colony(facilities=[facility])
        empire = _make_empire(colonies=[colony])

        events = engine.process_fuel_generation(tick=1, empires=[empire])

        assert facility.consumable_levels["fuel"] == pytest.approx(500.0)
        # No event or event with 0 generated
        if events:
            assert events[0].fuel_generated == pytest.approx(0.0)

    def test_returns_resupply_event_dataclass(self):
        """process_fuel_generation should return ResupplyEvent instances."""
        registries = _make_mock_registries()
        engine = ResupplyEngine(registries=registries)

        facility = _make_fuel_facility(consumable_levels={"fuel": 0.0})
        colony = _make_colony(facilities=[facility])
        empire = _make_empire(colonies=[colony])

        events = engine.process_fuel_generation(tick=1, empires=[empire])

        assert len(events) == 1
        event = events[0]
        assert isinstance(event, ResupplyEvent)
        assert event.facility_name == "Fuel Depot"
        assert event.fuel_generated > 0
        assert event.fuel_transferred == 0.0
        assert event.fleet_id is None

    def test_empty_empires_returns_empty(self):
        """Empty empires list should return empty events."""
        registries = _make_mock_registries()
        engine = ResupplyEngine(registries=registries)

        events = engine.process_fuel_generation(tick=1, empires=[])
        assert events == []

    def test_empire_with_no_colonies_returns_empty(self):
        """Empire with no colonies should return empty events."""
        registries = _make_mock_registries()
        engine = ResupplyEngine(registries=registries)

        empire = _make_empire(colonies=[])
        events = engine.process_fuel_generation(tick=1, empires=[empire])
        assert events == []

    def test_colony_with_no_facilities_returns_empty(self):
        """Colony with no facilities should return empty events."""
        registries = _make_mock_registries()
        engine = ResupplyEngine(registries=registries)

        colony = _make_colony(facilities=[])
        empire = _make_empire(colonies=[colony])
        events = engine.process_fuel_generation(tick=1, empires=[empire])
        assert events == []


# ===========================================================================
# Fleet Resupply Helpers
# ===========================================================================

def _make_mock_ship(
    fuel_capacity: float = 500.0,
    current_fuel: float = 500.0,
    fuel_cost_per_hex: float = 5.0,
    combat_capable: bool = True,
):
    """Create a mock ShipInstance with controlled fuel properties."""
    ship = MagicMock()
    ship.is_combat_capable.return_value = combat_capable
    ship.get_resource_capacity.return_value = fuel_capacity
    ship.get_all_resource_costs_per_hex.return_value = {"fuel": fuel_cost_per_hex}

    # Track resupply calls and update current_fuel accordingly
    _fuel_state = {"current": current_fuel}

    def _get_current_resource(resource_name):
        if resource_name == 'fuel':
            return _fuel_state["current"]
        return 0.0

    ship.get_current_resource.side_effect = _get_current_resource

    def _resupply(resource_name, amount):
        if resource_name != 'fuel':
            return 0.0
        space = fuel_capacity - _fuel_state["current"]
        actual = min(amount, space)
        _fuel_state["current"] += actual
        return actual

    ship.resupply.side_effect = _resupply
    return ship


def _make_mock_fleet(owner_id: int = 0, location=None, ships=None):
    """Create a mock Fleet with specified ships and location."""
    fleet = MagicMock()
    fleet.id = 1
    fleet.owner_id = owner_id
    fleet.location = location or HexCoord(0, 0)
    fleet.ships = ships or []
    return fleet


def _make_mock_galaxy(planets_at_hex=None):
    """Create a mock Galaxy with spatial lookup."""
    galaxy = MagicMock()
    _planets_map = planets_at_hex or {}

    def _get_planets(global_hex):
        return _planets_map.get(global_hex, [])

    galaxy.get_planets_at_global_hex.side_effect = _get_planets
    return galaxy


def _make_planet_with_fuel(
    owner_id: int = 0,
    fuel_level: float = 100.0,
    fuel_storage_amount: float = 500.0,
    fuel_gen_amount: float = 300.0,
):
    """Create a Planet with a fuel facility that has stored fuel."""
    registries = _make_mock_registries(
        fuel_tank_amount=fuel_storage_amount,
        fuel_gen_amount=fuel_gen_amount,
    )
    facility = _make_fuel_facility(
        consumable_levels={"fuel": fuel_level},
    )
    planet = MagicMock()
    planet.owner_id = owner_id
    planet.facilities = [facility]
    return planet, facility, registries


# Need HexCoord for fleet locations
from game.core.hex_math import HexCoord


# ===========================================================================
# Fuel Distribution Edge Cases
# ===========================================================================

class TestFuelDistributionEdges:
    """Direct coverage for ResupplyEngine._calculate_fuel_distribution()."""

    def test_fuel_distribution_ignores_non_combat_ships(self):
        registries = _make_mock_registries()
        engine = ResupplyEngine(registries=registries)
        ship = _make_mock_ship(combat_capable=False)
        fleet = _make_mock_fleet(ships=[ship])

        distribution = engine._calculate_fuel_distribution(fleet, available_fuel=100.0)

        assert distribution == {}
        ship.get_all_resource_costs_per_hex.assert_not_called()

    def test_fuel_distribution_skips_zero_total_fuel_cost(self):
        registries = _make_mock_registries()
        engine = ResupplyEngine(registries=registries)
        ship = _make_mock_ship(
            fuel_capacity=500.0,
            current_fuel=0.0,
            fuel_cost_per_hex=0.0,
        )
        fleet = _make_mock_fleet(ships=[ship])

        distribution = engine._calculate_fuel_distribution(fleet, available_fuel=100.0)

        assert distribution == {}
        ship.resupply.assert_not_called()

    def test_fuel_distribution_zero_available_returns_empty_for_empty_ships(self):
        registries = _make_mock_registries()
        engine = ResupplyEngine(registries=registries)
        ship = _make_mock_ship(
            fuel_capacity=500.0,
            current_fuel=0.0,
            fuel_cost_per_hex=5.0,
        )
        fleet = _make_mock_fleet(ships=[ship])

        distribution = engine._calculate_fuel_distribution(fleet, available_fuel=0.0)

        assert distribution == {}

    def test_fuel_distribution_caps_target_at_ship_capacity(self):
        registries = _make_mock_registries()
        engine = ResupplyEngine(registries=registries)
        capped = _make_mock_ship(
            fuel_capacity=50.0,
            current_fuel=0.0,
            fuel_cost_per_hex=10.0,
        )
        roomy = _make_mock_ship(
            fuel_capacity=500.0,
            current_fuel=0.0,
            fuel_cost_per_hex=10.0,
        )
        fleet = _make_mock_fleet(ships=[capped, roomy])

        distribution = engine._calculate_fuel_distribution(fleet, available_fuel=200.0)

        assert distribution[capped] == pytest.approx(50.0)
        assert distribution[roomy] == pytest.approx(100.0)

    def test_fuel_distribution_omits_ships_already_at_target_range(self):
        registries = _make_mock_registries()
        engine = ResupplyEngine(registries=registries)
        full = _make_mock_ship(
            fuel_capacity=100.0,
            current_fuel=100.0,
            fuel_cost_per_hex=10.0,
        )
        empty = _make_mock_ship(
            fuel_capacity=100.0,
            current_fuel=0.0,
            fuel_cost_per_hex=10.0,
        )
        fleet = _make_mock_fleet(ships=[full, empty])

        distribution = engine._calculate_fuel_distribution(fleet, available_fuel=100.0)

        assert full not in distribution
        assert distribution[empty] == pytest.approx(100.0)


# ===========================================================================
# Fuel Transfer Edge Cases
# ===========================================================================

class TestFuelTransferEdges:
    """Direct coverage for ResupplyEngine._transfer_fuel()."""

    def test_transfer_fuel_withdraws_only_actual_ship_acceptance(self):
        registries = _make_mock_registries()
        engine = ResupplyEngine(registries=registries)
        ship = MagicMock()
        ship.resupply.return_value = 25.0
        facility = MagicMock()

        total = engine._transfer_fuel({ship: 100.0}, available=100.0, facility=facility)

        ship.resupply.assert_called_once_with("fuel", 100.0)
        facility.withdraw_fuel.assert_called_once_with(25.0)
        assert total == pytest.approx(25.0)

    def test_transfer_fuel_caps_later_ships_at_remaining_available(self):
        registries = _make_mock_registries()
        engine = ResupplyEngine(registries=registries)
        first = MagicMock()
        second = MagicMock()
        first.resupply.return_value = 80.0
        second.resupply.return_value = 20.0
        facility = MagicMock()

        total = engine._transfer_fuel(
            {first: 80.0, second: 80.0},
            available=100.0,
            facility=facility,
        )

        first.resupply.assert_called_once_with("fuel", 80.0)
        second.resupply.assert_called_once_with("fuel", 20.0)
        facility.withdraw_fuel.assert_called_once_with(100.0)
        assert total == pytest.approx(100.0)

    def test_transfer_fuel_breaks_when_available_exhausted(self):
        registries = _make_mock_registries()
        engine = ResupplyEngine(registries=registries)
        first = MagicMock()
        second = MagicMock()
        first.resupply.return_value = 30.0
        facility = MagicMock()

        total = engine._transfer_fuel(
            {first: 30.0, second: 10.0},
            available=30.0,
            facility=facility,
        )

        first.resupply.assert_called_once_with("fuel", 30.0)
        second.resupply.assert_not_called()
        facility.withdraw_fuel.assert_called_once_with(30.0)
        assert total == pytest.approx(30.0)


# ===========================================================================
# Task 4.1: Fleet Resupply Tests
# ===========================================================================

class TestFleetResupply:
    """Tests for ResupplyEngine.process_fleet_resupply()."""

    def test_fleet_at_planet_receives_fuel(self):
        """Fleet at same location as planet with fuel facility gets resupplied."""
        registries = _make_mock_registries()
        engine = ResupplyEngine(registries=registries)

        # Ship with half fuel
        ship = _make_mock_ship(fuel_capacity=500.0, current_fuel=250.0, fuel_cost_per_hex=5.0)
        location = HexCoord(3, 4)
        fleet = _make_mock_fleet(owner_id=0, location=location, ships=[ship])

        # Planet with fuel at same location
        facility = _make_fuel_facility(consumable_levels={"fuel": 300.0})
        planet = MagicMock()
        planet.owner_id = 0
        planet.facilities = [facility]

        galaxy = _make_mock_galaxy(planets_at_hex={location: [planet]})

        empire = MagicMock()
        empire.fleets = [fleet]

        events = engine.process_fleet_resupply(tick=1, empires=[empire], galaxy=galaxy)

        # Ship should have been resupplied
        ship.resupply.assert_called()
        assert len(events) >= 1
        assert events[0].fuel_transferred > 0
        assert events[0].fleet_id == fleet.id

    def test_fleet_not_at_planet_no_fuel(self):
        """Fleet at different location than planet gets no fuel."""
        registries = _make_mock_registries()
        engine = ResupplyEngine(registries=registries)

        ship = _make_mock_ship(fuel_capacity=500.0, current_fuel=250.0)
        fleet_loc = HexCoord(3, 4)
        fleet = _make_mock_fleet(owner_id=0, location=fleet_loc, ships=[ship])

        # Planet at different location
        facility = _make_fuel_facility(consumable_levels={"fuel": 300.0})
        planet = MagicMock()
        planet.owner_id = 0
        planet.facilities = [facility]

        planet_loc = HexCoord(10, 10)
        galaxy = _make_mock_galaxy(planets_at_hex={planet_loc: [planet]})

        empire = MagicMock()
        empire.fleets = [fleet]

        events = engine.process_fleet_resupply(tick=1, empires=[empire], galaxy=galaxy)

        # No planets at fleet location -> no resupply
        ship.resupply.assert_not_called()
        assert len(events) == 0

    def test_owner_fleet_priority_over_others(self):
        """Owner's fleet gets fuel; other empire's fleet does not."""
        registries = _make_mock_registries()
        engine = ResupplyEngine(registries=registries)

        location = HexCoord(5, 5)

        # Owner's fleet (empire 0)
        owner_ship = _make_mock_ship(fuel_capacity=500.0, current_fuel=200.0)
        owner_fleet = _make_mock_fleet(owner_id=0, location=location, ships=[owner_ship])

        # Other empire's fleet (empire 1)
        other_ship = _make_mock_ship(fuel_capacity=500.0, current_fuel=200.0)
        other_fleet = _make_mock_fleet(owner_id=1, location=location, ships=[other_ship])

        # Planet owned by empire 0
        facility = _make_fuel_facility(consumable_levels={"fuel": 300.0})
        planet = MagicMock()
        planet.owner_id = 0
        planet.facilities = [facility]

        galaxy = _make_mock_galaxy(planets_at_hex={location: [planet]})

        empire_0 = MagicMock()
        empire_0.fleets = [owner_fleet]
        empire_1 = MagicMock()
        empire_1.fleets = [other_fleet]

        events = engine.process_fleet_resupply(
            tick=1, empires=[empire_0, empire_1], galaxy=galaxy
        )

        # Owner fleet gets fuel
        owner_ship.resupply.assert_called()
        # Other fleet does NOT get fuel
        other_ship.resupply.assert_not_called()

    def test_fuel_distributed_to_equalize_range(self):
        """Fuel is distributed to equalize effective range across fleet ships.

        PROJ-323 Task 5.18: hardcoded expected values (200.0 / 40.0).
        Derivation (validated against ResupplyEngine 2026-05-03):
          - 240 fuel available; combined cost 10+2=12/hex -> max equalized
            range = 240/12 = 20 hexes.
          - Ship A allocation = cost(10) * range(20) = 200.0
          - Ship B allocation = cost(2)  * range(20) =  40.0
        Total: 240.0. Updating these values without re-validating production
        is a regression signal — the engine has changed the equalization rule.
        """
        registries = _make_mock_registries()
        engine = ResupplyEngine(registries=registries)

        location = HexCoord(0, 0)

        # Ship A: high consumption, empty (cost=10/hex, capacity=500, current=0)
        ship_a = _make_mock_ship(fuel_capacity=500.0, current_fuel=0.0, fuel_cost_per_hex=10.0)
        # Ship B: low consumption, empty (cost=2/hex, capacity=200, current=0)
        ship_b = _make_mock_ship(fuel_capacity=200.0, current_fuel=0.0, fuel_cost_per_hex=2.0)

        fleet = _make_mock_fleet(owner_id=0, location=location, ships=[ship_a, ship_b])

        facility = _make_fuel_facility(consumable_levels={"fuel": 240.0})
        planet = MagicMock()
        planet.owner_id = 0
        planet.facilities = [facility]

        galaxy = _make_mock_galaxy(planets_at_hex={location: [planet]})

        empire = MagicMock()
        empire.fleets = [fleet]

        engine.process_fleet_resupply(tick=1, empires=[empire], galaxy=galaxy)

        # Hardcoded reference values; see docstring for derivation.
        ship_a.resupply.assert_called()
        ship_b.resupply.assert_called()

        a_call_args = ship_a.resupply.call_args
        assert a_call_args[0][0] == 'fuel'
        assert a_call_args[0][1] == pytest.approx(200.0)

        b_call_args = ship_b.resupply.call_args
        assert b_call_args[0][0] == 'fuel'
        assert b_call_args[0][1] == pytest.approx(40.0)

    def test_tanker_ships_partially_fueled(self):
        """With limited fuel, tanker (high capacity) gets less while combat ships get priority via equalization."""
        registries = _make_mock_registries()
        engine = ResupplyEngine(registries=registries)

        location = HexCoord(0, 0)

        # Combat ship: cost=10/hex, capacity=100, current=0
        combat_ship = _make_mock_ship(
            fuel_capacity=100.0, current_fuel=0.0, fuel_cost_per_hex=10.0
        )
        # Tanker: cost=1/hex, capacity=1000, current=0
        tanker = _make_mock_ship(
            fuel_capacity=1000.0, current_fuel=0.0, fuel_cost_per_hex=1.0
        )

        fleet = _make_mock_fleet(
            owner_id=0, location=location, ships=[combat_ship, tanker]
        )

        # 110 fuel available: cost 10+1=11/hex -> max_range = 110/11 = 10 hexes
        # Combat ship target: 10*10 = 100 (exactly at capacity)
        # Tanker target: 1*10 = 10 (well below 1000 capacity)
        facility = _make_fuel_facility(consumable_levels={"fuel": 110.0})
        planet = MagicMock()
        planet.owner_id = 0
        planet.facilities = [facility]

        galaxy = _make_mock_galaxy(planets_at_hex={location: [planet]})

        empire = MagicMock()
        empire.fleets = [fleet]

        events = engine.process_fleet_resupply(tick=1, empires=[empire], galaxy=galaxy)

        # Combat ship gets full fill (100 fuel)
        combat_call = combat_ship.resupply.call_args
        assert combat_call[0][1] == pytest.approx(100.0)

        # Tanker gets only 10 fuel (partially fueled)
        tanker_call = tanker.resupply.call_args
        assert tanker_call[0][1] == pytest.approx(10.0)

    def test_facility_with_no_fuel_no_transfer(self):
        """Facility with empty fuel storage transfers nothing."""
        registries = _make_mock_registries()
        engine = ResupplyEngine(registries=registries)

        location = HexCoord(0, 0)
        ship = _make_mock_ship(fuel_capacity=500.0, current_fuel=200.0)
        fleet = _make_mock_fleet(owner_id=0, location=location, ships=[ship])

        # Empty facility
        facility = _make_fuel_facility(consumable_levels={"fuel": 0.0})
        planet = MagicMock()
        planet.owner_id = 0
        planet.facilities = [facility]

        galaxy = _make_mock_galaxy(planets_at_hex={location: [planet]})

        empire = MagicMock()
        empire.fleets = [fleet]

        events = engine.process_fleet_resupply(tick=1, empires=[empire], galaxy=galaxy)

        ship.resupply.assert_not_called()
        assert len(events) == 0
