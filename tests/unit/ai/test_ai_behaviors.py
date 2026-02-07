import pytest
import pygame
from unittest.mock import MagicMock, patch

from game.ai.behaviors import KiteBehavior, FormationBehavior, RamBehavior


@pytest.fixture
def kite_setup():
    controller = MagicMock()
    ship = MagicMock()
    target = MagicMock()
    controller.ship = ship

    # Default mock values - both direct attributes and interface methods
    ship.position = pygame.math.Vector2(0, 0)
    ship.max_weapon_range = 1000
    target.position = pygame.math.Vector2(2000, 0)  # Far away initially

    # Interface method mocks
    ship.get_position.return_value = ship.position
    ship.get_weapon_range.return_value = ship.max_weapon_range

    behavior = KiteBehavior(controller)
    strategy = {'avoid_collisions': True}

    # Ensure check_avoidance returns None by default so it doesn't trigger
    controller.check_avoidance.return_value = None

    yield {
        'controller': controller,
        'ship': ship,
        'target': target,
        'behavior': behavior,
        'strategy': strategy
    }

    pygame.quit()


class TestKiteBehavior:

    def test_opt_dist_calculation(self, kite_setup):
        """Verify optimal distance calculation based on engage multiplier."""
        # Setup controller to return specific multiplier
        kite_setup['controller'].get_engage_distance_multiplier.return_value = 0.8

        # Run update
        kite_setup['behavior'].update(kite_setup['target'], kite_setup['strategy'])

        # Check that get_engage_distance_multiplier was called
        kite_setup['controller'].get_engage_distance_multiplier.assert_called_with(kite_setup['strategy'])

        # Expected opt_dist is 1000 * 0.8 = 800
        # Since dist (2000) > opt_dist (800), it should call navigate_to with stop_dist=opt_dist
        kite_setup['controller'].navigate_to.assert_called_with(
            kite_setup['target'].position,
            stop_dist=800.0,
            precise=True
        )

    def test_opt_dist_min_clamp(self, kite_setup):
        """Verify optimal distance is clamped to minimum 150."""
        kite_setup['controller'].get_engage_distance_multiplier.return_value = 0.1
        # max_range 1000 * 0.1 = 100. Should clamp to 150.

        kite_setup['behavior'].update(kite_setup['target'], kite_setup['strategy'])

        kite_setup['controller'].navigate_to.assert_called_with(
            kite_setup['target'].position,
            stop_dist=150,
            precise=True
        )

    def test_branching_close_in(self, kite_setup):
        """Behavior should close in when distance > optimal."""
        kite_setup['controller'].get_engage_distance_multiplier.return_value = 0.5  # opt_dist = 500
        kite_setup['target'].position = pygame.math.Vector2(1000, 0)  # dist = 1000

        kite_setup['behavior'].update(kite_setup['target'], kite_setup['strategy'])

        # Should navigate TO target with stop_dist = opt_dist
        kite_setup['controller'].navigate_to.assert_called_with(
            kite_setup['target'].position,
            stop_dist=500.0,
            precise=True
        )

    def test_branching_kite_maintain(self, kite_setup):
        """Behavior should kite (back away) when distance <= optimal."""
        kite_setup['controller'].get_engage_distance_multiplier.return_value = 0.5  # opt_dist = 500
        kite_setup['target'].position = pygame.math.Vector2(300, 0)  # dist = 300 (too close)

        # Vector from target to ship is (-300, 0) if ship is at 0,0 and target at 300,0?
        # Wait, ship is at 0,0. Target at 300,0.
        # Vector ship - target = (-300, 0). Normalize -> (-1, 0).
        # Kite pos = target.position (300,0) + (-1,0 * 500) = (300-500, 0) = (-200, 0).
        # Wait, let's re-read the code logic.
        # vec = ship.pos - target.pos
        # kite_pos = target.position + vec.normalize() * opt_dist

        kite_setup['behavior'].update(kite_setup['target'], kite_setup['strategy'])

        # Calculate expected position
        # ship(0,0), target(300,0) -> vec(-300, 0) -> norm(-1, 0)
        # kite_pos = (300,0) + (-1, 0)*500 = (-200, 0)

        # Verify call
        args, kwargs = kite_setup['controller'].navigate_to.call_args
        target_pos = args[0]
        assert target_pos == pygame.math.Vector2(-200, 0)
        assert kwargs['stop_dist'] == 0
        assert kwargs['precise'] is True

    def test_collision_avoidance_trigger(self, kite_setup):
        """Verify collision avoidance overrides kiting logic."""
        kite_setup['controller'].check_avoidance.return_value = pygame.math.Vector2(50, 50)

        kite_setup['behavior'].update(kite_setup['target'], kite_setup['strategy'])

        kite_setup['controller'].check_avoidance.assert_called()
        kite_setup['controller'].navigate_to.assert_called_with(
            pygame.math.Vector2(50, 50),
            stop_dist=0,
            precise=False
        )

    def test_collision_avoidance_disabled(self, kite_setup):
        """Verify avoidance check is skipped if strategy disables it."""
        kite_setup['strategy']['avoid_collisions'] = False
        kite_setup['controller'].get_engage_distance_multiplier.return_value = 1.0

        kite_setup['behavior'].update(kite_setup['target'], kite_setup['strategy'])

        kite_setup['controller'].check_avoidance.assert_not_called()


@pytest.fixture
def formation_setup():
    controller = MagicMock()
    ship = MagicMock()
    master = MagicMock()

    controller.ship = ship
    ship.formation.master = master

    # Defaults
    ship.position = pygame.math.Vector2(100, 100)
    ship.angle = 0
    ship.radius = 10
    ship.acceleration_rate = 5
    ship.turn_speed = 10
    ship.turn_throttle = 1.0
    ship.max_speed = 100
    ship.engine_throttle = 1.0
    ship.formation.offset = pygame.math.Vector2(50, 0)
    ship.formation.rotation_mode = 'relative'

    # Interface method mocks
    ship.get_position.return_value = ship.position
    ship.get_rotation.return_value = ship.angle
    ship.get_radius.return_value = ship.radius
    ship.get_acceleration_rate.return_value = ship.acceleration_rate
    ship.get_turn_speed.return_value = ship.turn_speed
    ship.get_max_speed.return_value = ship.max_speed
    ship.get_formation_offset.return_value = ship.formation.offset
    ship.get_formation_rotation_mode.return_value = ship.formation.rotation_mode
    ship.get_formation_master.return_value = master

    # Interface setters that update mock attributes
    def set_in_formation(value):
        ship.formation.active = value
    ship.set_in_formation.side_effect = set_in_formation

    def set_throttle(value):
        ship.engine_throttle = value
    ship.set_throttle.side_effect = set_throttle

    def set_rotation(value):
        ship.angle = value
    ship.set_rotation.side_effect = set_rotation

    def adjust_position(delta):
        ship.position = ship.position + delta
        ship.get_position.return_value = ship.position
    ship.adjust_position.side_effect = adjust_position

    master.is_alive = True
    master.is_derelict = False
    master.position = pygame.math.Vector2(0, 0)  # Master at 0,0
    master.angle = 0
    master.current_speed = 0
    master.is_thrusting = False
    master.engine_throttle = 0

    behavior = FormationBehavior(controller)
    strategy = {}

    return {
        'controller': controller,
        'ship': ship,
        'master': master,
        'behavior': behavior,
        'strategy': strategy
    }


class TestFormationBehavior:

    def test_abandon_if_master_invalid(self, formation_setup):
        """Should set in_formation False if master dead or missing."""
        formation_setup['master'].is_alive = False
        formation_setup['behavior'].update(None, formation_setup['strategy'])
        assert formation_setup['ship'].formation.active is False

    def test_target_pos_fixed_rotation(self, formation_setup):
        """Verify target position calculation for fixed rotation."""
        formation_setup['ship'].formation.rotation_mode = 'fixed'
        formation_setup['ship'].get_formation_rotation_mode.return_value = 'fixed'
        formation_setup['ship'].formation.offset = pygame.math.Vector2(50, 50)
        formation_setup['ship'].get_formation_offset.return_value = pygame.math.Vector2(50, 50)
        formation_setup['master'].position = pygame.math.Vector2(100, 100)
        formation_setup['master'].angle = 90  # Should ignore this for offset

        # We need to simulate the ship being far away so it hits the "Navigate" logic
        # allowing us to verify the target_pos calculation passed to navigate_to is NOT affected by master angle
        # Actually logic splits: if far -> navigate. if close -> drift.
        # Let's put ship far away.
        formation_setup['ship'].position = pygame.math.Vector2(5000, 5000)
        formation_setup['ship'].get_position.return_value = pygame.math.Vector2(5000, 5000)

        formation_setup['behavior'].update(None, formation_setup['strategy'])

        # Navigate logic uses prediction (master pos + velocity predict + offset)
        # Master speed 0 -> prediction is 0.
        # So target = master.pos (100,100) + offset (50,50) = 150, 150.

        args, _ = formation_setup['controller'].navigate_to.call_args
        target_pos = args[0]
        assert target_pos == pygame.math.Vector2(150, 150)

    def test_target_pos_relative_rotation(self, formation_setup):
        """Verify target position calculation for relative rotation."""
        formation_setup['ship'].formation.rotation_mode = 'relative'
        formation_setup['ship'].get_formation_rotation_mode.return_value = 'relative'
        # Offset is (50, 0) relative to master.
        formation_setup['ship'].formation.offset = pygame.math.Vector2(50, 0)
        formation_setup['ship'].get_formation_offset.return_value = pygame.math.Vector2(50, 0)
        formation_setup['master'].position = pygame.math.Vector2(100, 100)
        formation_setup['master'].angle = 90  # Facing down

        # Relative means offset rotates with master. (50, 0) rotated 90 deg -> (0, 50).
        # Target should be (100, 100) + (0, 50) = (100, 150).

        formation_setup['ship'].position = pygame.math.Vector2(5000, 5000)  # Force navigate logic
        formation_setup['ship'].get_position.return_value = pygame.math.Vector2(5000, 5000)

        formation_setup['behavior'].update(None, formation_setup['strategy'])

        args, _ = formation_setup['controller'].navigate_to.call_args
        target_pos = args[0]
        assert target_pos.x == pytest.approx(100)
        assert target_pos.y == pytest.approx(150)

    def test_drift_logic_correction(self, formation_setup):
        """Verify small error triggers drift correction logic."""
        # Set up scenario where we are CLOSE to target spot
        formation_setup['master'].position = pygame.math.Vector2(0, 0)
        formation_setup['master'].angle = 0
        formation_setup['ship'].formation.offset = pygame.math.Vector2(50, 0)
        formation_setup['ship'].get_formation_offset.return_value = pygame.math.Vector2(50, 0)
        # Target is (50,0). Ship is at (55, 0). Error 5.
        formation_setup['ship'].position = pygame.math.Vector2(55, 0)
        formation_setup['ship'].get_position.return_value = pygame.math.Vector2(55, 0)

        # Drift threshold check:
        # diameter = radius(10)*2 = 20.
        # accel(5)*1.2 = 6.
        # Threshold = 20. Dist 5 is <= 20. -> Enter Drift Logic.

        formation_setup['behavior'].update(None, formation_setup['strategy'])

        # Verify navigate_to NOT called
        formation_setup['controller'].navigate_to.assert_not_called()

        # Verify position updated (spring correction via adjust_position)
        # Future master pos = 0,0. Future offset = 50,0. Future target = 50,0.
        # Vec to spot = (50,0) - (55,0) = (-5, 0).
        # Correction = (-5, 0) * 0.2 = (-1, 0).
        # New pos should be (55,0) + (-1,0) = (54,0).
        formation_setup['ship'].adjust_position.assert_called()
        assert formation_setup['ship'].position.x < 55  # Moved left
        assert formation_setup['ship'].position.y == 0

    def test_velocity_sync(self, formation_setup):
        """Verify engine throttle is synced with master."""
        # Setup drift scenario
        formation_setup['master'].position = pygame.math.Vector2(0, 0)
        formation_setup['ship'].position = pygame.math.Vector2(50, 0)  # Target spot
        formation_setup['ship'].get_position.return_value = pygame.math.Vector2(50, 0)
        formation_setup['ship'].formation.offset = pygame.math.Vector2(50, 0)
        formation_setup['ship'].get_formation_offset.return_value = pygame.math.Vector2(50, 0)

        # Master is moving
        formation_setup['master'].is_thrusting = True
        formation_setup['master'].max_speed = 200
        formation_setup['master'].engine_throttle = 0.5
        # Master current target speed = 100.

        formation_setup['ship'].max_speed = 100
        formation_setup['ship'].get_max_speed.return_value = 100

        formation_setup['behavior'].update(None, formation_setup['strategy'])

        # Ship throttle should be master_speed (100) / ship_max (100) = 1.0
        assert formation_setup['ship'].engine_throttle == 1.0
        formation_setup['ship'].thrust_forward.assert_called()


@pytest.fixture
def ram_setup():
    controller = MagicMock()
    behavior = RamBehavior(controller)
    target = MagicMock()
    target.position = pygame.math.Vector2(100, 100)
    strategy = {}

    return {
        'controller': controller,
        'behavior': behavior,
        'target': target,
        'strategy': strategy
    }


class TestRamBehavior:

    def test_ram_parameters(self, ram_setup):
        """Verify RamBehavior calls navigate_to with correct params."""
        ram_setup['behavior'].update(ram_setup['target'], ram_setup['strategy'])

        ram_setup['controller'].navigate_to.assert_called_with(
            ram_setup['target'].position,
            stop_dist=0,
            precise=False
        )
