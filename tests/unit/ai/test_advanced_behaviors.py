import pytest
from unittest.mock import MagicMock
import pygame

from game.ai.behaviors import KiteBehavior, AttackRunBehavior, OrbitBehavior
from game.ai import AIController
from game.ai.interfaces.controllable import ShipControllableAdapter


@pytest.fixture
def advanced_setup():
    if not pygame.get_init():
        pygame.init()

    mock_controller = MagicMock()
    mock_controller.ship.position = pygame.math.Vector2(0, 0)
    mock_controller.ship.max_weapon_range = 1000
    mock_controller.ship.radius = 50

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
        # navigate_to(target_pos, stop_dist=opt_dist, precise=True)
        advanced_setup['mock_controller'].navigate_to.assert_called_with(
            advanced_setup['target'].position,
            stop_dist=1000.0,  # max_range * 1.0
            precise=True
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

        advanced_setup['mock_controller'].ship.position = pygame.math.Vector2(600, 0)
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

    def test_formation_integrity__ability_check(self, advanced_setup):
        """Verify formation breakdown checks operational propulsion abilities."""
        # This logic is in AIController._check_formation_integrity
        # But we can test it by manually creating a controller or moving logic to mixin?
        # It's a method on AIController. Let's instanciate a real one with mocks.

        mock_ship = advanced_setup['mock_controller'].ship
        # Use ShipControllableAdapter to match production behavior (battle_engine.py)
        real_controller = AIController(ShipControllableAdapter(mock_ship), MagicMock(), 0)

        # Setup Ship with Ability-based Logic (access through underlying ship)
        mock_ship.in_formation = True
        mock_ship.formation_master = MagicMock()
        mock_ship.formation_master.formation_members = [mock_ship]  # Raw ships in list

        # Case 1: Ability Healthy
        comp = MagicMock()
        comp.has_ability.side_effect = lambda x: x == 'CombatPropulsion'
        comp.current_hp = 100
        comp.max_hp = 100

        # Mock the Ship helper methods to return our component
        mock_ship.get_components_by_ability = MagicMock(return_value=[comp])

        real_controller._check_formation_integrity()
        assert mock_ship.in_formation is True

        # Case 2: Ability Damaged
        comp.current_hp = 50

        real_controller._check_formation_integrity()
        assert mock_ship.in_formation is False
