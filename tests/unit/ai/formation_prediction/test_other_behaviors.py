"""
Tests for other AI behaviors in behaviors.py.

Tests FleeBehavior, RamBehavior, AttackRunBehavior, OrbitBehavior,
DoNothingBehavior, StationaryFireBehavior, StraightLineBehavior, RotateOnlyBehavior.
"""

import pytest
import pygame
from unittest.mock import MagicMock


class TestOtherBehaviors:
    """Tests for other AI behaviors in behaviors.py."""

    def test_flee_behavior_basic(self, mock_controller, pygame_init):
        """FleeBehavior should navigate away from target."""
        from game.ai.behaviors import FleeBehavior

        mock_ship = MagicMock()
        mock_ship.position = pygame.math.Vector2(0, 0)
        mock_ship.comp_trigger_pulled = True
        mock_controller.ship = mock_ship

        # Interface methods
        mock_ship.get_position.return_value = mock_ship.position
        mock_ship.set_trigger_pulled.side_effect = lambda v: setattr(mock_ship, 'comp_trigger_pulled', v)

        target = MagicMock()
        target.position = pygame.math.Vector2(100, 0)

        behavior = FleeBehavior(mock_controller)
        behavior.update(target, {'fire_while_retreating': False})

        # Should set trigger to false when not firing while retreating
        assert mock_ship.comp_trigger_pulled is False

        # Should navigate away
        mock_controller.navigate_to.assert_called_once()
        nav_pos = mock_controller.navigate_to.call_args[0][0]

        # Navigate position should be away from target
        assert nav_pos.x < 0  # Opposite direction from target

    def test_ram_behavior_basic(self, mock_controller, pygame_init):
        """RamBehavior should navigate toward target."""
        from game.ai.behaviors import RamBehavior

        mock_ship = MagicMock()
        mock_ship.position = pygame.math.Vector2(0, 0)
        mock_controller.ship = mock_ship

        target = MagicMock()
        target.position = pygame.math.Vector2(100, 100)

        behavior = RamBehavior(mock_controller)
        behavior.update(target, {})

        # Should navigate to target
        mock_controller.navigate_to.assert_called_once_with(
            target.position, stop_dist=0, precise=False
        )

    def test_attack_run_behavior_approach(self, mock_controller, pygame_init):
        """AttackRunBehavior should approach initially."""
        from game.ai.behaviors import AttackRunBehavior

        mock_ship = MagicMock()
        mock_ship.position = pygame.math.Vector2(0, 0)
        mock_ship.max_weapon_range = 1000
        mock_controller.ship = mock_ship

        # Interface methods
        mock_ship.get_position.return_value = mock_ship.position
        mock_ship.get_weapon_range.return_value = mock_ship.max_weapon_range

        target = MagicMock()
        target.position = pygame.math.Vector2(2000, 0)  # Far away

        behavior = AttackRunBehavior(mock_controller)
        behavior.enter()

        assert behavior.attack_state == 'approach'

        behavior.update(target, {})

        # Should navigate toward target
        mock_controller.navigate_to.assert_called()

    def test_orbit_behavior_no_target(self, mock_controller, pygame_init):
        """OrbitBehavior should do nothing with no target."""
        from game.ai.behaviors import OrbitBehavior

        mock_ship = MagicMock()
        mock_controller.ship = mock_ship

        behavior = OrbitBehavior(mock_controller)
        behavior.update(None, {})

        # Should not call navigate_to
        mock_controller.navigate_to.assert_not_called()


class TestSpecialBehaviors:
    """Tests for special test behaviors."""

    def test_do_nothing_disables_firing(self, mock_controller):
        """DoNothingBehavior should disable firing."""
        from game.ai.behaviors import DoNothingBehavior

        mock_ship = MagicMock()
        mock_ship.comp_trigger_pulled = True
        mock_controller.ship = mock_ship

        # Interface method
        mock_ship.set_trigger_pulled.side_effect = lambda v: setattr(mock_ship, 'comp_trigger_pulled', v)

        behavior = DoNothingBehavior(mock_controller)
        behavior.update(None, {})

        assert mock_ship.comp_trigger_pulled is False

    def test_stationary_fire_allows_firing(self, mock_controller):
        """StationaryFireBehavior should allow firing."""
        from game.ai.behaviors import StationaryFireBehavior

        mock_ship = MagicMock()
        mock_ship.comp_trigger_pulled = True
        mock_controller.ship = mock_ship

        behavior = StationaryFireBehavior(mock_controller)
        behavior.update(None, {})

        # Should not change trigger state
        assert mock_ship.comp_trigger_pulled is True

    def test_straight_line_thrusts_forward(self, mock_controller):
        """StraightLineBehavior should thrust forward."""
        from game.ai.behaviors import StraightLineBehavior

        mock_ship = MagicMock()
        mock_controller.ship = mock_ship

        behavior = StraightLineBehavior(mock_controller)
        behavior.update(None, {})

        mock_ship.thrust_forward.assert_called_once()

    def test_rotate_only_rotates(self, mock_controller):
        """RotateOnlyBehavior should only rotate."""
        from game.ai.behaviors import RotateOnlyBehavior

        mock_ship = MagicMock()
        mock_controller.ship = mock_ship

        behavior = RotateOnlyBehavior(mock_controller)
        behavior.update(None, {'rotation_direction': 1})

        mock_ship.rotate.assert_called_once_with(1)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
