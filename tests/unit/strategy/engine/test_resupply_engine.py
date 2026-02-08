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
    resource_levels: dict = None,
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
    if resource_levels is not None:
        facility.resource_levels = resource_levels.copy()
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
        """ResupplyEngine must raise TypeError if registries is None."""
        with pytest.raises(TypeError):
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
        """Fuel generation should add fuel to facility's resource_levels."""
        registries = _make_mock_registries(fuel_gen_amount=300.0)
        engine = ResupplyEngine(registries=registries)

        facility = _make_fuel_facility(resource_levels={"fuel": 0.0})
        colony = _make_colony(facilities=[facility])
        empire = _make_empire(colonies=[colony])

        events = engine.process_fuel_generation(tick=1, empires=[empire])

        # 300 fuel/turn spread over 100 ticks = 3.0 per tick
        assert facility.resource_levels["fuel"] == pytest.approx(3.0)
        assert len(events) == 1
        assert events[0].fuel_generated == pytest.approx(3.0)
        assert events[0].facility_name == "Fuel Depot"

    def test_generation_accumulates_over_ticks(self):
        """Fuel should accumulate across multiple ticks."""
        registries = _make_mock_registries(fuel_gen_amount=300.0)
        engine = ResupplyEngine(registries=registries)

        facility = _make_fuel_facility(resource_levels={"fuel": 0.0})
        colony = _make_colony(facilities=[facility])
        empire = _make_empire(colonies=[colony])

        # Process 10 ticks
        for tick in range(1, 11):
            engine.process_fuel_generation(tick=tick, empires=[empire])

        # 3.0 per tick * 10 ticks = 30.0
        assert facility.resource_levels["fuel"] == pytest.approx(30.0)

    def test_generation_respects_max_storage(self):
        """Fuel generation should not exceed facility max storage capacity."""
        registries = _make_mock_registries(fuel_tank_amount=500.0, fuel_gen_amount=300.0)
        engine = ResupplyEngine(registries=registries)

        # Start nearly full
        facility = _make_fuel_facility(resource_levels={"fuel": 499.0})
        colony = _make_colony(facilities=[facility])
        empire = _make_empire(colonies=[colony])

        events = engine.process_fuel_generation(tick=1, empires=[empire])

        # Should cap at 500.0 (max), not 502.0
        assert facility.resource_levels["fuel"] == pytest.approx(500.0)
        assert events[0].fuel_generated == pytest.approx(1.0)

    def test_non_operational_facility_no_generation(self):
        """Non-operational facilities should not generate fuel."""
        registries = _make_mock_registries()
        engine = ResupplyEngine(registries=registries)

        facility = _make_fuel_facility(is_operational=False, resource_levels={"fuel": 0.0})
        colony = _make_colony(facilities=[facility])
        empire = _make_empire(colonies=[colony])

        events = engine.process_fuel_generation(tick=1, empires=[empire])

        assert facility.resource_levels["fuel"] == 0.0
        assert len(events) == 0

    def test_facility_without_synthesizer_no_generation(self):
        """Facilities without fuel synthesizer should not generate fuel."""
        registries = _make_mock_registries()
        engine = ResupplyEngine(registries=registries)

        # Facility with fuel tank but no synthesizer
        facility = _make_fuel_facility(has_synthesizer=False, resource_levels={"fuel": 100.0})
        colony = _make_colony(facilities=[facility])
        empire = _make_empire(colonies=[colony])

        events = engine.process_fuel_generation(tick=1, empires=[empire])

        assert facility.resource_levels["fuel"] == 100.0  # Unchanged
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

        f1 = _make_fuel_facility(instance_id="f1", resource_levels={"fuel": 0.0})
        f2 = _make_fuel_facility(instance_id="f2", resource_levels={"fuel": 0.0})
        colony1 = _make_colony(facilities=[f1])
        colony2 = _make_colony(facilities=[f2])
        empire1 = _make_empire(colonies=[colony1])
        empire2 = _make_empire(colonies=[colony2])

        events = engine.process_fuel_generation(tick=1, empires=[empire1, empire2])

        # Each facility gets 200/100 = 2.0 per tick
        assert f1.resource_levels["fuel"] == pytest.approx(2.0)
        assert f2.resource_levels["fuel"] == pytest.approx(2.0)
        assert len(events) == 2

    def test_facility_already_full_no_generation(self):
        """No fuel added when facility is already at max capacity."""
        registries = _make_mock_registries(fuel_tank_amount=500.0, fuel_gen_amount=300.0)
        engine = ResupplyEngine(registries=registries)

        facility = _make_fuel_facility(resource_levels={"fuel": 500.0})
        colony = _make_colony(facilities=[facility])
        empire = _make_empire(colonies=[colony])

        events = engine.process_fuel_generation(tick=1, empires=[empire])

        assert facility.resource_levels["fuel"] == pytest.approx(500.0)
        # No event or event with 0 generated
        if events:
            assert events[0].fuel_generated == pytest.approx(0.0)

    def test_returns_resupply_event_dataclass(self):
        """process_fuel_generation should return ResupplyEvent instances."""
        registries = _make_mock_registries()
        engine = ResupplyEngine(registries=registries)

        facility = _make_fuel_facility(resource_levels={"fuel": 0.0})
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
