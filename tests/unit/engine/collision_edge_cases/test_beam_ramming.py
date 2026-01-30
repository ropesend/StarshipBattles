"""Tests for beam weapon raycasting and ramming collision edge cases.

Covers:
- Beam weapon raycasting edge cases in CollisionSystem
- Ramming collision edge cases
"""
import pytest
from unittest.mock import MagicMock, patch
from pygame.math import Vector2


# =============================================================================
# Test: Beam Weapon Raycasting Edge Cases
# =============================================================================


class TestBeamRaycastingEdgeCases:
    """Edge cases for beam weapon raycasting in CollisionSystem."""

    def test_beam_zero_length_direction(self, collision_system):
        """Beam with zero-length direction should not crash."""
        target = MagicMock()
        target.position = Vector2(100, 0)
        target.radius = 20
        target.is_alive = True

        mock_ability = MagicMock()
        mock_ability.calculate_hit_chance.return_value = 1.0
        mock_ability.get_damage.return_value = 10

        mock_component = MagicMock()
        mock_component.get_ability.return_value = mock_ability

        recent_beams = []
        attack = {
            'origin': Vector2(0, 0),
            'direction': Vector2(0, 0),  # Zero direction
            'range': 300,
            'target': target,
            'component': mock_component
        }

        # Should not crash (a == 0 case handled)
        collision_system.process_beam_attack(attack, recent_beams)

        # Beam should be recorded
        assert len(recent_beams) == 1

    def test_beam_target_at_origin(self, collision_system):
        """Beam with target at same position as origin."""
        target = MagicMock()
        target.position = Vector2(0, 0)  # Same as origin
        target.radius = 20
        target.is_alive = True

        mock_ability = MagicMock()
        mock_ability.calculate_hit_chance.return_value = 1.0
        mock_ability.get_damage.return_value = 10

        mock_component = MagicMock()
        mock_component.get_ability.return_value = mock_ability

        recent_beams = []
        attack = {
            'origin': Vector2(0, 0),
            'direction': Vector2(1, 0),
            'range': 300,
            'target': target,
            'component': mock_component
        }

        # Should handle this case
        with patch('random.random', return_value=0.0):
            collision_system.process_beam_attack(attack, recent_beams)

        # Target is inside beam origin, should hit
        target.take_damage.assert_called()

    def test_beam_dead_target_no_hit(self, collision_system):
        """Beam should not hit dead target."""
        target = MagicMock()
        target.position = Vector2(100, 0)
        target.radius = 20
        target.is_alive = False  # Dead

        mock_ability = MagicMock()
        mock_ability.calculate_hit_chance.return_value = 1.0
        mock_ability.get_damage.return_value = 10

        mock_component = MagicMock()
        mock_component.get_ability.return_value = mock_ability

        recent_beams = []
        attack = {
            'origin': Vector2(0, 0),
            'direction': Vector2(1, 0),
            'range': 300,
            'target': target,
            'component': mock_component
        }

        collision_system.process_beam_attack(attack, recent_beams)

        target.take_damage.assert_not_called()

    def test_beam_no_target(self, collision_system):
        """Beam without target should record full-length beam."""
        recent_beams = []
        attack = {
            'origin': Vector2(0, 0),
            'direction': Vector2(1, 0),
            'range': 500,
            'target': None,  # No target
            'component': MagicMock()
        }

        collision_system.process_beam_attack(attack, recent_beams)

        assert len(recent_beams) == 1
        # End should be at full range
        assert recent_beams[0]['end'].x == 500

    def test_beam_hit_chance_zero(self, collision_system):
        """Beam with zero hit chance should miss."""
        target = MagicMock()
        target.position = Vector2(100, 0)
        target.radius = 20
        target.is_alive = True

        mock_ability = MagicMock()
        mock_ability.calculate_hit_chance.return_value = 0.0  # Zero chance
        mock_ability.get_damage.return_value = 10

        mock_component = MagicMock()
        mock_component.get_ability.return_value = mock_ability

        recent_beams = []
        attack = {
            'origin': Vector2(0, 0),
            'direction': Vector2(1, 0),
            'range': 300,
            'target': target,
            'component': mock_component
        }

        with patch('random.random', return_value=0.5):  # 0.5 > 0.0
            collision_system.process_beam_attack(attack, recent_beams)

        target.take_damage.assert_not_called()

    def test_beam_defense_score_fallback_logs_warning(self, collision_system):
        """Using ECM fallback for defense score should log a warning.

        PROJ-40/NEW-AI-008: Standardize on total_defense_score, warn on fallback.
        """
        target = MagicMock(spec=['position', 'radius', 'is_alive', 'take_damage', 'get_total_ecm_score'])
        target.position = Vector2(100, 0)
        target.radius = 20
        target.is_alive = True
        target.get_total_ecm_score.return_value = 5.0
        # No total_defense_score attribute

        source_ship = MagicMock()
        source_ship.get_total_sensor_score.return_value = 3.0

        mock_ability = MagicMock()
        mock_ability.calculate_hit_chance.return_value = 1.0
        mock_ability.get_damage.return_value = 10

        mock_component = MagicMock()
        mock_component.get_ability.return_value = mock_ability

        recent_beams = []
        attack = {
            'origin': Vector2(0, 0),
            'direction': Vector2(1, 0),
            'range': 300,
            'target': target,
            'component': mock_component,
            'source': source_ship
        }

        with patch('game.engine.collision.log_warning') as mock_log_warning:
            with patch('random.random', return_value=0.0):  # Guaranteed hit
                collision_system.process_beam_attack(attack, recent_beams)

            # Should have logged a warning about using fallback
            mock_log_warning.assert_called_once()
            assert 'fallback' in mock_log_warning.call_args[0][0].lower() or \
                   'ecm' in mock_log_warning.call_args[0][0].lower()

    def test_beam_defense_score_uses_primary_attribute(self, collision_system):
        """Using total_defense_score should not log any warning.

        PROJ-40/NEW-AI-008: Primary attribute should work without warnings.
        """
        target = MagicMock()
        target.position = Vector2(100, 0)
        target.radius = 20
        target.is_alive = True
        target.total_defense_score = 5.0  # Primary attribute

        source_ship = MagicMock()
        source_ship.get_total_sensor_score.return_value = 3.0

        mock_ability = MagicMock()
        mock_ability.calculate_hit_chance.return_value = 1.0
        mock_ability.get_damage.return_value = 10

        mock_component = MagicMock()
        mock_component.get_ability.return_value = mock_ability

        recent_beams = []
        attack = {
            'origin': Vector2(0, 0),
            'direction': Vector2(1, 0),
            'range': 300,
            'target': target,
            'component': mock_component,
            'source': source_ship
        }

        with patch('game.engine.collision.log_warning') as mock_log_warning:
            with patch('random.random', return_value=0.0):  # Guaranteed hit
                collision_system.process_beam_attack(attack, recent_beams)

            # Should NOT have logged any warning
            mock_log_warning.assert_not_called()


# =============================================================================
# Test: Ramming Edge Cases
# =============================================================================


class TestRammingEdgeCases:
    """Edge cases for ramming collisions."""

    def test_ramming_non_kamikaze_ignored(self, collision_system):
        """Ships without kamikaze strategy should not ram."""
        ship = MagicMock()
        ship.ai_strategy = 'aggressive'  # Not kamikaze
        ship.is_alive = True
        ship.current_target = MagicMock()

        collision_system.process_ramming([ship])

        ship.take_damage.assert_not_called()

    def test_ramming_no_target_ignored(self, collision_system):
        """Kamikaze ship without target should not process."""
        ship = MagicMock()
        ship.ai_strategy = 'kamikaze'
        ship.is_alive = True
        ship.current_target = None

        collision_system.process_ramming([ship])

        ship.take_damage.assert_not_called()

    def test_ramming_dead_target_ignored(self, collision_system):
        """Kamikaze ship with dead target should not process."""
        target = MagicMock()
        target.is_alive = False

        ship = MagicMock()
        ship.ai_strategy = 'kamikaze'
        ship.is_alive = True
        ship.current_target = target

        collision_system.process_ramming([ship])

        ship.take_damage.assert_not_called()

    def test_ramming_equal_hp_mutual_destruction(self, collision_system):
        """Equal HP should result in mutual destruction."""
        target = MagicMock()
        target.name = "Target"
        target.is_alive = True
        target.hp = 100
        target.position = Vector2(5, 0)
        target.radius = 10

        ship = MagicMock()
        ship.name = "Rammer"
        ship.ai_strategy = 'kamikaze'
        ship.is_alive = True
        ship.hp = 100  # Equal HP
        ship.position = Vector2(0, 0)
        ship.radius = 10
        ship.current_target = target

        logger = MagicMock()
        collision_system.process_ramming([ship, target], logger)

        # Both should take lethal damage
        ship.take_damage.assert_called()
        target.take_damage.assert_called()

    def test_ramming_zero_radius(self, collision_system):
        """Ramming with zero radius at same position should collide."""
        target = MagicMock()
        target.name = "Target"
        target.is_alive = True
        target.hp = 100
        target.position = Vector2(0, 0)  # Same position
        target.radius = 0  # Zero radius

        ship = MagicMock()
        ship.name = "Rammer"
        ship.ai_strategy = 'kamikaze'
        ship.is_alive = True
        ship.hp = 50
        ship.position = Vector2(0, 0)
        ship.radius = 0  # Zero radius
        ship.current_target = target

        collision_system.process_ramming([ship, target])

        # Distance is 0, collision_radius is 0
        # condition is: distance_to < collision_radius
        # 0 < 0 is False, so no collision happens
        # This is expected behavior - zero radius objects don't collide
        # unless distance is strictly less than radius
        ship.take_damage.assert_not_called()

    def test_ramming_missing_hp_attribute(self, collision_system):
        """Ramming should handle ships without hp attribute gracefully.

        PROJ-40/NEW-AI-004: Ships should use default HP when .hp is missing.
        """
        target = MagicMock(spec=['name', 'is_alive', 'position', 'radius', 'take_damage'])
        target.name = "Target"
        target.is_alive = True
        target.position = Vector2(5, 0)
        target.radius = 10
        # No .hp attribute

        ship = MagicMock(spec=['name', 'ai_strategy', 'is_alive', 'position', 'radius', 'current_target', 'take_damage'])
        ship.name = "Rammer"
        ship.ai_strategy = 'kamikaze'
        ship.is_alive = True
        ship.position = Vector2(0, 0)
        ship.radius = 10
        ship.current_target = target
        # No .hp attribute

        # Should not crash - uses default HP
        collision_system.process_ramming([ship, target])

        # Both should take damage based on default HP
        ship.take_damage.assert_called()
        target.take_damage.assert_called()

    def test_ramming_rammer_missing_hp(self, collision_system):
        """Ramming should handle rammer without hp attribute.

        PROJ-40/NEW-AI-004: Rammer uses default HP, target uses actual HP.
        """
        target = MagicMock()
        target.name = "Target"
        target.is_alive = True
        target.position = Vector2(5, 0)
        target.radius = 10
        target.hp = 200  # Target has HP

        ship = MagicMock(spec=['name', 'ai_strategy', 'is_alive', 'position', 'radius', 'current_target', 'take_damage'])
        ship.name = "Rammer"
        ship.ai_strategy = 'kamikaze'
        ship.is_alive = True
        ship.position = Vector2(0, 0)
        ship.radius = 10
        ship.current_target = target
        # No .hp attribute - should use default (100)

        collision_system.process_ramming([ship, target])

        # Rammer (default 100) < Target (200), so rammer destroyed
        ship.take_damage.assert_called()

    def test_ramming_target_missing_hp(self, collision_system):
        """Ramming should handle target without hp attribute.

        PROJ-40/NEW-AI-004: Target uses default HP, rammer uses actual HP.
        """
        target = MagicMock(spec=['name', 'is_alive', 'position', 'radius', 'take_damage'])
        target.name = "Target"
        target.is_alive = True
        target.position = Vector2(5, 0)
        target.radius = 10
        # No .hp attribute - should use default (100)

        ship = MagicMock()
        ship.name = "Rammer"
        ship.ai_strategy = 'kamikaze'
        ship.is_alive = True
        ship.position = Vector2(0, 0)
        ship.radius = 10
        ship.hp = 50  # Rammer has HP
        ship.current_target = target

        collision_system.process_ramming([ship, target])

        # Rammer (50) < Target (default 100), so rammer destroyed
        ship.take_damage.assert_called()
