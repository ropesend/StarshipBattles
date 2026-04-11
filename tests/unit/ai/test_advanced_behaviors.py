import pytest
from unittest.mock import MagicMock
import pygame

from game.ai.behaviors import KiteBehavior, AttackRunBehavior, OrbitBehavior


@pytest.fixture
def advanced_setup():
    if not pygame.get_init():
        pygame.init()

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

    pygame.quit()


class TestAdvancedBehaviors:

    def test_kite_behavior(self, advanced_setup):
        """Test KiteBehavior navigation logic."""
        kite = KiteBehavior(advanced_setup['mock_controller'])

        # Strategy: Engage at max range
        strategy = {'engage_distance': 'max_range'}

        # Setup mock return values explicitly to avoid odd collisions
        advanced_setup['mock_controller'].get_engage_distance_multiplier = MagicMock(return_value=1.0)
        advanced_setup['mock_controller'].check_avoidance = MagicMock(return_value=None)

        # Scenario 1: Target too far (2000 > 1000)
        # Should navigate TO target
        advanced_setup['target'].position = pygame.math.Vector2(2000, 0)
        # Scenario 1: Target too far (2000 > 1000)
        # Should navigate TO target
        advanced_setup['target'].position = pygame.math.Vector2(2000, 0)
        kite.update(advanced_setup['target'], strategy)

        # Check navigate_to call
        # navigate_to(target_pos, stop_dist=opt_dist)
        advanced_setup['mock_controller'].navigate_to.assert_called_with(
            advanced_setup['target'].position,
            stop_dist=1000.0  # max_range * 1.0
        )

        # Scenario 2: Target too close (500 < 1000)
        advanced_setup['target'].position = pygame.math.Vector2(500, 0)

        kite.update(advanced_setup['target'], strategy)

        # Should navigate AWAY (Kite position)
        args, _ = advanced_setup['mock_controller'].navigate_to.call_args
        dest = args[0]  # target_pos
        assert dest.x == pytest.approx(-500.0, abs=1.0)
        assert dest.y == 0

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

