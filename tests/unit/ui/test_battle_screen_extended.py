import pytest
import pygame
from unittest.mock import MagicMock
from game.ui.screens.battle_screen import BattleScreen
from game.simulation.entities.ship import Ship


class TestBattleScreenExtended:
    """Test BattleScreen beam attack processing logic."""

    def test_process_beam_attack_logic(self, fresh_registries):
        """Verify _process_beam_attack applies damage to target."""
        scene = BattleScreen(1000, 1000)
        ship = Ship("Target", 0, 0, (255,255,255), team_id=1, registries=fresh_registries)
        ship.radius = 20
        # Mock take_damage on combat engine
        ship.combat_engine.take_damage = MagicMock()

        # Mock the ability that will be returned by get_ability
        mock_ability = MagicMock()
        mock_ability.calculate_hit_chance.return_value = 1.0
        mock_ability.get_damage.return_value = 25

        # Mock the component to return the mock ability
        mock_comp = MagicMock()
        mock_comp.shots_hit = 0
        mock_comp.get_ability.return_value = mock_ability

        beam = {
            'type': 'beam',
            'damage': 25,
            'target': ship,
            'origin': pygame.math.Vector2(0,0),
            'direction': pygame.math.Vector2(1,0),
            'range': 100,
            'component': mock_comp
        }

        scene.engine.collision_system.process_beam_attack(beam, scene.engine.recent_beams)
        ship.combat_engine.take_damage.assert_called_with(25)
