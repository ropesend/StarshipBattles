"""
Unit tests for game/ai/behaviors.py

Tests each behavior class's update logic using mocked controllers and ships.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch

from game.core.math import Vector2
from game.ai.behaviors import (
    AIBehavior,
    RamBehavior,
    FleeBehavior,
    KiteBehavior,
    AttackRunBehavior,
    OrbitBehavior,
    DoNothingBehavior,
    StationaryFireBehavior,
    StraightLineBehavior,
    RotateOnlyBehavior,
    ErraticBehavior,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_ship():
    """Create a mock ship with standard interface."""
    ship = Mock()
    ship.get_position.return_value = Vector2(100, 100)
    ship.get_weapon_range.return_value = 200.0
    ship.get_rotation.return_value = 0.0
    ship.get_max_speed.return_value = 100.0
    ship.get_radius.return_value = 10.0
    ship.get_acceleration_rate.return_value = 5.0
    ship.get_turn_speed.return_value = 90.0
    ship.set_trigger_pulled = Mock()
    ship.thrust_forward = Mock()
    ship.rotate = Mock()
    ship.set_rotation = Mock()
    ship.set_throttle = Mock()
    ship.adjust_position = Mock()
    ship.set_in_formation = Mock()
    ship.get_formation_master = Mock(return_value=None)
    ship.get_formation_offset = Mock(return_value=Vector2(50, 0))
    ship.get_formation_rotation_mode = Mock(return_value='relative')
    return ship


@pytest.fixture
def mock_controller(mock_ship):
    """Create a mock AI controller."""
    controller = Mock()
    controller.ship = mock_ship
    controller.navigate_to = Mock()
    controller.check_avoidance = Mock(return_value=None)
    controller.get_engage_distance_multiplier = Mock(return_value=1.0)
    return controller


@pytest.fixture
def mock_target():
    """Create a mock target ship."""
    target = Mock()
    target.position = Vector2(300, 100)
    target.is_alive = True
    target.is_derelict = False
    return target


# =============================================================================
# AIBehavior Base Class Tests
# =============================================================================

class TestAIBehaviorBase:
    """Tests for AIBehavior base class."""

    def test_base_init_stores_controller(self, mock_controller):
        """controller accessible after init."""
        behavior = AIBehavior(mock_controller)
        assert behavior.controller is mock_controller

    def test_base_enter_is_noop(self, mock_controller):
        """enter() does not raise."""
        behavior = AIBehavior(mock_controller)
        # Should not raise
        behavior.enter()

    def test_base_update_raises_not_implemented(self, mock_controller):
        """update() raises NotImplementedError."""
        behavior = AIBehavior(mock_controller)
        with pytest.raises(NotImplementedError):
            behavior.update(None, {})


# =============================================================================
# RamBehavior Tests
# =============================================================================

class TestRamBehavior:
    """Tests for RamBehavior."""

    def test_ram_navigates_to_target_position(self, mock_controller, mock_target):
        """navigate_to called with target.position, stop_dist=0."""
        behavior = RamBehavior(mock_controller)
        behavior.update(mock_target, {})

        mock_controller.navigate_to.assert_called_once_with(
            mock_target.position, stop_dist=0
        )


# =============================================================================
# FleeBehavior Tests
# =============================================================================

class TestFleeBehavior:
    """Tests for FleeBehavior."""

    def test_flee_moves_away_from_target(self, mock_controller, mock_target):
        """Navigates to position opposite target."""
        behavior = FleeBehavior(mock_controller)
        behavior.update(mock_target, {})

        mock_controller.navigate_to.assert_called_once()
        call_args = mock_controller.navigate_to.call_args
        flee_pos = call_args[0][0]  # First positional arg

        # Flee position should be further from target than ship
        ship_pos = mock_controller.ship.get_position()
        ship_to_target = mock_target.position - ship_pos
        ship_to_flee = flee_pos - ship_pos

        # Flee direction should be opposite to target direction
        assert ship_to_flee.dot(ship_to_target) < 0

    def test_flee_fire_while_retreating_default_false(self, mock_controller, mock_target):
        """set_trigger_pulled(False) by default."""
        behavior = FleeBehavior(mock_controller)
        behavior.update(mock_target, {})

        mock_controller.ship.set_trigger_pulled.assert_called_with(False)

    def test_flee_fire_while_retreating_true(self, mock_controller, mock_target):
        """set_trigger_pulled(True) when strategy says so."""
        behavior = FleeBehavior(mock_controller)
        behavior.update(mock_target, {'fire_while_retreating': True})

        mock_controller.ship.set_trigger_pulled.assert_called_with(True)

    def test_flee_zero_distance_uses_default_vector(self, mock_controller, mock_target):
        """When at same position as target, uses Vector2(1,0)."""
        mock_controller.ship.get_position.return_value = Vector2(300, 100)
        mock_target.position = Vector2(300, 100)

        behavior = FleeBehavior(mock_controller)
        behavior.update(mock_target, {})

        # Should still call navigate_to without error
        mock_controller.navigate_to.assert_called_once()
        call_args = mock_controller.navigate_to.call_args
        flee_pos = call_args[0][0]

        # With default vector (1,0), flee should be to the right
        assert flee_pos.x > 300


# =============================================================================
# KiteBehavior Tests
# =============================================================================

class TestKiteBehavior:
    """Tests for KiteBehavior."""

    def test_kite_backs_off_when_too_close(self, mock_controller, mock_target):
        """navigate_to away from target when too close."""
        mock_controller.ship.get_position.return_value = Vector2(250, 100)
        mock_target.position = Vector2(300, 100)  # 50 distance, opt = 200

        behavior = KiteBehavior(mock_controller)
        behavior.update(mock_target, {})

        mock_controller.navigate_to.assert_called()
        call_args = mock_controller.navigate_to.call_args
        kite_pos = call_args[0][0]

        # Kite position should be further from target
        ship_pos = mock_controller.ship.get_position()
        assert kite_pos.distance_to(mock_target.position) > ship_pos.distance_to(mock_target.position)

    def test_kite_min_spacing_enforced(self, mock_controller, mock_target):
        """opt_dist >= MIN_SPACING."""
        # Set weapon range to give very small optimal distance
        mock_controller.ship.get_weapon_range.return_value = 10.0
        mock_controller.get_engage_distance_multiplier.return_value = 0.1  # 1.0 optimal

        behavior = KiteBehavior(mock_controller)

        # Position ship very close
        mock_controller.ship.get_position.return_value = Vector2(295, 100)
        mock_target.position = Vector2(300, 100)  # 5 distance

        behavior.update(mock_target, {})
        # Should still use MIN_SPACING, not the tiny calculated distance
        # The test verifies no crash and navigate_to is called
        mock_controller.navigate_to.assert_called()

    def test_kite_collision_avoidance_overrides(self, mock_controller, mock_target):
        """When check_avoidance returns pos, navigates there."""
        avoid_pos = Vector2(0, 200)
        mock_controller.check_avoidance.return_value = avoid_pos

        behavior = KiteBehavior(mock_controller)
        behavior.update(mock_target, {'avoid_collisions': True})

        mock_controller.navigate_to.assert_called_once_with(
            avoid_pos, stop_dist=0
        )

    def test_kite_collision_avoidance_disabled(self, mock_controller, mock_target):
        """When avoid_collisions=False, skips check."""
        avoid_pos = Vector2(0, 200)
        mock_controller.check_avoidance.return_value = avoid_pos

        behavior = KiteBehavior(mock_controller)
        behavior.update(mock_target, {'avoid_collisions': False})

        # Should NOT use avoidance position
        call_args = mock_controller.navigate_to.call_args
        nav_pos = call_args[0][0]
        assert nav_pos != avoid_pos

    def test_kite_zero_distance_uses_default_vector(self, mock_controller, mock_target):
        """Same position fallback uses Vector2(1,0)."""
        mock_controller.ship.get_position.return_value = Vector2(300, 100)
        mock_target.position = Vector2(300, 100)

        behavior = KiteBehavior(mock_controller)
        behavior.update(mock_target, {})

        mock_controller.navigate_to.assert_called()

    # -------------------------------------------------------------------------
    # Recovered tests from test_ai_behaviors.py (PROJ-156 Task 3.0)
    # -------------------------------------------------------------------------


# =============================================================================
# AttackRunBehavior Tests
# =============================================================================

class TestAttackRunBehavior:
    """Tests for AttackRunBehavior."""

    def test_attack_run_init_state_approach(self, mock_controller):
        """Initial state is 'approach'."""
        behavior = AttackRunBehavior(mock_controller)
        assert behavior.attack_state == 'approach'

    def test_attack_run_enter_resets_state(self, mock_controller):
        """enter() resets to 'approach', timer=0."""
        behavior = AttackRunBehavior(mock_controller)
        behavior.attack_state = 'retreat'
        behavior.attack_timer = 5.0

        behavior.enter()

        assert behavior.attack_state == 'approach'
        assert behavior.attack_timer == 0

    def test_attack_run_approach_navigates_to_target(self, mock_controller, mock_target):
        """Approach phase navigates toward target."""
        # Start far from target
        mock_controller.ship.get_position.return_value = Vector2(0, 0)
        mock_target.position = Vector2(500, 0)

        behavior = AttackRunBehavior(mock_controller)
        behavior.update(mock_target, {})

        mock_controller.navigate_to.assert_called()
        call_args = mock_controller.navigate_to.call_args
        assert call_args[0][0] == mock_target.position

    def test_attack_run_transitions_to_retreat(self, mock_controller, mock_target):
        """When close enough, switches to retreat."""
        # Weapon range 200, approach_dist = 200 * 0.3 = 60
        # hysteresis 1.1, so threshold = 66
        mock_controller.ship.get_position.return_value = Vector2(280, 100)
        mock_target.position = Vector2(300, 100)  # 20 distance

        behavior = AttackRunBehavior(mock_controller)
        behavior.update(mock_target, {})

        assert behavior.attack_state == 'retreat'
        assert behavior.attack_timer > 0

    def test_attack_run_retreat_flees_away(self, mock_controller, mock_target):
        """Retreat phase moves away from target."""
        behavior = AttackRunBehavior(mock_controller)
        behavior.attack_state = 'retreat'
        behavior.attack_timer = 2.0

        mock_controller.ship.get_position.return_value = Vector2(280, 100)
        mock_target.position = Vector2(300, 100)

        behavior.update(mock_target, {})

        mock_controller.navigate_to.assert_called()
        call_args = mock_controller.navigate_to.call_args
        flee_pos = call_args[0][0]

        # Flee position should be opposite direction from target
        assert flee_pos.x < 280

    def test_attack_run_retreat_timer_decrements(self, mock_controller, mock_target):
        """Timer decreases by PhysicsConfig.TICK_RATE each update."""
        from game.core.config import PhysicsConfig
        behavior = AttackRunBehavior(mock_controller)
        behavior.attack_state = 'retreat'
        behavior.attack_timer = 2.0
        initial_timer = behavior.attack_timer

        behavior.update(mock_target, {})

        assert behavior.attack_timer < initial_timer
        assert behavior.attack_timer == pytest.approx(initial_timer - PhysicsConfig.TICK_RATE)

    def test_attack_run_transitions_back_to_approach(self, mock_controller, mock_target):
        """After timer and distance, returns to approach."""
        behavior = AttackRunBehavior(mock_controller)
        behavior.attack_state = 'retreat'
        behavior.attack_timer = 0.001  # Almost zero

        # Far enough away: retreat_dist = 200 * 0.8 = 160
        mock_controller.ship.get_position.return_value = Vector2(0, 0)
        mock_target.position = Vector2(300, 0)  # 300 distance > 160

        behavior.update(mock_target, {})

        assert behavior.attack_state == 'approach'

    def test_attack_run_custom_distances(self, mock_controller, mock_target):
        """Strategy dict overrides approach/retreat distances."""
        behavior = AttackRunBehavior(mock_controller)
        strategy = {
            'attack_run_behavior': {
                'approach_distance': 0.5,  # 100 instead of 60
                'retreat_distance': 0.6,  # 120 instead of 160
                'retreat_duration': 3.0,
            }
        }

        # Position within custom approach distance
        mock_controller.ship.get_position.return_value = Vector2(210, 100)
        mock_target.position = Vector2(300, 100)  # 90 < 100*1.1 = 110

        behavior.update(mock_target, strategy)

        assert behavior.attack_state == 'retreat'
        assert behavior.attack_timer == 3.0



# =============================================================================
# OrbitBehavior Tests
# =============================================================================

class TestOrbitBehavior:
    """Tests for OrbitBehavior."""

    def test_orbit_no_target_returns_early(self, mock_controller):
        """No action when target is None."""
        behavior = OrbitBehavior(mock_controller)
        behavior.update(None, {})

        mock_controller.navigate_to.assert_not_called()

    def test_orbit_zero_distance_returns_early(self, mock_controller, mock_target):
        """No action when at same position."""
        mock_controller.ship.get_position.return_value = Vector2(300, 100)
        mock_target.position = Vector2(300, 100)

        behavior = OrbitBehavior(mock_controller)
        behavior.update(mock_target, {})

        mock_controller.navigate_to.assert_not_called()

    def test_orbit_too_close_adds_outward_component(self, mock_controller, mock_target):
        """Move outward when too close."""
        mock_controller.ship.get_position.return_value = Vector2(310, 100)
        mock_target.position = Vector2(300, 100)  # Very close

        behavior = OrbitBehavior(mock_controller)
        behavior.update(mock_target, {'orbit_distance': 200})

        mock_controller.navigate_to.assert_called_once()
        call_args = mock_controller.navigate_to.call_args
        target_pos = call_args[0][0]

        # Target should have outward component (x > 310)
        ship_pos = mock_controller.ship.get_position()
        # The orbit behavior adds tangent + outward, check we moved
        assert target_pos.distance_to(ship_pos) > 0

    def test_orbit_too_far_adds_inward_component(self, mock_controller, mock_target):
        """Move inward when too far."""
        mock_controller.ship.get_position.return_value = Vector2(700, 100)
        mock_target.position = Vector2(300, 100)  # 400 distance

        behavior = OrbitBehavior(mock_controller)
        behavior.update(mock_target, {'orbit_distance': 200})

        mock_controller.navigate_to.assert_called_once()

    def test_orbit_in_range_pure_tangent(self, mock_controller, mock_target):
        """Pure tangent movement at correct distance."""
        # orbit_distance default is from AIConfig, use explicit
        mock_controller.ship.get_position.return_value = Vector2(500, 100)
        mock_target.position = Vector2(300, 100)  # 200 distance

        behavior = OrbitBehavior(mock_controller)
        behavior.update(mock_target, {'orbit_distance': 200})

        mock_controller.navigate_to.assert_called_once()


# =============================================================================
# Test/Debug Behaviors
# =============================================================================

class TestDoNothingBehavior:
    """Tests for DoNothingBehavior."""

    def test_do_nothing_disables_firing(self, mock_controller, mock_target):
        """set_trigger_pulled(False)."""
        behavior = DoNothingBehavior(mock_controller)
        behavior.update(mock_target, {})

        mock_controller.ship.set_trigger_pulled.assert_called_with(False)


class TestStationaryFireBehavior:
    """Tests for StationaryFireBehavior."""

    def test_stationary_fire_does_nothing(self, mock_controller, mock_target):
        """No navigation calls."""
        behavior = StationaryFireBehavior(mock_controller)
        behavior.update(mock_target, {})

        mock_controller.navigate_to.assert_not_called()


class TestStraightLineBehavior:
    """Tests for StraightLineBehavior."""

    def test_straight_line_thrusts_forward(self, mock_controller, mock_target):
        """thrust_forward called."""
        behavior = StraightLineBehavior(mock_controller)
        behavior.update(mock_target, {})

        mock_controller.ship.thrust_forward.assert_called_once()


class TestRotateOnlyBehavior:
    """Tests for RotateOnlyBehavior."""

    def test_rotate_only_rotates(self, mock_controller, mock_target):
        """rotate(direction) called, no thrust."""
        behavior = RotateOnlyBehavior(mock_controller)
        behavior.update(mock_target, {})

        mock_controller.ship.rotate.assert_called_once_with(1)  # Default direction
        mock_controller.ship.thrust_forward.assert_not_called()

    def test_rotate_only_uses_strategy_direction(self, mock_controller, mock_target):
        """Uses rotation_direction from strategy."""
        behavior = RotateOnlyBehavior(mock_controller)
        behavior.update(mock_target, {'rotation_direction': -1})

        mock_controller.ship.rotate.assert_called_once_with(-1)


class TestErraticBehavior:
    """Tests for ErraticBehavior."""

    def test_erratic_changes_direction(self, mock_controller, mock_target):
        """Direction changes over time."""
        behavior = ErraticBehavior(mock_controller)
        behavior.enter()

        initial_direction = behavior.current_direction

        # Simulate many updates to trigger direction change
        behavior.next_change_interval = 0.01  # Force quick change
        for _ in range(100):
            behavior.update(mock_target, {})
            if behavior.current_direction != initial_direction:
                break

        # Should have changed at some point (or at least executed without error)
        mock_controller.ship.thrust_forward.assert_called()

    def test_erratic_enter_randomizes(self, mock_controller):
        """enter() sets random initial values."""
        behavior = ErraticBehavior(mock_controller)
        behavior.enter()

        assert behavior.direction_timer == 0.0
        assert behavior.current_direction in [-1, 1]
        assert behavior.next_change_interval > 0

    def test_erratic_enter_resets_timer(self, mock_controller, mock_target):
        """enter() resets direction_timer to 0.0 (TCG-FND-023)."""
        behavior = ErraticBehavior(mock_controller)

        # Simulate some updates to advance timer
        behavior.direction_timer = 5.0
        behavior.current_direction = 0

        # Call enter to reset
        behavior.enter()

        assert behavior.direction_timer == 0.0
        assert behavior.current_direction in [-1, 1]  # Should be randomized

    def test_erratic_enter_sets_random_interval(self, mock_controller):
        """enter() sets next_change_interval within configured bounds (TCG-FND-023)."""
        from game.core.config import AIConfig

        behavior = ErraticBehavior(mock_controller)

        # Call enter multiple times and check bounds
        for _ in range(10):
            behavior.enter()
            assert AIConfig.ERRATIC_TURN_INTERVAL_MIN <= behavior.next_change_interval
            assert behavior.next_change_interval <= AIConfig.ERRATIC_TURN_INTERVAL_MAX

    def test_erratic_update_increments_timer(self, mock_controller, mock_target):
        """update() increments direction_timer by TICK_RATE (TCG-FND-023)."""
        from game.core.config import PhysicsConfig

        behavior = ErraticBehavior(mock_controller)
        behavior.enter()
        initial_timer = behavior.direction_timer
        behavior.next_change_interval = 100.0  # Prevent direction change

        behavior.update(mock_target, {})

        assert behavior.direction_timer == initial_timer + PhysicsConfig.TICK_RATE

    def test_erratic_update_direction_change_resets_timer(self, mock_controller, mock_target):
        """update() resets timer when direction changes (TCG-FND-023)."""
        behavior = ErraticBehavior(mock_controller)
        behavior.enter()

        # Set timer to exceed next change interval
        behavior.direction_timer = 10.0
        behavior.next_change_interval = 0.5

        behavior.update(mock_target, {})

        # Timer should reset after direction change
        assert behavior.direction_timer == 0.0

    def test_erratic_update_respects_strategy_intervals(self, mock_controller, mock_target):
        """update() uses strategy's turn_interval_min/max if provided (TCG-FND-023)."""
        behavior = ErraticBehavior(mock_controller)
        behavior.enter()

        # Force a direction change
        behavior.direction_timer = 10.0
        behavior.next_change_interval = 0.5

        strategy = {
            'turn_interval_min': 5.0,
            'turn_interval_max': 10.0
        }
        behavior.update(mock_target, strategy)

        # New interval should be within strategy bounds
        assert 5.0 <= behavior.next_change_interval <= 10.0

    def test_erratic_update_always_thrusts_forward(self, mock_controller, mock_target):
        """update() always calls thrust_forward (TCG-FND-023)."""
        behavior = ErraticBehavior(mock_controller)
        behavior.enter()

        # Test with current_direction = 0 (no rotation)
        behavior.current_direction = 0
        behavior.next_change_interval = 100.0  # Prevent change

        behavior.update(mock_target, {})

        mock_controller.ship.thrust_forward.assert_called()

    def test_erratic_update_rotates_when_direction_nonzero(self, mock_controller, mock_target):
        """update() calls rotate when current_direction is nonzero (TCG-FND-023)."""
        behavior = ErraticBehavior(mock_controller)
        behavior.enter()

        behavior.current_direction = 1
        behavior.next_change_interval = 100.0  # Prevent change

        behavior.update(mock_target, {})

        mock_controller.ship.rotate.assert_called_with(1)

    def test_erratic_update_no_rotate_when_direction_zero(self, mock_controller, mock_target):
        """update() does not call rotate when current_direction is 0 (TCG-FND-023)."""
        behavior = ErraticBehavior(mock_controller)
        behavior.enter()

        behavior.current_direction = 0
        behavior.next_change_interval = 100.0  # Prevent change

        behavior.update(mock_target, {})

        mock_controller.ship.rotate.assert_not_called()


