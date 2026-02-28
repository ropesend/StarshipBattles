"""Integration tests for storm effects during turn processing (PROJ-189 Phase 8).

Tests verify that:
- Fleets in storm hexes take environmental damage during turn processing
- Fleets in storm hexes have fuel drained
- Environmental events are recorded
- Fleet movement speed is reduced in storm hexes
- Fleets outside storms are unaffected
"""

import pytest
import random
from unittest.mock import MagicMock, patch

from game.core.hex_math import HexCoord
from game.strategy.data.galaxy import Galaxy, StarSystem
from game.strategy.data.storm import Storm, StormEffect
from game.strategy.data.fleet import Fleet
from game.strategy.data.empire import Empire
from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.services.area_effect_manager import AreaEffectManager
from game.strategy.services.fleet_speed_calculator import FleetSpeedCalculator


def create_mock_ship_for_storm_test(name: str = "TestShip", owner_id: int = 0):
    """Create a mock ship with known stats for storm integration testing.

    Uses MagicMock to bypass the registry-based stat calculation system.

    Creates a ship with:
    - 100 max HP
    - 10 fuel capacity
    - Strategic movement (for fleet speed)
    """
    from unittest.mock import MagicMock

    ship = MagicMock()
    ship.instance_id = f"test-{name}-{id(name)}"
    ship.name = name
    ship.owner_id = owner_id
    ship.is_alive = True
    ship.is_derelict = False

    # Stats returned by get_calculated_stats
    ship.get_calculated_stats.return_value = {
        'max_hp': 100,
        'mass': 1000,
        'strategic_movement': 200,  # Results in ~5 hex/turn
        'resource_storage': {'fuel': 10},
    }

    # Current HP starts at 100, can be modified
    ship.current_hp = 100

    # Combat capable
    ship.is_combat_capable.return_value = True

    # Resource tracking
    ship._fuel = 10.0

    def get_current_resource(resource_type):
        if resource_type == 'fuel':
            return ship._fuel
        return 0.0

    def consume_resource(resource_type, amount):
        if resource_type == 'fuel' and ship._fuel >= amount:
            ship._fuel -= amount
            return True
        return False

    ship.get_current_resource.side_effect = get_current_resource
    ship.consume_resource.side_effect = consume_resource

    return ship


def create_test_storm(
    location: HexCoord,
    damage_per_tick: float = 0.0,
    fuel_drain_per_tick: float = 0.0,
    strategic_mult: float = 1.0,
    name: str = "Test Storm",
) -> Storm:
    """Create a storm with specified effects at a single hex."""
    return Storm(
        name=name,
        storm_type="ion_storm",
        location=location,
        hex_offsets=frozenset([HexCoord(0, 0)]),  # Single hex at location
        effects=StormEffect(
            damage_per_tick=damage_per_tick,
            fuel_drain_per_tick=fuel_drain_per_tick,
            strategic_mult=strategic_mult,
        ),
    )


class TestTurnProcessingStorms:
    """Integration tests for storm effects during turn processing."""

    def test_fleet_in_storm_takes_environmental_damage(self, fresh_registries):
        """Fleet in storm hex takes environmental damage over full turn."""
        # Create galaxy with system
        galaxy = Galaxy(radius=100)
        system = StarSystem("Alpha", HexCoord(0, 0))
        galaxy.add_system(system)

        # Add storm at hex (10, 0) with 1.0 damage per tick
        # Over 100 ticks, this should deal 1.0 total damage (1/100 per tick)
        storm_location = HexCoord(10, 0)
        storm = create_test_storm(storm_location, damage_per_tick=1.0)
        system.storms.append(storm)
        galaxy.register_zone(system, storm)

        # Create fleet at storm location
        ship = create_mock_ship_for_storm_test("Frigate1")
        initial_hp = ship.current_hp  # 100

        fleet_location = system.global_location + storm_location
        fleet = Fleet(fleet_id=1, owner_id=0, location=fleet_location)
        fleet.add_ship(ship)

        # Create empire with fleet
        empire = Empire(empire_id=0, name="TestEmpire", color=(255, 255, 255))
        empire.fleets.append(fleet)

        # Process full turn (100 ticks)
        engine = TurnEngine(registries=fresh_registries)
        engine.process_turn([empire], galaxy)

        # Verify damage was dealt
        # damage_per_tick=1.0 means 1.0 total per turn (applied as 1/100 per tick)
        expected_damage = 1.0
        actual_damage = initial_hp - ship.current_hp
        assert actual_damage == pytest.approx(expected_damage, abs=0.01), (
            f"Expected ~{expected_damage} damage, got {actual_damage}"
        )

    def test_fleet_in_storm_has_fuel_drained(self, fresh_registries):
        """Fleet in storm hex has fuel drained over full turn."""
        # Create galaxy with system
        galaxy = Galaxy(radius=100)
        system = StarSystem("Alpha", HexCoord(0, 0))
        galaxy.add_system(system)

        # Add storm with fuel drain
        storm_location = HexCoord(10, 0)
        storm = create_test_storm(storm_location, fuel_drain_per_tick=0.5)
        system.storms.append(storm)
        galaxy.register_zone(system, storm)

        # Create fleet at storm location with full fuel
        ship = create_mock_ship_for_storm_test("Frigate1")
        ship._fuel = 10.0  # Set initial fuel (mocked implementation)
        initial_fuel = ship.get_current_resource('fuel')

        fleet_location = system.global_location + storm_location
        fleet = Fleet(fleet_id=1, owner_id=0, location=fleet_location)
        fleet.add_ship(ship)

        # Create empire with fleet
        empire = Empire(empire_id=0, name="TestEmpire", color=(255, 255, 255))
        empire.fleets.append(fleet)

        # Process full turn
        engine = TurnEngine(registries=fresh_registries)
        engine.process_turn([empire], galaxy)

        # Verify fuel was drained
        # fuel_drain_per_tick=0.5 means 0.5 total per turn
        expected_drain = 0.5
        actual_drain = initial_fuel - ship.get_current_resource('fuel')
        assert actual_drain == pytest.approx(expected_drain, abs=0.01), (
            f"Expected ~{expected_drain} fuel drained, got {actual_drain}"
        )

    def test_environmental_events_recorded(self, fresh_registries):
        """Environmental events are recorded during turn processing."""
        # Create galaxy with storm
        galaxy = Galaxy(radius=100)
        system = StarSystem("Alpha", HexCoord(0, 0))
        galaxy.add_system(system)

        storm_location = HexCoord(10, 0)
        storm = create_test_storm(
            storm_location,
            damage_per_tick=0.5,
            fuel_drain_per_tick=0.2,
            name="Ion Storm Alpha"
        )
        system.storms.append(storm)
        galaxy.register_zone(system, storm)

        # Create fleet at storm location
        ship = create_mock_ship_for_storm_test("Frigate1")
        fleet_location = system.global_location + storm_location
        fleet = Fleet(fleet_id=1, owner_id=0, location=fleet_location)
        fleet.add_ship(ship)

        empire = Empire(empire_id=0, name="TestEmpire", color=(255, 255, 255))
        empire.fleets.append(fleet)

        # Process turn
        engine = TurnEngine(registries=fresh_registries)
        engine.process_turn([empire], galaxy)

        # Verify events were recorded
        assert len(engine.last_environmental_events) > 0, "No environmental events recorded"

        # Check event properties
        event = engine.last_environmental_events[0]
        assert event.fleet_id == fleet.id
        assert event.storm_name == "Ion Storm Alpha"
        assert event.damage_dealt > 0
        assert event.fuel_drained > 0

    def test_fleet_outside_storm_unaffected(self, fresh_registries):
        """Fleet outside storm hex takes no damage and no fuel drain."""
        # Create galaxy with storm
        galaxy = Galaxy(radius=100)
        system = StarSystem("Alpha", HexCoord(0, 0))
        galaxy.add_system(system)

        # Storm at (10, 0)
        storm = create_test_storm(HexCoord(10, 0), damage_per_tick=10.0, fuel_drain_per_tick=5.0)
        system.storms.append(storm)
        galaxy.register_zone(system, storm)

        # Fleet at (20, 0) - outside storm
        ship = create_mock_ship_for_storm_test("Frigate1")
        initial_hp = ship.current_hp
        ship._fuel = 10.0  # Set initial fuel (mocked implementation)
        initial_fuel = ship.get_current_resource('fuel')

        fleet_location = system.global_location + HexCoord(20, 0)
        fleet = Fleet(fleet_id=1, owner_id=0, location=fleet_location)
        fleet.add_ship(ship)

        empire = Empire(empire_id=0, name="TestEmpire", color=(255, 255, 255))
        empire.fleets.append(fleet)

        # Process turn
        engine = TurnEngine(registries=fresh_registries)
        engine.process_turn([empire], galaxy)

        # Verify no damage or fuel drain
        assert ship.current_hp == initial_hp, "Ship took damage outside storm"
        assert ship.get_current_resource('fuel') == initial_fuel, "Ship lost fuel outside storm"
        assert len(engine.last_environmental_events) == 0, "Environmental events recorded for fleet outside storm"


class TestFleetSpeedInStorms:
    """Tests for fleet movement speed reduction in storm hexes."""

    def test_fleet_speed_reduced_in_storm(self):
        """Fleet speed is reduced by storm's strategic_mult."""
        # Create ship with known speed
        ship = create_mock_ship_for_storm_test("Frigate1")
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
        fleet.add_ship(ship)

        # Calculate base speed
        base_speed = FleetSpeedCalculator.calculate_fleet_speed(fleet)
        assert base_speed > 0, "Ship should have base speed"

        # Create environmental effects with strategic_mult=0.5
        from game.strategy.services.area_effect_manager import EnvironmentalEffects
        effects = EnvironmentalEffects(
            strategic_mult=0.5,
            in_storm=True,
        )

        # Calculate speed with environment
        modified_speed = FleetSpeedCalculator.calculate_fleet_speed_with_environment(fleet, effects)

        # Speed should be halved
        expected_speed = int(base_speed * 0.5)
        assert modified_speed == expected_speed, (
            f"Expected speed {expected_speed}, got {modified_speed}"
        )

    def test_fleet_speed_unchanged_outside_storm(self):
        """Fleet speed is unchanged when no environmental effects."""
        ship = create_mock_ship_for_storm_test("Frigate1")
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
        fleet.add_ship(ship)

        base_speed = FleetSpeedCalculator.calculate_fleet_speed(fleet)

        # No environmental effects
        modified_speed = FleetSpeedCalculator.calculate_fleet_speed_with_environment(fleet, None)

        assert modified_speed == base_speed, "Speed changed without environmental effects"

    def test_multiple_storms_stack_multiplicatively(self):
        """Overlapping storms reduce speed multiplicatively."""
        # Create galaxy with overlapping storms
        galaxy = Galaxy(radius=100)
        system = StarSystem("Alpha", HexCoord(0, 0))
        galaxy.add_system(system)

        # Two storms at same hex, each with 0.5 strategic_mult
        storm_location = HexCoord(10, 0)
        storm1 = Storm(
            name="Storm 1",
            storm_type="ion_storm",
            location=storm_location,
            hex_offsets=frozenset([HexCoord(0, 0)]),
            effects=StormEffect(strategic_mult=0.5),
        )
        storm2 = Storm(
            name="Storm 2",
            storm_type="dark_nebula",
            location=storm_location,
            hex_offsets=frozenset([HexCoord(0, 0)]),
            effects=StormEffect(strategic_mult=0.5),
        )
        system.storms.extend([storm1, storm2])
        galaxy.register_zone(system, storm1)
        galaxy.register_zone(system, storm2)

        # Query effects
        area_mgr = AreaEffectManager()
        global_hex = system.global_location + storm_location
        effects = area_mgr.get_effects_at_global_hex(galaxy, global_hex)

        # Should be 0.5 * 0.5 = 0.25
        assert effects.strategic_mult == pytest.approx(0.25), (
            f"Expected strategic_mult=0.25, got {effects.strategic_mult}"
        )
