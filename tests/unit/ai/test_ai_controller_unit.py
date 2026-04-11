"""
Unit tests for game/ai/controller.py

Tests AIController behavior selection, engage distance logic, and targeting.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch

from game.core.math import Vector2


@pytest.fixture
def mock_ship():
    """Create a mock ship with standard interface."""
    ship = Mock()
    ship.get_position.return_value = Vector2(100, 100)
    ship.get_weapon_range.return_value = 200.0
    ship.get_rotation.return_value = 0.0
    ship.get_max_speed.return_value = 100.0
    ship.get_radius.return_value = 10.0
    ship.get_vehicle_type.return_value = 'Frigate'
    ship.get_ai_strategy.return_value = 'standard_ranged'
    ship.get_team_id.return_value = 0
    ship.is_alive.return_value = True
    ship.get_current_target.return_value = None
    ship.get_max_targets.return_value = 1
    ship.get_components_by_ability.return_value = []
    ship.set_trigger_pulled = Mock()
    ship.set_current_target = Mock()
    ship.set_secondary_targets = Mock()
    ship.set_throttle = Mock()
    ship.set_turn_throttle = Mock()
    ship.id = 'test_ship'
    return ship


@pytest.fixture
def mock_grid():
    """Create a mock spatial grid."""
    grid = Mock()
    grid.query_radius.return_value = []
    grid.query_radius_exact.return_value = []
    return grid


@pytest.fixture
def mock_strategy_manager():
    """Create mock StrategyManager with default strategy."""
    with patch('game.ai.controller.get_default_strategy_manager') as mock_sm:
        instance = Mock()
        instance.resolve_strategy.return_value = {
            'definition': {},
            'targeting': {'rules': []},
            'movement': {
                'behavior': 'kite',
                'engage_distance': 'max_range',
                'retreat_hp_threshold': 0.1,
            }
        }
        mock_sm.return_value = instance
        yield mock_sm


@pytest.fixture
def controller(mock_ship, mock_grid, mock_strategy_manager):
    """Create an AIController instance."""
    from game.ai.controller import AIController
    return AIController(mock_ship, mock_grid, enemy_team_id=1)


class TestGetEngageDistanceMultiplier:
    """Tests for get_engage_distance_multiplier."""

    def test_get_engage_distance_max_range(self, controller):
        """'max_range' returns 1.0."""
        result = controller.get_engage_distance_multiplier({'engage_distance': 'max_range'})
        assert result == 1.0

    def test_get_engage_distance_ram(self, controller):
        """'ram' returns 0.0."""
        result = controller.get_engage_distance_multiplier({'engage_distance': 'ram'})
        assert result == 0.0

    def test_get_engage_distance_numeric(self, controller):
        """0.8 returns 0.8."""
        result = controller.get_engage_distance_multiplier({'engage_distance': 0.8})
        assert result == 0.8

    def test_get_engage_distance_default(self, controller):
        """Unknown string returns 1.0."""
        result = controller.get_engage_distance_multiplier({'engage_distance': 'unknown'})
        assert result == 1.0

    def test_get_engage_distance_missing_key(self, controller):
        """Missing key returns 1.0 (default)."""
        result = controller.get_engage_distance_multiplier({})
        assert result == 1.0


class TestBehaviorSelection:
    """Tests for behavior selection logic."""

    def test_behavior_selection_flee(self, mock_ship, mock_grid, mock_strategy_manager):
        """HP below threshold -> 'flee' behavior."""
        from game.ai.controller import AIController

        # Set up target so behavior runs
        target = Mock()
        target.is_alive = True
        target.position = Vector2(200, 100)
        mock_ship.get_current_target.return_value = target

        # Mock HP to be below retreat threshold (10%)
        with patch('game.ai.controller.get_hp_percent', return_value=0.05):
            controller = AIController(mock_ship, mock_grid, enemy_team_id=1)
            controller.update()

        assert controller.current_behavior is controller.behaviors['flee']

    def test_behavior_selection_policy(self, mock_ship, mock_grid, mock_strategy_manager):
        """Normal HP -> policy behavior (kite/ram/etc)."""
        from game.ai.controller import AIController

        target = Mock()
        target.is_alive = True
        target.position = Vector2(200, 100)
        mock_ship.get_current_target.return_value = target

        # Normal HP (50%)
        with patch('game.ai.controller.get_hp_percent', return_value=0.5):
            controller = AIController(mock_ship, mock_grid, enemy_team_id=1)
            controller.update()

        # Default behavior from mock strategy is 'kite'
        assert controller.current_behavior is controller.behaviors['kite']


class TestSatelliteException:
    """Tests for satellite-specific behavior."""

    def test_satellite_exception_no_movement(self, mock_ship, mock_grid, mock_strategy_manager):
        """Vehicle type 'Satellite' skips movement."""
        from game.ai.controller import AIController

        mock_ship.get_vehicle_type.return_value = 'Satellite'

        target = Mock()
        target.is_alive = True
        mock_ship.get_current_target.return_value = target

        with patch('game.ai.controller.get_hp_percent', return_value=0.5):
            controller = AIController(mock_ship, mock_grid, enemy_team_id=1)
            controller.update()

        # Satellite should not have a behavior assigned
        assert controller.current_behavior is None


class TestDeadShipHandling:
    """Tests for dead ship handling."""

    def test_dead_ship_no_action(self, mock_ship, mock_grid, mock_strategy_manager):
        """update() returns early for dead ship."""
        from game.ai.controller import AIController

        mock_ship.is_alive.return_value = False

        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)
        controller.update()

        # Should not set any behavior
        assert controller.current_behavior is None
        # Should not try to set target
        mock_ship.set_current_target.assert_not_called()


class TestFindTarget:
    """Tests for target finding logic."""

    def test_find_target_returns_highest_scored(self, mock_ship, mock_grid, mock_strategy_manager):
        """Multiple enemies, returns best scored."""
        from game.ai.controller import AIController

        # Create enemy ships
        enemy1 = Mock()
        enemy1.is_alive = True
        enemy1.team_id = 1
        enemy1.position = Vector2(200, 100)
        enemy1.id = 'enemy1'
        enemy1.get_components_by_ability = Mock(return_value=[])

        enemy2 = Mock()
        enemy2.is_alive = True
        enemy2.team_id = 1
        enemy2.position = Vector2(300, 100)
        enemy2.id = 'enemy2'
        enemy2.get_components_by_ability = Mock(return_value=[])

        mock_grid.query_radius.return_value = [enemy1, enemy2]
        mock_grid.query_radius_exact.return_value = [enemy1, enemy2]

        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)

        # Mock TargetEvaluator to return different scores
        with patch('game.ai.controller.TargetEvaluator.evaluate') as mock_eval:
            mock_eval.side_effect = lambda ship, target, rules, **kwargs: (
                100.0 if target.id == 'enemy1' else 50.0
            )
            with patch('game.ai.controller.is_combatant', return_value=True):
                result = controller.find_target()

        assert result is enemy1

    def test_find_target_no_enemies_returns_none(self, mock_ship, mock_grid, mock_strategy_manager):
        """Empty grid returns None."""
        from game.ai.controller import AIController

        mock_grid.query_radius.return_value = []
        mock_grid.query_radius_exact.return_value = []

        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)
        result = controller.find_target()

        assert result is None

    def test_find_target_filters_allies(self, mock_ship, mock_grid, mock_strategy_manager):
        """Only returns enemies, not allies."""
        from game.ai.controller import AIController

        ally = Mock()
        ally.is_alive = True
        ally.team_id = 0  # Same team as our ship
        ally.position = Vector2(200, 100)
        ally.get_components_by_ability = Mock(return_value=[])

        enemy = Mock()
        enemy.is_alive = True
        enemy.team_id = 1
        enemy.position = Vector2(300, 100)
        enemy.id = 'enemy'
        enemy.get_components_by_ability = Mock(return_value=[])

        mock_grid.query_radius.return_value = [ally, enemy]
        mock_grid.query_radius_exact.return_value = [ally, enemy]

        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)

        with patch('game.ai.controller.TargetEvaluator.evaluate', return_value=50.0):
            with patch('game.ai.controller.is_combatant', return_value=True):
                result = controller.find_target()

        assert result is enemy

    def test_find_target_filters_dead(self, mock_ship, mock_grid, mock_strategy_manager):
        """Only returns alive enemies."""
        from game.ai.controller import AIController

        dead_enemy = Mock()
        dead_enemy.is_alive = False
        dead_enemy.team_id = 1
        dead_enemy.position = Vector2(200, 100)
        dead_enemy.get_components_by_ability = Mock(return_value=[])

        alive_enemy = Mock()
        alive_enemy.is_alive = True
        alive_enemy.team_id = 1
        alive_enemy.position = Vector2(300, 100)
        alive_enemy.id = 'alive'
        alive_enemy.get_components_by_ability = Mock(return_value=[])

        mock_grid.query_radius.return_value = [dead_enemy, alive_enemy]
        mock_grid.query_radius_exact.return_value = [dead_enemy, alive_enemy]

        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)

        with patch('game.ai.controller.TargetEvaluator.evaluate', return_value=50.0):
            with patch('game.ai.controller.is_combatant', return_value=True):
                result = controller.find_target()

        assert result is alive_enemy


class TestBehaviorContextMerging:
    """Tests for behavior context merging (TCG-FND-002)."""

    def test_behavior_context_includes_movement_policy(self, mock_ship, mock_grid):
        """Behavior context includes movement policy fields."""
        from game.ai.controller import AIController

        # Set up strategy with specific movement policy
        with patch('game.ai.controller.get_default_strategy_manager') as mock_sm:
            instance = Mock()
            instance.resolve_strategy.return_value = {
                'definition': {'fire_while_retreating': True},
                'targeting': {'rules': []},
                'movement': {
                    'behavior': 'attack_run',
                    'engage_distance': 0.8,
                    'retreat_hp_threshold': 0.2,
                    'approach_distance': 0.5,
                }
            }
            mock_sm.return_value = instance

            # Set up target so behavior actually runs
            target = Mock()
            target.is_alive = True
            target.position = Vector2(200, 100)
            mock_ship.get_current_target.return_value = target

            controller = AIController(mock_ship, mock_grid, enemy_team_id=1)

            # Capture the context passed to behavior.update
            captured_context = None
            original_update = controller.behaviors['attack_run'].update

            def capture_update(tgt, ctx):
                nonlocal captured_context
                captured_context = ctx
                return original_update(tgt, ctx)

            with patch.object(controller.behaviors['attack_run'], 'update', side_effect=capture_update):
                with patch('game.ai.controller.get_hp_percent', return_value=0.5):
                    controller.update()

            # Context should contain merged movement policy + definition
            assert captured_context is not None
            assert captured_context.get('approach_distance') == 0.5
            assert captured_context.get('fire_while_retreating') is True

    def test_behavior_context_definition_overrides_movement(self, mock_ship, mock_grid):
        """Definition fields override movement policy fields if both present."""
        from game.ai.controller import AIController

        with patch('game.ai.controller.get_default_strategy_manager') as mock_sm:
            instance = Mock()
            instance.resolve_strategy.return_value = {
                'definition': {'engage_distance': 0.9},  # Override
                'targeting': {'rules': []},
                'movement': {
                    'behavior': 'kite',
                    'engage_distance': 0.5,  # Will be overridden
                    'retreat_hp_threshold': 0.1,
                }
            }
            mock_sm.return_value = instance

            target = Mock()
            target.is_alive = True
            target.position = Vector2(200, 100)
            mock_ship.get_current_target.return_value = target

            controller = AIController(mock_ship, mock_grid, enemy_team_id=1)

            captured_context = None
            original_update = controller.behaviors['kite'].update

            def capture_update(tgt, ctx):
                nonlocal captured_context
                captured_context = ctx
                return original_update(tgt, ctx)

            with patch.object(controller.behaviors['kite'], 'update', side_effect=capture_update):
                with patch('game.ai.controller.get_hp_percent', return_value=0.5):
                    controller.update()

            # Definition should override movement policy
            assert captured_context.get('engage_distance') == 0.9


class TestSecondaryTargetAcquisition:
    """Tests for secondary target acquisition (TCG-FND-002)."""

    def test_secondary_targets_with_multiplex_tracking(self, mock_ship, mock_grid):
        """Ship with multiplex tracking gets secondary targets."""
        from game.ai.controller import AIController

        mock_ship.get_max_targets.return_value = 3  # Multiplex tracking
        mock_ship.get_radius.return_value = 10.0  # Ensure numeric radius

        # Primary target
        primary = Mock()
        primary.is_alive = True
        primary.team_id = 1
        primary.position = Vector2(200, 100)
        primary.id = 'primary'
        primary.radius = 10.0
        primary.get_components_by_ability = Mock(return_value=[])

        # Secondary targets
        secondary1 = Mock()
        secondary1.is_alive = True
        secondary1.team_id = 1
        secondary1.position = Vector2(300, 100)
        secondary1.id = 'secondary1'
        secondary1.radius = 10.0
        secondary1.get_components_by_ability = Mock(return_value=[])

        secondary2 = Mock()
        secondary2.is_alive = True
        secondary2.team_id = 1
        secondary2.position = Vector2(400, 100)
        secondary2.id = 'secondary2'
        secondary2.radius = 10.0
        secondary2.get_components_by_ability = Mock(return_value=[])

        mock_grid.query_radius.return_value = [primary, secondary1, secondary2]
        mock_grid.query_radius_exact.return_value = [primary, secondary1, secondary2]
        mock_ship.get_current_target.return_value = primary

        with patch('game.ai.controller.get_default_strategy_manager') as mock_sm:
            instance = Mock()
            instance.resolve_strategy.return_value = {
                'definition': {},
                'targeting': {'rules': []},
                'movement': {'behavior': 'kite', 'retreat_hp_threshold': 0.1}
            }
            mock_sm.return_value = instance

            controller = AIController(mock_ship, mock_grid, enemy_team_id=1)

            with patch('game.ai.controller.TargetEvaluator.evaluate', return_value=50.0):
                with patch('game.ai.controller.is_combatant', return_value=True):
                    with patch('game.ai.controller.get_hp_percent', return_value=0.5):
                        controller.update()

            # Should set secondary targets (max 2 since max_targets=3 and 1 is primary)
            mock_ship.set_secondary_targets.assert_called()
            secondary_call = mock_ship.set_secondary_targets.call_args[0][0]
            assert len(secondary_call) <= 2

    def test_no_secondary_targets_without_multiplex(self, mock_ship, mock_grid):
        """Ship without multiplex tracking gets empty secondary targets."""
        from game.ai.controller import AIController

        mock_ship.get_max_targets.return_value = 1  # No multiplex

        target = Mock()
        target.is_alive = True
        target.position = Vector2(200, 100)
        mock_ship.get_current_target.return_value = target

        with patch('game.ai.controller.get_default_strategy_manager') as mock_sm:
            instance = Mock()
            instance.resolve_strategy.return_value = {
                'definition': {},
                'targeting': {'rules': []},
                'movement': {'behavior': 'kite', 'retreat_hp_threshold': 0.1}
            }
            mock_sm.return_value = instance

            controller = AIController(mock_ship, mock_grid, enemy_team_id=1)

            with patch('game.ai.controller.get_hp_percent', return_value=0.5):
                controller.update()

            # Should set empty secondary targets
            mock_ship.set_secondary_targets.assert_called_with([])


class TestCheckAvoidance:
    """TCG-FND-007: Tests for check_avoidance() collision detection logic."""

    def test_avoidance_returns_none_when_no_threats(self, mock_ship, mock_grid, mock_strategy_manager):
        """No nearby objects returns None."""
        from game.ai.controller import AIController

        mock_grid.query_radius.return_value = []
        mock_grid.query_radius_exact.return_value = []

        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)
        result = controller.check_avoidance()

        assert result is None

    def test_avoidance_skips_self_via_adapter(self, mock_ship, mock_grid, mock_strategy_manager):
        """Self is excluded via adapter unwrapping."""
        from game.ai.controller import AIController
        from game.ai.interfaces.controllable import ShipControllableAdapter

        # The ship adapter wraps a raw ship - use spec to pass isinstance check
        raw_ship = Mock()
        mock_adapter = Mock(spec=ShipControllableAdapter)
        mock_adapter.ship = raw_ship
        mock_adapter.get_position.return_value = Vector2(100, 100)
        mock_adapter.get_radius.return_value = 10.0

        # Grid returns the raw ship (which should be skipped as self)
        raw_ship.is_alive = True
        raw_ship.position = Vector2(100.0, 100.0)
        mock_grid.query_radius.return_value = [raw_ship]
        mock_grid.query_radius_exact.return_value = [raw_ship]

        controller = AIController(mock_adapter, mock_grid, enemy_team_id=1)
        result = controller.check_avoidance()

        # Should return None because raw_ship is self
        assert result is None

    def test_avoidance_skips_dead_objects(self, mock_ship, mock_grid, mock_strategy_manager):
        """Dead objects are skipped."""
        from game.ai.controller import AIController

        dead_ship = Mock()
        dead_ship.is_alive = False
        dead_ship.position = Vector2(110.0, 100.0)

        mock_grid.query_radius.return_value = [dead_ship]
        mock_grid.query_radius_exact.return_value = [dead_ship]

        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)
        result = controller.check_avoidance()

        assert result is None

    def test_avoidance_skips_non_combatants(self, mock_ship, mock_grid, mock_strategy_manager):
        """Non-combatant objects are skipped."""
        from game.ai.controller import AIController

        non_combatant = Mock()
        non_combatant.is_alive = True
        non_combatant.position = Vector2(110.0, 100.0)

        mock_grid.query_radius.return_value = [non_combatant]
        mock_grid.query_radius_exact.return_value = [non_combatant]

        with patch('game.ai.controller.is_combatant', return_value=False):
            controller = AIController(mock_ship, mock_grid, enemy_team_id=1)
            result = controller.check_avoidance()

        assert result is None

    def test_avoidance_returns_target_for_close_object(self, mock_ship, mock_grid, mock_strategy_manager):
        """Close object within threshold returns avoidance target."""
        from game.ai.controller import AIController
        from game.core.config import BattleTuning

        close_ship = Mock()
        close_ship.is_alive = True
        close_ship.position = Vector2(115.0, 100.0)  # 15 units away
        close_ship.radius = 10.0

        mock_ship.get_position.return_value = Vector2(100.0, 100.0)
        mock_ship.get_radius.return_value = 10.0

        mock_grid.query_radius.return_value = [close_ship]
        mock_grid.query_radius_exact.return_value = [close_ship]

        with patch('game.ai.controller.is_combatant', return_value=True):
            controller = AIController(mock_ship, mock_grid, enemy_team_id=1)
            result = controller.check_avoidance()

        # Distance 15 < threshold (10 + 10 + COLLISION_BUFFER)
        # Should return an avoidance target position
        assert result is not None
        assert isinstance(result, Vector2)

    def test_avoidance_calculates_correct_direction(self, mock_ship, mock_grid, mock_strategy_manager):
        """Avoidance direction is away from the threat."""
        from game.ai.controller import AIController

        threat = Mock()
        threat.is_alive = True
        threat.position = Vector2(120.0, 100.0)  # East of ship
        threat.radius = 10.0

        mock_ship.get_position.return_value = Vector2(100.0, 100.0)
        mock_ship.get_radius.return_value = 10.0

        mock_grid.query_radius.return_value = [threat]
        mock_grid.query_radius_exact.return_value = [threat]

        with patch('game.ai.controller.is_combatant', return_value=True):
            controller = AIController(mock_ship, mock_grid, enemy_team_id=1)
            result = controller.check_avoidance()

        # Ship at (100, 100), threat at (120, 100)
        # Avoidance should be west of ship (negative x direction)
        assert result is not None
        assert result.x < mock_ship.get_position().x

    def test_avoidance_handles_zero_distance(self, mock_ship, mock_grid, mock_strategy_manager):
        """Zero distance (coincident objects) uses default direction."""
        from game.ai.controller import AIController

        # Object at exact same position
        threat = Mock()
        threat.is_alive = True
        threat.position = Vector2(100.0, 100.0)  # Same as ship!
        threat.radius = 10.0

        mock_ship.get_position.return_value = Vector2(100.0, 100.0)
        mock_ship.get_radius.return_value = 10.0

        mock_grid.query_radius.return_value = [threat]
        mock_grid.query_radius_exact.return_value = [threat]

        with patch('game.ai.controller.is_combatant', return_value=True):
            controller = AIController(mock_ship, mock_grid, enemy_team_id=1)
            result = controller.check_avoidance()

        # Should return a valid position (using default (1, 0) direction)
        assert result is not None
        assert isinstance(result, Vector2)

    def test_avoidance_selects_closest_threat(self, mock_ship, mock_grid, mock_strategy_manager):
        """Multiple threats: avoidance targets closest one."""
        from game.ai.controller import AIController

        close_threat = Mock()
        close_threat.is_alive = True
        close_threat.position = Vector2(115.0, 100.0)  # 15 units away
        close_threat.radius = 10.0

        far_threat = Mock()
        far_threat.is_alive = True
        far_threat.position = Vector2(80.0, 100.0)  # 20 units away (but still in threshold)
        far_threat.radius = 10.0

        mock_ship.get_position.return_value = Vector2(100.0, 100.0)
        mock_ship.get_radius.return_value = 10.0

        mock_grid.query_radius.return_value = [far_threat, close_threat]
        mock_grid.query_radius_exact.return_value = [far_threat, close_threat]

        with patch('game.ai.controller.is_combatant', return_value=True):
            controller = AIController(mock_ship, mock_grid, enemy_team_id=1)
            result = controller.check_avoidance()

        # Should avoid the closer threat (at 115, 100)
        assert result is not None
        # Avoidance should be away from close_threat (west of ship)
        assert result.x < mock_ship.get_position().x


class TestNavigateTo:
    """TCG-FND-008: Tests for navigate_to() angle wrapping and thresholds."""

    def test_navigate_rotates_right_for_clockwise_target(self, mock_ship, mock_grid, mock_strategy_manager):
        """Ship rotates right (positive) when target is clockwise."""
        from game.ai.controller import AIController

        # Ship facing north (90 degrees), target to the east (0 degrees)
        mock_ship.get_position.return_value = Vector2(100.0, 100.0)
        mock_ship.get_rotation.return_value = 90.0
        mock_ship.rotate = Mock()

        target_pos = Vector2(200.0, 100.0)  # East: atan2(0, 100) = 0 degrees

        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)
        controller.navigate_to(target_pos)

        # angle_diff(90, 0) = -90 (need to rotate counterclockwise/left)
        # direction = -1
        mock_ship.rotate.assert_called_with(-1)

    def test_navigate_rotates_left_for_counterclockwise_target(self, mock_ship, mock_grid, mock_strategy_manager):
        """Ship rotates left (negative) when target is counterclockwise."""
        from game.ai.controller import AIController

        # Ship facing east (0 degrees), target to the north (90 degrees)
        mock_ship.get_position.return_value = Vector2(100.0, 100.0)
        mock_ship.get_rotation.return_value = 0.0
        mock_ship.rotate = Mock()

        target_pos = Vector2(100.0, 200.0)  # North: atan2(100, 0) = 90 degrees

        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)
        controller.navigate_to(target_pos)

        # angle_diff(0, 90) = 90 (need to rotate counterclockwise/positive)
        # direction = 1
        mock_ship.rotate.assert_called_with(1)

    def test_navigate_no_rotation_within_5_degrees(self, mock_ship, mock_grid, mock_strategy_manager):
        """No rotation when within 5 degree threshold."""
        from game.ai.controller import AIController

        mock_ship.get_position.return_value = Vector2(100.0, 100.0)
        mock_ship.get_rotation.return_value = 2.0  # Almost facing target
        mock_ship.rotate = Mock()
        mock_ship.thrust_forward = Mock()

        # Target at ~0 degrees (east), ship facing 2 degrees
        target_pos = Vector2(200.0, 100.0)

        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)
        controller.navigate_to(target_pos)

        # angle_diff(2, 0) = -2, abs(-2) < 5
        # Should NOT rotate
        mock_ship.rotate.assert_not_called()

    def test_navigate_thrusts_within_30_degrees(self, mock_ship, mock_grid, mock_strategy_manager):
        """Ship thrusts forward when within 30 degree threshold."""
        from game.ai.controller import AIController

        mock_ship.get_position.return_value = Vector2(100.0, 100.0)
        mock_ship.get_rotation.return_value = 20.0  # Within 30 degrees of target
        mock_ship.rotate = Mock()
        mock_ship.thrust_forward = Mock()

        target_pos = Vector2(200.0, 100.0)  # 0 degrees (east)

        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)
        controller.navigate_to(target_pos)

        # angle_diff(20, 0) = -20, abs(-20) < 30 and distance > 0
        mock_ship.thrust_forward.assert_called()

    def test_navigate_no_thrust_outside_30_degrees(self, mock_ship, mock_grid, mock_strategy_manager):
        """Ship does not thrust when outside 30 degree threshold."""
        from game.ai.controller import AIController

        mock_ship.get_position.return_value = Vector2(100.0, 100.0)
        mock_ship.get_rotation.return_value = 50.0  # 50 degrees from target
        mock_ship.rotate = Mock()
        mock_ship.thrust_forward = Mock()

        target_pos = Vector2(200.0, 100.0)  # 0 degrees (east)

        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)
        controller.navigate_to(target_pos)

        # angle_diff(50, 0) = -50, abs(-50) > 30
        mock_ship.thrust_forward.assert_not_called()

    def test_navigate_angle_wrapping_at_360_boundary(self, mock_ship, mock_grid, mock_strategy_manager):
        """Angle wrapping works correctly at 360/0 boundary."""
        from game.ai.controller import AIController

        mock_ship.get_position.return_value = Vector2(100.0, 100.0)
        mock_ship.get_rotation.return_value = 350.0  # Near 360
        mock_ship.rotate = Mock()
        mock_ship.thrust_forward = Mock()

        # Target slightly past 0 (10 degrees)
        target_pos = Vector2(200.0, 117.63)  # atan2(17.63, 100) ~ 10 degrees

        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)
        controller.navigate_to(target_pos)

        # Ship at 350, target at ~10
        # Shortest path: 350 -> 360/0 -> 10 = 20 degrees counterclockwise
        # angle_diff(350, 10) = 20 (positive = counterclockwise)
        mock_ship.rotate.assert_called_with(1)

    def test_navigate_angle_wrapping_at_180_boundary(self, mock_ship, mock_grid, mock_strategy_manager):
        """Angle wrapping works correctly at 180 boundary."""
        from game.ai.controller import AIController

        mock_ship.get_position.return_value = Vector2(100.0, 100.0)
        mock_ship.get_rotation.return_value = 170.0
        mock_ship.rotate = Mock()
        mock_ship.thrust_forward = Mock()

        # Target at 190 degrees
        target_pos = Vector2(100.0 - 98.48, 100.0 - 17.36)  # ~190 degrees

        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)
        controller.navigate_to(target_pos)

        # angle_diff(170, 190) = 20 (positive)
        mock_ship.rotate.assert_called_with(1)

    def test_navigate_stops_at_stop_distance(self, mock_ship, mock_grid, mock_strategy_manager):
        """No thrust when within stop distance."""
        from game.ai.controller import AIController

        mock_ship.get_position.return_value = Vector2(100.0, 100.0)
        mock_ship.get_rotation.return_value = 0.0
        mock_ship.rotate = Mock()
        mock_ship.thrust_forward = Mock()

        # Target very close
        target_pos = Vector2(105.0, 100.0)  # 5 units away

        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)
        controller.navigate_to(target_pos, stop_dist=10.0)  # Stop at 10 units

        # Distance 5 < stop_dist 10, should not thrust
        mock_ship.thrust_forward.assert_not_called()

    def test_navigate_target_directly_behind(self, mock_ship, mock_grid, mock_strategy_manager):
        """Navigate to target directly behind ship (180 degrees)."""
        from game.ai.controller import AIController

        mock_ship.get_position.return_value = Vector2(100.0, 100.0)
        mock_ship.get_rotation.return_value = 0.0  # Facing east
        mock_ship.rotate = Mock()
        mock_ship.thrust_forward = Mock()

        # Target to the west (180 degrees)
        target_pos = Vector2(0.0, 100.0)  # atan2(0, -100) = 180 degrees

        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)
        controller.navigate_to(target_pos)

        # angle_diff(0, 180) = 180 or -180
        # Either rotation direction is valid at exactly 180
        mock_ship.rotate.assert_called()
        # Should NOT thrust (abs(180) > 30)
        mock_ship.thrust_forward.assert_not_called()

    def test_navigate_target_at_same_position(self, mock_ship, mock_grid, mock_strategy_manager):
        """Navigate to target at same position (zero distance)."""
        from game.ai.controller import AIController

        mock_ship.get_position.return_value = Vector2(100.0, 100.0)
        mock_ship.get_rotation.return_value = 0.0
        mock_ship.rotate = Mock()
        mock_ship.thrust_forward = Mock()

        # Target at same position
        target_pos = Vector2(100.0, 100.0)

        controller = AIController(mock_ship, mock_grid, enemy_team_id=1)
        controller.navigate_to(target_pos)

        # atan2(0, 0) = 0, so target_angle = 0
        # distance = 0, so no thrust (0 > 0 is False)
        mock_ship.thrust_forward.assert_not_called()
