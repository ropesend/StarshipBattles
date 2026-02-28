"""Tests for EnvironmentalHazardEngine (PROJ-189 Phase 5).

Test environmental damage and fuel drain processing during the 100-tick turn loop.
"""

import pytest
from unittest.mock import MagicMock, patch
from dataclasses import dataclass

from game.strategy.engine.environmental_hazard_engine import (
    EnvironmentalHazardEngine,
    EnvironmentalEvent,
)
from game.strategy.services.area_effect_manager import AreaEffectManager, EnvironmentalEffects
from game.core.hex_math import HexCoord


def create_mock_ship(instance_id="ship-001", max_hp=100, current_fuel=100.0):
    """Create a mock ship with fuel and HP."""
    ship = MagicMock()
    ship.instance_id = instance_id
    ship.name = f"Test Ship {instance_id}"
    ship.current_hp = None  # Full HP by default
    ship.is_alive = True
    ship.is_derelict = False
    ship.is_combat_capable.return_value = True
    ship.get_current_resource.return_value = current_fuel
    ship.consume_resource.return_value = True
    ship.get_calculated_stats.return_value = {"max_hp": max_hp}
    return ship


@pytest.fixture
def mock_ship():
    """Create a mock ship with fuel and HP."""
    return create_mock_ship()


@pytest.fixture
def mock_fleet(mock_ship):
    """Create a mock fleet with one ship."""
    fleet = MagicMock()
    fleet.id = 1
    fleet.location = HexCoord(0, 0)
    fleet.ships = [mock_ship]
    fleet.get_combat_capable_ships.return_value = [mock_ship]
    return fleet


@pytest.fixture
def mock_empire(mock_fleet):
    """Create a mock empire with one fleet."""
    empire = MagicMock()
    empire.id = 0
    empire.fleets = [mock_fleet]
    return empire


@pytest.fixture
def mock_galaxy():
    """Create a mock galaxy."""
    galaxy = MagicMock()
    return galaxy


@pytest.fixture
def area_effect_manager():
    """Create a real AreaEffectManager (with mock galaxy)."""
    return AreaEffectManager()


class TestEnvironmentalEvent:
    """Test EnvironmentalEvent dataclass."""

    def test_create_environmental_event(self):
        """Test creating an EnvironmentalEvent."""
        event = EnvironmentalEvent(
            fleet_id=1,
            storm_name="Ion Storm",
            damage_dealt=5.0,
            fuel_drained=2.0,
            tick=50,
        )
        assert event.fleet_id == 1
        assert event.storm_name == "Ion Storm"
        assert event.damage_dealt == 5.0
        assert event.fuel_drained == 2.0
        assert event.tick == 50


class TestEnvironmentalHazardEngine:
    """Test EnvironmentalHazardEngine."""

    def test_engine_creation_with_default_area_effect_manager(self):
        """Test creating engine with default AreaEffectManager."""
        engine = EnvironmentalHazardEngine()
        assert engine._area_effect_manager is not None

    def test_engine_creation_with_injected_area_effect_manager(self, area_effect_manager):
        """Test creating engine with injected AreaEffectManager."""
        engine = EnvironmentalHazardEngine(area_effect_manager=area_effect_manager)
        assert engine._area_effect_manager is area_effect_manager

    def test_fleet_outside_storm_unaffected(self, mock_empire, mock_galaxy):
        """Test that fleets outside storms are unaffected."""
        # Mock area_effect_manager returns no effects
        mock_area_manager = MagicMock()
        mock_area_manager.get_effects_at_global_hex.return_value = EnvironmentalEffects()

        engine = EnvironmentalHazardEngine(area_effect_manager=mock_area_manager)
        events = engine.process_environmental_tick(50, [mock_empire], mock_galaxy)

        # No events should be generated
        assert len(events) == 0

    def test_fleet_in_storm_takes_damage(self, mock_empire, mock_galaxy, mock_fleet, mock_ship):
        """Test that fleets in storm take damage over multiple ticks."""
        # Storm with 10 damage per tick (becomes 0.1 per tick after /100)
        storm_effects = EnvironmentalEffects(
            in_storm=True,
            damage_per_tick=10.0,  # 10 per turn = 0.1 per tick
            fuel_drain_per_tick=0.0,
            storm_names=["Ion Storm"],
        )

        mock_area_manager = MagicMock()
        mock_area_manager.get_effects_at_global_hex.return_value = storm_effects

        engine = EnvironmentalHazardEngine(area_effect_manager=mock_area_manager)

        # Process tick 1
        events = engine.process_environmental_tick(1, [mock_empire], mock_galaxy)

        # Should generate one event
        assert len(events) == 1
        event = events[0]
        assert event.fleet_id == mock_fleet.id
        assert event.storm_name == "Ion Storm"
        assert event.damage_dealt == pytest.approx(0.1)  # 10 / 100
        assert event.tick == 1

    def test_fleet_in_storm_fuel_drain_accumulates(self, mock_empire, mock_galaxy, mock_fleet, mock_ship):
        """Test that fuel drain accumulates over ticks."""
        # Storm with 5 fuel drain per tick (becomes 0.05 per tick after /100)
        storm_effects = EnvironmentalEffects(
            in_storm=True,
            damage_per_tick=0.0,
            fuel_drain_per_tick=5.0,  # 5 per turn = 0.05 per tick
            storm_names=["Nebula"],
        )

        mock_area_manager = MagicMock()
        mock_area_manager.get_effects_at_global_hex.return_value = storm_effects

        engine = EnvironmentalHazardEngine(area_effect_manager=mock_area_manager)
        events = engine.process_environmental_tick(25, [mock_empire], mock_galaxy)

        # Should generate one event
        assert len(events) == 1
        event = events[0]
        assert event.fuel_drained == pytest.approx(0.05)  # 5 / 100
        assert event.damage_dealt == 0.0

        # Verify consume_resource was called
        mock_ship.consume_resource.assert_called_once()

    def test_fleet_in_storm_with_zero_damage_takes_no_damage(self, mock_empire, mock_galaxy, mock_fleet, mock_ship):
        """Test that fleets in storm with damage_per_tick=0 take no damage."""
        storm_effects = EnvironmentalEffects(
            in_storm=True,
            damage_per_tick=0.0,
            fuel_drain_per_tick=0.0,
            storm_names=["Calm Nebula"],
        )

        mock_area_manager = MagicMock()
        mock_area_manager.get_effects_at_global_hex.return_value = storm_effects

        engine = EnvironmentalHazardEngine(area_effect_manager=mock_area_manager)
        events = engine.process_environmental_tick(50, [mock_empire], mock_galaxy)

        # Should still generate event for tracking, but with 0 damage/drain
        assert len(events) == 1
        assert events[0].damage_dealt == 0.0
        assert events[0].fuel_drained == 0.0

    def test_multiple_fleets_in_same_storm_independent(self, mock_empire, mock_galaxy, mock_ship):
        """Test multiple fleets in same storm take independent damage."""
        # Create second fleet with second ship
        mock_ship2 = create_mock_ship("ship-002", max_hp=80, current_fuel=50.0)

        mock_fleet2 = MagicMock()
        mock_fleet2.id = 2
        mock_fleet2.location = HexCoord(0, 0)  # Same location
        mock_fleet2.ships = [mock_ship2]
        mock_fleet2.get_combat_capable_ships.return_value = [mock_ship2]

        mock_empire.fleets.append(mock_fleet2)

        storm_effects = EnvironmentalEffects(
            in_storm=True,
            damage_per_tick=10.0,
            fuel_drain_per_tick=2.0,
            storm_names=["Ion Storm"],
        )

        mock_area_manager = MagicMock()
        mock_area_manager.get_effects_at_global_hex.return_value = storm_effects

        engine = EnvironmentalHazardEngine(area_effect_manager=mock_area_manager)
        events = engine.process_environmental_tick(1, [mock_empire], mock_galaxy)

        # Should generate events for both fleets
        assert len(events) == 2
        fleet_ids = {e.fleet_id for e in events}
        assert fleet_ids == {1, 2}

        # Each fleet should have been processed independently
        for event in events:
            assert event.damage_dealt == pytest.approx(0.1)  # 10 / 100
            assert event.fuel_drained == pytest.approx(0.02)  # 2 / 100

    def test_damage_distributed_across_ships(self, mock_empire, mock_galaxy, mock_fleet, mock_ship):
        """Test that damage is distributed across ships in fleet."""
        # Add second ship to fleet
        mock_ship2 = create_mock_ship("ship-002", max_hp=80, current_fuel=80.0)

        mock_fleet.ships.append(mock_ship2)
        mock_fleet.get_combat_capable_ships.return_value = [mock_ship, mock_ship2]

        storm_effects = EnvironmentalEffects(
            in_storm=True,
            damage_per_tick=20.0,  # 0.2 per tick total
            fuel_drain_per_tick=4.0,  # 0.04 per tick per ship
            storm_names=["Plasma Storm"],
        )

        mock_area_manager = MagicMock()
        mock_area_manager.get_effects_at_global_hex.return_value = storm_effects

        engine = EnvironmentalHazardEngine(area_effect_manager=mock_area_manager)
        events = engine.process_environmental_tick(1, [mock_empire], mock_galaxy)

        # One event per fleet
        assert len(events) == 1
        event = events[0]

        # Total damage for fleet (distributed, but totaled)
        assert event.damage_dealt == pytest.approx(0.2)
        # Fuel drain applied to each ship
        assert event.fuel_drained == pytest.approx(0.08)  # 0.04 per ship * 2 ships

    def test_multiple_empires_processed(self, mock_galaxy):
        """Test that multiple empires are all processed."""
        # Create two empires with fleets at different locations
        mock_ship1 = create_mock_ship("ship-001")

        empire1 = MagicMock()
        empire1.id = 0
        fleet1 = MagicMock()
        fleet1.id = 1
        fleet1.location = HexCoord(0, 0)
        fleet1.ships = [mock_ship1]
        fleet1.get_combat_capable_ships.return_value = [mock_ship1]
        empire1.fleets = [fleet1]

        mock_ship2 = create_mock_ship("ship-002")

        empire2 = MagicMock()
        empire2.id = 1
        fleet2 = MagicMock()
        fleet2.id = 2
        fleet2.location = HexCoord(5, 5)  # Different location
        fleet2.ships = [mock_ship2]
        fleet2.get_combat_capable_ships.return_value = [mock_ship2]
        empire2.fleets = [fleet2]

        storm_effects = EnvironmentalEffects(
            in_storm=True,
            damage_per_tick=10.0,
            storm_names=["Cosmic Storm"],
        )

        mock_area_manager = MagicMock()
        mock_area_manager.get_effects_at_global_hex.return_value = storm_effects

        engine = EnvironmentalHazardEngine(area_effect_manager=mock_area_manager)
        events = engine.process_environmental_tick(1, [empire1, empire2], mock_galaxy)

        # Both fleets should have events
        assert len(events) == 2
        fleet_ids = {e.fleet_id for e in events}
        assert fleet_ids == {1, 2}

    def test_empty_fleet_generates_no_event(self, mock_empire, mock_galaxy, mock_fleet):
        """Test that empty fleets don't generate events."""
        mock_fleet.ships = []
        mock_fleet.get_combat_capable_ships.return_value = []

        storm_effects = EnvironmentalEffects(
            in_storm=True,
            damage_per_tick=10.0,
            storm_names=["Ion Storm"],
        )

        mock_area_manager = MagicMock()
        mock_area_manager.get_effects_at_global_hex.return_value = storm_effects

        engine = EnvironmentalHazardEngine(area_effect_manager=mock_area_manager)
        events = engine.process_environmental_tick(1, [mock_empire], mock_galaxy)

        # No events for empty fleet
        assert len(events) == 0

    def test_derelict_ships_not_affected(self, mock_empire, mock_galaxy, mock_fleet, mock_ship):
        """Test that derelict ships are not affected by storm damage."""
        mock_ship.is_combat_capable.return_value = False  # Derelict
        mock_fleet.get_combat_capable_ships.return_value = []

        storm_effects = EnvironmentalEffects(
            in_storm=True,
            damage_per_tick=10.0,
            storm_names=["Ion Storm"],
        )

        mock_area_manager = MagicMock()
        mock_area_manager.get_effects_at_global_hex.return_value = storm_effects

        engine = EnvironmentalHazardEngine(area_effect_manager=mock_area_manager)
        events = engine.process_environmental_tick(1, [mock_empire], mock_galaxy)

        # No events when no combat-capable ships
        assert len(events) == 0

    def test_multiple_storms_combined_effects(self, mock_empire, mock_galaxy, mock_fleet, mock_ship):
        """Test fleet in overlapping storms gets combined effects."""
        # AreaEffectManager already aggregates, so we test the aggregated result
        combined_effects = EnvironmentalEffects(
            in_storm=True,
            damage_per_tick=15.0,  # Combined from 2 storms
            fuel_drain_per_tick=5.0,  # Combined
            storm_names=["Ion Storm", "Plasma Cloud"],
        )

        mock_area_manager = MagicMock()
        mock_area_manager.get_effects_at_global_hex.return_value = combined_effects

        engine = EnvironmentalHazardEngine(area_effect_manager=mock_area_manager)
        events = engine.process_environmental_tick(1, [mock_empire], mock_galaxy)

        assert len(events) == 1
        event = events[0]
        # Storm name is first in list
        assert event.storm_name == "Ion Storm"
        assert event.damage_dealt == pytest.approx(0.15)
        assert event.fuel_drained == pytest.approx(0.05)


class TestTurnEngineIntegration:
    """Test EnvironmentalHazardEngine integration with TurnEngine."""

    def test_turn_engine_has_environmental_engine_property(self, fresh_registries):
        """Test TurnEngine creates environmental engine via lazy-init."""
        from game.strategy.engine.turn_engine import TurnEngine

        engine = TurnEngine(registries=fresh_registries)
        env_engine = engine.environmental_engine

        # Should create default EnvironmentalHazardEngine
        assert env_engine is not None
        assert isinstance(env_engine, EnvironmentalHazardEngine)

    def test_turn_engine_accepts_injected_environmental_engine(self, fresh_registries):
        """Test TurnEngine accepts injected environmental engine."""
        from game.strategy.engine.turn_engine import TurnEngine

        mock_env_engine = MagicMock()
        engine = TurnEngine(registries=fresh_registries, environmental_engine=mock_env_engine)

        assert engine.environmental_engine is mock_env_engine

    def test_turn_engine_calls_environmental_engine_each_tick(self, fresh_registries):
        """Test TurnEngine calls environmental engine during process_turn."""
        from game.strategy.engine.turn_engine import TurnEngine

        # Create mock engines
        mock_env_engine = MagicMock()
        mock_env_engine.process_environmental_tick.return_value = []

        # Use mock for other engines to speed up test
        mock_movement = MagicMock()
        mock_movement.collect_movements.return_value = []
        mock_movement.apply_movements.return_value = []

        mock_production = MagicMock()
        mock_order_proc = MagicMock()
        mock_order_proc.process_instant_orders.return_value = []
        mock_conflict = MagicMock()
        mock_resource = MagicMock()
        mock_population = MagicMock()
        mock_resupply = MagicMock()
        mock_harvesting = MagicMock()
        mock_maintenance = MagicMock()
        mock_maintenance.process_maintenance_tick.return_value = []
        mock_action = MagicMock()
        mock_action.process_action_ticks.return_value = []

        engine = TurnEngine(
            registries=fresh_registries,
            movement_engine=mock_movement,
            production_engine=mock_production,
            order_processor=mock_order_proc,
            conflict_engine=mock_conflict,
            resource_engine=mock_resource,
            population_engine=mock_population,
            resupply_engine=mock_resupply,
            harvesting_engine=mock_harvesting,
            maintenance_engine=mock_maintenance,
            action_engine=mock_action,
            environmental_engine=mock_env_engine,
        )

        # Create minimal empires and galaxy
        mock_empire = MagicMock()
        mock_empire.fleets = []
        mock_galaxy = MagicMock()

        engine.process_turn([mock_empire], mock_galaxy)

        # Should be called 100 times (once per tick)
        assert mock_env_engine.process_environmental_tick.call_count == 100

    def test_turn_engine_accumulates_environmental_events(self, fresh_registries):
        """Test TurnEngine accumulates environmental events from all ticks."""
        from game.strategy.engine.turn_engine import TurnEngine

        # Create mock environmental engine that returns events
        mock_env_engine = MagicMock()
        # Return one event on ticks 10, 50, 90
        def side_effect(tick, empires, galaxy):
            if tick in [10, 50, 90]:
                return [EnvironmentalEvent(
                    fleet_id=1,
                    storm_name="Test Storm",
                    damage_dealt=0.1,
                    fuel_drained=0.05,
                    tick=tick,
                )]
            return []

        mock_env_engine.process_environmental_tick.side_effect = side_effect

        # Use mock for other engines
        mock_movement = MagicMock()
        mock_movement.collect_movements.return_value = []
        mock_movement.apply_movements.return_value = []

        mock_production = MagicMock()
        mock_order_proc = MagicMock()
        mock_order_proc.process_instant_orders.return_value = []
        mock_conflict = MagicMock()
        mock_resource = MagicMock()
        mock_population = MagicMock()
        mock_resupply = MagicMock()
        mock_harvesting = MagicMock()
        mock_maintenance = MagicMock()
        mock_maintenance.process_maintenance_tick.return_value = []
        mock_action = MagicMock()
        mock_action.process_action_ticks.return_value = []

        engine = TurnEngine(
            registries=fresh_registries,
            movement_engine=mock_movement,
            production_engine=mock_production,
            order_processor=mock_order_proc,
            conflict_engine=mock_conflict,
            resource_engine=mock_resource,
            population_engine=mock_population,
            resupply_engine=mock_resupply,
            harvesting_engine=mock_harvesting,
            maintenance_engine=mock_maintenance,
            action_engine=mock_action,
            environmental_engine=mock_env_engine,
        )

        mock_empire = MagicMock()
        mock_empire.fleets = []
        mock_galaxy = MagicMock()

        engine.process_turn([mock_empire], mock_galaxy)

        # Should have accumulated 3 events
        assert len(engine.last_environmental_events) == 3
        event_ticks = [e.tick for e in engine.last_environmental_events]
        assert event_ticks == [10, 50, 90]
