"""Tests for AI behaviors that involve spatial reasoning.

PROJ-323 Task 5.11: vector arithmetic in test bodies is intentional and
acceptable for spatial behavior tests. Each test documents the expected
geometry inline (e.g. "ship at 1000, target at origin, expect tangential
movement"). The fixture below describes the standard scenario:
  - ship at origin (0, 0)
  - max weapon range 1000 units
  - target far away at (2000, 0) by default, repositioned per test

This is intentionally accepted as documented intent (CAT-12 finding marked
"acceptable for spatial behavior tests"). No further refactor needed.
"""
import pytest
from unittest.mock import MagicMock
import pygame

from game.ai.behaviors import KiteBehavior, AttackRunBehavior, OrbitBehavior


@pytest.fixture
def advanced_setup():
    """Standard spatial-test scenario: ship at origin, target at (2000, 0).

    See module docstring for geometry conventions used by tests in this file.
    """
    mock_controller = MagicMock()
    ship = mock_controller.ship
    ship.position = pygame.math.Vector2(0, 0)
    ship.max_weapon_range = 1000
    ship.radius = 50

    # Interface method mocks
    ship.get_position.return_value = ship.position
    ship.get_weapon_range.return_value = ship.max_weapon_range
    ship.get_radius.return_value = ship.radius

    target = MagicMock()
    target.position = pygame.math.Vector2(2000, 0)  # Far away
    target.velocity = pygame.math.Vector2(0, 0)

    yield {
        'mock_controller': mock_controller,
        'target': target
    }


class TestAdvancedBehaviors:

    def test_kite_behavior(self, advanced_setup):
        """Test KiteBehavior smooth orbital navigation."""
        kite = KiteBehavior(advanced_setup['mock_controller'])

        strategy = {'engage_distance': 'max_range'}
        advanced_setup['mock_controller'].get_engage_distance_multiplier = MagicMock(return_value=1.0)
        advanced_setup['mock_controller'].check_avoidance = MagicMock(return_value=None)

        # Scenario 1: Target far away (2000 > 1000 weapon range)
        # Should navigate mostly toward target with some tangential component
        advanced_setup['target'].position = pygame.math.Vector2(2000, 0)
        kite.update(advanced_setup['target'], strategy)

        args, kwargs = advanced_setup['mock_controller'].navigate_to.call_args
        dest = args[0]
        assert dest.x > 0, "Should move toward target (positive X)"
        assert kwargs.get('stop_dist', 0) == 0, "Should always thrust (stop_dist=0)"

        # Scenario 2: Target too close (500 < 1000 weapon range)
        advanced_setup['target'].position = pygame.math.Vector2(500, 0)
        kite.update(advanced_setup['target'], strategy)

        args, _ = advanced_setup['mock_controller'].navigate_to.call_args
        dest = args[0]
        rel = dest - pygame.math.Vector2(0, 0)  # ship at origin
        # Should move outward (away from target) with tangential component
        assert rel.x < 0 or abs(rel.y) > 0, "Should orbit outward when too close"

    def test_attack_run_behavior(self, advanced_setup):
        """Test AttackRun (Boom and Zoom) logic."""
        attack = AttackRunBehavior(advanced_setup['mock_controller'])
        attack.enter()  # Reset state

        # Config
        strategy = {
            'attack_run_behavior': {
                'approach_distance': 0.2,  # 200 units
                'retreat_distance': 0.8,  # 800 units
                'retreat_duration': 2.0
            }
        }

        # 1. Approach Phase
        advanced_setup['target'].position = pygame.math.Vector2(2000, 0)

        attack.update(advanced_setup['target'], strategy)

        assert attack.attack_state == 'approach'
        # Should drive TO target
        advanced_setup['mock_controller'].navigate_to.assert_called()

        # 2. Trigger Retreat
        # Distance < approach (200 * 1.5 = 300 hysteresis)
        advanced_setup['target'].position = pygame.math.Vector2(100, 0)

        attack.update(advanced_setup['target'], strategy)

        assert attack.attack_state == 'retreat'
        assert attack.attack_timer == 2.0

        # 3. Retreat Phase
        # Mock timer decrement implicitly handled by update call? No, logic decrements it.
        # We just need to check if it calls navigate_to with retreat vector
        advanced_setup['mock_controller'].navigate_to.reset_mock()
        attack.update(advanced_setup['target'], strategy)

        assert attack.attack_timer < 2.0
        advanced_setup['mock_controller'].navigate_to.assert_called()

    def test_orbit_behavior(self, advanced_setup):
        """Test Orbit circling logic."""
        orbit = OrbitBehavior(advanced_setup['mock_controller'])
        strategy = {'orbit_distance': 500}

        ship_pos = pygame.math.Vector2(600, 0)
        advanced_setup['mock_controller'].ship.position = ship_pos
        advanced_setup['mock_controller'].ship.get_position.return_value = ship_pos
        advanced_setup['target'].position = pygame.math.Vector2(0, 0)
        # Dist 600 (Too far)

        orbit.update(advanced_setup['target'], strategy)

        # Radial: Ship-Target = (600,0) -> (1,0) (Actually vec_to_target is -600... wait)
        # vec_to_target = Target(0) - Ship(600) = (-600, 0) -> norm (-1, 0) (Left)
        # Tangent: (-y, x) -> (0, -1) (Up)
        # Too far (600 > 550): Move dir = Tangent + Radial*0.5
        # Tangent(0,-1) + Radial(-1,0)*0.5 = (-0.5, -1)
        # Normalized...

        args, _ = advanced_setup['mock_controller'].navigate_to.call_args
        dest = args[0]
        # Destination should have negative X (inward) and negative Y (ccw orbit)
        rel_move = dest - advanced_setup['mock_controller'].ship.position

        assert rel_move.x < 0  # Moving Left (Inward)
        assert rel_move.y < 0  # Moving Up (Orbit)


class TestKiteBehaviorSmooth:
    """Tests for smooth orbital kite behavior.

    The kite behavior should smoothly transition from closing to orbiting
    as the ship approaches optimal range, rather than stopping and reversing.
    """

    def test_far_from_target_navigates_toward(self, advanced_setup):
        """When far from optimal range, ship should close in toward target."""
        kite = KiteBehavior(advanced_setup['mock_controller'])
        strategy = {'engage_distance': 'max_range'}
        advanced_setup['mock_controller'].get_engage_distance_multiplier = MagicMock(return_value=1.0)
        advanced_setup['mock_controller'].check_avoidance = MagicMock(return_value=None)

        # Ship at origin, target at 3000 — well beyond weapon range 1000
        advanced_setup['mock_controller'].ship.get_position.return_value = pygame.math.Vector2(0, 0)
        advanced_setup['target'].position = pygame.math.Vector2(3000, 0)

        kite.update(advanced_setup['target'], strategy)

        args, _ = advanced_setup['mock_controller'].navigate_to.call_args
        dest = args[0]
        # Should navigate mostly toward target (positive X)
        rel = dest - pygame.math.Vector2(0, 0)
        assert rel.x > 0, "Ship should move toward target when far away"

    def test_at_optimal_range_orbits_tangentially(self, advanced_setup):
        """At optimal range, ship should orbit (tangential movement, not stop/reverse)."""
        kite = KiteBehavior(advanced_setup['mock_controller'])
        strategy = {'engage_distance': 'max_range'}
        advanced_setup['mock_controller'].get_engage_distance_multiplier = MagicMock(return_value=1.0)
        advanced_setup['mock_controller'].check_avoidance = MagicMock(return_value=None)

        # Ship at optimal distance from target (1000 units = weapon range * 1.0)
        advanced_setup['mock_controller'].ship.get_position.return_value = pygame.math.Vector2(1000, 0)
        advanced_setup['target'].position = pygame.math.Vector2(0, 0)

        kite.update(advanced_setup['target'], strategy)

        args, kwargs = advanced_setup['mock_controller'].navigate_to.call_args
        dest = args[0]
        ship_pos = pygame.math.Vector2(1000, 0)
        rel = dest - ship_pos

        # At optimal range, movement should be primarily tangential (Y component)
        # not radially away (positive X) as the old behavior would do
        assert abs(rel.y) > abs(rel.x) * 0.5, \
            f"At optimal range, tangential component should dominate, got rel={rel}"

    def test_too_close_moves_outward_while_orbiting(self, advanced_setup):
        """When too close, ship should have outward + tangential component."""
        kite = KiteBehavior(advanced_setup['mock_controller'])
        strategy = {'engage_distance': 'max_range'}
        advanced_setup['mock_controller'].get_engage_distance_multiplier = MagicMock(return_value=1.0)
        advanced_setup['mock_controller'].check_avoidance = MagicMock(return_value=None)

        # Ship at 500 units — well inside optimal range of 1000
        advanced_setup['mock_controller'].ship.get_position.return_value = pygame.math.Vector2(500, 0)
        advanced_setup['target'].position = pygame.math.Vector2(0, 0)

        kite.update(advanced_setup['target'], strategy)

        args, _ = advanced_setup['mock_controller'].navigate_to.call_args
        dest = args[0]
        ship_pos = pygame.math.Vector2(500, 0)
        rel = dest - ship_pos

        # Should move outward (positive X = away from target at origin)
        assert rel.x > 0, "Ship should have outward component when too close"
        # Should also have tangential component (orbiting, not just fleeing)
        assert abs(rel.y) > 0, "Ship should have tangential component even when too close"

    def test_navigate_to_called_with_zero_stop_dist(self, advanced_setup):
        """Ship should always thrust (stop_dist=0) for continuous movement."""
        kite = KiteBehavior(advanced_setup['mock_controller'])
        strategy = {'engage_distance': 'max_range'}
        advanced_setup['mock_controller'].get_engage_distance_multiplier = MagicMock(return_value=1.0)
        advanced_setup['mock_controller'].check_avoidance = MagicMock(return_value=None)

        # At optimal range
        advanced_setup['mock_controller'].ship.get_position.return_value = pygame.math.Vector2(1000, 0)
        advanced_setup['target'].position = pygame.math.Vector2(0, 0)

        kite.update(advanced_setup['target'], strategy)

        _, kwargs = advanced_setup['mock_controller'].navigate_to.call_args
        assert kwargs.get('stop_dist', 0) == 0, "Should never stop — always thrust"

