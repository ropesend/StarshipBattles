"""Tests for FleetMovementEngine (PROJ-189 Phase 5).

Test environmental effect integration for storm speed reduction.
PROJ-191 Phase 3: Updated mocks to use spec= for type safety.
"""

import pytest
from unittest.mock import MagicMock, patch

from game.strategy.engine.fleet_movement_engine import FleetMovementEngine
from game.strategy.services.area_effect_manager import AreaEffectManager, EnvironmentalEffects
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import OrderType
from game.strategy.data.empire import Empire
from game.core.hex_math import HexCoord


def create_mock_fleet(fleet_id=1, speed=5.0, location=HexCoord(0, 0)):
    """Create a mock fleet with configurable properties."""
    fleet = MagicMock(spec=Fleet)
    fleet.id = fleet_id
    fleet.speed = speed
    fleet.location = location
    fleet.ships = []
    fleet.get_current_order.return_value = None
    fleet.resources.has_resources_for_movement.return_value = True
    fleet.path = []
    return fleet


class TestFleetMovementEngineEnvironmentalEffects:
    """Test environmental effect integration."""

    def test_fleet_outside_storm_moves_at_normal_speed(self):
        """Test fleet outside storm uses base speed."""
        mock_area_manager = MagicMock()
        mock_area_manager.get_effects_at_global_hex.return_value = EnvironmentalEffects()

        engine = FleetMovementEngine(area_effect_manager=mock_area_manager)

        # Create fleet with speed 5
        fleet = create_mock_fleet(speed=5.0)
        empire = MagicMock(spec=Empire)
        empire.fleets = [fleet]
        galaxy = MagicMock()

        # At speed 5, interval = 100 // 5 = 20, so fleet should move on tick 20
        with patch.object(engine, 'calculate_next_hex', return_value=HexCoord(1, 0)):
            # Tick 10: shouldn't move (10 % 20 != 0)
            moves = engine.collect_movements([empire], galaxy, 10)
            assert len(moves) == 0

            # Tick 20: should move (20 % 20 == 0)
            moves = engine.collect_movements([empire], galaxy, 20)
            assert len(moves) == 1

    def test_fleet_in_storm_moves_at_reduced_speed(self):
        """Test fleet in storm with strategic_mult=0.5 moves at half speed."""
        storm_effects = EnvironmentalEffects(
            in_storm=True,
            strategic_mult=0.5,  # 50% speed
            storm_names=["Ion Storm"],
        )

        mock_area_manager = MagicMock()
        mock_area_manager.get_effects_at_global_hex.return_value = storm_effects

        engine = FleetMovementEngine(area_effect_manager=mock_area_manager)

        # Create fleet with base speed 4
        fleet = create_mock_fleet(speed=4.0)
        empire = MagicMock(spec=Empire)
        empire.fleets = [fleet]
        galaxy = MagicMock()

        # With strategic_mult=0.5, effective speed = 4 * 0.5 = 2
        # Interval = 100 // 2 = 50, so fleet moves on tick 50
        with patch.object(engine, 'calculate_next_hex', return_value=HexCoord(1, 0)):
            # Tick 25: shouldn't move (25 % 50 != 0)
            moves = engine.collect_movements([empire], galaxy, 25)
            assert len(moves) == 0

            # Tick 50: should move (50 % 50 == 0)
            moves = engine.collect_movements([empire], galaxy, 50)
            assert len(moves) == 1

    def test_fleet_in_storm_with_zero_speed_cannot_move(self):
        """Test fleet in storm with strategic_mult=0 cannot move."""
        storm_effects = EnvironmentalEffects(
            in_storm=True,
            strategic_mult=0.0,  # Completely stuck
            storm_names=["Dead Zone"],
        )

        mock_area_manager = MagicMock()
        mock_area_manager.get_effects_at_global_hex.return_value = storm_effects

        engine = FleetMovementEngine(area_effect_manager=mock_area_manager)

        fleet = create_mock_fleet(speed=5.0)
        empire = MagicMock(spec=Empire)
        empire.fleets = [fleet]
        galaxy = MagicMock()

        # With effective speed 0, fleet cannot move
        with patch.object(engine, 'calculate_next_hex', return_value=HexCoord(1, 0)):
            for tick in [1, 25, 50, 75, 100]:
                moves = engine.collect_movements([empire], galaxy, tick)
                assert len(moves) == 0, f"Fleet should not move on tick {tick}"

    def test_engine_creates_default_area_effect_manager(self):
        """Test engine creates default AreaEffectManager if not provided."""
        engine = FleetMovementEngine()

        # Access through collect_movements to trigger lazy init
        fleet = create_mock_fleet(speed=5.0)
        empire = MagicMock(spec=Empire)
        empire.fleets = [fleet]

        # Create a mock galaxy that returns empty zones
        galaxy = MagicMock()
        galaxy.get_zones_at_global_hex.return_value = []

        with patch.object(engine, 'calculate_next_hex', return_value=HexCoord(1, 0)):
            engine.collect_movements([empire], galaxy, 20)

        # Should have created default AreaEffectManager
        assert engine._area_effect_manager is not None

    def test_fleet_in_severe_storm_significantly_slowed(self):
        """Test fleet in severe storm with strategic_mult=0.2 moves 5x slower."""
        storm_effects = EnvironmentalEffects(
            in_storm=True,
            strategic_mult=0.2,  # 20% speed
            storm_names=["Plasma Storm"],
        )

        mock_area_manager = MagicMock()
        mock_area_manager.get_effects_at_global_hex.return_value = storm_effects

        engine = FleetMovementEngine(area_effect_manager=mock_area_manager)

        # Create fleet with base speed 5
        fleet = create_mock_fleet(speed=5.0)
        empire = MagicMock(spec=Empire)
        empire.fleets = [fleet]
        galaxy = MagicMock()

        # With strategic_mult=0.2, effective speed = 5 * 0.2 = 1
        # Interval = 100 // 1 = 100, so fleet moves only on tick 100
        with patch.object(engine, 'calculate_next_hex', return_value=HexCoord(1, 0)):
            # Tick 50: shouldn't move
            moves = engine.collect_movements([empire], galaxy, 50)
            assert len(moves) == 0

            # Tick 100: should move
            moves = engine.collect_movements([empire], galaxy, 100)
            assert len(moves) == 1

    def test_multiple_fleets_with_different_effects(self):
        """Test multiple fleets get their own environmental effects."""
        # Fleet 1 at (0,0) - no storm
        # Fleet 2 at (5,5) - in storm with strategic_mult=0.5
        def side_effect(galaxy, location):
            if location == HexCoord(5, 5):
                return EnvironmentalEffects(
                    in_storm=True,
                    strategic_mult=0.5,
                    storm_names=["Ion Storm"],
                )
            return EnvironmentalEffects()

        mock_area_manager = MagicMock()
        mock_area_manager.get_effects_at_global_hex.side_effect = side_effect

        engine = FleetMovementEngine(area_effect_manager=mock_area_manager)

        # Fleet 1: speed 4, not in storm, moves every 25 ticks
        fleet1 = create_mock_fleet(fleet_id=1, speed=4.0, location=HexCoord(0, 0))

        # Fleet 2: speed 4, in storm with 0.5 mult, effective speed 2, moves every 50 ticks
        fleet2 = create_mock_fleet(fleet_id=2, speed=4.0, location=HexCoord(5, 5))

        empire = MagicMock(spec=Empire)
        empire.fleets = [fleet1, fleet2]
        galaxy = MagicMock()

        with patch.object(engine, 'calculate_next_hex', return_value=HexCoord(1, 0)):
            # Tick 25: only fleet1 should move
            moves = engine.collect_movements([empire], galaxy, 25)
            assert len(moves) == 1
            assert moves[0][0].id == 1

            # Tick 50: both should move
            moves = engine.collect_movements([empire], galaxy, 50)
            assert len(moves) == 2
            fleet_ids = {m[0].id for m in moves}
            assert fleet_ids == {1, 2}


class TestFleetMovementEngineGetEffectiveSpeed:
    """Test _get_effective_fleet_speed helper."""

    def test_effective_speed_without_storm(self):
        """Test effective speed equals base speed when not in storm."""
        mock_area_manager = MagicMock()
        mock_area_manager.get_effects_at_global_hex.return_value = EnvironmentalEffects()

        engine = FleetMovementEngine(area_effect_manager=mock_area_manager)

        fleet = create_mock_fleet(speed=5.0)
        galaxy = MagicMock()

        effective_speed = engine._get_effective_fleet_speed(fleet, galaxy)
        assert effective_speed == 5.0

    def test_effective_speed_with_storm(self):
        """Test effective speed reduced by storm strategic_mult."""
        storm_effects = EnvironmentalEffects(
            in_storm=True,
            strategic_mult=0.5,
            storm_names=["Test Storm"],
        )

        mock_area_manager = MagicMock()
        mock_area_manager.get_effects_at_global_hex.return_value = storm_effects

        engine = FleetMovementEngine(area_effect_manager=mock_area_manager)

        fleet = create_mock_fleet(speed=4.0)
        galaxy = MagicMock()

        effective_speed = engine._get_effective_fleet_speed(fleet, galaxy)
        assert effective_speed == 2.0  # 4 * 0.5 = 2


# =============================================================================
# PROJ-207 EP-005: Error Handling Consistency Tests
# =============================================================================

class TestFleetMovementEngineErrorHandling:
    """Tests for consistent error handling in apply_movement.

    PROJ-207 EP-005: Warp failures should pop_order() not clear_orders().
    Stranded (no fuel) should clear_orders() since fleet cannot move at all.
    """

    def test_stranded_fleet_clears_all_orders(self):
        """Stranded fleet (no fuel) clears entire order queue.

        When a fleet has no movement resources, it cannot execute ANY orders
        that require movement, so clearing the queue is correct.
        """
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine

        engine = FleetMovementEngine()

        fleet = create_mock_fleet(speed=5.0, location=HexCoord(0, 0))
        fleet.resources.has_resources_for_movement.return_value = False  # No fuel
        fleet.clear_orders = MagicMock()
        fleet.pop_order = MagicMock()

        galaxy = MagicMock()

        result = engine.apply_movement(fleet, HexCoord(1, 0), galaxy)

        assert result.moved is False
        assert result.stranded is True
        fleet.clear_orders.assert_called_once()
        fleet.pop_order.assert_not_called()

    def test_warp_no_capability_pops_single_order(self):
        """Warp failure (no capability) preserves subsequent orders.

        When a WARP order fails because the fleet lacks warp capability,
        the fleet can still move normally, so subsequent orders should survive.
        """
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine

        engine = FleetMovementEngine()

        fleet = create_mock_fleet(speed=5.0, location=HexCoord(0, 0))
        fleet.resources.has_resources_for_movement.return_value = True
        fleet.capabilities.can_use_warp.return_value = False  # No warp capability
        fleet.clear_orders = MagicMock()
        fleet.pop_order = MagicMock()

        galaxy = MagicMock()

        # Simulate warp jump (distance > 1)
        result = engine.apply_movement(fleet, HexCoord(10, 10), galaxy)

        assert result.moved is False
        assert result.warp_blocked is True
        fleet.pop_order.assert_called_once()
        fleet.clear_orders.assert_not_called()

    def test_warp_insufficient_resources_pops_single_order(self):
        """Warp failure (insufficient resources) preserves subsequent orders.

        When a WARP order fails because of insufficient warp resources,
        the fleet can still move normally, so subsequent orders should survive.
        """
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine

        engine = FleetMovementEngine()

        fleet = create_mock_fleet(speed=5.0, location=HexCoord(0, 0))
        fleet.resources.has_resources_for_movement.return_value = True
        fleet.capabilities.can_use_warp.return_value = True  # Has capability
        fleet.resources.has_resources_for_warp.return_value = False  # But no resources
        fleet.clear_orders = MagicMock()
        fleet.pop_order = MagicMock()

        galaxy = MagicMock()

        # Simulate warp jump (distance > 1)
        result = engine.apply_movement(fleet, HexCoord(10, 10), galaxy)

        assert result.moved is False
        assert result.warp_blocked is False  # Not blocked by capability
        fleet.pop_order.assert_called_once()
        fleet.clear_orders.assert_not_called()

    def test_warp_with_colonize_preserves_colonize_on_failure(self):
        """WARP + COLONIZE queue: WARP fails, COLONIZE is preserved.

        This tests the user-facing behavior: if a player queues WARP then
        COLONIZE, and WARP fails (no capability), the COLONIZE order should
        remain in the queue for manual handling.
        """
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine
        from game.strategy.data.order_types import FleetOrder, OrderType

        engine = FleetMovementEngine()

        # Use a real fleet-like object with order queue
        orders = [
            FleetOrder(OrderType.WARP, HexCoord(10, 10)),
            FleetOrder(OrderType.COLONIZE, MagicMock()),  # Planet mock
        ]

        fleet = create_mock_fleet(speed=5.0, location=HexCoord(0, 0))
        fleet.resources.has_resources_for_movement.return_value = True
        fleet.capabilities.can_use_warp.return_value = False  # No warp capability
        fleet.orders = orders

        # Real pop_order behavior
        def pop_order_impl():
            if fleet.orders:
                fleet.orders.pop(0)
        fleet.pop_order = MagicMock(side_effect=pop_order_impl)
        fleet.clear_orders = MagicMock()

        galaxy = MagicMock()

        # Simulate warp jump (distance > 1)
        result = engine.apply_movement(fleet, HexCoord(10, 10), galaxy)

        assert result.moved is False
        assert result.warp_blocked is True
        # COLONIZE should still be in the queue
        assert len(fleet.orders) == 1
        assert fleet.orders[0].type == OrderType.COLONIZE

    def test_single_move_order_stranded_clears_queue(self):
        """Single MOVE order fails (stranded) → queue is empty.

        When the only order is a MOVE that fails due to being stranded,
        the queue should end up empty.
        """
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine
        from game.strategy.data.order_types import FleetOrder, OrderType

        engine = FleetMovementEngine()

        orders = [FleetOrder(OrderType.MOVE, HexCoord(1, 0))]

        fleet = create_mock_fleet(speed=5.0, location=HexCoord(0, 0))
        fleet.resources.has_resources_for_movement.return_value = False  # Stranded
        fleet.orders = orders

        # Real clear_orders behavior
        def clear_orders_impl():
            fleet.orders.clear()
        fleet.clear_orders = MagicMock(side_effect=clear_orders_impl)
        fleet.pop_order = MagicMock()

        galaxy = MagicMock()

        result = engine.apply_movement(fleet, HexCoord(1, 0), galaxy)

        assert result.moved is False
        assert result.stranded is True
        assert len(fleet.orders) == 0
